#!/usr/bin/python3

# test_namespace_handlers.py
# Date:  25/02/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
from pprint import pprint

from eds4jinja2.adapters import first_key, first_key_value, invert_dict
from eds4jinja2.adapters.namespace_handler import NamespaceInventory
from eds4jinja2.adapters.prefix_cc_fetcher import prefix_cc_lookup_prefix, prefix_cc_lookup_base_uri, prefix_cc_all


def test_prefix_cc_all():
    p = prefix_cc_all()
    assert "rdfs" in p
    assert "skos" in p
    assert "skosxl" in p
    assert len(p) > 2000


def test_first_key_in_dict():
    assert first_key({"ns0": "", "nq": "", "addf": "", "az": ""}) == "az"
    assert first_key({"addf": "", "az": "", "ab": ""}) == "ab"
    assert first_key({"ns0": "", "nq": ""}) == "nq"
    assert first_key({"": "", "nq": ""}) == ""
    assert not first_key({})
    assert not first_key(None)
    assert first_key_value({"ns0": "1", "nq": "2", "addf": "3", "az": "4"}) == "4"


def test_prefix_cc_prefix():
    assert prefix_cc_lookup_prefix("skos")["skos"] == "http://www.w3.org/2004/02/skos/core#"
    assert prefix_cc_lookup_prefix("dct")["dct"] == "http://purl.org/dc/terms/"
    assert prefix_cc_lookup_prefix("dcterms")["dcterms"] == "http://purl.org/dc/terms/"
    assert prefix_cc_lookup_prefix("rdf")["rdf"] == "http://www.w3.org/1999/02/22-rdf-syntax-ns#"


def test_prefix_cc_lookup_base_uri():
    assert "skos" in prefix_cc_lookup_base_uri("http://www.w3.org/2004/02/skos/core#")
    assert "rdf" in prefix_cc_lookup_base_uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    assert prefix_cc_lookup_base_uri("http://xmlns.com/foaf/0.1/")
    assert not prefix_cc_lookup_base_uri("http://purl.org/dc/terms/")
    assert not prefix_cc_lookup_base_uri("http://fg fdhrewyre")
    assert not prefix_cc_lookup_base_uri("http://fg/fdhrewyre")


def test_invert_dict(dummy_prefixes):
    reduced_d = invert_dict(dummy_prefixes, True)
    assert "http://www.w3.org/2002/07/owl#" in reduced_d
    unreduced_d = invert_dict(dummy_prefixes, False)

    assert "dct" in unreduced_d["http://purl.org/dc/terms/"]
    assert "dcterms" in unreduced_d["http://purl.org/dc/terms/"]


def test_ns_inventory(dummy_prefixes):
    ni = NamespaceInventory(dummy_prefixes)
    assert "dcterms" not in ni.namespaces_dict()
    assert "dct" in ni.namespaces_dict()
    assert "http://purl.org/vocab/frbr/core#" not in ni.namespaces_dict()


def test_uri_to_qname(dummy_prefixes):
    ni = NamespaceInventory(dummy_prefixes)
    assert ni.uri_to_qname("http://www.w3.org/2004/02/skos/core#Concept") == "skos:Concept"
    assert ni.uri_to_qname("http://www.w3.org/2004/02/skos/1core#Concept") == "ns2:Concept"
    assert ni.uri_to_qname("http://www.w3.org/2004/02/skos/2core#Concept") == "ns3:Concept"


def test_simplify_uri_to_qname_open(dummy_df):
    ni = NamespaceInventory()
    ni.simplify_uri_to_qname(dummy_df, target_columns=["s", "p", "o"])

    ns_inv = ni.namespaces_dict()
    assert "ns1" in ns_inv
    assert "rdf" in ns_inv
    assert "skos" in ns_inv

    idp = invert_dict(ns_inv)
    assert "http://publications.europa.eu/resource/authority/corporate-body/" in idp
    assert "http://www.w3.org/1999/02/22-rdf-syntax-ns#" in idp
    assert "http://www.w3.org/2004/02/skos/core#"


def test_simplify_uri_to_qname_close(dummy_df):
    ni = NamespaceInventory()
    ni.simplify_uri_to_qname(dummy_df, prefix_cc_lookup=False, target_columns=["s", "p", "o"])

    ns_inv = ni.namespaces_dict()
    assert "ns1" in ns_inv
    assert "rdf" in ns_inv
    assert "ns2" in ns_inv
    assert "ns3" in ns_inv


def test_new_namespace_inventory(dummy_prefixes):
    nm = NamespaceInventory(dummy_prefixes)
    assert nm.uri_to_qname(
        "http://publications.europa.eu/resource/authority/corporate-body/COB1") == "corporate-body:COB1"
    assert nm.uri_to_qname(
        "http://publications.e67u/resource/authority/corporate-body/cmdfg34") == "ns1:cmdfg34"
    assert nm.uri_to_qname("http://www.w3.org/2004/02/skos/core#Concept") == "skos:Concept"



