# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2023-04-08 17:46:26
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2023-04-12 01:02:25

import json
import random
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from pprint import pprint
import requests



endpoint = "http://localhost:7200"
repo = "db"

headers = {
    "Content-Type": "application/sparql-update",
    "Accept": "application/json"
}

client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)

""" Delete driver

    Parameters
    ----------
    name : str
        Driver's name
    """
def delete_pilot(driver_code):
    query = """
    PREFIX driver: <http://f1/driver/pred/> 
    
    DELETE {
        ?s ?p ?o .
    }
    WHERE { 
        ?s driver:forename ?forename ;
        driver:surname ?surname ;
        driver:nationality ?nationality ;
        driver:code "DRIVER_CODE" ;
        ?p ?o .
    
    }
    """

    query = query.replace("DRIVER_CODE", driver_code.upper())

    response = requests.post(
        f"{endpoint}/repositories/{repo}/statements",
        headers = headers,
        data = query
    )
    print(response.status_code)
    return {'status_code': response.status_code}


""" Delete team

    Parameters
    ----------
    name : str
        Teams's name
    """
def delete_team(team):
    query = """
    PREFIX team: <http://f1/team/pred/> 
    
    DELETE {
        ?s ?p ?o .
    }
    WHERE {
        ?s team:name "TEAM_NAME" ;
        team:nationality ?nationality ;
        ?p ?o .
    }
    """
    
    query = query.replace("TEAM_NAME", team)

    response = requests.post(
        f"{endpoint}/repositories/{repo}/statements",
        headers = headers,
        data = query
    )

    return {'status_code': response.status_code}


""" Delete contract

    Parameters
    ----------
    driver : str
        Driver's name
    team : str
        Teams's name
    season : int
        Contract's year
    """
def delete_contract(driver, team, season):
    driver_id = get_pilot_info(driver)[0]
    team_id = get_team_info(team)[team][0][0][0]
    
    query = """
    PREFIX contract: <http://f1/contract/pred/>

    DELETE {
    ?contract ?p ?o .
    }
    WHERE {
        ?contract contract:team TEAM_NAME ;
                contract:driver DRIVER_NAME ;
                contract:year CONTRACT_YEAR ;
                ?p ?o .
    }
    """

    query = query.replace("TEAM_NAME", str(team_id))
    query = query.replace("DRIVER_NAME", str(driver_id))
    query = query.replace("CONTRACT_YEAR", str(season))

    response = requests.post(
        f"{endpoint}/repositories/{repo}/statements",
        headers = headers,
        data = query
    )

    return {'status_code': response.status_code}


""" Create driver

    Parameters
    ----------
    forename : str
        Driver's forename
    surname : str
        Driver's surname
    nationality : str
        Driver's nationality
    code : str
        Driver's code
    """
def create_pilot(forename, surname, nationality, code):
    driver_id = hash(random.randint(1, 1000))
    
    query = f"""
    PREFIX driver: <http://f1/driver/pred/>
    PREFIX id: <http://f1/driver/id/>

    INSERT DATA {{
        id:{driver_id} driver:forename "{forename}" ;
                 driver:surname "{surname}" ;
                 driver:nationality "{nationality}" ;
                 driver:code "{code}" .
    }}
    """


    response = requests.post(
        f"{endpoint}/repositories/{repo}/statements",
        headers = headers,
        data = query
    )

    return {'status_code': response.status_code}


#create_pilot("Santosi", "Edu", "Portuguese", "SAN")


""" Create team

    Parameters
    ----------
    name : str
        Team's name
    nationality : str
        Team's nationality
    """
def create_team(name, nationality):
    
    team_id = hash(random.randint(1, 1000)) + 1111111
    print(team_id)

    query = f"""
    PREFIX team: <http://f1/team/pred/>
    PREFIX id: <http://f1/team/id/>

    INSERT DATA {{
        id:{team_id} team:name "{name}" ;
                 team:nationality "{nationality}" 
    }}
    """


    response = requests.post(
        f"{endpoint}/repositories/{repo}/statements",
        headers = headers,
        data = query
    )
    #print(response)

    return {'status_code': response.status_code}

#create_team("EI5", "Portuguese")


""" Create contract

    Parameters
    ----------
    driver : str
        Driver's name
    team : str
        Team's name
    season : int
        Season
    """
def create_contract(driver, team, season):
    
    #TODO: generate id to team

    query = f"""
    PREFIX contract: <http://f1/contract/pred/>

    INSERT DATA {{
        _:contract contract:driver "{driver}" ;
                 contract:team "{team}" ;
                 contract:year "{season}" 
    }}
    """


    response = requests.post(
        f"{endpoint}/repositories/{repo}/statements",
        headers = headers,
        data = query
    )
    print(response)

    return {'status_code': response.status_code}



def do_inferences():
    veterans_inference()
    champions_inference()
    team_champions_inference()
    teammates_inference()


def veterans_inference():
    query = """
    PREFIX driver: <http://f1/driver/pred/>
    PREFIX contract: <http://f1/contract/pred/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX f1: <http://f1/>

    PREFIX veteran: <http://f1/veteran/>

    INSERT {
        GRAPH veteran:graph_temp { ?driver driver:years ?count }
    }
    WHERE {
        SELECT ?driver (COUNT(?contract) as ?count)
        WHERE {
            ?driver driver:signed_for ?contract .
        }
        GROUP BY ?driver
        HAVING (?count > 3)
    };

    INSERT { ?driver driver:years ?count }
    WHERE {
        GRAPH veteran:graph_temp { ?driver driver:years ?count }.
    };

    DROP GRAPH veteran:graph_temp;
    """

    payload_query = {"update": query}
    response = accessor.sparql_update(body=payload_query, repo_name=repo)


def champions_inference():
    query = """
    PREFIX driver: <http://f1/driver/pred/>
    PREFIX driver_final_standings: <http://f1/driver_final_standing/pred/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX f1: <http://f1/>



    PREFIX champion: <http://f1/champion/>

    INSERT {
        GRAPH champion:graph_temp { ?driver driver:champs ?count }
    }
    WHERE {
        SELECT ?driver (COUNT(DISTINCT ?season) as ?count) WHERE
        {   
            ?driver driver:finished_in ?dfs.
            ?dfs driver_final_standings:season ?season.
            ?dfs driver_final_standings:position ?position.

            FILTER (?position = '1')
        }
        GROUP BY ?driver
    };

    INSERT { ?driver driver:champs ?count }
    WHERE {
        GRAPH champion:graph_temp { ?driver driver:champs ?count }.
    };

    DROP GRAPH champion:graph_temp;
    """
    
    payload_query = {"update": query}
    response = accessor.sparql_update(body=payload_query, repo_name=repo)


def team_champions_inference():
    query = """
    PREFIX team: <http://f1/team/pred/>
    PREFIX team_final_standings: <http://f1/team_final_standing/pred/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX f1: <http://f1/>



    PREFIX team_champion: <http://f1/team_champion/pred/>

    INSERT {
        GRAPH team_champion:graph_temp { ?team team:team_champs ?count }
    }
    WHERE {
        SELECT ?team (COUNT(DISTINCT ?season) as ?count) WHERE
        {   
            ?team team:finished_in ?tfs.
            ?tfs team_final_standings:season ?season.
            ?tfs team_final_standings:position ?position.

            FILTER (?position = '1')
        }
        GROUP BY ?team
    };

    INSERT { ?team team:team_champs ?count }
    WHERE {
        GRAPH team_champion:graph_temp { ?team team:team_champs ?count }.
    };

    DROP GRAPH team_champion:graph_temp;
    """
    
    payload_query = {"update": query}
    response = accessor.sparql_update(body=payload_query, repo_name=repo)


def teammates_inference():
    query = """
    PREFIX driver: <http://f1/driver/pred/> 
    PREFIX contract: <http://f1/contract/pred/>
    PREFIX team: <http://f1/team/pred/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX f1: <http://f1/>

    INSERT {
        ?d1 driver:teammate ?d2 .
    }
    WHERE {
        ?d1 rdf:type f1:Driver .
        ?d2 rdf:type f1:Driver .
        
        ?d1 driver:code ?d1_code .
        ?d2 driver:code ?d2_code .
        
        ?d1 driver:signed_for ?contract1 .
        ?contract1 rdf:type f1:Contract .
        ?d2 driver:signed_for ?contract2 .
        ?contract2 rdf:type f1:Contract .
        
        ?contract1 contract:year ?year .
        ?contract2 contract:year ?year .
        
        ?team rdf:type f1:Team .
        ?team team:signed ?contract1 .
        ?team team:signed ?contract2 .
        
        FILTER(?d1_code != ?d2_code)
        
    }
    """
    
    payload_query = {"update": query}
    response = accessor.sparql_update(body=payload_query, repo_name=repo)