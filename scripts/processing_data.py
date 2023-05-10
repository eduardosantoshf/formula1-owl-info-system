# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2023-03-25 19:38:14
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2023-03-30 09:29:42

import csv
from pprint import pprint

base_rdf = "http://f1"

contract_triples = set()
driver_triples = set()
team_triples = set()
race_triples = set()
driver_standing_triples = set()
driver_final_standing_triples = set()
team_final_standing_triples = set()

triples = [
    contract_triples,
    driver_triples,
    team_triples,
    race_triples,
    driver_standing_triples,
    driver_final_standing_triples,
    team_final_standing_triples
]

### Load drivers
drivers_dict = {}
with open('../datasets/drivers.csv', 'r') as file:
    file.readline()
    reader = csv.reader(file)

    for row in reader:
        driver_id = row[0]
        row.pop(0)
        drivers_dict[driver_id] = row

### Load races and create Contract entities
races_dict = {}
with open('../datasets/races.csv', 'r') as file:
    file.readline()
    reader = csv.reader(file)

    processed_contracts = []

    for row in reader:
        race_id = row[0]
        row.pop(0)

        races_dict[race_id] = row

### Load status
status_dict = {}
with open('../datasets/status.csv', 'r') as file:
    file.readline()
    reader = csv.reader(file)

    for row in reader:
        status_dict[row[0]] = row[1]

### Load teams
teams_dict = {}
with open("../datasets/teams.csv") as file:
    file.readline()
    reader = csv.reader(file)

    for row in reader:
        t_id = row[0]
        row.pop(0)
        teams_dict[t_id] = row


######################################################### Processing data ######################################################### 

with open("../datasets/team_final_standings.csv") as file:
    file.readline()
    reader = csv.reader(file)

    for row in reader:
        team_base_rdf = "<{}/team".format(base_rdf)
        team_final_standing_base_rdf = "<{}/team_final_standing".format(base_rdf)

        team_final_standing_id = "{}/id/{}>".format(team_final_standing_base_rdf, row[0])

        team_final_standing_season_pred = "{}/pred/season>".format(team_final_standing_base_rdf)
        team_final_standing_season = "\"{}\"".format(races_dict[row[1]][0])
        team_final_standing_triples.add("{} {} {} .".format(team_final_standing_id, team_final_standing_season_pred, team_final_standing_season))

        team_final_standing_position_pred = "{}/pred/position>".format(team_final_standing_base_rdf)
        team_final_standing_position = "\"{}\"".format(row[4])
        team_final_standing_triples.add("{} {} {} .".format(team_final_standing_id, team_final_standing_position_pred, team_final_standing_position))

        team_final_standing_points_pred = "{}/pred/points>".format(team_final_standing_base_rdf)
        team_final_standing_points = "\"{}\"".format(row[3])
        team_final_standing_triples.add("{} {} {} .".format(team_final_standing_id, team_final_standing_points_pred, team_final_standing_points))

        team_id = "{}/id/{}>".format(team_base_rdf, row[2])
        team_final_standing_pred = "{}/pred/finished_in>".format(team_base_rdf)
        team_triples.add("{} {} {} .".format(team_id, team_final_standing_pred, team_final_standing_id))


with open('../datasets/results.csv', 'r') as file:
    file.readline()
    reader = csv.reader(file)

    processed_races = []
    processed_drivers = []
    processed_contracts = {}

    for row in reader:
        # Races
        race_base_rdf = "<{}/race".format(base_rdf)
        r_id = row[1]
        race_id = "{}/id/{}>".format(race_base_rdf, r_id)
        if r_id not in processed_races:
            race_info = races_dict[r_id]

            race_season_pred = "{}/pred/season>".format(race_base_rdf)
            race_season = "\"{}\"".format(race_info[0])
            race_triples.add("{} {} {} .".format(race_id, race_season_pred, race_season))

            race_round_pred = "{}/pred/round>".format(race_base_rdf)
            race_round = "\"{}\"".format(race_info[1])
            race_triples.add("{} {} {} .".format(race_id, race_round_pred, race_round))

            race_name_pred = "{}/pred/name>".format(race_base_rdf)
            race_name = "\"{}\"".format(race_info[2])
            race_triples.add("{} {} {} .".format(race_id, race_name_pred, race_name))

            processed_races.append(r_id)

        # Drivers
        driver_base_rdf = "<{}/driver".format(base_rdf)
        
        d_id = row[2]
        t_id = row[3]

        driver_id = "{}/id/{}>".format(driver_base_rdf, d_id)
        team_id = "{}/id/{}>".format(team_base_rdf, t_id)

        if d_id not in processed_drivers:
            driver_info = drivers_dict[d_id]

            driver_code_pred = "{}/pred/code>".format(driver_base_rdf)
            driver_code = "\"{}\"".format(driver_info[0])
            driver_triples.add("{} {} {} .".format(driver_id, driver_code_pred, driver_code))

            driver_surname_pred = "{}/pred/surname>".format(driver_base_rdf)
            driver_surname = "\"{}\"".format(driver_info[1])
            driver_triples.add("{} {} {} .".format(driver_id, driver_surname_pred, driver_surname))

            driver_forename_pred = "{}/pred/forename>".format(driver_base_rdf)
            driver_forename = "\"{}\"".format(driver_info[2])
            driver_triples.add("{} {} {} .".format(driver_id, driver_forename_pred, driver_forename))

            driver_nationality_pred = "{}/pred/nationality>".format(driver_base_rdf)
            driver_nationality = "\"{}\"".format(driver_info[3])
            driver_triples.add("{} {} {} .".format(driver_id, driver_nationality_pred, driver_nationality))

            processed_races.append(r_id)

        # Teams
        team_id = "{}/id/{}>".format(team_base_rdf, t_id)

        team_info = teams_dict[t_id]

        team_code_pred = "{}/pred/name>".format(team_base_rdf)
        team_name = "\"{}\"".format(team_info[1])
        team_triples.add("{} {} {} .".format(team_id, team_code_pred, team_name))

        team_code_pred = "{}/pred/nationality>".format(team_base_rdf)
        team_nationality = "\"{}\"".format(team_info[2])
        team_triples.add("{} {} {} .".format(team_id, team_code_pred, team_nationality))

        # Driver Standing
        driver_standing_base_rdf = "<{}/driver_standing".format(base_rdf)
        driver_standing_id = "{}/id/{}>".format(driver_standing_base_rdf, row[0])

        driver_standing_grid_pred = "{}/pred/grid>".format(driver_standing_base_rdf)
        driver_standing_grid = "\"{}\"".format(row[4])
        driver_standing_triples.add("{} {} {} .".format(driver_standing_id, driver_standing_grid_pred, driver_standing_grid))

        driver_standing_position_pred = "{}/pred/position>".format(driver_standing_base_rdf)
        driver_standing_position = "\"{}\"".format(row[5])
        driver_standing_triples.add("{} {} {} .".format(driver_standing_id, driver_standing_position_pred, driver_standing_position))

        driver_standing_points_pred = "{}/pred/points>".format(driver_standing_base_rdf)
        driver_standing_points = "\"{}\"".format(row[6])
        driver_standing_triples.add("{} {} {} .".format(driver_standing_id, driver_standing_points_pred, driver_standing_points))

        driver_standing_status_pred = "{}/pred/status>".format(driver_standing_base_rdf)
        driver_standing_status = "\"{}\"".format(status_dict[row[7]])
        driver_standing_triples.add("{} {} {} .".format(driver_standing_id, driver_standing_status_pred, driver_standing_status))

        driver_standing_driver_pred = "{}/pred/for>".format(driver_standing_base_rdf)
        driver_standing_triples.add("{} {} {} .".format(driver_standing_id, driver_standing_driver_pred, driver_id))

        driver_standing_race_pred = "{}/pred/at>".format(driver_standing_base_rdf)
        driver_standing_triples.add("{} {} {} .".format(driver_standing_id, driver_standing_race_pred, race_id))

        driver_code_pred = "{}/pred/has>".format(driver_base_rdf)
        driver_triples.add("{} {} {} .".format(driver_id, driver_code_pred, driver_standing_id))

        race_round_pred = "{}/pred/has>".format(race_base_rdf)
        race_triples.add("{} {} {} .".format(race_id, race_round_pred, driver_standing_id))

        # Contracts
        contract_base_rdf = "<{}/contract".format(base_rdf)

        contract_id = "{}/id/{}>".format(contract_base_rdf, row[0])

        contract_year_pred = "{}/pred/year>".format(contract_base_rdf)
        contract_year = "\"{}\"".format(races_dict[row[1]][0])
        contract_triples.add("{} {} {} .".format(contract_id, contract_year_pred, contract_year))

        contract_driver_pred = "{}/pred/driver>".format(contract_base_rdf)
        contract_driver = "\"{}\"".format(row[2])
        contract_triples.add("{} {} {} .".format(contract_id, contract_driver_pred, contract_driver))

        contract_team_pred = "{}/pred/team>".format(contract_base_rdf)
        contract_team = "\"{}\"".format(row[3])
        contract_triples.add("{} {} {} .".format(contract_id, contract_team_pred, contract_team))

        if (row[2], row[3]) not in processed_contracts.keys():
            processed_contracts[(row[2], row[3])] = [races_dict[row[1]][0]]

            # Driver - Contract
            driver_contract_pred = "{}/pred/signed_for>".format(driver_base_rdf)
            driver_triples.add("{} {} {} .".format(driver_id, driver_contract_pred, contract_id))

            # Team - Contract
            team_contract_pred = "{}/pred/signed>".format(team_base_rdf)
            team_triples.add("{} {} {} .".format(team_id, team_contract_pred, contract_id))
        else:
            if races_dict[row[1]][0] not in processed_contracts[(row[2], row[3])]:
                processed_contracts[(row[2], row[3])].append(races_dict[row[1]][0])

                # Driver - Contract
                driver_contract_pred = "{}/pred/signed_for>".format(driver_base_rdf)
                driver_triples.add("{} {} {} .".format(driver_id, driver_contract_pred, contract_id))

                # Team - Contract
                team_contract_pred = "{}/pred/signed>".format(team_base_rdf)
                team_triples.add("{} {} {} .".format(team_id, team_contract_pred, contract_id))
        

with open('../datasets/driver_final_standings.csv', 'r') as file:
    file.readline()
    reader = csv.reader(file)

    for row in reader:
        driver_final_standing_base_rdf = "<{}/driver_final_standing".format(base_rdf)

        driver_final_standing_id = "{}/id/{}>".format(driver_final_standing_base_rdf, row[0])

        driver_final_standing_season_pred = "{}/pred/season>".format(driver_final_standing_base_rdf)
        driver_final_standing_season = "\"{}\"".format(races_dict[row[1]][0])
        driver_final_standing_triples.add("{} {} {} .".format(driver_final_standing_id, driver_final_standing_season_pred, driver_final_standing_season))

        driver_final_standing_points_pred = "{}/pred/points>".format(driver_final_standing_base_rdf)
        driver_final_standing_points = "\"{}\"".format(row[3])
        driver_final_standing_triples.add("{} {} {} .".format(driver_final_standing_id, driver_final_standing_points_pred, driver_final_standing_points))

        driver_final_standing_position_pred = "{}/pred/position>".format(driver_final_standing_base_rdf)
        driver_final_standing_position = "\"{}\"".format(row[4])
        driver_final_standing_triples.add("{} {} {} .".format(driver_final_standing_id, driver_final_standing_position_pred, driver_final_standing_position))

        driver_id = "{}/id/{}>".format(driver_base_rdf, row[2])
        driver_final_standing_pred = "{}/pred/finished_in>".format(driver_base_rdf)
        driver_triples.add("{} {} {} .".format(driver_id, driver_final_standing_pred, driver_final_standing_id))


f1_set = set()
for triple in triples:
    for t in triple: 
        f1_set.add(t)

# Save triples on .nt file
with open("../datasets/f1.nt", "w") as output_file:
    for s in f1_set:
        output_file.write("{}\n".format(s))
