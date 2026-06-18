"""
test_parallel_executor.py

Unit tests for the opt-in parallel pre-warm executor: all-or-nothing fan-out, the
content-addressed temp cache, the record/render phases, memoisation, and the
collision-safe cache key.
"""
import threading

import pandas as pd
import pytest

from eds4jinja2.builders.parallel_executor import (
    run_parallel, FetchCache, FetchCoordinator, CachingDataSource, Phase,
    wrap_builders, TABULAR, TREE,
)


# --- run_parallel -----------------------------------------------------------

def test_run_parallel_preserves_order_and_runs_concurrently():
    barrier = threading.Barrier(4)

    def thunk(i):
        barrier.wait(timeout=5)  # only completes if all 4 run at once
        return i * 10

    results = run_parallel([(lambda i=i: thunk(i)) for i in range(4)], max_workers=4)
    assert results == [0, 10, 20, 30]


def test_run_parallel_all_or_nothing_reraises():
    def boom():
        raise ValueError("kaboom")

    with pytest.raises(ValueError, match="kaboom"):
        run_parallel([lambda: 1, boom, lambda: 3], max_workers=3)


# --- FetchCache -------------------------------------------------------------

def test_fetch_cache_roundtrip_and_cleanup():
    cache = FetchCache()
    payload = (pd.DataFrame({"a": [1, 2]}), None)
    assert not cache.has("k")
    cache.put("k", payload)
    assert cache.has("k")
    df, error = cache.get("k")
    assert error is None and df["a"].tolist() == [1, 2]
    directory = cache.directory
    cache.cleanup()
    assert not directory.exists()


# --- Fake data source -------------------------------------------------------

class _FakeDS:
    def __init__(self):
        self.calls = 0
        self._q = None

    def with_query(self, q):
        self._q = q
        return self

    def fetch_tabular(self):
        self.calls += 1
        return pd.DataFrame({"q": [self._q]}), None

    def fetch_tree(self):
        self.calls += 1
        return {"head": {"vars": ["q"]}, "results": {"bindings": []}}, None

    def __str__(self):
        return "fake"


# --- record / prewarm / render ---------------------------------------------

def test_record_returns_placeholder_without_executing():
    coordinator = FetchCoordinator()
    ds = _FakeDS()
    proxy = CachingDataSource(ds, coordinator, source_id=("from_x", (), ()))
    df, error = proxy.with_query("Q1").fetch_tabular()
    assert error is None and df.empty   # placeholder, not real result
    assert ds.calls == 0                # real fetch never invoked during record
    coordinator.cache.cleanup()


def test_prewarm_then_render_serves_from_cache():
    coordinator = FetchCoordinator()
    ds = _FakeDS()
    proxy = CachingDataSource(ds, coordinator, source_id=("from_x", (), ()))
    proxy.with_query("Q1").fetch_tabular()      # record
    coordinator.prewarm(max_workers=2)          # executes once
    coordinator.set_phase(Phase.RENDER)
    df, error = CachingDataSource(ds, coordinator, ("from_x", (), ())).with_query("Q1").fetch_tabular()
    assert error is None and df["q"].tolist() == ["Q1"]   # real result, from cache
    assert ds.calls == 1                                   # executed exactly once (memoised)
    coordinator.cache.cleanup()


def test_render_cache_miss_runs_live():
    coordinator = FetchCoordinator()
    ds = _FakeDS()
    coordinator.set_phase(Phase.RENDER)  # nothing pre-warmed
    df, error = CachingDataSource(ds, coordinator, ("from_x", (), ())).with_query("NEW").fetch_tabular()
    assert error is None and df["q"].tolist() == ["NEW"]
    assert ds.calls == 1
    coordinator.cache.cleanup()


def test_identical_queries_recorded_once():
    coordinator = FetchCoordinator()
    ds = _FakeDS()
    for _ in range(3):
        CachingDataSource(ds, coordinator, ("from_x", (), ())).with_query("SAME").fetch_tabular()
    coordinator.prewarm(max_workers=4)
    assert ds.calls == 1  # three identical fetches collapsed to one
    coordinator.cache.cleanup()


def test_distinct_queries_get_distinct_keys():
    coordinator = FetchCoordinator()
    ds = _FakeDS()
    CachingDataSource(ds, coordinator, ("from_x", (), ())).with_query("A").fetch_tabular()
    CachingDataSource(ds, coordinator, ("from_x", (), ())).with_query("B").fetch_tabular()
    coordinator.prewarm(max_workers=4)
    assert ds.calls == 2
    coordinator.cache.cleanup()


def test_prewarm_aborts_on_fetch_error():
    class _FailingDS(_FakeDS):
        def fetch_tabular(self):
            return None, "boom"

    coordinator = FetchCoordinator()
    CachingDataSource(_FailingDS(), coordinator, ("from_x", (), ())).with_query("Q").fetch_tabular()
    with pytest.raises(RuntimeError, match="all-or-nothing"):
        coordinator.prewarm(max_workers=2)
    coordinator.cache.cleanup()


# --- wrap_builders ----------------------------------------------------------

def test_wrap_builders_only_wraps_named_data_sources():
    coordinator = FetchCoordinator()
    builders = {"from_x": lambda src: _FakeDS(), "helper": lambda x: x * 2}
    wrapped = wrap_builders(builders, {"from_x"}, coordinator)
    assert isinstance(wrapped["from_x"]("s"), CachingDataSource)
    assert wrapped["helper"](3) == 6  # untouched
    coordinator.cache.cleanup()
