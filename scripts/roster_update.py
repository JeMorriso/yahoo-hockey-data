from league_setup import LeagueDBComposite
import argparse
import datetime
import os
import copy

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--league_type', required=True)
parser.add_argument('-i', '--league_id', type=int, required=True)
parser.add_argument('-s', '--start-date', type=datetime.date.fromisoformat)
parser.add_argument('-e', '--end-date', type=datetime.date.fromisoformat)
parser.add_argument('-d', '--date', type=datetime.date.fromisoformat)

if __name__ == "__main__":
    args = parser.parse_args()

    api_url = "https://fantasysports.yahooapis.com/fantasy/v2"
    league_url = api_url + "/leagues;league_keys=" + args.league_type + ".l." + str(args.league_id)

    # not sure why YahooLeagueData's working directory is the project base folder, while this script lives in /scripts
    old_path = os.getcwd()
    os.chdir('../')
    league_db_composite = LeagueDBComposite(league_url, setup=False)
    os.chdir(old_path)

    # check if start-date, end-date options provided, and if so, loop
    if args.start_date:
        # today is default end date
        if not args.end_date:
            args.end_date = datetime.datetime.today()

        # get weeks from db
        sql = "select start_date from week"

    # only updating rosters for 1 day
    else:
        # if date not provided default to today
        if not args.date:
            args.date = datetime.datetime.today()

        league_db_composite.roster_player_update(args.date)

