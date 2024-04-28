import requests

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
        print(response.text)
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
