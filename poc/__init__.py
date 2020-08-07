"""
__init__.py
Date:  07/08/2020
Author: Eugeniu Costetchi
Email: costezki.eugen@gmail.com 
"""

SPARQL_TEMPLATE_CORRECT = '''
{% set queryString = 'SELECT * WHERE { ?s ?p ?o. } limit 10' %}\n
{% set endpoint = 'http://localhost:3030/subdiv' %}\n
{% set q = x.fetch_tree(queryString, endpoint) %} \n
query {{ q }}
'''

SPARQL_TEMPLATE_FAULTY_QUERY = '''
{% set queryString = 'SELECT *  LIMIT 10' %}\n
{% set endpoint = 'http://localhost:3030/subdiv' %}\n
{% set content, error = x.sparql_query(queryString, endpoint).fetch_tabular() %} \n
query {{ content }}
error {{ error }}
'''

SPARQL_TEMPLATE_FAULTY_ENDPOINT = '''
{% set queryString = 'SELECT *  LIMIT 10' %}\n
{% set endpoint = 'faulty_endpoint' %}\n
{% set q = x.sparql_query(queryString, endpoint).fetch_tabular() %} \n
query {{ q }}
'''
