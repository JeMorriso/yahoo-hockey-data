import requests
import json
from utils import util

class NHLConnection:
    def __init__(self):
        self.NHL_base_url = "https://statsapi.web.nhl.com/api/v1/"

    def api_call(self, endpoint):
        r = requests.get(endpoint)
        r_json = json.dumps(r.json(), indent=4)
        return json.loads(r_json)

    def parse_raw_NHL_teams(self):
        teams_data = self.api_call("https://statsapi.web.nhl.com/api/v1/teams")

        teams = []
        for team in teams_data['teams']:
            teams.append({'team_id': team['id'], 'team_name': team['name'], 'abbreviation': team['abbreviation']})

        return teams

    # NHL.com's player result is a list with elements in a particular order
    def parse_player(self, player):

        player_dict = { 'nhl_id': player[0],
                        'birth_date': player[-5],
                        'birth_state_province': player[-7],
                        'nationality': player[-6],
                        'height': util.height_to_int(player[5]),
                        'weight': player[6] }
        return player_dict

    def find_player_from_suggestions(self, player):
        # return suggested players based on last name query
        suggestions = self.api_call(f"https://suggest.svc.nhl.com/svc/suggest/v1/minactiveplayers/{player['last_name']}")

        # each suggested player's info delimited by |
        # if there is only 1 result, found the player
        if len(suggestions['suggestions']) == 1:
            return suggestions['suggestions'][0].split('|')

        # if there are multiple suggested players, then use first and last names and NHL team to pick the correct one
        else:
            for str_ in suggestions['suggestions']:
                player_list = str_.split('|')
                if player_list[2] == player['first_name'] and player_list[-4] == player['nhl_team']:
                    return player_list

            # if it's STILL not working try searching by first name (Kyle Connor appears for 'Kyle' but not for 'Connor' for some reason)
            suggestions = self.api_call(
                f"https://suggest.svc.nhl.com/svc/suggest/v1/minactiveplayers/{player['first_name']}")

            for str_ in suggestions['suggestions']:
                player_list = str_.split('|')
                if player_list[2] == player['first_name'] and player_list[-4] == player['nhl_team']:
                    return player_list

        # assume if we get here that the player is inactive.
        return None

    # return all NHL.com game ids for a given date
    def parse_raw_daily_schedule(self, date):
        schedule_url = self.NHL_base_url + f"/schedule?date={date.strftime('%Y-%m-%d')}"
        schedule = self.api_call(schedule_url)

        if schedule['totalGames'] == 0:
            return

        game_ids = []
        games = schedule['dates'][0]['games']
        for game in games:
            # not a regular season game
            if game['gameType'] != 'R':
                continue
            game_ids.append(game['gamePk'])

        return game_ids

    def parse_raw_boxscore(self, game_id):
        boxscore_url = self.NHL_base_url + "/game/{}/boxscore".format(game_id)
        boxscore = self.api_call(boxscore_url)

        return boxscore['teams']

    # makes more sense to have this method call parse_raw_boxscore directly then having 2 separate calls on client side
    def parse_raw_boxscore_to_player_ids(self, game_id):
        boxscore = self.parse_raw_boxscore(game_id)

        player_stats = {}
        for p_data in boxscore['away']['players'].values():
            player_stats[p_data['person']['id']] = p_data['stats']

        for p_data in boxscore['home']['players'].values():
            player_stats[p_data['person']['id']] = p_data['stats']

        return player_stats

    def parse_raw_skater_stats(self):
        pass

