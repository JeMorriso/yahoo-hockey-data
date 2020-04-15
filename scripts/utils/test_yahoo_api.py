from yahooleaguedata import YahooLeagueData

api_url = "https://fantasysports.yahooapis.com/fantasy/v2"
league_url = api_url + "/leagues;league_keys=nhl.l.18538"
league = YahooLeagueData(league_url)
