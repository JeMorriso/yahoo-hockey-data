from league_setup import LeagueDBComposite
import argparse
import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--league_type', required=True)
parser.add_argument('-i', '--league_id', type=int, required=True)
parser.add_argument('-s', '--start-date', type=datetime.date.fromisoformat)
parser.add_argument('-e', '--end-date', type=datetime.date.fromisoformat)

if __name__ == "__main__":
    args = parser.parse_args()

    api_url = "https://fantasysports.yahooapis.com/fantasy/v2"
    league_url = api_url + "/leagues;league_keys=" + args.league_type + ".l." + str(args.league_id)

    league_db_composite = LeagueDBComposite(league_url, setup=False)

    # check if start-date, end-date options provided, and if so, loop
    if args.start_date:
        # today is default end date
        if not args.end_date:
            pass


    exit
