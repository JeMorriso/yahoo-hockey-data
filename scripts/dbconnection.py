import mysql.connector
import os
import datetime


class DBConnection:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=os.getenv("HOST"),
            user=os.getenv("USER"),
            # os.getenv('DATABASE") not working in pycharm
            database="in_it_to_winnik",
            # os.getenv('PASSWORD') not working in pycharm
            password="moomoo")

    # this makes me think that it's not useful to store both yahoo and my own IDs
    def get_league_id(self, league):
        cursor = self.connection.cursor()

        # get the league id (the database id, not the yahoo id)
        sql = "select id from league where yahoo_id = %s"
        # using C-style string formatting with tuple in cursor.execute prevents SQL injection attacks
        cursor.execute(sql, (league['league_id'],))
        # fetchone returns a tuple
        league_id = cursor.fetchone()[0]

        cursor.close()
        return league_id

    def get_team_ids(self, team_keys):
        cursor = self.connection.cursor()

        team_ids = {}
        # get all the team ids from the database
        for yahoo_key in team_keys:
            sql = "select id from fantasy_team where yahoo_key = %s"
            cursor.execute(sql, (yahoo_key,))
            # relying on teams being in database here, no error checking
            team_ids[yahoo_key] = cursor.fetchone()[0]

        cursor.close()
        return team_ids

    def get_player(self, yahoo_key):
        cursor = self.connection.cursor()

        sql = "select * from player where yahoo_key = %s"
        cursor.execute(sql, (yahoo_key,))
        result = cursor.fetchone()
        player = None
        if result:
            player = result[0]

        cursor.close()
        return player

    def get_player_NHL_id(self, id_):
        cursor = self.connection.cursor()

        sql = "select nhl_id from player where id = %s"
        cursor.execute(sql, (id_,))
        result = cursor.fetchone()

        # roster table may have players that aren't in player table because their NHL id could not be found,
        # because they aren't active in the NHL (Klas Dahlbeck).
        # foreign keys CAN have null values
        nhl_id = None
        if result is not None:
            nhl_id = result[0]

        cursor.close()
        return nhl_id

    def get_week(self, date, league_id):
        cursor = self.connection.cursor()

        sql = "select * from week where league_id = %s and start_date <= %s and end_date >= %s"
        cursor.execute(sql, (league_id, date, date))
        week = cursor.fetchone()

        cursor.close()
        # return week number, start and end dates
        return week[2], week[3], week[4]

    # get all players on some roster on a given date
    def get_player_ids_on_rosters(self, date):
        cursor = self.connection.cursor()

        sql = "select player_id from roster where start_date <= %s and end_date >= %s"
        cursor.execute(sql, (date, date))
        player_ids = cursor.fetchall()

        cursor.close()

        # convert list of tuples into list of player_ids
        return [x[0] for x in player_ids]

    def get_player_nhl_team(self, id, date):
        cursor = self.connection.cursor()

        sql = "select nhl_id from player_nhl_team where player_id = %s and start_date <= %s and end_date >= %s"
        cursor.execute(sql, (id, date, date))
        team_id = cursor.fetchone()

        cursor.close()
        return team_id

    def get_NHL_team_ids(self):
        cursor = self.connection.cursor()

        sql = "select nhl_id from nhl_team"
        cursor.execute(sql)
        nhl_teams = cursor.fetchall()

        cursor.close()
        return [x[0] for x in nhl_teams]

    def insert_league_data(self, league_object):
        cursor = self.connection.cursor()

        # check if league already exists in db, and if not, insert
        sql = "select * from league where yahoo_id = %(league_id)s"
        cursor.execute(sql, league_object)
        cursor.fetchall()
        if cursor.rowcount == 0: 
            # brackets with quotes on each line is just multiline string in Python
            # see python mysql cursor.execute for formatting explanation
            sql = ("insert into league"
                "(yahoo_id, yahoo_key, name, url, num_teams, weekly_deadline, scoring_type,"
                "start_date, end_date, start_week, end_week)"
                "values(%(league_id)s, %(league_key)s, %(name)s, %(url)s, %(num_teams)s, %(weekly_deadline)s,"
                "%(scoring_type)s, %(start_date)s, %(end_date)s, %(start_week)s, %(end_week)s)")

            cursor.execute(sql, league_object)
            self.connection.commit()

        cursor.close()

    # league must already exist in league table
    def insert_scoring_categories(self, categories, league):
        cursor = self.connection.cursor()

        # for each category, check if category exists in scoring_category table, and if not, insert it
        # insert each category and league pair into league_scoring_category
        for category in categories:
            sql = "select * from scoring_category where category_abbreviation = %s"
            # need to have comma so that it gets treated as a tuple, not a scalar (see mySQL docs)
            cursor.execute(sql, (category['category_abbreviation'],))
            cursor.fetchall()
            if cursor.rowcount == 0:
                sql = ("insert into scoring_category"
                        "(category_name, category_abbreviation, position_type)"
                        "values(%(category_name)s, %(category_abbreviation)s, %(position_type)s)")
        
                cursor.execute(sql, category)
                self.connection.commit()

            league_id = self.get_league_id(league)

            # get the category id
            sql = "select id from scoring_category where category_abbreviation = %s"
            cursor.execute(sql, (category['category_abbreviation'],))
            # fetchone returns a tuple
            category_id = cursor.fetchone()[0]

            # now check the other table
            sql = """select * from league_scoring_category where
                        category_id = %s
                        AND league_id = %s"""
            cursor.execute(sql, (category_id, league_id))
            cursor.fetchall()
            if cursor.rowcount == 0:
                sql = "insert into league_scoring_category (league_id, category_id) values(%s, %s)"
                cursor.execute(sql, (league_id, category_id))
        
        self.connection.commit()
        cursor.close()

    # league must already exist in league table
    def insert_fantasy_teams(self, teams, league):
        cursor = self.connection.cursor()

        league_id = self.get_league_id(league)

        for team in teams:
            sql = "select * from fantasy_team where yahoo_key = %s"
            cursor.execute(sql, (team['yahoo_key'],))
            cursor.fetchall()
            if cursor.rowcount == 0:
                # makes it easier to insert into db
                team['league_id'] = league_id

                sql = """insert into fantasy_team 
                (yahoo_key, yahoo_id, name, logo_url, manager, league_id)
                values(%(yahoo_key)s, %(yahoo_id)s, %(name)s, %(logo_url)s, %(manager)s, %(league_id)s)"""

                cursor.execute(sql, team)

        self.connection.commit()
        cursor.close()

    def insert_weeks(self, weeks, league):
        cursor = self.connection.cursor()

        league_id = self.get_league_id(league)

        for i, week in enumerate(weeks):
            sql = "select * from week where league_id = %s and week_number = %s"
            cursor.execute(sql, (league_id, i+1))
            cursor.fetchall()
            if cursor.rowcount == 0:
                # makes it easier to insert into db
                week['league_id'] = league_id
                week['week_number'] = i+1

                sql = """insert into week
                (league_id, week_number, start_date, end_date)
                values(%(league_id)s, %(week_number)s, %(start_date)s, %(end_date)s)"""
                cursor.execute(sql, week)

        self.connection.commit()
        cursor.close()

    # teams, weeks must already be in db
    def insert_matchups(self, matchups_dict, league):
        cursor = self.connection.cursor();

        team_ids = self.get_team_ids(matchups_dict['team_keys'])

        for i, week in enumerate(matchups_dict['matchups_by_week']):
            # get the week id
            sql = "select id from week where league_id = %s and week_number = %s"
            cursor.execute(sql, (self.get_league_id(league), i+1))
            week_id = cursor.fetchone()[0]

            for matchup in week:
                # check if it's already in the db
                sql = "select * from matchup where home_id = %s and away_id = %s and week_id = %s"
                cursor.execute(sql, (team_ids[matchup[0]], team_ids[matchup[1]], week_id))
                cursor.fetchall()
                if cursor.rowcount == 0:
                    sql = """insert into matchup
                    (home_id, away_id, week_id)
                    values(%s, %s, %s)"""
                    cursor.execute(sql, (team_ids[matchup[0]], team_ids[matchup[1]], week_id))

        self.connection.commit()
        cursor.close()

    def insert_NHL_teams(self, teams):
        cursor = self.connection.cursor()

        for team in teams:
            sql = "select * from nhl_team where abbreviation = %s"
            cursor.execute(sql, (team['abbreviation'],))
            cursor.fetchall()
            if cursor.rowcount == 0:
                sql = """insert into nhl_team 
                (nhl_id, name, abbreviation)
                values(%(team_id)s, %(team_name)s, %(abbreviation)s)"""

                cursor.execute(sql, team)

        self.connection.commit()
        cursor.close()

    def insert_rosters(self, rosters, start_date, end_date):
        cursor = self.connection.cursor()

        db_team_ids = self.get_team_ids([x['team_key'] for x in rosters])
        for i, roster in enumerate(rosters):
            for player in rosters[i]['roster']:
                db_player_id = self.get_player(player['player_key'])
                # check that same player, date combo has not been already inserted
                sql = "select * from roster where player_id = %s and start_date = %s and end_date = %s"
                cursor.execute(sql, (db_player_id, start_date, end_date))
                cursor.fetchall()
                if cursor.rowcount == 0:
                    sql = """insert into roster
                    (team_id, player_id, selected_position, start_date, end_date)
                    values(%s, %s, %s, %s, %s)"""
                    cursor.execute(sql, (db_team_ids[roster['team_key']], db_player_id, player['selected_position'], start_date, end_date))

        self.connection.commit()
        cursor.close()

    def insert_players(self, players):
        cursor = self.connection.cursor()

        for player in players:
            # check if player already in db
            sql = "select * from player where yahoo_key = %s"
            cursor.execute(sql, (player['yahoo_key'],))
            cursor.fetchall()
            if cursor.rowcount == 0:
                print(player)
                sql = """insert into player 
                (first_name, last_name, yahoo_id, yahoo_key, nhl_id, birth_date, birth_state_province, nationality, height, weight)
                values(%(first_name)s, %(last_name)s, %(yahoo_id)s, %(yahoo_key)s, %(nhl_id)s, %(birth_date)s, %(birth_state_province)s, %(nationality)s, %(height)s, %(weight)s)"""
                cursor.execute(sql, player)

        self.connection.commit()
        cursor.close()

