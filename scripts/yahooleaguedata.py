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
