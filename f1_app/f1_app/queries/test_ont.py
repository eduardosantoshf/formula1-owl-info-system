import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from difflib import SequenceMatcher
import re
from pprint import pprint

endpoint = "http://localhost:7200"
repo = "teste"

client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)



query = """
PREFIX driver: <http://f1/driver/pred/>
PREFIX rdf: <http://www.w3.org/2000/01/rdf-schema#label>
PREFIX rdfs: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT * WHERE
{
    ?driver_id driver:code ?code.
    ?driver_id driver:forename ?forename.
    ?driver_id driver:surname ?surname.
    ?driver_id driver:nationality ?nationality.



}

"""



payload_query = {"query": query}
response = accessor.sparql_select(body=payload_query, repo_name=repo)
print(response)
response = json.loads(response)
