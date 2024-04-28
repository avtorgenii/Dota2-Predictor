import requests
from bs4 import BeautifulSoup
import json
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
}


def get_version_by_match(match_id):
    url = f"https://www.datdota.com/matches/{match_id}"

    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, "html.parser")

        h2_element = soup.find('h2')

        # Extract version number from each h2 element
        version = str(re.findall(r'Patch (\d+\.\d+)', h2_element.get_text())[0]).replace('Patch ', '')

        return version

    else:
        print("Failed to retrieve VERSION from the website.")
        return 7.35


def get_players_and_heroes_by_match(match_id):
    url = f"https://www.datdota.com/matches/{match_id}"

    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, "html.parser")

        """ Getting all heroes from match"""
        # Find all <img> elements with title attribute
        tbody_elements = soup.find_all('tbody')

        players_and_heroes = []

        for tbody in tbody_elements:
            tr_elements = tbody.find_all('tr')
            for tr in tr_elements:
                td_elements = tr.find_all('td')
                if len(td_elements) >= 2:
                    hero = td_elements[0].find('img')['title'].replace(' ', '-').replace("'", "").lower()
                    player_href = td_elements[1].find('a')['href']
                    player_name = td_elements[1].find('a').text
                    player_id = player_href.split('/')[-1]

                    players_and_heroes.append({f"{player_id}": hero})

        # Returning first 5 as Radiant team, and other 5 as Dire
        return players_and_heroes[:5], players_and_heroes[5:]

    else:
        print("Failed to retrieve PLAYERS AND HEROES from the website.")
        return None



