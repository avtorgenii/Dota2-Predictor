import csv
import json
import time
from datetime import datetime
import pandas as pd

import stratz as st
import dotabuff as db


def get_incomplete_matches():
    with open("incomplete_matches.txt", 'r') as file:
        for line in file:
            ids = [id for id in line.replace("'", "").split(", ")]

        return ids


def get_incomplete_players():
    with open("incomplete_players.txt", 'r') as file:
        for line in file:
            ids = [id for id in line.replace("'", "").split(", ")]

        return ids





def csv_to_json(csv_file_path, json_file_path, prs):
    failed = []
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        data = []
        for i, row in enumerate(csv_reader):
            new_row = prs(row)
            print(i)

            if type(new_row) is dict:
                data.append(new_row)
            elif new_row is not None:
                failed.append(new_row)

    # Write JSON file
    write_json(json_file_path, data)

    return failed


def write_json(file_path, data):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def synergy_proc(row):
    return {'heroes_id': [row['hero1_id'], row['hero2_id']], 'winrate': row['winrate']}


def get_version_by_date(date):
    date = datetime.strptime(date, '%d %b %Y %H:%M')

    date_of_733 = datetime.strptime("20 apr 2023", '%d %b %Y')
    date_of_734 = datetime.strptime("9 aug 2023", '%d %b %Y')
    date_of_735 = datetime.strptime("15 dec 2023", '%d %b %Y')

    if date_of_734 > date > date_of_733:
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

    match_id = row["Match ID"]

    # if match_id not in inc_matches:  # Download only incompleted matches
    #    return None

    result = row['Winner']

    version = get_version_by_date(row['Start Date/Time'])

    var = st.get_players_by_match_id(match_id)

    if var is None:
        print(f"FAILED TO DOWNLOAD PLAYERS INFO FOR MATCH: {match_id}")
        return match_id

    radiant, dire, players = var

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
        return match_id


def write_players_to_file(ids):
    # Read existing data from the file
    with open("players.txt", 'r+') as file:
        data = [int(line.strip().replace("\n", "")) for line in file]

    # Combine existing data with new ids, removing duplicates
    data.extend(ids)
    data = set(data)

    # Write the data back to the file
    with open("players.txt", 'w') as file:
        for id in data:
            file.write(str(id) + '\n')


def complete_players_info():
    # Example player sample:
    """
    {
        "<player_id>": {
            "MatchesAmount": 10000,
            "Winrate": 56.8,
            "DivisionRank": 27,
            "Signatures": [
                "storm-spirit",
                "slark",
                "juggernaut"
            ]
        }
    }
    """

    with open("players.txt", 'r') as file:
        data = []

        for line in file:
            data = [id for id in line.replace("'", "").split(", ")]

        ds = []
        incomplete_players = []
        completed_players = []

        i = 0

        for player_id in data:
            if player_id in inc_players:

                if i > 22:
                    break

                i += 1

                matches_amount, winrate = st.get_player_number_of_matches_and_winrate(player_id)
                rank = db.get_player_rank_in_division(player_id)
                signatures = db.get_players_signatures(player_id)

                if None not in [matches_amount, winrate, rank, signatures]:
                    d = {
                        f"{player_id}": {
                            "MatchesAmount": matches_amount,
                            "Winrate": winrate,
                            "DivisionRank": rank,
                            "Signatures": signatures
                        }
                    }

                    print(d)
                    ds.append(d)
                    completed_players.append(player_id)
                else:
                    incomplete_players.append(player_id)

    with open("players.json", 'w') as file:
        json.dump(ds, file, indent=4)

    new_list = list(filter(lambda x: x not in completed_players, inc_players))

    with open("incomplete_players.txt", 'w') as file:
        for id in new_list:
            file.write(id + ", ")

    return incomplete_players


def download_all_networthes(match_to_start_from):
    i = 0

    can = False

    with open("matches.json", 'r') as file:
        data = json.load(file)

        for match in data:
            if i >= 190:
                break
            for match_id, match_info in match.items():
                if not can:
                    if match_id == str(match_to_start_from):
                        can = True
                    else:
                        continue

                print(match_id)

                time.sleep(2)
                i += 1
                print(i)

                # Iterate through each key-value pair in the nested dictionaries
                for player in match_info['Radiant']:
                    for k, v in player.items():
                        nw = st.get_player_networth_in_match(match_id, k)
                        d = {"Hero": v, "Networth": nw}
                        player[k] = d

                        print("     ", end="")
                        print(d)

                for player in match_info['Dire']:
                    for k, v in player.items():
                        nw = st.get_player_networth_in_match(match_id, k)
                        d = {"Hero": v, "Networth": nw}
                        player[k] = d

                        print("     ", end="")
                        print(d)

        with open("matches.json", 'w') as fl:
            json.dump(data, fl, indent=4)





def download_matches_info():
    return csv_to_json('matches.csv', 'matches0.json', matches_proc)


def unite_playe_jsons():
    data = []

    for i in range(1, 10):
        with open(f"players_info ({i}).json", 'r') as file:
            data.extend(json.load(file))

    with open("players.json", 'r') as file:
        data.extend(json.load(file))

    with open("players.json", 'w') as file:
        json.dump(data, file, indent=4)


def get_all_players_from_matches():
    with open('matches.json', 'r') as file:
        data = json.load(file)

        ids = []

        for match in data:
            for match_id, details in match.items():
                for team in ["Radiant", "Dire"]:
                    for player in details[team]:
                        player_id = list(player.keys())[0]
                        ids.append(player_id)

        return list(set(ids))


def get_all_players_from_players():
    with open('players.json', 'r') as file:
        data = json.load(file)
        ids = [list(player.keys())[0] for player in data]

        return list(set(ids))


def remove_all_matches_after(in_match_id):  # Removes in_match_id to
    with open('matches_dict.json', 'r') as file:
        data = json.load(file)

        out = []

        for match_id, details in data.items():
            if match_id != str(in_match_id):
                out.append({match_id: details})
            else:
                with open('matches_dict.json', 'w') as fl:
                    json.dump(out, fl, indent=4)



if __name__ == '__main__':
    # inc_matches = get_incomplete_matches()
    # inc_players = get_incomplete_players()
    # download_all_networthes(7555924572)
    pass