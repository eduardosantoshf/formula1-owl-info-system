import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from difflib import SequenceMatcher
import re

endpoint = "http://localhost:7200"
repo = "db"

client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)


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

    SELECT ?driver_code ?forename ?surname ?nationality WHERE
    {
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

    return([(pilot['driver_code']['value'], pilot['forename']['value'], pilot['surname']['value'], pilot['nationality']['value']) for pilot in data])



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

    SELECT ?code ?forename ?surname ?nationality ?year ?team_name WHERE
    {
        ?driver_id driver:code ?code.
        ?driver_id driver:forename ?forename.
        ?driver_id driver:surname ?surname.
        ?driver_id driver:nationality ?nationality.
        ?driver_id driver:signed_for ?contract.

        ?contract contract:year ?year.
        ?contract contract:team ?team.

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

    SELECT ?code ?forename ?surname ?nationality ?year ?team_name ?team_nationality WHERE
    {
        ?driver_id driver:code ?code.
        ?driver_id driver:forename ?forename.
        ?driver_id driver:surname ?surname.
        ?driver_id driver:nationality ?nationality.
        ?driver_id driver:signed_for ?contract.

        ?contract contract:year ?year.
        ?contract contract:team ?team.

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

    SELECT ?code ?year ?team_name WHERE
    {
        ?driver_id driver:code ?code.
        ?driver_id driver:signed_for ?contract.

        ?contract contract:year ?year.
        ?contract contract:team ?team.

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
    
        



    

#print(get_pilot_info("Hamilton"))
#print(list_all_pilots())
#print(get_pilots_by_season(2022))
#print(get_team_pilots_by_season(2022, "Mercedes"))
#print(get_pilot_teams("GAS"))
