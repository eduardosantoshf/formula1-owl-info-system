# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2023-04-11 14:02:17
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2023-05-30 23:16:05
import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from difflib import SequenceMatcher
from SPARQLWrapper import SPARQLWrapper2
from datetime import datetime
import re
import yaml
import os
import re

dirname, filename = os.path.split(os.path.abspath(__file__))
print("running from", dirname)
print("file is", filename)

endpoint = "http://localhost:7200"
repo = "db"

client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)

sparql = SPARQLWrapper2("https://dbpedia.org/sparql")

drivers_data = {
  "Sebastian Vettel": "Sebastian_Vettel",
  "Lando Norris": "Lando_Norris",
  "Valtteri Bottas": "Valtteri_Bottas",
  "Lance Stroll": "Lance_Stroll",
  "Sergio Pérez": "Sergio_Pérez",
  "Pierre Gasly": "Pierre_Gasly",
  "Carlos Sainz": "Carlos_Sainz_Jr\.",
  "Kevin Magnussen": "Kevin_Magnussen",
  "Charles Leclerc": "Charles_Leclerc",
  "George Russell": "George_Russell_\(racing_driver\)",
  "Max Verstappen": "Max_Verstappen",
  "Romain Grosjean": "Romain_Grosjean",
  "Mick Schumacher": "Mick_Schumacher",
  "Daniel Ricciardo": "Daniel_Ricciardo",
  "Esteban Ocon": "Esteban_Ocon",
  "Nicholas Latifi": "Nicholas_Latifi",
  "Nico Hülkenberg": "Nico_Hülkenberg",
  "Alexander Albon": "Alex_Albon",
  "Robert Kubica": "Robert_Kubica",
  "Kimi Räikkönen": "Kimi_Räikkönen",
  "Yuki Tsunoda": "Yuki_Tsunoda",
  "Fernando Alonso": "Fernando_Alonso",
  "Daniil Kvyat": "Daniil_Kvyat",
  "Antonio Giovinazzi": "Antonio_Giovinazzi",
  "Nikita Mazepin": "Nikita_Mazepin",
  "Zhou Guanyu": "Zhou_Guanyu",
  "Pietro Fittipaldi": "Pietro_Fittipaldi",
  "Nyck de Vries": "Nyck_de_Vries",
  "Jack Aitken": "Jack_Aitken",
  "Lewis Hamilton": "Lewis_Hamilton"
}

""" Get pilot's biography

    Parameters
    ----------
    str : pilot

    Returns
    -------
    str : bio
"""     
def get_pilots_bio():

    drivers_bio = {}
    
    for driver in drivers_data.keys():
        query = """
        PREFIX db: <http://dbpedia.org/resource/>
        PREFIX dbo: <http://dbpedia.org/ontology/>

        SELECT ?biography
        WHERE {
        db:DRIVER_NAME dbo:abstract ?biography .
        FILTER (LANG(?biography) = 'en')
        }
        """
        
        query = query.replace("DRIVER_NAME", drivers_data[driver])

        sparql.setQuery(query)
        results = sparql.query()

        data = results.bindings

        drivers_bio[driver] = str(data[0]["biography"])[15:-2]

    if results:
        return drivers_bio
    else:
        return []

DRIVERS_BIO = get_pilots_bio()


""" Get information for a specific pilot

    Parameters
    ----------
    name : str
        Pilot name

    Returns
    -------
    list
        [driver_code, forename, surname, nationality]
    """
def get_pilot_info(name):
    query = """
    PREFIX driver: <http://f1/driver/pred/> 

    SELECT ?driver_code ?forename ?surname ?nationality WHERE
    {
    {
    SELECT DISTINCT ?driver_code ?forename ?surname ?nationality
    WHERE{
        ?driver_id driver:code ?driver_code.
        ?driver_id driver:nationality ?nationality.
        ?driver_id driver:forename ?forename.
        ?driver_id driver:surname ?surname.
        FILTER regex(?forename, "DRIVER_NAME" , "i")
    }
    }
    UNION
    {
    SELECT DISTINCT ?driver_code ?forename ?surname ?nationality
    WHERE{
        ?driver_id driver:code ?driver_code.
        ?driver_id driver:nationality ?nationality.
        ?driver_id driver:forename ?forename.
        ?driver_id driver:surname ?surname.
        FILTER regex(?surname, "DRIVER_NAME" , "i")
    }
    }
    }
    
    """

    query = query.replace("DRIVER_NAME", name)

    payload_query = {"query": query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo)

    response = json.loads(response)

    if response['results']['bindings']:
        data = response['results']['bindings'][0]
        return [data['driver_code']['value'], data['forename']['value'], data['surname']['value'], data['nationality']['value']]
    else:
        return []
    
def get_pilot_age(driver):
    # Define a regular expression pattern to match the birthdate
        pattern = r"born (\d{1,2} \w+ \d{4})"

        # Search for the birthdate pattern in the text
        match = re.search(pattern, DRIVERS_BIO[driver])

        if match:
            birthdate_str = match.group(1)
            birthdate = datetime.strptime(birthdate_str, "%d %B %Y").date()
            today = datetime.today().date()
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

            return age
        else:
            print("Birthdate not found.")


""" Get all pilots

    Parameters
    ----------
    None

    Returns
    -------
    list : tuples
        [(driver_code, forename, surname, nationality)]
    """
def list_all_pilots():
    query = """
    PREFIX driver: <http://f1/driver/pred/> 
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX f1: <http://f1/>

    SELECT ?driver_code ?forename ?surname ?nationality WHERE
    {
        ?driver_id rdf:type f1:Driver .
        ?driver_id driver:code ?driver_code.
        ?driver_id driver:nationality ?nationality.
        ?driver_id driver:forename ?forename.
        ?driver_id driver:surname ?surname.
    }
    
    """

    payload_query = {"query": query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo)

    response = json.loads(response)

    data = response['results']['bindings']

    pilots = []
    for pilot in data:
        pilot_name = f"{pilot['surname']['value']} {pilot['forename']['value']}" if pilot['surname']['value'] != "Guanyu" else f"{pilot['forename']['value']} {pilot['surname']['value']}"

        # get driver's age
        age = get_pilot_age(pilot_name)            

        pilots +=  [(pilot['driver_code']['value'], pilot['forename']['value'], pilot['surname']['value'], pilot['nationality']['value'], age, DRIVERS_BIO[pilot_name])]
    
    return(pilots)


""" Get all pilots for a specific season

    Parameters
    ----------
    season : int
        year of the season

    Returns
    -------
    list : tuples
        [(driver_code, forename, surname, nationality, year, team_name)]
    """
def get_pilots_by_season(season):

    query = """
    PREFIX driver: <http://f1/driver/pred/> 
    PREFIX contract: <http://f1/contract/pred/>
    PREFIX team: <http://f1/team/pred/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX f1: <http://f1/>

    SELECT ?code ?forename ?surname ?nationality ?year ?team_name WHERE
    {
        ?driver_id rdf:type f1:Driver .
        ?driver_id driver:code ?code.
        ?driver_id driver:forename ?forename.
        ?driver_id driver:surname ?surname.
        ?driver_id driver:nationality ?nationality.
        ?driver_id driver:signed_for ?contract.
    
		?contract rdf:type f1:Contract .
        ?contract contract:year ?year.
		
    	?team_id rdf:type f1:Team .
        ?team_id team:signed ?contract.
        ?team_id team:name ?team_name.


        FILTER regex(?year, "SEASON_YEAR", "i")
    }

    ORDER BY ASC( ?team_name )
    
    """
    query = query.replace("SEASON_YEAR", str(season))
    payload_query = {"query": query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo)
    print(response)
    response = json.loads(response)

    if response['results']['bindings']:
        data = response['results']['bindings']
        return [(pilot['code']['value'], 
                 pilot['forename']['value'], 
                 pilot['surname']['value'], 
                 pilot['nationality']['value'],
                 pilot['year']['value'],
                 pilot['team_name']['value']) for pilot in data]
    else:
        return []



""" Get pilots for a specific team for a specific season 

    Parameters
    ----------
    season : int
        year of the season
    team : str
        team name

    Returns
    -------
    list : tuples
        [(driver_code, forename, surname, nationality, year, team_name, team_nationality)]
    """
def get_team_pilots_by_season(season, team_name):

    query = """
    PREFIX driver: <http://f1/driver/pred/> 
    PREFIX contract: <http://f1/contract/pred/>
    PREFIX team: <http://f1/team/pred/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX f1: <http://f1/>

    SELECT ?code ?forename ?surname ?nationality ?year ?team_name ?team_nationality WHERE
    {
        ?driver_id rdf:type f1:Driver .
        ?driver_id driver:code ?code.
        ?driver_id driver:forename ?forename.
        ?driver_id driver:surname ?surname.
        ?driver_id driver:nationality ?nationality.
        ?driver_id driver:signed_for ?contract.

        ?contract rdf:type f1:Contract .
        ?contract contract:year ?year.

        ?team_id rdf:type f1:Team .
        ?team_id team:signed ?contract.
        ?team_id team:name ?team_name.
        ?team_id team:nationality ?team_nationality.


        FILTER (regex(?year, "SEASON_YEAR", "i") && regex(?team_name, "TEAM_NAME", "i"))
    }
    
    """
    query = query.replace("SEASON_YEAR", str(season))
    query = query.replace("TEAM_NAME", team_name)

    payload_query = {"query": query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo)
    print(response)
    response = json.loads(response)

    if response['results']['bindings']:
        data = response['results']['bindings']
        return [(pilot['code']['value'], 
                 pilot['forename']['value'], 
                 pilot['surname']['value'], 
                 pilot['nationality']['value'],
                 pilot['year']['value'],
                 pilot['team_name']['value'],
                 pilot['team_nationality']['value']) for pilot in data]
    else:
        return []



""" Get every team for a pilot

    Parameters
    ----------
    code : str
        pilot code

    Returns
    -------
    list : tuples
        [(driver_code, year, team_name)]
    """
def get_pilot_teams(code):

    query = """
    PREFIX driver: <http://f1/driver/pred/> 
    PREFIX contract: <http://f1/contract/pred/>
    PREFIX team: <http://f1/team/pred/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX f1: <http://f1/>

    SELECT ?code ?year ?team_name WHERE
    {   
        ?driver_id rdf:type f1:Driver .
        ?driver_id driver:code ?code.
        ?driver_id driver:signed_for ?contract.

        ?contract rdf:type f1:Contract .
        ?contract contract:year ?year.

        ?team_id rdf:type f1:Team .
        ?team_id team:signed ?contract.
        ?team_id team:name ?team_name.


        FILTER (regex(?code, "DRIVER_CODE", "i"))
    }

    
    """
    query = query.replace("DRIVER_CODE", code)

    payload_query = {"query": query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo)

    response = json.loads(response)

    if response['results']['bindings']:
        data = response['results']['bindings']
        return [(pilot['code']['value'], 
                 pilot['year']['value'],
                 pilot['team_name']['value']) for pilot in data]
    else:
        return []
    

def get_pilot_teammates(code):

    query = """
    PREFIX driver: <http://f1/driver/pred/> 
    PREFIX contract: <http://f1/contract/pred/>
    PREFIX team: <http://f1/team/pred/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX f1: <http://f1/>

    select ?code2 ?surname ?forename where { 
        ?d rdf:type f1:Driver .
        ?d driver:teammate ?d2 .
        ?d driver:code ?code .
        
        ?d2 driver:code ?code2 .
        ?d2 driver:forename ?forename .
        ?d2 driver:surname ?surname .

        FILTER (regex(?code, "DRIVER_CODE", "i"))
    }
    """
    query = query.replace("DRIVER_CODE", code)

    payload_query = {"query": query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo)

    response = json.loads(response)

    if response['results']['bindings']:
        data = response['results']['bindings']
        return [(pilot['code2']['value'], 
                 pilot['surname']['value'],
                 pilot['forename']['value']) for pilot in data]
    else:
        return []
    
        



    

#print(get_pilot_info("Hamilton"))
#list_all_pilots()
#print(get_pilots_by_season(2022))
#print(get_team_pilots_by_season(2022, "Mercedes"))
#print(get_pilot_teams("GAS"))

