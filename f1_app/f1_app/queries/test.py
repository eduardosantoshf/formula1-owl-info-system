# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2023-03-24 22:34:42
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2023-03-26 19:56:22

import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from difflib import SequenceMatcher
import re

endpoint = "http://localhost:7200"
repo = "db"

client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)

query = """ 
    SELECT DISTINCT ?subj ?pred ?obj
    WHERE {
        <http://f1/driver/id/1> <http://f1/driver/pred/drived_on> ?obj
    }
    LIMIT 10

"""

#res = accessor.sparql_select(body={"query": query}, repo_name=repo)

#print(res)

query2 = """
    PREFIX driver: <http://f1/driver/pred/>
    SELECT DISTINCT ?driver_id ?forename
    WHERE {
        ?driver_id driver:forename ?forename.
    }
    LIMIT 10
"""


#res2 = accessor.sparql_select(body={"query": query2}, repo_name=repo)

#print(res2)

#query3 = """
#    PREFIX driver: <http://f1/driver/pred/>
#    SELECT DISTINCT ?driver_id ?driver_standing
#    WHERE {
#        ?driver_id driver:has ?driver_standing.
#    }
#    LIMIT 10
#"""

# BUG: corrigir querie
query3 = """
    PREFIX driver: <http://f1/driver/pred/>
    PREFIX driver_standing: <http://f1/driver_standing/pred/>
    PREFIX id: <http://f1/driver_standing/id/>
    PREFIX race: <http://f1/race/pred/>
    
    SELECT * WHERE 
    {
    {
        SELECT ?driver_id WHERE
        {
            ?driver_id driver:has id:25790.
        }
    }
    UNION
    {
        SELECT ?race_id ?points WHERE
        {
            id:25790 driver_standing:at ?race_id.
            id:25790 driver_standing:points ?points.
        }
    }
    UNION
    {
        SELECT ?race_name WHERE
        {
            ?race race:has id:25790.
            ?race_id race:name ?race_name.
            
            
        }
    }
    }

    LIMIT 10
"""

res3 = accessor.sparql_select(body={"query": query3}, repo_name=repo)

print(res3)


#update = """
#    INSERT DATA { <http://movies.org/en/bad_taste> <http://movies.org/pred/starring> <http://movies.org/guid/9202a8c04000641f80000000010cf900> . }
#"""
#
#res2 = accessor.sparql_update(body={"update": update}, repo_name=repo)
#
#print(res2)


