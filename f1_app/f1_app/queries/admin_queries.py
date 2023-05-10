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


#create_contract("1", "1111562", 2023)