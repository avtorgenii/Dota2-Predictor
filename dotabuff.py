import random

import requests
from bs4 import BeautifulSoup
import json

versions = ['7.33', '7.34', '7.35']
heroes = []

with open('heroes', 'r') as heroes_file:
    for line in heroes_file:
        heroes.append(line.replace('\n', ''))

# List of dictionaries example:
"""
counter_win_rates_example = [
    {
        'Version': {7.30},
        'Win_Rates':
            [
                {
                    'Main_Hero1': [
                        {'Oppose_Hero1': {55}},
                        {'Oppose_Hero2': {45}}
                    ]
                },
                {
                    'Main_Hero2': [
                        {'Oppose_Hero1': {55}},
                        {'Oppose_Hero2': {45}}
                    ]
                }
            ]
    }
]
"""

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
}


def get_random_headers():
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.91 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.92 Safari/537.36"
    ]

    user_agent = random.choice(user_agents)

    return {
        "User-Agent": user_agent
    }

def get_random_prefix():
    prefixes = ['ru', 'www', 'cn', 'pl']

    return random.choice(prefixes)

def download_counter_pick_winrates():
    for version in versions:
        counter_win_rates = []
        for hero in heroes:
            url = f"https://{get_random_prefix()}.dotabuff.com/heroes/{hero}/counters?date=patch_{version}"

            response = requests.get(url, headers=get_random_headers())

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the HTML content of the page
                soup = BeautifulSoup(response.content, "html.parser")

                # Find all <td> elements with the data-value attribute
                td_elements = soup.find_all("td", {"data-value": True})

                needed = td_elements[40:]
                output = []

                # Extract the data-value attribute from each <td> element and print it
                for td in needed:
                    data_value = td["data-value"]
                    output.append(data_value)

                heroes_n_wr = {'Heroes': output[::4], 'WinRates': output[2::4]}
                # print(heroes_n_wr)

                list_of_heroes_n_wr = [{f'{hero}': win_rate} for hero, win_rate in
                                       zip(heroes_n_wr['Heroes'], heroes_n_wr['WinRates'])]

                list_of_heroes_n_wr = sorted(list_of_heroes_n_wr, key=lambda x: list(x.keys())[0])

                counter_win_rates.append({f'{hero}': list_of_heroes_n_wr})

                print(f"Downloading for {hero} done")



            else:
                print("Failed to retrieve data from the website.")

        with open(f'heroes_counter_winrates_{version}.json', 'w') as file:
            json.dump(counter_win_rates, file, indent=4)


def get_players_signatures(player_id):
    url = f"https://{get_random_prefix()}.dotabuff.com/players/{player_id}"

    response = requests.get(url, headers=get_random_headers())

    if response.status_code == 200:
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')

        tags = soup.find_all('div', class_='r-none-mobile')

        # Extracting only blocks with href inside
        tags_with_a = [tag for tag in tags if tag.a]

        # Pulling only 3 most played heroes
        signatures = []

        for tag in tags_with_a[:3]:
            if tag.a:
                hero_name = tag.a.text.replace(' ', '-').replace("'", "").lower()
                signatures.append(hero_name)

        if len(signatures) > 0:
            return signatures
        else:
            print(f"Failed to retrieve SIGNATURES data from Dotabuff for {player_id}")
        return None

    else:
        print(f"Failed to retrieve SIGNATURES data from Dotabuff for {player_id}")
        return None


def get_player_rank_in_division(player_id):
    url = f"https://{get_random_prefix()}.dotabuff.com/players/{player_id}"

    response = requests.get(url, headers=get_random_headers())

    if response.status_code == 200:

        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')

        rank_value_div = soup.find('div', class_='leaderboard-rank-value')
        if rank_value_div:
            rank_value = rank_value_div.text.strip()
            return int(rank_value.replace(",", ""))
        else:
            print("Rank value not found, returning -1 instead")
            return -1
    else:
        print(f"Failed to retrieve RANK IN DIVISION data from Dotabuff for {player_id}")
        return None
