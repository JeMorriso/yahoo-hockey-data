from yahoo_oauth import OAuth2
import json


class YahooLeagueData:
    def __init__(self, league_url):
        self.api_url = "https://fantasysports.yahooapis.com/fantasy/v2"
        self.league_url = league_url
        self.auth = OAuth2(None,None, from_file='credentials.json', base_url=self.api_url)

    # execute API call and return python object from returned data
    def api_call(self, endpoint):
        # rauth utilizes python Requests module, so its a python Requests response object that is being returned.
        # decodes the response into json format
        response = self.auth.session.get(endpoint, params={'format': 'json'})
        response_json = json.dumps(response.json())

        # now take the json and turn it into a python object
        return json.loads(response_json)

    def parse_raw_league_data(self):
        league_data = self.api_call(self.league_url)

        # grab the relevant data
        return league_data['fantasy_content']['leagues']['0']['league'][0]

    def parse_raw_scoring_categories(self):
        settings_data = self.api_call(self.league_url + "/settings")
        settings_data = settings_data['fantasy_content']['leagues']['0']['league'][1]['settings'][0]['stat_categories']['stats']

        scoring_categories = []
        for category_dict in settings_data:
            position = 'skater' if category_dict['stat']['position_type'] == 'P' else 'goalie'
            scoring_categories.append({ 'category_abbreviation': category_dict['stat']['display_name'], \
                'category_name': category_dict['stat']['name'], \
                'position_type': position})

        return scoring_categories

    def parse_raw_teams(self):
        teams_data = self.api_call(self.league_url + "/teams")

        teams_data = teams_data['fantasy_content']['leagues']['0']['league'][1]['teams']

        # remove count key
        teams_data.pop('count', None)

        teams = []
        for team in teams_data:
            team = teams_data[team]['team'][0]
            teams.append({'name': team[2]['name'], 'yahoo_key': team[0]['team_key'], \
                          'yahoo_id': team[1]['team_id'], 'logo_url': team[5]['team_logos'][0]['team_logo']['url'], \
                          'manager': team[19]['managers'][0]['manager']['nickname']})

        return teams

    def parse_raw_weeks(self):
        teams = self.parse_raw_teams()
        # here we're using the first team in the league's matchup endpoint to extract the beginning and end dates for each week
        matchup_data = self.api_call(self.api_url + '/team/' + teams[0]['yahoo_key'] + '/matchups')

        matchups = matchup_data['fantasy_content']['team'][1]['matchups']

        # remove count key
        matchups.pop('count', None)

        weeks = []
        for matchup in matchups:
            weeks.append({'start_date': matchups[matchup]['matchup']['week_start'], \
                          'end_date':  matchups[matchup]['matchup']['week_end']})

        return weeks
