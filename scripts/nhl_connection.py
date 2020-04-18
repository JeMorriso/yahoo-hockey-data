import requests
import json

class NHLConnection:
    def __init__(self):
        self.NHL_base_url = "https://statsapi.web.nhl.com/api/v1/"

    def api_call(self, endpoint):
        r = requests.get(endpoint)
        r_json = json.dumps(r.json(), indent=4)
        return json.loads(r_json)

    def parse_player(self, player):
        pass

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
