import mysql.connector
import os


class DBConnection:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=os.getenv("HOST"),
            user=os.getenv("USER"),
            database=os.getenv("DATABASE"),
            # os.getenv('PASSWORD') not working in pycharm
            password=os.getenv("PASSWORD"))

    def insert_league_data(self, league_object):
        cursor = self.connection.cursor()

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

    # def