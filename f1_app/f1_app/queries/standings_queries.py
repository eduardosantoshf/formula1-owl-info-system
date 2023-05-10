import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from difflib import SequenceMatcher
import re

endpoint = "http://localhost:7200"
repo = "db"

client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)


""" Get final standings of all seasons for a specific pilot

    Parameters
    ----------
    code : str
        Pilot code

    Returns
    -------
    list : tuples
        [(driver_code, forename, surname, nationality, season, position, points)]
    """
def pilot_final_standings_by_season(code):
    query = """
    PREFIX driver: <http://f1/driver/pred/> 
    PREFIX driver_final_standings: <http://f1/driver_final_standing/pred/>

    SELECT ?driver_code ?forename ?surname ?nationality ?season ?position ?points WHERE
    {   
        ?driver_id driver:code ?driver_code.
        ?driver_id driver:nationality ?nationality.
        ?driver_id driver:forename ?forename.
        ?driver_id driver:surname ?surname.

        FILTER regex(?driver_code, "DRIVER_CODE" , "i")

        ?driver_id driver:finished_in ?dfs.
        ?dfs driver_final_standings:season ?season.
        ?dfs driver_final_standings:position ?position.
        ?dfs driver_final_standings:points ?points.

    }
    
    """

    query = query.replace("DRIVER_CODE", code)

    payload_query = {"query": query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo)
    #print(response)
    response = json.loads(response)

    if response['results']['bindings']:
        data = response['results']['bindings']
        return [(pilot['driver_code']['value'], 
                 pilot['forename']['value'], 
                 pilot['surname']['value'], 
                 pilot['nationality']['value'],
                 pilot['season']['value'],
                 pilot['position']['value'],
                 pilot['points']['value']) for pilot in data]
    else:
        return []
    


""" Get final standings of all seasons for a specific team

    Parameters
    ----------
    name : str
        Team name

    Returns
    -------
    list : tuples
        [(team_name, team_nationality, season, position, points)]
    """
def team_final_standings_by_season(name):
    query = """
    PREFIX team: <http://f1/team/pred/> 
    PREFIX team_final_standings: <http://f1/team_final_standing/pred/>

    SELECT ?team_name ?team_nationality ?season ?position ?points WHERE
    {   
        ?team_id team:name ?team_name.
        ?team_id team:nationality ?team_nationality.

        FILTER regex(?team_name, "TEAM_NAME" , "i")

        ?team_id team:finished_in ?tfs.
        ?tfs team_final_standings:season ?season.
        ?tfs team_final_standings:position ?position.
        ?tfs team_final_standings:points ?points.

    }
    
    """

    query = query.replace("TEAM_NAME", name)

    payload_query = {"query": query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo)

    response = json.loads(response)

    if response['results']['bindings']:
        data = response['results']['bindings']
        return [(team['team_name']['value'],
                 team['team_nationality']['value'],
                 team['season']['value'],
                 team['position']['value'],
                 team['points']['value']) for team in data]
    else:
        return []



""" Get number of championships for a specific pilot

    Parameters
    ----------
    code : str
        Pilot code

    Returns
    -------
    list 
        [driver_code, forename, surname, nationality, number_of_championships]
    """
def pilot_total_championships(code):
    query = """
    PREFIX driver: <http://f1/driver/pred/> 
    PREFIX driver_final_standings: <http://f1/driver_final_standing/pred/>

    SELECT ?driver_code ?forename ?surname ?nationality (count(distinct ?season) as ?count) WHERE
    {   
        ?driver_id driver:code ?driver_code.
        ?driver_id driver:nationality ?nationality.
        ?driver_id driver:forename ?forename.
        ?driver_id driver:surname ?surname.

        FILTER regex(?driver_code, "DRIVER_CODE" , "i")

        ?driver_id driver:finished_in ?dfs.
        ?dfs driver_final_standings:season ?season.
        ?dfs driver_final_standings:position ?position.

        FILTER (?position = '1')
    }
    GROUP BY ?driver_code ?forename ?surname ?nationality
    """

    query = query.replace("DRIVER_CODE", code)

    payload_query = {"query": query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo)

    response = json.loads(response)

    if response['results']['bindings']:
        data = response['results']['bindings'][0]
        return [data['driver_code']['value'], 
                 data['forename']['value'], 
                 data['surname']['value'], 
                 data['nationality']['value'],
                 data['count']['value']]
    else:
        return []



""" Get number of championships for a specific team

    Parameters
    ----------
    name : str
        Team name

    Returns
    -------
    list 
        [team_name, team_nationality, number_of_championships]
    """
def team_total_championships(name):
    query = """
    PREFIX team: <http://f1/team/pred/> 
    PREFIX team_final_standings: <http://f1/team_final_standing/pred/>

    SELECT ?team_name ?team_nationality (count(distinct ?season) as ?count) WHERE
    {   
        ?team_id team:name ?team_name.
        ?team_id team:nationality ?team_nationality.

        FILTER regex(?team_name, "TEAM_NAME" , "i")

        ?team_id team:finished_in ?tfs.
        ?tfs team_final_standings:season ?season.
        ?tfs team_final_standings:position ?position.

        FILTER (?position = '1')
    }
    GROUP BY ?team_name ?team_nationality
    """

    query = query.replace("TEAM_NAME", name)

    payload_query = {"query": query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo)

    response = json.loads(response)

    if response['results']['bindings']:
        data = response['results']['bindings'][0]
        return [data['team_name']['value'],
                 data['team_nationality']['value'],
                 data['count']['value']]
    else:
        return []



""" Get final standings of all pilots for a specific season

    Parameters
    ----------
    season : int
        Season year

    Returns
    -------
    list : tuples
        [(driver_code, forename, surname, nationality, team_name, position, points)]
    """
def pilots_season_final_standings(season):
    query = """
    PREFIX driver: <http://f1/driver/pred/> 
    PREFIX driver_final_standings: <http://f1/driver_final_standing/pred/>
    PREFIX contract: <http://f1/contract/pred/>
    PREFIX team: <http://f1/team/pred/>

    SELECT ?driver_code ?forename ?surname ?nationality ?team_name ?position ?points WHERE
    {   
        ?driver_id driver:code ?driver_code.
        ?driver_id driver:nationality ?nationality.
        ?driver_id driver:forename ?forename.
        ?driver_id driver:surname ?surname.

        ?driver_id driver:finished_in ?dfs.
        ?dfs driver_final_standings:season ?season.
        ?dfs driver_final_standings:position ?position.
        ?dfs driver_final_standings:points ?points.

        ?driver_id driver:signed_for ?contract.

        ?contract contract:year ?year.

        ?team_id team:signed ?contract.
        ?team_id team:name ?team_name.

        FILTER regex(?season, "SEASON_YEAR" , "i")
        FILTER regex(?year, "SEASON_YEAR" , "i")

    }

    ORDER BY ASC( xsd:long ( STR(?position) ) )
    
    """

    query = query.replace("SEASON_YEAR", str(season))

    payload_query = {"query": query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo)
    #print(response)
    response = json.loads(response)

    if response['results']['bindings']:
        data = response['results']['bindings']
        return [(pilot['driver_code']['value'], 
                 pilot['forename']['value'], 
                 pilot['surname']['value'], 
                 pilot['nationality']['value'],
                 pilot['team_name']['value'],
                 pilot['position']['value'],
                 pilot['points']['value']) for pilot in data]
    else:
        return []



""" Get final standings of all teams for a specific season

    Parameters
    ----------
    season : int
        Season year

    Returns
    -------
    list : tuples
        [(team_name, team_nationality, season, position, points)]
    """
def teams_season_final_standings(season):
    query = """
    PREFIX team: <http://f1/team/pred/> 
    PREFIX team_final_standings: <http://f1/team_final_standing/pred/>

    SELECT ?team_name ?team_nationality ?season ?position ?points WHERE
    {   
        ?team_id team:name ?team_name.
        ?team_id team:nationality ?team_nationality.

        ?team_id team:finished_in ?tfs.
        ?tfs team_final_standings:season ?season.
        ?tfs team_final_standings:position ?position.
        ?tfs team_final_standings:points ?points.

        FILTER regex(?season, "SEASON_YEAR" , "i")

    }

    ORDER BY ASC( xsd:long ( STR(?position) ) )
    
    """

    query = query.replace("SEASON_YEAR", str(season))

    payload_query = {"query": query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo)

    response = json.loads(response)

    if response['results']['bindings']:
        data = response['results']['bindings']
        return [(team['team_name']['value'],
                 team['team_nationality']['value'],
                 team['season']['value'],
                 team['position']['value'],
                 team['points']['value']) for team in data]
    else:
        return []







#print(pilot_final_standings_by_season("HAM"))
#print(team_final_standings_by_season("Mercedes"))

#print(pilot_total_championships("HAM"))
#print(team_total_championships("Mercedes"))

print(pilots_season_final_standings(2022))
#print(teams_season_final_standings(2021))