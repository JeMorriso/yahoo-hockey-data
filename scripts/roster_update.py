from league_setup import LeagueDBComposite
import argparse
import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--league_type', required=True)
parser.add_argument('-i', '--league_id', type=int, required=True)
parser.add_argument('-s', '--start-date', type=datetime.date.fromisoformat)
parser.add_argument('-e', '--end-date', type=datetime.date.fromisoformat)
parser.add_argument('-d', '--date', type=datetime.date.fromisoformat)


# get data from yahoo, and then insert into db
def roster_update(date):
    rosters = league_db_composite.league.parse_raw_rosters(datetime.datetime.strftime(date, "%Y-%m-%d"))

    # for each player, check if they exist in the DB yet, and if not, get their NHL id
    pass


if __name__ == "__main__":
    args = parser.parse_args()

    api_url = "https://fantasysports.yahooapis.com/fantasy/v2"
    league_url = api_url + "/leagues;league_keys=" + args.league_type + ".l." + str(args.league_id)

    league_db_composite = LeagueDBComposite(league_url, setup=False)

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

        roster_update(args.date)

