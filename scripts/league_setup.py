from yahoo_oauth import OAuth2
import json
import argparse

from dbconnection import DBConnection
# importing class Yahoo_League_Data
from yahooleaguedata import YahooLeagueData

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--league_type', required=True)
parser.add_argument('-i', '--league_id', type=int, required=True)


def setup(db):

    league_object = league.parse_raw_league_data()
    db.insert_league_data(league_object)

if __name__ == '__main__':
    args = parser.parse_args()

    api_url = "https://fantasysports.yahooapis.com/fantasy/v2"
    league_url = api_url + "/leagues;league_keys=" + args.league_type + ".l." + str(args.league_id)

    db = DBConnection()
    league = YahooLeagueData(league_url)

    setup(db)

