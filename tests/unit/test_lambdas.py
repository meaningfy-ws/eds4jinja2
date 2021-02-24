#!/usr/bin/python3

# test_lambdas.py
# Date:  24/02/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import json


def test_call_lambda():
    """
        testing that the json.dumps can be passed **kwargs arguments
    :return:
    """
    dummy_lambda = lambda obj, **kwargs: json.dumps(obj, **kwargs)
    obj = {"z": 5, "a": 1, "b": 2, "c": 3}
    print(dummy_lambda(obj, indent=4, sort_keys=True))
