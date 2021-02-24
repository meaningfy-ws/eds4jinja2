#!/usr/bin/python3

# test_lambdas.py
# Date:  24/02/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
import json

import tests


def test_call_lambda():
    """
        testing that the json.dumps can be passed **kwargs arguments
    :return:
    """
    dummy_lambda = lambda obj, **kwargs: json.dumps(obj, **kwargs)
    obj = {"z": 5, "a": 1, "b": 2, "c": 3}
    print(dummy_lambda(obj, indent=4, sort_keys=True))


def test_dict_filtering_and_list_extension_in_template(eds_environment):
    DUMMY1 = '''
    - First we create a global_list
    {% set global_list = [] %}
    - Then we extend whenever we need its content with additional values (but this method leaves a `None` string)
    {{ global_list.extend(["z","c","p"]) }}
    {% set global_list = global_list + ["_q","_w","_d"] %}
    List content after two extensions: {{  global_list}}
    
    - We have a dictionary
    {% set content = {"z": 5, "a": 1, "b": 2, "c": 3} %} \n
    content:  {{ content }} \n
    
    - The dictionary can be filtered based on the content of the global_list 
    filtered:  {{ content | select("in",global_list) | list }} \n
    
    - We render content of the dict based on the filter [select] in global_list 
    {% for pref in content| select("in",global_list) %}\n
      PREFIX  {{ pref }}: {{content[pref]}}
    {% endfor %}
    
    - We render the list [reject] filtered based on the dict content
        {% for pref in global_list| reject("in",content) %}\n
      Missing  {{ pref }}
    {% endfor %}
    
    TODO: We need a functions that goes into a columns of a Pandas dataframe and 
    generates prefix definitions from the values there. The assumption is that it is a column with VALID URIs. 
    
    It may search for 
     (a) bare URI notation: http://op.europa.eu/resources/authority/country/ROU
     (b) Turtle URI notation (between angular brakets): <http://op.europa.eu/resources/authority/country/ROU>
    '''

    template = eds_environment.from_string(DUMMY1)
    rendered_text = template.render()
    print()
    print(rendered_text)
