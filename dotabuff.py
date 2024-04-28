import requests
from bs4 import BeautifulSoup
import time
import random
import json

versions = ['7.30', '7.31', '7.32', '7.33', '7.34', '7.35']
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

for version in versions:
    counter_win_rates = []
    for hero in heroes:
        url = f"https://ru.dotabuff.com/heroes/{hero}/counters?date=patch_{version}"

        response = requests.get(url, headers=headers)

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

        # Introduce a random delay before making the next request
        # delay = random.uniform(0, 1)  # Random delay between 0 to 1 seconds
        # time.sleep(delay)

    with open(f'heroes_counter_winrates_{version}.json', 'w') as file:
        json.dump(counter_win_rates, file, indent=4)
