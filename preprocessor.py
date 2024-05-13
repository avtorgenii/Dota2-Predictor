import json
import pandas as pd
import numpy as np


def convert_players_json_to_one_dict():
    out = {}
    with open('players.json', 'r') as file:
        data = json.load(file)

        for player in data:
            for player_id, details in player.items():
                out[player_id] = details

    with open('players_dict.json', 'w') as file:
        json.dump(out, file, indent=4)


def convert_matches_json_to_one_dict():
    out = {}
    with open('matches_dict.json', 'r') as file:
        data = json.load(file)

        for match in data:
            for match_id, details in match.items():
                out[match_id] = details

    with open('matches_dict.json', 'w') as file:
        json.dump(out, file, indent=4)


def remove_all_matches_after(in_match_id):  # Removes in_match_id too
    with open('matches_dict.json', 'r') as file:
        data = json.load(file)

        out = []

        for match_id, details in data.items():
            if match_id != str(in_match_id):
                out.append({match_id: details})
            else:
                with open('matches_dict.json', 'w') as fl:
                    json.dump(out, fl, indent=4)


def convert_heroes_winrates_json_to_one_dict():  # Converts file from used folder
    out = {}
    for v in [7.33, 7.34, 7.35]:
        with open(f'heroes_counter_winrates_{v}.json', 'r') as file:
            data = json.load(file)

            for hero in data:
                for hero_id, details in hero.items():
                    out[hero_id] = {}
                    for c_details in details:
                        c_key = list(c_details.keys())[0]

                        c_new_key = c_key.lower().replace(' ', '-').replace("'", "")

                        out[hero_id][c_new_key] = c_details[c_key]

        with open(f'heroes_counter_winrates_{v}_dict.json', 'w') as file:
            json.dump(out, file, indent=4)


def convert_synergies_winrates_json_to_one_dict():
    out = {}
    with open('synergies.json', 'r') as file:
        data = json.load(file)
        result_dict = {}
        for item in data:
            hero_id_list = item["heroes_id"]
            winrate = item["winrate"]
            for hero_id in hero_id_list:
                if hero_id not in result_dict:
                    result_dict[hero_id] = {}
                for other_hero_id in hero_id_list:
                    if other_hero_id != hero_id:
                        result_dict[hero_id][other_hero_id] = winrate

        with open('synergies_dict.json', 'w') as fl:
            json.dump(result_dict, fl, indent=4)


# Calculations

def calc_difference_in_matches(in_match_id, players_data, matches_data):  # RadiantMatches - DireMatches

    details = matches_data[str(in_match_id)]

    radiant_matches = 0
    dire_matches = 0

    for player in details['Radiant']:
        player_id = list(player.keys())[0]
        radiant_matches += players_data[player_id]['MatchesAmount']

        # print(radiant_matches)

    for player in details['Dire']:
        player_id = list(player.keys())[0]
        dire_matches += players_data[player_id]['MatchesAmount']

        # print(dire_matches)

    return radiant_matches - dire_matches


def calc_difference_in_avg_winrates(in_match_id, players_data, matches_data):  # RadiantAvgWinrate - DireAvgWinrate

    details = matches_data[str(in_match_id)]

    radiant_wrs = 0
    dire_wrs = 0

    for player in details['Radiant']:
        player_id = list(player.keys())[0]
        radiant_wrs += players_data[player_id]['Winrate']

    # print(radiant_wrs)

    for player in details['Dire']:
        player_id = list(player.keys())[0]
        dire_wrs += players_data[player_id]['Winrate']

    # print(dire_wrs)

    return round((radiant_wrs - dire_wrs) / 5, 5)


def calc_difference_in_avg_counter_winrates(in_match_id,
                                            matches_data):  # RadiantAvgWinrateCounter - DireAvgWinrateCounter

    details = matches_data[str(in_match_id)]

    version = details['Version']

    with open(f'heroes_counter_winrates_{version}_dict.json', 'r') as h_file:
        heroes_data = json.load(h_file)

        radiant_heroes = []
        dire_heroes = []

        radiant_wrs = []
        dire_wrs = []

        for player in details['Radiant']:
            player_id = list(player.keys())[0]
            hero = player[player_id]['Hero']
            radiant_heroes.append(hero)

        # print(radiant_heroes)

        for player in details['Dire']:
            player_id = list(player.keys())[0]
            hero = player[player_id]['Hero']
            dire_heroes.append(hero)

        # print(dire_heroes)

        for r_hero in radiant_heroes:
            for d_hero in dire_heroes:
                radiant_wrs.append(float(heroes_data[r_hero][d_hero]))

        r_avg = sum(radiant_wrs) / len(radiant_wrs)

        # print(r_avg)

        for d_hero in dire_heroes:
            for r_hero in radiant_heroes:
                dire_wrs.append(float(heroes_data[d_hero][r_hero]))

        d_avg = sum(dire_wrs) / len(dire_wrs)

        # print(d_avg)

        return round((r_avg - d_avg) / 100, 5)


def calc_difference_in_avg_synergy_winrates(in_match_id,
                                            matches_data,
                                            synergies_data):  # RadiantAvgWinrateSynergy - DireAvgWinrateSynergy
    details = matches_data[str(in_match_id)]

    radiant_heroes = []
    dire_heroes = []

    radiant_wrs = []
    dire_wrs = []

    for player in details['Radiant']:
        player_id = list(player.keys())[0]
        hero = player[player_id]['Hero']
        radiant_heroes.append(hero)

    # print(radiant_heroes)

    for player in details['Dire']:
        player_id = list(player.keys())[0]
        hero = player[player_id]['Hero']
        dire_heroes.append(hero)

    # print(dire_heroes)

    for r_hero in radiant_heroes:
        for r2_hero in radiant_heroes:
            if r_hero != r2_hero:
                try:
                    wr = float(synergies_data[r_hero][r2_hero])
                except Exception:
                    wr = 0.5

                radiant_wrs.append(wr)

    # print(radiant_wrs)

    for d_hero in dire_heroes:
        for d2_hero in dire_heroes:
            if d_hero != d2_hero:
                try:
                    wr = float(synergies_data[d_hero][d2_hero])
                except Exception:
                    wr = 0.5

                dire_wrs.append(wr)

    # print(dire_wrs)

    r_avg = sum(radiant_wrs) / len(radiant_wrs)
    d_avg = sum(dire_wrs) / len(dire_wrs)

    return round(r_avg - d_avg, 5)


def calc_difference_in_networthes(in_match_id,
                                  matches_data):  # RadiantNetworth - DireNetworth (on 10th minute of game)

    details = matches_data[str(in_match_id)]

    radiant_nw = 0
    dire_nw = 0

    for player in details['Radiant']:
        player_id = list(player.keys())[0]
        nw = player[player_id]['Networth']
        radiant_nw += 0 if nw is None else nw

    # print(radiant_nw)

    for player in details['Dire']:
        player_id = list(player.keys())[0]
        nw = player[player_id]['Networth']
        dire_nw += 0 if nw is None else nw

    # print(dire_nw)

    return radiant_nw - dire_nw


def is_player_on_signature(in_player_id, in_match_id, players_data, matches_data):
    details = matches_data[str(in_match_id)]

    # print(details['Radiant'])

    for player in details['Radiant']:
        player_id = list(player.keys())[0]

        if player_id == str(in_player_id):
            hero = player[player_id]['Hero']

            signatures = players_data[str(in_player_id)]['Signatures']

            if hero in signatures:
                return True

    for player in details['Dire']:
        player_id = list(player.keys())[0]

        if player_id == str(in_player_id):
            hero = player[player_id]['Hero']

            signatures = players_data[str(in_player_id)]['Signatures']

            if hero in signatures:
                return True

    return False


def get_signature_and_rank_for_player(in_player_id, in_match_id, players_data, matches_data):
    on_signature = is_player_on_signature(in_player_id, in_match_id, players_data, matches_data)
    rank = players_data[str(in_player_id)]['DivisionRank']

    # If player is on signature return 1, else return 0
    return 1 if on_signature else 0, rank


def combine_all_data_for_match(in_match_id):
    with open('matches_dict.json') as m_file:
        matches_data = json.load(m_file)

        with open('players_dict.json') as p_file:
            players_data = json.load(p_file)

            with open('synergies_dict.json') as s_file:
                synergies_data = json.load(s_file)

                # Winner will be 1 if Radiant won, if Dire 0
                winner = 1 if matches_data[str(in_match_id)]['Winner'] == 'Radiant' else 0

                matches_diff = calc_difference_in_matches(in_match_id, players_data, matches_data)
                winrates_diff = calc_difference_in_avg_winrates(in_match_id, players_data, matches_data)
                counter_diff = calc_difference_in_avg_counter_winrates(in_match_id, matches_data)
                synergies_diff = calc_difference_in_avg_synergy_winrates(in_match_id, matches_data, synergies_data)
                networthes_diff = calc_difference_in_networthes(in_match_id, matches_data)

                radiant_ranks = []
                dire_ranks = []

                # 1 if on signature, 0 if not
                radiant_signatures = []
                dire_signatures = []

                for player in matches_data[str(in_match_id)]['Radiant']:
                    player_id = list(player.keys())[0]
                    on_signature, rank = get_signature_and_rank_for_player(player_id, in_match_id, players_data,
                                                                           matches_data)

                    radiant_ranks.append(rank)
                    radiant_signatures.append(on_signature)

                for player in matches_data[str(in_match_id)]['Dire']:
                    player_id = list(player.keys())[0]
                    on_signature, rank = get_signature_and_rank_for_player(player_id, in_match_id, players_data,
                                                                           matches_data)

                    dire_ranks.append(rank)
                    dire_signatures.append(on_signature)

                out = [matches_diff, winrates_diff, counter_diff, synergies_diff, networthes_diff]

                ranks = radiant_ranks + dire_ranks

                out.extend(ranks)

                out.extend(radiant_signatures)
                out.extend(dire_signatures)

                # Out will be X and Winner Y
                return out, winner


def get_data_for_all_matches():
    with open('matches_dict.json', 'r') as file:
        data = json.load(file)

        xs = []
        ys = []

        for match_id, _ in data.items():
            x, y = combine_all_data_for_match(match_id)
            # print(f"Match id {match_id}: {x}, {y}")
            xs.append(x)
            ys.append(y)

        return xs, ys


def get_data_for_matches_as_dataframe():
    xs, ys = get_data_for_all_matches()

    column_names = ["Matches diff", "Winrates diff", "Counter picks winrate diff", "Synergies winrates diff",
                    "Networthes diff",
                    "R1 rank", "R2 rank", "R3 rank", "R4 rank", "R5 rank",
                    "D1 rank", "D2 rank", "D3 rank", "D4 rank", "D5 rank",
                    "R1 on signature", "R2 on signature", "R3 on signature", "R4 on signature", "R5 on signature",
                    "D1 on signature", "D2 on signature", "D3 on signature", "D4 on signature", "D5 on signature"]

    # Create DataFrame
    df = pd.DataFrame(xs, columns=column_names)

    # Add ys as a column to the DataFrame
    df['Winner'] = ys

    column = df.pop('Winner')

    df.insert(0, column.name, column)

    return df


def df_to_csv():
    get_data_for_matches_as_dataframe().to_csv('all_data.csv', index=False)


def csv_to_df():
    df = pd.read_csv('all_data.csv')
    return df


if __name__ == "__main__":
    df_to_csv()
