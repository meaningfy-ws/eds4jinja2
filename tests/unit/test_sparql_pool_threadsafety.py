"""
test_sparql_pool_threadsafety.py

The remote SPARQL pool must not share one mutable SPARQLWrapper across threads — concurrent
queries to the same endpoint would clobber each other's query string. The pool is per-thread:
reused within a thread (single-threaded behaviour unchanged), isolated across threads.
"""
import threading
from concurrent.futures import ThreadPoolExecutor

from eds4jinja2.adapters.remote_sparql_ds import SPARQLClientPool

ENDPOINT = "http://example.org/sparql"


def test_same_wrapper_reused_within_a_thread():
    a = SPARQLClientPool.create_or_reuse_connection(ENDPOINT)
    b = SPARQLClientPool.create_or_reuse_connection(ENDPOINT)
    assert a is b


def test_distinct_wrappers_across_threads():
    wrappers = {}
    barrier = threading.Barrier(2)  # force both threads alive at the same time

    def grab(name):
        barrier.wait()
        wrappers[name] = SPARQLClientPool.create_or_reuse_connection(ENDPOINT)

    t1 = threading.Thread(target=grab, args=("t1",))
    t2 = threading.Thread(target=grab, args=("t2",))
    t1.start(); t2.start(); t1.join(); t2.join()

    assert wrappers["t1"] is not wrappers["t2"]


def test_concurrent_queries_do_not_clobber_each_other():
    # Each thread sets its own query and must read back exactly that query.
    results = {}

    def set_and_read(query):
        wrapper = SPARQLClientPool.create_or_reuse_connection(ENDPOINT)
        wrapper.setQuery(query)
        results[query] = wrapper.queryString

    queries = [f"SELECT * WHERE {{ ?s ?p {i} }}" for i in range(8)]
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(set_and_read, queries))

    for query in queries:
        assert results[query] == query
