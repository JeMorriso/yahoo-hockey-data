from yahoo_oauth import OAuth2
import json
import os


class YahooLeagueData:
    def __init__(self, league_url):
        self.api_url = "https://fantasysports.yahooapis.com/fantasy/v2"
        self.league_url = league_url

        print(os.getcwd())
        self.auth = OAuth2(None, None, from_file='credentials.json', base_url=self.api_url)

    # execute API call and return python object from returned data
    def api_call(self, endpoint):
        # rauth utilizes python Requests module, so its a python Requests response object that is being returned.
        # decodes the response into json format
        response = self.auth.session.get(endpoint, params={'format': 'json'})
        response_json = json.dumps(response.json())

        # now take the json and turn it into a python object
        return json.loads(response_json)

    def parse_raw_league_data(self):
        league_data = self.api_call(self.league_url)

        # grab the relevant data
        return league_data['fantasy_content']['leagues']['0']['league'][0]

    def parse_raw_scoring_categories(self):
        settings_data = self.api_call(self.league_url + "/settings")
        settings_data = settings_data['fantasy_content']['leagues']['0']['league'][1]['settings'][0]['stat_categories']['stats']

        scoring_categories = []
        for category_dict in settings_data:
            position = 'skater' if category_dict['stat']['position_type'] == 'P' else 'goalie'
            scoring_categories.append({ 'category_abbreviation': category_dict['stat']['display_name'], \
                'category_name': category_dict['stat']['name'], \
                'position_type': position})

        return scoring_categories

    def parse_raw_teams(self):
        teams_data = self.api_call(self.league_url + "/teams")

        teams_data = teams_data['fantasy_content']['leagues']['0']['league'][1]['teams']

        # remove count key
        teams_data.pop('count', None)

        teams = []
        for team in teams_data:
            team = teams_data[team]['team'][0]
            teams.append({'name': team[2]['name'], 'yahoo_key': team[0]['team_key'], \
                          'yahoo_id': team[1]['team_id'], 'logo_url': team[5]['team_logos'][0]['team_logo']['url'], \
                          'manager': team[19]['managers'][0]['manager']['nickname']})

        return teams

    def parse_raw_weeks(self):
        teams = self.parse_raw_teams()
        # here we're using the first team in the league's matchup endpoint to extract the beginning and end dates for each week
        matchup_data = self.api_call(self.api_url + '/team/' + teams[0]['yahoo_key'] + '/matchups')

        matchups = matchup_data['fantasy_content']['team'][1]['matchups']
        # remove count key
        matchups.pop('count', None)

        weeks = []
        # the weeks are sequential, so use index of weeks to figure out which week it is
        for matchup in matchups:
            weeks.append({'start_date': matchups[matchup]['matchup']['week_start'], \
                          'end_date':  matchups[matchup]['matchup']['week_end']})

        return weeks

    # return all regular season matchups
    def parse_raw_matchups(self):
        # get access to the team key so that we can build the matchup endpoint url
        teams = self.parse_raw_teams()

        settings_data = self.api_call(self.league_url + '/settings')
        reg_season_weeks = int(settings_data['fantasy_content']['leagues']['0']['league'][1]['settings'][0]['playoff_start_week'])-1

        # list of lists that store each matchup each week
        matchups_by_week = [[] for i in range(0, reg_season_weeks)]
        # also store team_keys, it's easier on database side
        team_keys = []

        for team in teams:
            matchup_data = self.api_call(self.api_url + '/team/' + team['yahoo_key'] + '/matchups')

            team_key = matchup_data['fantasy_content']['team'][0][0]['team_key']
            team_keys.append(team_key)

            matchups = matchup_data['fantasy_content']['team'][1]['matchups']

            # remove count key
            matchups.pop('count', None)

            for matchup in matchups:
                # if playoffs matchup, skip
                if int(matchups[matchup]['matchup']['week']) <= reg_season_weeks:
                    week_index_zero = int(matchups[matchup]['matchup']['week'])-1
                    opponent_team_key = matchups[matchup]['matchup']['0']['teams']['1']['team'][0][0]['team_key']
                    # check if the opponent already exists in one of the lists for the week
                    # if so, add this team to that list, otherwise add this team to a new list
                    for pair in matchups_by_week[week_index_zero]:
                        if opponent_team_key in pair:
                            pair.append(team_key)
                            break
                    else:
                        matchups_by_week[week_index_zero].append([team_key])

        return {'team_keys': team_keys, 'matchups_by_week': matchups_by_week}

    def _find_player_nhl_team(self, player_data):
        for dict_ in player_data:
            if 'editorial_team_abbr' in dict_:
                return dict_['editorial_team_abbr']
        return None

    # using date here so that it is flexible with daily-updating leagues
    def parse_raw_rosters(self, date=None):
        players = []
        rosters = []
        for team in self.parse_raw_teams():
            # optionally turn this into another function parse_raw_roster
            roster_url = f"{self.api_url}/team/{team['yahoo_key']}/roster;date={date}"
            roster = self.api_call(roster_url)

            roster = roster['fantasy_content']['team'][1]['roster']['0']['players']
            # remove count key
            roster.pop('count', None)

            roster_cleaned = []

            for player in roster:
                try:
                    nhl_team = roster[player]['player'][0][6]['editorial_team_abbr']
                except:
                    nhl_team = self._find_player_nhl_team(roster[player]['player'][0])

                # players list does not need to keep track of fantasy teams
                players.append({'first_name': roster[player]['player'][0][2]['name']['first'],
                                       'last_name': roster[player]['player'][0][2]['name']['last'],
                                       'yahoo_id': roster[player]['player'][0][1]['player_id'],
                                       'yahoo_key': roster[player]['player'][0][0]['player_key'],
                                       # NHL_team is for referencing NHL.com's API; doesn't go into player table
                                       'NHL_team': nhl_team})

                roster_cleaned.append({ # player_key doesn't go in roster table it is for getting player id from DB
                                        'player_key': roster[player]['player'][0][0]['player_key'],
                                        # similarly for team_key
                                        'team_key': team['yahoo_key'],
                                        'selected_position': roster[player]['player'][1]['selected_position'][1]['position']
                                        # dates not handled in this method since it was called with a date and weeks are variable
                                     })

            rosters.append(roster_cleaned)

        # this is a tuple being returned
        return rosters, players
