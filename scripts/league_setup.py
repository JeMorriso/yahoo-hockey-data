from yahoo_oauth import OAuth2
import json
import argparse
import datetime

from dbconnection import DBConnection
from yahooleaguedata import YahooLeagueData
from nhl_connection import NHLConnection

# not sure how to handle other league types yet
    # would need different database most likely
parser = argparse.ArgumentParser()
parser.add_argument('-t', '--league_type', required=True)
parser.add_argument('-i', '--league_id', type=int, required=True)

class LeagueDBComposite:
    def __init__(self, league_url, setup=False):
        self.db = DBConnection()
        self.league = YahooLeagueData(league_url)
        self.nhl = NHLConnection()
        if setup:
            self.setup_league()

    # gathers necessary information about the league as the first step, storing it to DB
    def setup_league(self):
        league_info = self.league.parse_raw_league_data()
        self.db.insert_league_data(league_info)

        categories = self.league.parse_raw_scoring_categories()
        self.db.insert_scoring_categories(categories, league_info)

        teams = self.league.parse_raw_teams()
        self.db.insert_fantasy_teams(teams, league_info)

        weeks = self.league.parse_raw_weeks()
        self.db.insert_weeks(weeks, league_info)

        matchups_dict = self.league.parse_raw_matchups()
        self.db.insert_matchups(matchups_dict, league_info)

    # get data from yahoo, and then insert into db
    def roster_player_update(self, date):
        rosters, players = self.league.parse_raw_rosters(datetime.datetime.strftime(date, "%Y-%m-%d"))

        # need to get league information to get week from database
        league = self.league.parse_raw_league_data()
        league_id = self.db.get_league_id(league)

        # figure out which week we're inserting roster data for
        week, start_date, end_date = self.db.get_week(date, league_id)

        self.player_update(players)
        self.roster_update(rosters, start_date, end_date)

    def player_update(self, players):
        # list of players to retrieve their NHL teams
        new_players = []

        # for each player, check if they exist in the DB yet, and if not, get their NHL id
        # need to get player's current NHL team from Yahoo in order to cross reference to correct player on NHL.com
        for player in players:
            db_player = self.db.get_player(player['yahoo_key'])
            if db_player is None:
                new_players.append(player)

        # this was causing big issues without copy
        new_players = self.league.get_players_nhl_teams(new_players)

        to_remove = []

        for i, player in enumerate(new_players):
            player_list = self.nhl.find_player_from_suggestions(player)

            # couldn't find player - treat this as inactive - remove them from the list
            # potential unexpected behaviour here
            if player_list is None:
                to_remove.append(player)

            # otherwise, take player_list and turn it into a dictionary containing the necessary info
            # about the player from NHL.com, and update the player dictionary with it
            else:
                print(player)
                player.update(self.nhl.parse_player(player_list))

        # remove inactive players (Klas Dahlbeck)
        for x in to_remove:
            new_players.remove(x)

        # commit all the new players to db
        self.db.insert_players(new_players)

    def roster_update(self, rosters, start_date, end_date):
        # check each player to see if their roster entry should be updated

        self.db.insert_rosters(rosters, start_date, end_date)


if __name__ == '__main__':
    args = parser.parse_args()

    api_url = "https://fantasysports.yahooapis.com/fantasy/v2"
    league_url = api_url + "/leagues;league_keys=" + args.league_type + ".l." + str(args.league_id)

    league_db_composite = LeagueDBComposite(league_url, setup=True)

