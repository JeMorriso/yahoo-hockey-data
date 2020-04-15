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


def setup():
    league_info = league.parse_raw_league_data()
    db.insert_league_data(league_info)

    categories = league.parse_raw_scoring_categories()
    db.insert_scoring_categories(categories, league_info)

    teams = league.parse_raw_teams()
    db.insert_fantasy_teams(teams, league_info)

    weeks = league.parse_raw_weeks()
    db.insert_weeks(weeks, league_info)

    matchups_dict = league.parse_raw_matchups()
    db.insert_matchups(matchups_dict, league_info)


if __name__ == '__main__':
    args = parser.parse_args()

    api_url = "https://fantasysports.yahooapis.com/fantasy/v2"
    league_url = api_url + "/leagues;league_keys=" + args.league_type + ".l." + str(args.league_id)

    db = DBConnection()
    league = YahooLeagueData(league_url)

    setup()

