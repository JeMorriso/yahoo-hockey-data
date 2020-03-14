from yahoo_oauth import OAuth2
import json
import argparse

import db

db_connection = db.connect()

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--league_type', required=True)
parser.add_argument('-i', '--league_id', type=int, required=True)

args = parser.parse_args()

api_url = "https://fantasysports.yahooapis.com/fantasy/v2"
league_url = api_url + "/league/" + args.league_type + "/l." + str(args.league_id)

oauth = OAuth2(None,None, from_file='credentials.json', base_url=api_url)

setup()

def setup():
  response = oauth.session.get(league_url, params={'format': 'json'})
  
