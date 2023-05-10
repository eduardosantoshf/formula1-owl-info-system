import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from difflib import SequenceMatcher
import re

endpoint = "http://localhost:7200"
repo = "db"

client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)


""" Get races for a specific season

    Parameters
    ----------
    season : int
        Season year

    Returns
    -------
    list : tuples
        [(race_id, race_name, season, round)]
    """
def races_by_season(season):
    query = """
    PREFIX race: <http://f1/race/pred/> 

    SELECT ?race_id ?race_name ?season ?round WHERE
    {   
        ?race_id race:name ?race_name.
        ?race_id race:season ?season.
        ?race_id race:round ?round.

        FILTER regex(?season, "SEASON_YEAR" , "i")

    }

    ORDER BY ASC( xsd:long ( STR(?round) ) )
    
    """

    query = query.replace("SEASON_YEAR", str(season))

    payload_query = {"query": query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo)
    #print(response)
    response = json.loads(response)

    if response['results']['bindings']:
        data = response['results']['bindings']
        return [(race['race_id']['value'].split("/")[-1], 
                 race['race_name']['value'], 
                 race['season']['value'],
                 race['round']['value']) for race in data]
    else:
        return []



""" Get pilot standings for all races for a specific season

    Parameters
    ----------
    code : str
        Pilot code
    season: int
        Season year

    Returns
    -------
    list : tuples
        [(driver_code, forename, surname, nationality, season, race_name, round, grid, status, position, points)]
    """
def pilot_standings_races_by_season(code, season):
    query = """
    PREFIX driver: <http://f1/driver/pred/>
    PREFIX driver_standing: <http://f1/driver_standing/pred/>
    PREFIX race: <http://f1/race/pred/> 

    SELECT ?code ?forename ?surname ?nationality ?season ?race_name ?round ?grid ?status ?position ?points WHERE
    {   
        ?driver_id driver:code ?code.
        ?driver_id driver:forename ?forename.
        ?driver_id driver:surname ?surname.
        ?driver_id driver:nationality ?nationality.
        ?driver_id driver:has ?driver_standing.

        ?driver_standing driver_standing:grid ?grid.
        ?driver_standing driver_standing:status ?status.
        ?driver_standing driver_standing:position ?position.
        ?driver_standing driver_standing:points ?points.
        ?driver_standing driver_standing:at ?race_id. 

        ?race_id race:name ?race_name.
        ?race_id race:season ?season.
        ?race_id race:round ?round.

        FILTER (regex(?season, "SEASON_YEAR" , "i") && regex(?code, "DRIVER_CODE" , "i"))

    }

    ORDER BY ASC( xsd:long ( STR(?round) ) )
    
    """

    query = query.replace("DRIVER_CODE", code)
    query = query.replace("SEASON_YEAR", str(season))

    payload_query = {"query": query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo)
    #print(response)
    response = json.loads(response)

    if response['results']['bindings']:
        data = response['results']['bindings']
        return [(pilot_info['code']['value'], 
                 pilot_info['forename']['value'], 
                 pilot_info['surname']['value'], 
                 pilot_info['nationality']['value'],
                 pilot_info['season']['value'],
                 pilot_info['race_name']['value'],
                 pilot_info['round']['value'],
                 pilot_info['grid']['value'], 
                 pilot_info['status']['value'],
                 pilot_info['position']['value'], 
                 pilot_info['points']['value']) for pilot_info in data]
    else:
        return []



""" Get all pilots standings for a specific race for a specific season

    Parameters
    ----------
    name : str
        Race name
    season: int
        Season year

    Returns
    -------
    list : tuples
        [(driver_code, forename, surname, nationality, season, race_name, round, grid, status, position, points)]
    """
def all_pilots_standings_by_race_by_season(race_name, season):
    query = """
    PREFIX driver: <http://f1/driver/pred/>
    PREFIX driver_standing: <http://f1/driver_standing/pred/>
    PREFIX race: <http://f1/race/pred/> 
    PREFIX contract: <http://f1/contract/pred/>
    PREFIX team: <http://f1/team/pred/>

    SELECT ?code ?forename ?surname ?nationality ?season ?race_name ?round ?grid ?status ?position ?points ?team_name WHERE
    {   
        ?driver_id driver:code ?code.
        ?driver_id driver:forename ?forename.
        ?driver_id driver:surname ?surname.
        ?driver_id driver:nationality ?nationality.
        ?driver_id driver:has ?driver_standing.

        ?driver_standing driver_standing:grid ?grid.
        ?driver_standing driver_standing:status ?status.
        ?driver_standing driver_standing:position ?position.
        ?driver_standing driver_standing:points ?points.
        ?driver_standing driver_standing:at ?race_id. 

        ?race_id race:name ?race_name.
        ?race_id race:season ?season.
        ?race_id race:round ?round.

        ?driver_id driver:signed_for ?contract.
        ?contract contract:year ?season.
        ?team_id team:signed ?contract.
        ?team_id team:name ?team_name.

        FILTER (regex(?season, "SEASON_YEAR" , "i") && regex(?race_name, "RACE_NAME", "i"))

    }

    ORDER BY ASC( xsd:long ( STR(?position) ) )
    
    """

    query = query.replace("SEASON_YEAR", str(season))
    query = query.replace("RACE_NAME", race_name)

    payload_query = {"query": query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo)
    #print(response)
    response = json.loads(response)

    if response['results']['bindings']:
        data = response['results']['bindings']
        return [(pilot_info['code']['value'], 
                 pilot_info['forename']['value'], 
                 pilot_info['surname']['value'], 
                 pilot_info['nationality']['value'],
                 pilot_info['team_name']['value'],
                 pilot_info['season']['value'],
                 pilot_info['race_name']['value'],
                 pilot_info['round']['value'],
                 pilot_info['grid']['value'], 
                 pilot_info['status']['value'],
                 pilot_info['position']['value'], 
                 pilot_info['points']['value']) for pilot_info in data]
    else:
        return []





#print(races_by_season(2022))
#print(pilot_standings_races_by_season("HAM", 2019))
#print(all_pilots_standings_by_race_by_season("Australian Grand Prix", 2019))