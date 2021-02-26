#!/usr/bin/python3

# prefix_cc_fetcher.py
# Date:  25/02/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import json

import requests

from eds4jinja2.adapters import invert_dict

PREFIX_CC_ALL_JSON = "http://prefix.cc/popular/all.file.json"
PREFIX_CC_LOOKUP_URL = "http://prefix.cc/"
PREFIX_CC_REVERSE_LOOKUP_URL = "http://prefix.cc/reverse"


def prefix_cc_lookup_prefix(prefix: str) -> str:
    """
        Lookup a prefix at prefix.cc API and return the base namespace.
    :param prefix:
    :return: the namespace definition
    """
    response = requests.get(url=PREFIX_CC_LOOKUP_URL + f"{prefix}.file.json")
    # response.raise_for_status()
    return json.loads(response.content) if response.content else None


def prefix_cc_lookup_base_uri(base_uri: str) -> str:
    """
        Lookup a base namespace on prefix.cc API and return the first prefix (shortest and first in an ordered list).
        If the base_uri is not in the namespace definitions then return None.
    :param base_uri:
    :return: the prefix
    """
    payload = {"uri": base_uri, "format": "json"}
    response = requests.get(url=PREFIX_CC_REVERSE_LOOKUP_URL, params=payload)
    if response.ok:
        namespaces = json.loads(response.content)
        return namespaces if base_uri in invert_dict(namespaces) else None


def prefix_cc_all() -> dict:
    """
        Return all definitions from the prefix.cc
    :return:
    """
    response = requests.get(url=PREFIX_CC_ALL_JSON)
    return json.loads(response.content) if response.ok else None