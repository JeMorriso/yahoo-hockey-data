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
    league_object = league.parse_raw_league_data()
    db.insert_league_data(league_object)

    categories_object = league.parse_raw_scoring_categories()
    db.insert_scoring_categories(categories_object, league_object)

    # insert fantasy teams
    # insert weeks


if __name__ == '__main__':
    args = parser.parse_args()

    api_url = "https://fantasysports.yahooapis.com/fantasy/v2"
    league_url = api_url + "/leagues;league_keys=" + args.league_type + ".l." + str(args.league_id)

    db = DBConnection()
    league = YahooLeagueData(league_url)

    setup()

