import requests
from bs4 import BeautifulSoup

# Query example
"""
query = f'''
{{
    player(steamAccountId: {}) {{
        matchCount
        steamAccountId
        steamAccount {{
            realName
            avatar
        }}
    }}
}}
'''
"""

url = 'https://api.stratz.com/graphql'
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJTdWJqZWN0IjoiZjIwYzA5YmQtNTI3MS00ODA5LWEzNmYtN2ViMzU5NTI4NGY0IiwiU3RlYW1JZCI6IjI3NzE4MzU5OCIsIm5iZiI6MTcxMzQ3OTkwMSwiZXhwIjoxNzQ1MDE1OTAxLCJpYXQiOjE3MTM0Nzk5MDEsImlzcyI6Imh0dHBzOi8vYXBpLnN0cmF0ei5jb20ifQ.SMY12XInn6R8jxd2iQTqSX5L0zQNUZ1s0J5smEP1nnk'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
}


def make_request(query):
    # Make the request
    response = requests.post(url, json={'query': query}, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        # Print the error message
        return None


def get_and_save_all_heroes():
    query = f'''
    {{
        constants {{
            heroes(gameVersionId: 172, language: ENGLISH) {{
                displayName
            }}
        }}
    }}
    '''

    response = make_request(query)

    heroes_dict = response['data']['constants']['heroes']

    heroes = []

    for d in heroes_dict:
        hero = d['displayName'].replace(' ', '-').replace("'", "").lower()
        heroes.append(hero)
        heroes = sorted(heroes)

    with open('heroes', 'w') as file:
        for hero in heroes:
            file.write(hero + '\n')


def get_players_by_match_id(match_id):
    query = f'''
    {{
        match(id: {match_id}) {{
            radiantTeam {{
                members(skip: 0, take: 5) {{
                    steamAccountId,
                    steamAccount {{
                        proSteamAccount {{
                            name
                        }}
                    }}
                }}
            }},
            direTeam {{
                members(skip: 0, take: 5) {{
                    steamAccountId,
                    steamAccount {{
                        proSteamAccount {{
                            name
                        }}
                    }}
                }}
            }},
            players {{
                steamAccountId,
                isRadiant,
                hero {{
                    displayName
                }}
            }}
        }}
    }}
    '''

    response = make_request(query)

    if response is None:
        return None
    else:

        # Sample response for radiantTeam and direTeam parts:
        """
        {'data':
            {'match': {
                'radiantTeam': {
                    'members': [
                        {'steamAccountId': 331855530, 'steamAccount': {'proSteamAccount': {'name': 'Pure'}}},
                        {'steamAccountId': 164199202, 'steamAccount': {'proSteamAccount': {'name': '9Class'}}},
                        {'steamAccountId': 140288368, 'steamAccount': {'proSteamAccount': {'name': 'Tobi'}}},
                        {'steamAccountId': 136829091, 'steamAccount': {'proSteamAccount': {'name': 'Whitemon'}}},
                        {'steamAccountId': 94054712, 'steamAccount': {'proSteamAccount': {'name': 'Topson'}}}]},
                'direTeam': {
                    'members': [
                        {'steamAccountId': 25907144, 'steamAccount': {'proSteamAccount': {'name': 'Cr1t-'}}},
                        {'steamAccountId': 898455820, 'steamAccount': {'proSteamAccount': {'name': 'Malr1ne'}}},
                        {'steamAccountId': 183719386, 'steamAccount': {'proSteamAccount': {'name': 'ATF'}}},
                        {'steamAccountId': 100058342, 'steamAccount': {'proSteamAccount': {'name': 'skiter'}}},
                        {'steamAccountId': 10366616, 'steamAccount': {'proSteamAccount': {'name': 'Sneyking'}}}]}}}}
        """

        radiant = []
        dire = []
        players = []

        for member in response['data']['match']['radiantTeam']['members']:
            player_id = member['steamAccountId']
            player_nickname = member['steamAccount']['proSteamAccount']['name']

            players.append({f"{player_id}": player_nickname})

        for member in response['data']['match']['direTeam']['members']:
            player_id = member['steamAccountId']
            player_nickname = member['steamAccount']['proSteamAccount']['name']

            players.append({f"{player_id}": player_nickname})

        for player in response['data']['match']['players']:
            hero = player['hero']['displayName'].replace(' ', '-').replace("'", "").lower()
            if player['isRadiant']:
                radiant.append({f"{player['steamAccountId']}": hero})
            else:
                dire.append({f"{player['steamAccountId']}": hero})

        return radiant, dire, players


def get_player_networth_in_match(match_id, player_id):
    # We will pull data about first 10 minutes of the match for player
    minute = 10

    query = f'''
        {{
            match(id: {match_id}) {{
               players(steamAccountId: {player_id}) {{
                    stats {{
                        networthPerMinute
                    }}
               }}
            }}
        }}
        '''

    response = make_request(query)
    extracted = response['data']['match']['players'][0]['stats']['networthPerMinute'][minute]

    if response is None or extracted is None:
        return None
    else:
        return response['data']['match']['players'][0]['stats']['networthPerMinute'][minute]


def get_player_rank_in_division(player_id):
    query = f'''
            {{
                player(steamAccountId: {player_id}) {{
                    leaderboardRanks(skip: 0, take: 1){{
                        rank
                    }}
                }}
            }}
            '''

    response = make_request(query)

    if response is None:
        return None
    else:
        try:
            data = response['data']['player']['leaderboardRanks'][0]['rank']
            if data is not None:
                return data
            else:
                return -1
        except IndexError:
            return -1


def get_player_number_of_matches_and_winrate(player_id):
    query = f'''
                {{
                    player(steamAccountId: {player_id}) {{
                        matchCount,
                        winCount
                    }}
                }}
                '''

    response = make_request(query)
    extracted = response['data']['player']['matchCount']

    if response is None or extracted is None:
        return None
    else:
        num_matches = response['data']['player']['matchCount']
        win_count = response['data']['player']['winCount']

        return num_matches, round(win_count / num_matches, 3)


def get_hero_by_id(hero_id):
    query = f'''
                    {{
                    constants{{
                        hero(id: {hero_id}, gameVersionId: 172, language: ENGLISH) {{
                            displayName
                        }}
                        }}
                    }}
                    '''

    response = make_request(query)
    extracted = response['data']['constants']['hero']

    if response is None or extracted is None:
        return None
    else:
        return extracted




