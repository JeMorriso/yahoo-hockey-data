from yahoo_oauth import OAuth2
import json

url = "https://fantasysports.yahooapis.com/fantasy/v2"
league_url = "https://fantasysports.yahooapis.com/fantasy/v2/league/nhl.l.18538"

oauth = OAuth2(None,None, from_file='credentials.json', base_url=url)

# print relevant league data to json files so that I can see what is important to get from Yahoo

# league information
# response = oauth.session.get(league_url, params={'format': 'json'})

# with open("league.json", "w") as outfile:
#     json.dump(response.json(), outfile, indent=4)

# # team information
# response = oauth.session.get(league_url + "/teams", params={'format': 'json'})

# with open("teams.json", "w") as outfile:
#     json.dump(response.json(), outfile, indent=4)

# # roster information
# response = oauth.session.get(url + "/team/nhl.l.18538.t.1/roster;week=10", params={'format': 'json'})

# with open("roster.json", "w") as outfile:
#     json.dump(response.json(), outfile, indent=4)

# matchup information
# week does nothing with matchups
response = oauth.session.get(url + "/team/nhl.l.18538.t.1/matchups;week=10", params={'format': 'json'})

with open("matchup.json", "w") as outfile:
    json.dump(response.json(), outfile, indent=4)

# # stats information
# response = oauth.session.get(url + "/team/nhl.l.18538.t.1/stats", params={'format': 'json'})

# with open("stats.json", "w") as outfile:
#     json.dump(response.json(), outfile, indent=4)

# # scoreboard information
# response = oauth.session.get(league_url + "/scoreboard;week1", params={'format': 'json'})

# with open("scoreboard.json", "w") as outfile:
#     json.dump(response.json(), outfile, indent=4)

# league settings information
response = oauth.session.get(league_url + "/settings", params={'format': 'json'})

with open("settings.json", "w") as outfile:
    json.dump(response.json(), outfile, indent=4)

