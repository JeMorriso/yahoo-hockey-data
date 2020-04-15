import mysql.connector
import os


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
        cursor.execute(sql, (league['league_id'],))
        # fetchone returns a tuple
        league_id = cursor.fetchone()[0]

        return league_id

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
            # clear the query
            # cursor.fetchall()

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

    def insert_weeks(self, weeks, league):
        cursor = self.connection.cursor()

        league_id = self.get_league_id(league)

        for week in weeks:
            sql = "select * from week where league_id = %s and week_number = %s"
            cursor.execute(sql, (league_id, weeks.index(week)+1))
            cursor.fetchall()
            if cursor.rowcount == 0:
                # makes it easier to insert into db
                week['league_id'] = league_id
                week['week_number'] = weeks.index(week)+1

                sql = """insert into week
                (league_id, week_number, start_date, end_date)
                values(%(league_id)s, %(week_number)s, %(start_date)s, %(end_date)s)"""
                cursor.execute(sql, week)

        self.connection.commit()
