# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2023-05-21 12:31:55
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2023-05-21 12:32:07

from SPARQLWrapper import SPARQLWrapper2
import yaml

with open('drivers.yaml', 'r') as file:
    # Load the YAML data
    data = yaml.safe_load(file)
    print(data)


sparql = SPARQLWrapper2("https://dbpedia.org/sparql")
query = """
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?age
WHERE {
    <http://dbpedia.org/resource/Charles_Leclerc> dbo:birthDate ?birthdate .
    BIND(year(now()) - year(?birthdate) - if(month(now()) < month(?birthdate) || (month(now()) = month(?birthdate) && day(now()) < day(?birthdate)), 1, 0) AS ?age)
}

"""
sparql.setQuery(query)
results = sparql.query()

print(results.bindings)

query = """
PREFIX db: <http://dbpedia.org/resource/>
PREFIX dbo: <http://dbpedia.org/ontology/>

SELECT ?biography
WHERE {
  db:Charles_Leclerc dbo:abstract ?biography .
  FILTER (LANG(?biography) = 'en')
}

"""

sparql.setQuery(query)
results = sparql.query()

print(results.bindings)

query = """
PREFIX db: <http://dbpedia.org/resource/>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>

SELECT ?property ?value
WHERE {
  db:Charles_Leclerc ?property ?value .
  FILTER (STRSTARTS(STR(?property), STR(dbp:)))
}

"""

sparql.setQuery(query)
results = sparql.query()

print(results.bindings)

query = """
PREFIX db: <http://dbpedia.org/resource/>
PREFIX dbo: <http://dbpedia.org/ontology/>

SELECT ?biography
WHERE {
  db:Charles_Leclerc dbo:abstract ?biography .
  FILTER (LANG(?biography) = 'en')
}
"""

sparql.setQuery(query)
results = sparql.query()

print(results.bindings)