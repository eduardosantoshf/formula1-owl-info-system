import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from difflib import SequenceMatcher
import re
from pprint import pprint

endpoint = "http://localhost:7200"
repo = "db"

client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)


""" Get drivers with 4+ years of exerience

    Parameters
    ----------

    Returns
    -------
    list : tuples
        [(code, forename, surname, nationality, years)]
    """
def experience_drivers():
    query = """
    PREFIX driver: <http://f1/driver/pred/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX f1: <http://f1/>

    SELECT ?d ?code ?forename ?surname ?nationality ?years WHERE
    {
        ?d rdf:type f1:Veteran .

        ?d driver:code ?code.
        ?d driver:forename ?forename.
        ?d driver:surname ?surname.
        ?d driver:nationality ?nationality.
        ?d driver:years ?years.

    }
    
    """


    payload_query = {"query": query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo)
    #print(response)
    response = json.loads(response)


    if response['results']['bindings']:
        data = response['results']['bindings']
        return [(pilot['code']['value'], 
                 pilot['forename']['value'], 
                 pilot['surname']['value'], 
                 pilot['nationality']['value'],
                 pilot['years']['value']) for pilot in data]
    else:
        return []
    


""" Top 5 pilots with most championships

    Parameters
    ----------

    Returns
    -------
    list : tuples
        [(driver_code, forename, surname, nationality, number_of_championships)]
    """
def best_pilots():
    query = """
    PREFIX driver: <http://f1/driver/pred/> 
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX f1: <http://f1/>

    SELECT ?d ?code ?forename ?surname ?nationality ?count WHERE
    {   
    	?d rdf:type f1:Champion .
        ?d driver:code ?code.
        ?d driver:nationality ?nationality.
        ?d driver:forename ?forename.
        ?d driver:surname ?surname.
    	?d driver:champs ?count.
    }
    """


    payload_query = {"query": query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo)
    #print(response)
    response = json.loads(response)

    if response['results']['bindings']:
        data = response['results']['bindings']
        return [(pilot['code']['value'], 
                 pilot['forename']['value'], 
                 pilot['surname']['value'], 
                 pilot['nationality']['value'],
                 pilot['count']['value']) for pilot in data]
    else:
        return []
    


""" Top 5 teams with most championships

    Parameters
    ----------

    Returns
    -------
    list 
        [team_name, team_nationality, number_of_championships]
    """
def best_teams():
    query = """
    PREFIX team: <http://f1/team/pred/> 
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX f1: <http://f1/>

    SELECT ?team_name ?team_nationality ?count WHERE
    {   
    	?t rdf:type f1:Best_teams .
        ?t team:name ?team_name.
        ?t team:nationality ?team_nationality.
    	?t team:team_champs ?count.
    }

    """

    payload_query = {"query": query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo)

    response = json.loads(response)

    if response['results']['bindings']:
        data = response['results']['bindings']
        return [(pilot['team_name']['value'],
                 pilot['team_nationality']['value'],
                 pilot['count']['value']) for pilot in data]
    else:
        return [] 



""" Pilots that finished top 3 more times

    Parameters
    ----------

    Returns
    -------
    list : tuples
        [(driver_code, forename, surname, nationality, count)]
    """
def pilots_finished_top3():
    query = """
    PREFIX driver: <http://f1/driver/pred/> 
    PREFIX driver_final_standings: <http://f1/driver_final_standing/pred/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX f1: <http://f1/>

    SELECT ?driver_code ?forename ?surname ?nationality (COUNT(DISTINCT ?season) as ?count) WHERE
    {   
        ?driver_id rdf:type f1:Driver .
        ?driver_id driver:code ?driver_code.
        ?driver_id driver:nationality ?nationality.
        ?driver_id driver:forename ?forename.
        ?driver_id driver:surname ?surname.

        ?driver_id driver:finished_in ?dfs.
        ?dfs driver_final_standings:season ?season.
        ?dfs driver_final_standings:position ?position.

        FILTER (?position = '1' || ?position = '2' || ?position = '3')
    }
    GROUP BY ?driver_code ?forename ?surname ?nationality
    ORDER BY DESC(?count)
    """


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
                 pilot['count']['value']) for pilot in data]
    else:
        return []
    


""" Pilots that finished top 3 more times by season

    Parameters
    ----------
    season : str
        Year

    Returns
    -------
    list : tuples
        [(driver_code, forename, surname, nationality, count)]
    """
def pilots_finished_top3_by_season(season):
    query = """
    PREFIX driver: <http://f1/driver/pred/>
    PREFIX driver_standing: <http://f1/driver_standing/pred/>
    PREFIX race: <http://f1/race/pred/> 

    SELECT ?driver_code ?forename ?surname ?nationality (COUNT(DISTINCT ?race_id) as ?count) WHERE
    {   
        ?driver_id driver:code ?driver_code.
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

        FILTER (regex(?season, "SEASON_YEAR" , "i"))
        FILTER (?position = '1' || ?position = '2' || ?position = '3')

    }

    GROUP BY ?driver_code ?forename ?surname ?nationality
    ORDER BY DESC(?count)
    
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
                 pilot['count']['value']) for pilot in data]
    else:
        return []
    


""" Get pilots with most retired cars by season

    Parameters
    ----------
    season: int
        Season year

    Returns
    -------
    list : tuples
        [(driver_code, forename, surname, nationality, count)]
    """
def pilots_most_retired_cars_by_season(season):
    query = """
    PREFIX driver: <http://f1/driver/pred/>
    PREFIX driver_standing: <http://f1/driver_standing/pred/>
    PREFIX race: <http://f1/race/pred/> 

    SELECT ?driver_code ?forename ?surname ?nationality (COUNT(DISTINCT ?race_id) as ?count) WHERE
    {   
        ?driver_id driver:code ?driver_code.
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

        FILTER (regex(?season, "SEASON_YEAR" , "i"))
        FILTER (?status != 'Accident' && ?status != 'Finished')

    }

    GROUP BY ?driver_code ?forename ?surname ?nationality
    ORDER BY DESC(?count)
    
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
                 pilot['count']['value']) for pilot in data]
    else:
        return []
    


""" Get pilots with most accidents by season

    Parameters
    ----------
    season: int
        Season year

    Returns
    -------
    list : tuples
        [(driver_code, forename, surname, nationality, count)]
    """
def pilots_most_accidents_by_season(season):
    query = """
    PREFIX driver: <http://f1/driver/pred/>
    PREFIX driver_standing: <http://f1/driver_standing/pred/>
    PREFIX race: <http://f1/race/pred/> 

    SELECT ?driver_code ?forename ?surname ?nationality (COUNT(DISTINCT ?race_id) as ?count) WHERE
    {   
        ?driver_id driver:code ?driver_code.
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

        FILTER (regex(?season, "SEASON_YEAR" , "i"))
        FILTER (?status = 'Accident')

    }

    GROUP BY ?driver_code ?forename ?surname ?nationality
    ORDER BY DESC(?count)
    
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
                 pilot['count']['value']) for pilot in data]
    else:
        return []


#pprint(experience_drivers())
#pprint(best_pilots())
#pprint(best_teams())

#pprint(pilots_finished_top3_by_season(2022))

#pprint(pilots_most_retired_cars_by_season(2021))

#pprint(pilots_most_accidents_by_season(2022))