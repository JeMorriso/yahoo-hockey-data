from yahoo_oauth import OAuth2
import json


class YahooLeagueData:
    def __init__(self, league_url):
        self.api_url = "https://fantasysports.yahooapis.com/fantasy/v2"
        self.league_url = league_url
        self.auth = OAuth2(None,None, from_file='credentials.json', base_url=self.api_url)

    def parse_raw_league_data(self):
        # rauth utilizes python Requests module, so its a python Requests response object that is being returned.

        # decodes the response into json format
        response = self.auth.session.get(self.league_url, params={'format': 'json'})
        league_json = (json.dumps(response.json(), indent=4))

        # now take the json and turn it into a python object
        league_object = json.loads(league_json)

        # grab the relevant data
        return league_object['fantasy_content']['leagues']['0']['league'][0]
