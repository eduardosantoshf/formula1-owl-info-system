# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2023-03-26 22:49:05
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2023-04-09 15:21:49

import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from difflib import SequenceMatcher
import re

endpoint = "http://localhost:7200"
repo = "db"

client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)


def get_team_info(team_name):
    query = """
    PREFIX team: <http://f1/team/pred/> 

    SELECT DISTINCT ?team_id ?team_name ?team_nationality
    WHERE{ 
        ?team_id team:nationality ?team_nationality.
        ?team_id team:name ?team_name.
    }
    
    
    """

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo)
    res = json.loads(res)

    all_teams = [(t["team_id"]["value"].split("id/")[1], t["team_name"]["value"], t["team_nationality"]["value"]) for t in res['results']['bindings']]

    probably_similar = {}
    for team in all_teams:
        sim_ratio = SequenceMatcher(None, team_name.lower(), team[1].lower()).ratio()
        if sim_ratio > 0.50:
            if team_name not in probably_similar:
                probably_similar[team_name] = [((team[0], team[1], team[2]), sim_ratio)]
            else:
                probably_similar[team_name].append(((team[0], team[1], team[2]), sim_ratio))

    most_similar = {k: sorted(v, key = lambda x: x[1], reverse = True)[:3] for k, v in probably_similar.items()}

    #print(f"Most similar: {most_similar}")
    return most_similar

def get_all_teams():
    query = """
    PREFIX team: <http://f1/team/pred/> 

    SELECT DISTINCT ?team_id ?team_name ?team_nationality
    WHERE{ 
        ?team_id team:nationality ?team_nationality.
        ?team_id team:name ?team_name.
    }
    """

    #query = query.replace("DRIVER_NAME", name)

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo)
    res = json.loads(res)

    all_teams = [(t["team_name"]["value"], t['team_nationality']['value']) for t in res['results']['bindings']]

    print(all_teams)

    return all_teams



""" Get every driver for a team

    Parameters
    ----------
    name : str
        team code

    Returns
    -------
    list : tuples
        [(year, team_name, forename, surname)]
    """
def get_team_drivers(name):

    query = """
    PREFIX driver: <http://f1/driver/pred/> 
    PREFIX contract: <http://f1/contract/pred/>
    PREFIX team: <http://f1/team/pred/>

    SELECT  ?year ?team_name ?forename ?surname WHERE
    {
        ?driver_id driver:code ?code.
        ?driver_id driver:signed_for ?contract.
        ?driver_id driver:forename ?forename.
        ?driver_id driver:surname ?surname.

        ?contract contract:year ?year.
        ?contract contract:team ?team.

        ?team_id team:signed ?contract.
        ?team_id team:name ?team_name.


        FILTER (regex(?team_name, "TEAM_NAME", "i"))
    }

    ORDER BY DESC(?year)

    
    """
    query = query.replace("TEAM_NAME", name)

    payload_query = {"query": query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo)

    response = json.loads(response)

    if response['results']['bindings']:
        data = response['results']['bindings']
        return [(x['year']['value'],
                 x['team_name']['value'],
                 x['forename']['value'],
                 x['surname']['value']) for x in data]
    else:
        return []

#get_all_teams()
#print(get_team_drivers("Mercedes"))

