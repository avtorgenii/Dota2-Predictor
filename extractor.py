import csv
import json
from datetime import datetime

import stratz as st


def csv_to_json(csv_file_path, json_file_path, prs):
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        data = []
        for row in csv_reader:
            new_row = prs(row)
            data.append(new_row)

    # Write JSON file
    write_json(json_file_path, data)


def write_json(file_path, data):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def synergy_proc(row):
    return {'heroes_id': [row['hero1_id'], row['hero2_id']], 'winrate': row['winrate']}


def get_version_by_date(date):
    date = datetime.strptime(date, '%d %b %Y %H:%M')

    date_of_730 = datetime.strptime("29 oct 2021", '%d %b %Y')
    date_of_731 = datetime.strptime("23 feb 2022", '%d %b %Y')
    date_of_732 = datetime.strptime("24 aug 2022", '%d %b %Y')
    date_of_733 = datetime.strptime("20 apr 2023", '%d %b %Y')
    date_of_734 = datetime.strptime("9 aug 2023", '%d %b %Y')
    date_of_735 = datetime.strptime("15 dec 2023", '%d %b %Y')

    if date_of_731 > date > date_of_730:
        return '7.30'
    elif date_of_732 > date > date_of_731:
        return '7.31'
    elif date_of_733 > date > date_of_732:
        return '7.32'
    elif date_of_734 > date > date_of_733:
        return '7.33'
    elif date_of_735 > date > date_of_734:
        return '7.34'
    else:
        return '7.35'


def matches_proc(row):
    # Row sample
    """
    row = {
        "<id>": {
            "Winner": 'radiant',
            "Radiant":
                {
                    "<Yatoro_id>": 'abbaddon',
                    "<Miposhka_id>": 'witch-doctor'
                }
            ,
            "Dire": {},
            "Version": 7.30
        }
    }
    """

    # Because of some strange encoding problem, csv reader assigns first column such strange name...
    # match_id = row['п»ї"Match ID"']
    match_id = row["Match ID"]  # Works only for test.csv :)
    result = row['Winner']

    version = get_version_by_date(row['Start Date/Time'])

    radiant, dire, players = st.get_players_by_match_id(match_id)

    # Add new players to existing players file
    write_players_to_file(players)

    if radiant is not None and dire is not None:
        print(f"Downloading and parsing data for {match_id} finished")

        return {
            f"{match_id}": {
                "Winner": result,
                "Radiant": radiant,
                "Dire": dire,
                "Version": version
            }
        }
    else:
        # In case if for some match failed to get players, save its id for later download
        print(f"FAILED TO DOWNLOAD PLAYERS INFO FOR MATCH: {match_id}")
        return {}


def write_players_to_file(ids_and_players):
    with open("players.json", 'r+') as file:
        try:
            data = json.load(file)
        except json.decoder.JSONDecodeError:
            data = {}

    for id_and_name in ids_and_players:
        for player_id, player_name in id_and_name.items():
            data[player_id] = player_name

    with open("players.json", 'w') as file:
        json.dump(data, file)


# csv_to_json('synergies.csv', 'synergies.json', synergy_proc)

csv_to_json('test', 'matches.json', matches_proc)
