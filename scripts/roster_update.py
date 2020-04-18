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

# get data from yahoo, and then insert into db
def roster_player_update(date):
    rosters, players = league_db_composite.league.parse_raw_rosters(datetime.datetime.strftime(date, "%Y-%m-%d"))

    player_update(players)
    roster_update(date)


def player_update(players):
    # list of players to retrieve their NHL teams
    new_players = []

    # for each player, check if they exist in the DB yet, and if not, get their NHL id
    # need to get player's current NHL team from Yahoo in order to cross reference to correct player on NHL.com
    for player in players:
        db_player = league_db_composite.db.get_player(player['yahoo_key'])
        if db_player is None:
            new_players.append(player)

    new_players_with_teams = league_db_composite.league.get_players_nhl_teams(new_players)

    for player in new_players_with_teams:
        player_list = league_db_composite.nhl.find_player_from_suggestions(player)

        # couldn't find player - treat this as inactive - remove them from the list
        # potential unexpected behaviour here
        if player is None:
            new_players_with_teams.remove(player)

        # otherwise, take player_list and turn it into a dictionary containing the necessary info
        # about the player from NHL.com, and update the player dictionary with it
        else:
            player.update(league_db_composite.nhl.parse_player(player_list))

    # commit all the new players to db
    league_db_composite.db.insert_players(new_players_with_teams)


def roster_update(date):
    league_db_composite.db.insert_rosters()





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

        roster_player_update(args.date)

