#!/usr/bin/python3

# parallel_executor.py
# Opt-in parallel pre-warm of report data fetches.

"""
Large reports are slow because Jinja2 renders sequentially and each ``fetch_*`` blocks on a
SPARQL query. Jinja2 rendering itself cannot be parallelised, so the lever is to decouple data
*fetching* from rendering:

1. **Record** — render the template once into a throwaway buffer; every ``fetch_*`` registers
   its (source, query, method) unit and returns an empty placeholder instead of executing.
2. **Pre-warm** — run every recorded unit concurrently on a thread pool, staging each result in
   a temp-folder cache keyed by a collision-safe hash. **All-or-nothing**: any failure aborts
   the whole report (no partial output).
3. **Render** — render for real; each ``fetch_*`` serves its result from the cache. A query not
   seen during recording (data-dependent control flow) runs live as a graceful fallback.
4. **Cleanup** — the temp folder is removed afterwards, on success and on failure alike.

Concurrency is threads-only via a small :class:`Executor` seam (a future Celery/process backend
could slot in here). Network I/O and oxigraph in-memory queries release the GIL, so threads give
real speed-up; rdflib in-memory queries are GIL-bound (correct, limited speed-up).

This is entirely opt-in: with ``parallelism`` unset or ``1`` the report builder never touches any
of this and behaves exactly as before.
"""
import hashlib
import pickle
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
from pathlib import Path

# config / structural constants (no free strings)
PARALLELISM = "parallelism"
DEFAULT_PARALLELISM = 1
PREWARM_TEMP_DIR = "prewarm_temp_dir"

TABULAR = "tabular"
TREE = "tree"

_FLUENT_METHODS = ("with_query", "with_query_from_file", "with_uri")


class Phase(Enum):
    RECORD = "record"
    RENDER = "render"


def run_parallel(thunks, max_workers):
    """
        Run all thunks concurrently and return their results in input order.

        All-or-nothing: the first thunk to raise re-raises here (after the pool drains), so the
        caller can abort the whole report without using any partial result.
    """
    thunks = list(thunks)
    results = [None] * len(thunks)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(thunk): index for index, thunk in enumerate(thunks)}
        for future in as_completed(futures):
            results[futures[future]] = future.result()  # re-raises the first failure
    return results


class FetchCache:
    """ A temp-folder-backed, content-addressed cache of (content, error) fetch results.

    Values are pickled because they mix pandas DataFrames with SPARQL-JSON dicts. This is
    SAFE: the cache only ever loads data this same process wrote, into a temp dir it created
    during one report build — never untrusted input. # ponytail: pickle, internal-only cache
    """

    def __init__(self, directory=None):
        self._dir = Path(directory) if directory else Path(tempfile.mkdtemp(prefix="eds4jinja2-prewarm-"))

    @property
    def directory(self) -> Path:
        return self._dir

    def _path(self, key: str) -> Path:
        return self._dir / f"{key}.pickle"

    def has(self, key: str) -> bool:
        return self._path(key).exists()

    def put(self, key: str, value) -> None:
        with open(self._path(key), "wb") as handle:
            pickle.dump(value, handle)

    def get(self, key: str):
        with open(self._path(key), "rb") as handle:
            return pickle.load(handle)

    def cleanup(self) -> None:
        shutil.rmtree(self._dir, ignore_errors=True)


class FetchCoordinator:
    """
        Drives the record -> pre-warm -> render phases and owns the result cache.
        One coordinator per report build.
    """

    def __init__(self, cache: FetchCache = None):
        self._cache = cache if cache is not None else FetchCache()
        self._phase = Phase.RECORD
        self._registry = {}  # key -> (real_ds, method); dict dedupes identical fetches (memoisation)

    @property
    def cache(self) -> FetchCache:
        return self._cache

    def set_phase(self, phase: Phase) -> None:
        self._phase = phase

    def fetch(self, real_ds, source_id, query_repr, method):
        key = _cache_key(source_id, query_repr, method)
        if self._phase is Phase.RECORD:
            self._registry[key] = (real_ds, method)  # identical key overwrites -> fetched once
            return _placeholder(method)
        if self._cache.has(key):
            return self._cache.get(key)
        return _invoke(real_ds, method)  # cache miss -> graceful live fetch

    def prewarm(self, max_workers: int) -> None:
        items = list(self._registry.items())
        if not items:
            return
        thunks = [(lambda ds=ds, m=m: _invoke(ds, m)) for _, (ds, m) in items]
        results = run_parallel(thunks, max_workers)
        for (key, _), (content, error) in zip(items, results):
            if error is not None:
                raise RuntimeError(f"Pre-warm fetch failed (all-or-nothing): {error}")
            self._cache.put(key, (content, error))

    def cleanup(self) -> None:
        self._cache.cleanup()


class CachingDataSource:
    """
        A transparent proxy over a real DataSource. It captures the query arguments (so the cache
        key is exact, never the truncated ``__str__``), keeps the fluent chaining intact, and
        routes ``fetch_*`` through the coordinator.
    """

    def __init__(self, real, coordinator: FetchCoordinator, source_id):
        self._real = real
        self._coordinator = coordinator
        self._source_id = source_id
        self._query_repr = None

    def with_query(self, *args, **kwargs):
        self._query_repr = ("with_query", args, _sorted_kwargs(kwargs))
        self._real.with_query(*args, **kwargs)
        return self

    def with_query_from_file(self, *args, **kwargs):
        self._query_repr = ("with_query_from_file", args, _sorted_kwargs(kwargs))
        self._real.with_query_from_file(*args, **kwargs)
        return self

    def with_uri(self, *args, **kwargs):
        self._query_repr = ("with_uri", args, _sorted_kwargs(kwargs))
        self._real.with_uri(*args, **kwargs)
        return self

    def fetch_tabular(self):
        return self._coordinator.fetch(self._real, self._source_id, self._query_repr, TABULAR)

    def fetch_tree(self):
        return self._coordinator.fetch(self._real, self._source_id, self._query_repr, TREE)

    def __getattr__(self, name):
        # passthrough for anything we don't intercept (keeps the proxy faithful)
        return getattr(self._real, name)


def wrap_builders(builders: dict, builder_names, coordinator: FetchCoordinator) -> dict:
    """
        Return a copy of ``builders`` where each data-source builder (by name) yields a
        CachingDataSource. Non-data-source helpers are passed through untouched.
    """
    wrapped = dict(builders)
    for name in builder_names:
        if name not in wrapped:
            continue
        original = wrapped[name]
        wrapped[name] = _make_wrapping_builder(name, original, coordinator)
    return wrapped


def _make_wrapping_builder(name, original, coordinator):
    def builder(*args, **kwargs):
        real = original(*args, **kwargs)
        source_id = (name, args, _sorted_kwargs(kwargs))
        return CachingDataSource(real, coordinator, source_id)
    return builder


def _sorted_kwargs(kwargs: dict):
    return tuple(sorted(kwargs.items())) if kwargs else ()


def _cache_key(source_id, query_repr, method) -> str:
    return hashlib.sha256(repr((source_id, query_repr, method)).encode("utf-8")).hexdigest()


def _invoke(real_ds, method):
    return getattr(real_ds, f"fetch_{method}")()


def _placeholder(method):
    import pandas as pd
    if method == TABULAR:
        return pd.DataFrame(), None
    return {"head": {"vars": []}, "results": {"bindings": []}}, None
