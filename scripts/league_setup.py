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
        categories = self.append_snake_case_categories(categories, self.nhl.categories)
        self.db.insert_scoring_categories(categories, league_info)

        teams = self.league.parse_raw_teams()
        self.db.insert_fantasy_teams(teams, league_info)

        weeks = self.league.parse_raw_weeks()
        self.db.insert_weeks(weeks, league_info)

        matchups_dict = self.league.parse_raw_matchups()
        self.db.insert_matchups(matchups_dict, league_info)

        nhl_teams = self.nhl.parse_raw_NHL_teams()
        self.db.insert_NHL_teams(nhl_teams)

    def append_snake_case_categories(self, categories, nhl_categories):
        cat_snake_dict = {'G': 'goals', 'A': 'assists', 'PIM': 'penalty_minutes', 'PPG': 'powerplay_goals', 'PPA': 'powerplay_assists', \
                    'SHP': 'shorthanded_points', 'GWG': 'game_winning_goals', 'SOG': 'shots_on_goal', 'FW': 'faceoff_wins', \
                    'HIT': 'hits', 'BLK': 'blocks', 'W': 'wins', 'GA': 'goals_against', 'GAA': 'goals_against_average', \
                    'SV': 'saves', 'SA': 'shots_against', 'SV%': 'save_percentage', 'SHO': 'shutouts'}

        for cat in categories:
            cat['category_snake_case'] = cat_snake_dict[cat['category_abbreviation']]

        # turn categories into a dict for adding NHL categories
        categories_dict = { x['category_snake_case']: x for x in categories}

        for k, v in nhl_categories['skater'].items():
            # not a category being tracked in the fantasy league
            if k not in categories_dict:
                # don't need abbrev for NHL categories, only yahoo
                categories_dict[k] = {'category_abbreviation': None, 'category_name': v, 'position_type': 'skater', \
                                        'is_fantasy_category': False, 'category_snake_case': k}

        for k, v in nhl_categories['goalie'].items():
            # not a category being tracked in the fantasy league
            if k not in categories_dict:
                # don't need abbrev for NHL categories, only yahoo
                categories_dict[k] = {'category_abbreviation': None, 'category_name': v, 'position_type': 'goalie', \
                                        'is_fantasy_category': False, 'category_snake_case': k}

        return list(categories_dict.values())

    # get data from yahoo, and then insert into db
    def roster_player_update(self, date):
        rosters, players = self.league.parse_raw_rosters(datetime.datetime.strftime(date, "%Y-%m-%d"))

        # need to get league information to get week from database
        league = self.league.parse_raw_league_data()
        league_id = self.db.get_league_id(league)

        # figure out which week we're inserting roster data for
        week, start_date, end_date = self.db.get_week(date, league_id)

        # this list is needed for players who don't return an id from NHL.com
        # they should not be inserted into player nor roster tables
        unavailable_players = []
        self.player_update(players, unavailable_players)
        # remove unavailable players from rosters
        for p in unavailable_players:
            for roster in rosters:
                to_remove = []
                for roster_p in roster['roster']:
                    if p['yahoo_key'] == roster_p['player_key']:
                        to_remove.append(roster_p)
                for x in to_remove:
                    print(roster)
                    roster['roster'].remove(x)
                    print(roster)


        # use this Sunday as the end date because certain weeks are long but you can change your roster for the Monday in the middle
        # 0 is Monday, 6 is Sunday
        this_Sunday = start_date + datetime.timedelta(days=(6-start_date.weekday()))
        if date <= this_Sunday:
            self.roster_update(rosters, start_date, this_Sunday)
        else:
            self.roster_update(rosters, this_Sunday + datetime.timedelta(days=1), end_date)

    def player_update(self, players, unavailable_players):
        # list of players to retrieve their NHL teams
        new_players = []

        # for each player, check if they exist in the DB yet, and if not, get their NHL id
        # need to get player's current NHL team from Yahoo in order to cross reference to correct player on NHL.com
        for player in players:
            db_player = self.db.get_player(player['yahoo_key'])
            if db_player is None:
                new_players.append(player)

        new_players = self.league.get_players_nhl_teams(new_players)

        for i, player in enumerate(new_players):
            player_list = self.nhl.find_player_from_suggestions(player)

            # couldn't find player - treat this as inactive - remove them from the list
            # potential unexpected behaviour here
            if player_list is None:
                unavailable_players.append(player)

            # otherwise, take player_list and turn it into a dictionary containing the necessary info
            # about the player from NHL.com, and update the player dictionary with it
            else:
                player.update(self.nhl.parse_player(player_list))
                print(player)

        # remove inactive players (Klas Dahlbeck)
        for x in unavailable_players:
            new_players.remove(x)

        # commit all the new players to db
        self.db.insert_players(new_players)

    def roster_update(self, rosters, start_date, end_date):
        # list containing records that need to be inserted into roster table
        insert_rosters = [{'team_key': x['team_key'], 'roster': []} for x in rosters]

        team_ids = self.db.get_team_ids([x['team_key'] for x in rosters])
        # dictionary comprehension is better than for loop
        team_ids_inverse = {v: k for k, v in team_ids.items()}

        # check each player to see if their roster entry should be updated
        for i, roster in enumerate(rosters):
            for player in roster['roster']:
                db_id = self.db.get_player(player['player_key'])
                # check the day before start_date to compare the last entry in roster table to the current player status
                db_player = self.db.get_player_roster(db_id, start_date - datetime.timedelta(days=1))
                if db_player is not None:
                    # if team and position matches, update the entry in the db
                    if team_ids_inverse[db_player[1]] == roster['team_key'] and db_player[3] == player['selected_position']:
                        self.db.update_player_roster(db_id, start_date - datetime.timedelta(days=1), end_date)
                    else:
                        insert_rosters[i]['roster'].append(player)
                # this branch should only be reached the first time a player is added to a roster (all players in first week for example)
                else:
                    print(f"player not found in db: {player}")
                    #TODO: insert debug statement here
                    insert_rosters[i]['roster'].append(player)

        self.db.insert_rosters(insert_rosters, start_date, end_date)

    def stats_update(self, date):
        game_ids = self.nhl.parse_raw_daily_schedule(date)

        # build dictionary of players appearing in boxscores on this date
        # this way there is no need to keep track of player NHL teams, and no brute force necessary because dict
        played_on_this_date = {}
        if game_ids is not None:
            for game_id in game_ids:
                played_on_this_date.update(self.nhl.parse_raw_boxscore_to_player_ids(game_id))

        # retrieve all the players on rosters on date
        db_player_ids = self.db.get_player_ids_on_rosters(date)
        # get their NHL ids
        nhl_ids = {}
        for p_id in db_player_ids:
            nhl_id = self.db.get_player_NHL_id(p_id)

            # should never be None - need to improve error handling from db.get_player_NHL_id
            if nhl_id is not None:
                nhl_ids[nhl_id] = p_id
            else:
                # TODO: log error
                pass

        for p_id in nhl_ids.keys():
            if p_id in played_on_this_date:
                if 'skaterStats' in played_on_this_date[p_id]:
                    player = self.nhl.parse_skater_stats(played_on_this_date[p_id]['skaterStats'])
                    player['skater_id'] = nhl_ids[p_id]
                    player['date_'] = datetime.datetime.strftime(date, "%Y-%m-%d")

                    self.db.insert_skater_stats(player)

                elif 'goalieStats' in played_on_this_date[p_id]:
                    player = self.nhl.parse_goalie_stats(played_on_this_date[p_id]['goalieStats'])
                    player['goalie_id'] = nhl_ids[p_id]
                    player['date_'] = datetime.datetime.strftime(date, "%Y-%m-%d")

                    self.db.insert_goalie_stats(player)


if __name__ == '__main__':
    args = parser.parse_args()

    api_url = "https://fantasysports.yahooapis.com/fantasy/v2"
    league_url = api_url + "/leagues;league_keys=" + args.league_type + ".l." + str(args.league_id)

    league_db_composite = LeagueDBComposite(league_url, setup=True)

