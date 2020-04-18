from yahooleaguedata import YahooLeagueData
import json
import os


api_url = "https://fantasysports.yahooapis.com/fantasy/v2"
league_url = api_url + "/leagues;league_keys=nhl.l.18538"

old_path = os.getcwd()
os.chdir('../../')
league = YahooLeagueData(league_url)
os.chdir(old_path)

league.parse_raw_teams()
league.parse_raw_rosters()


