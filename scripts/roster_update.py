from league_setup import LeagueDBComposite
import argparse
import datetime
import os

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

        # get start date's week from db
        # TODO: if start in second half of week, it will still run over first half because we're getting start date from db
        week, start_date, end_date = league_db_composite.db.get_week(args.start_date, league_db_composite.db.get_league_id(league_db_composite.league.parse_raw_league_data()))
        # the database actually returns a date object since the type in the database is specified as 'date'
        current_date = start_date
        while current_date <= args.end_date:
            league_db_composite.roster_player_update(current_date)
            # the only week that doesn't start on a Monday is week 1
            # if before Monday in week 1
            if week == 1 and current_date <= start_date + datetime.timedelta(days=(6 - start_date.weekday())):
                # this line sets current date to this Monday (relative to prev current date) (unless current day is Monday)
                current_date += datetime.timedelta(days=(0 - current_date.weekday()) % 7)
            else:
                current_date += datetime.timedelta(days=7)

    # only updating rosters for 1 day
    else:
        # if date not provided default to today
        if not args.date:
            args.date = datetime.datetime.today()

        league_db_composite.roster_player_update(args.date)

