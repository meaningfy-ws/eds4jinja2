#!/usr/bin/python3

# graph_store.py
# A pluggable in-memory RDF graph store: load RDF sources once, query many times.

"""
The built-in graph store lets eds4jinja2 *load* RDF file(s)/URL(s) into an in-memory
graph (configurable engine: rdflib by default, oxigraph opt-in) and query it — the
"generate a report directly from RDF files, no SPARQL server" scenario.

It is the additive file-loading layer beneath :class:`InMemorySPARQLDataSource`: the
``from_rdf`` template builder composes ``InMemorySPARQLDataSource(make_graph_store(...).query)``.
Sources are parsed exactly once at construction, fixing the per-query re-parse smell of
``RDFFileDataSource``.

``pyoxigraph`` is reached only through :class:`OxigraphGraphStore` and is imported lazily,
so it stays an opt-in extra (``pip install eds4jinja2[oxigraph]``); the rdflib path needs
no extra dependency.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Union

import rdflib

from eds4jinja2.models.data_source import Engine

DEFAULT_RDF_FORMAT = "application/n-triples"

# Map a file extension to an RDF media type, used when loading remote sources (URLs) for
# the oxigraph engine, which parses bytes rather than fetching URLs itself.
_EXTENSION_TO_MEDIA_TYPE = {
    ".ttl": "text/turtle",
    ".nt": "application/n-triples",
    ".n3": "text/n3",
    ".rdf": "application/rdf+xml",
    ".xml": "application/rdf+xml",
    ".owl": "application/rdf+xml",
    ".jsonld": "application/ld+json",
    ".json": "application/ld+json",
    ".nq": "application/n-quads",
    ".trig": "application/trig",
}

OXIGRAPH_MISSING_MESSAGE = (
    "The 'oxigraph' engine requires pyoxigraph, which is not installed. "
    "Install it with: pip install eds4jinja2[oxigraph]")

Sources = Union[str, Path, List[Union[str, Path]]]


class GraphStorePort(ABC):
    """ A minimal port: load RDF sources into the held graph, and run SPARQL queries. """

    @abstractmethod
    def load(self, source: str) -> None:
        """ Parse a single RDF source (file path or URL) into the in-memory graph. """

    @abstractmethod
    def query(self, sparql: str):
        """ Run a SPARQL query, returning an engine-native result object that
        :class:`InMemorySPARQLDataSource` can normalise. """


class RdflibGraphStore(GraphStorePort):
    """ In-memory store backed by an ``rdflib.Graph`` (the default engine). """

    def __init__(self, graph: Optional[rdflib.Graph] = None):
        self._graph = graph if graph is not None else rdflib.Graph()

    def load(self, source: str) -> None:
        # rdflib.parse handles both local paths and URLs and guesses the format.
        self._graph.parse(str(source))

    def query(self, sparql: str):
        return self._graph.query(sparql)

    @property
    def graph(self) -> rdflib.Graph:
        return self._graph


class OxigraphGraphStore(GraphStorePort):
    """ In-memory store backed by a pyoxigraph ``Store`` (opt-in, lazily imported). """

    def __init__(self, store=None):
        pyoxigraph = _import_pyoxigraph()
        self._store = store if store is not None else pyoxigraph.Store()

    def load(self, source: str) -> None:
        source = str(source)
        media_type = _media_type_for(source)
        if _is_url(source):
            import requests
            response = requests.get(source)
            response.raise_for_status()
            self._store.load(response.content, media_type)
        else:
            self._store.load(path=source, format=media_type)

    def query(self, sparql: str):
        return self._store.query(sparql)

    @property
    def store(self):
        return self._store


def make_graph_store(engine: Engine = Engine.RDFLIB, sources: Sources = None,
                     graph=None) -> GraphStorePort:
    """
        Build a graph store for the given engine and load each source exactly once.

    :param engine: ``Engine.RDFLIB`` (default) or ``Engine.OXIGRAPH``
    :param sources: a single file path/URL or an iterable of them
    :param graph: an existing native graph/store to wrap instead of creating a fresh one
    """
    engine = Engine(engine)
    store: GraphStorePort = (RdflibGraphStore(graph) if engine == Engine.RDFLIB
                             else OxigraphGraphStore(graph))
    for source in _as_source_list(sources):
        store.load(str(source))
    return store


def _as_source_list(sources: Sources) -> List[Union[str, Path]]:
    if not sources:
        return []
    if isinstance(sources, (str, Path)):
        return [sources]
    return list(sources)


def _is_url(source: str) -> bool:
    return source.startswith("http://") or source.startswith("https://")


def _media_type_for(source: str) -> str:
    return _EXTENSION_TO_MEDIA_TYPE.get(Path(source).suffix.lower(), DEFAULT_RDF_FORMAT)


def _import_pyoxigraph():
    try:
        import pyoxigraph
        return pyoxigraph
    except ImportError as error:
        raise ImportError(OXIGRAPH_MISSING_MESSAGE) from error
