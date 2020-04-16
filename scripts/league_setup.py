from yahoo_oauth import OAuth2
import json
import argparse

from dbconnection import DBConnection
from yahooleaguedata import YahooLeagueData

# not sure how to handle other league types yet
    # would need different database most likely
parser = argparse.ArgumentParser()
parser.add_argument('-t', '--league_type', required=True)
parser.add_argument('-i', '--league_id', type=int, required=True)

class LeagueDBComposite:
    def __init__(self, league_url, setup=False):
        self.db = DBConnection()
        self.league = YahooLeagueData(league_url)
        if setup:
            self.setup_league()

    # gathers necessary information about the league as the first step, storing it to DB
    def setup_league(self):
        league_info = self.league.parse_raw_league_data()
        self.db.insert_league_data(league_info)

        categories = self.league.parse_raw_scoring_categories()
        self.db.insert_scoring_categories(categories, league_info)

        teams = self.league.parse_raw_teams()
        self.db.insert_fantasy_teams(teams, league_info)

        weeks = self.league.parse_raw_weeks()
        self.db.insert_weeks(weeks, league_info)

        matchups_dict = self.league.parse_raw_matchups()
        self.db.insert_matchups(matchups_dict, league_info)


if __name__ == '__main__':
    args = parser.parse_args()

    api_url = "https://fantasysports.yahooapis.com/fantasy/v2"
    league_url = api_url + "/leagues;league_keys=" + args.league_type + ".l." + str(args.league_id)

    league_db_composite = LeagueDBComposite(league_url, setup=True)

