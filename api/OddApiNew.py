import os

import requests
import json
from bs4 import BeautifulSoup
from api.FixtureScrape import getCsv
import pandas as pd

from dataclasses import dataclass, asdict
@dataclass
class Game:
    date : str
    home : str
    away : str
    odds : list
    league: str
    def __post_init__(self):
        for odd in self.odds:
                float(odd)

nameMap = {}

with open("api/map.json", "r", encoding="utf-8") as f:
    nameMap = json.loads(f.read())

leagueMap = {
    "Serie A": "soccer-italy-serie-a",
    "Champions League": "soccer-international-clubs-uefa-champions-league",
    "Europa League": "soccer-international-clubs-uefa-europa-league",
    "Conference League": "soccer-international-clubs-t6eeb-uefa-europa-conference-league",
    "Premier League": "soccer-england-premier-league",
    "Bundesliga": "soccer-germany-bundesliga",
    "La Liga": "soccer-spain-laliga",
    "Serie B": "soccer-italy-serie-b",
    "Ligue 1": "soccer-france-ligue-1"
}

class BetAPI:
    def __init__(self):
        self.urlBetBase = "https://sports-api.cloudbet.com/pub/v2/odds/competitions/"
        self.db = None
    def cache_db(self, league):
        if not os.path.exists(f"api/cache/{league}cache.csv"):
            self.db = getCsv(league)
        else:
            self.db = pd.read_csv(f"api/cache/{league}cache.csv")
            return self.db

    def get_request(self, league):
        leagueformat = leagueMap[league]
        self.cache_db(league)
        headers = {
            "accept": "application/json",
            "X-API-Key": "eyJhbGciOiJSUzI1NiIsImtpZCI6Img4LThRX1YwZnlUVHRPY2ZXUWFBNnV2bktjcnIyN1YzcURzQ2Z4bE44MGMiLCJ0eXAiOiJKV1QifQ.eyJhY2Nlc3NfdGllciI6ImFmZmlsaWF0ZSIsImV4cCI6MjA3ODMzNDc0NCwiaWF0IjoxNzYyOTc0NzQ0LCJqdGkiOiI1ZWIwNGZjNS0xMjhiLTRhNGEtOTMyNS03Nzk3M2IwYjFmOWQiLCJzdWIiOiIxN2U0ZDk4MS1jODA1LTRkZDMtYmVmYi01NzhjNTkwNWMwY2EiLCJ0ZW5hbnQiOiJjbG91ZGJldCIsInV1aWQiOiIxN2U0ZDk4MS1jODA1LTRkZDMtYmVmYi01NzhjNTkwNWMwY2EifQ.leilGTjGj7zcxFC9zmsUAsK0UAezmGw9aZZrdFHtqtmO821nm4jr7HmqBVgtKzUTPEGpj10JPZVAjf-yr-F83iVLHQrclei-V-q56gxww8GPDd2ns8TMtOfU7SmWgiRzAa7e3wbFwurN9OgmIX-wYo6WvvBPPEdHWi2JesIORGyC8JwIW4f3O8pCcnCOvts2cE9sjO_WoocX-rW9a11EtgfgYST_JvmcvcXoA-Wt7BB3wjOXHuleYY2jT1vwjvlNTQFKPcRdzls_z2EhkUE6BJmpqsfGdNfNje7pYp3zqBzW0Q_lFkZuUZ1j3s2d_RCShU5YzMBbvIJiB0ss4SwCtw"
        }
        url = self.urlBetBase + leagueformat + "?markets=soccer.match_odds"
        response = requests.get(url, headers=headers)
        print(response.status_code)

        events = response.json()["events"]
        gamebets = []
        print(f"DB DB \n{self.db}")
        for event in events:
            if event["home"] is None:
                continue
            gameondb = self.db[(self.db["Home Team"] == nameMap[league][event["home"]["name"]]) & (self.db["Away Team"] == nameMap[league][event["away"]["name"]])]
            oddsraw = event["markets"]["soccer.match_odds"]["submarkets"]["period=ft"]["selections"]
            oddselab = [oddsraw[i]["price"] for i in range(len(oddsraw))]



            gameobj = Game(gameondb["dateEvent"].iloc[0], gameondb["Home Team"].iloc[0], gameondb["Away Team"].iloc[0], oddselab, league)
            print(gameobj)
            gamebets.append(gameobj)
        return gamebets
    def get_other_bet(self, league):
        leagueformat = leagueMap[league]
        self.cache_db(league)
        headers = {
            "accept": "application/json",
            "X-API-Key": "eyJhbGciOiJSUzI1NiIsImtpZCI6Img4LThRX1YwZnlUVHRPY2ZXUWFBNnV2bktjcnIyN1YzcURzQ2Z4bE44MGMiLCJ0eXAiOiJKV1QifQ.eyJhY2Nlc3NfdGllciI6ImFmZmlsaWF0ZSIsImV4cCI6MjA3ODMzNDc0NCwiaWF0IjoxNzYyOTc0NzQ0LCJqdGkiOiI1ZWIwNGZjNS0xMjhiLTRhNGEtOTMyNS03Nzk3M2IwYjFmOWQiLCJzdWIiOiIxN2U0ZDk4MS1jODA1LTRkZDMtYmVmYi01NzhjNTkwNWMwY2EiLCJ0ZW5hbnQiOiJjbG91ZGJldCIsInV1aWQiOiIxN2U0ZDk4MS1jODA1LTRkZDMtYmVmYi01NzhjNTkwNWMwY2EifQ.leilGTjGj7zcxFC9zmsUAsK0UAezmGw9aZZrdFHtqtmO821nm4jr7HmqBVgtKzUTPEGpj10JPZVAjf-yr-F83iVLHQrclei-V-q56gxww8GPDd2ns8TMtOfU7SmWgiRzAa7e3wbFwurN9OgmIX-wYo6WvvBPPEdHWi2JesIORGyC8JwIW4f3O8pCcnCOvts2cE9sjO_WoocX-rW9a11EtgfgYST_JvmcvcXoA-Wt7BB3wjOXHuleYY2jT1vwjvlNTQFKPcRdzls_z2EhkUE6BJmpqsfGdNfNje7pYp3zqBzW0Q_lFkZuUZ1j3s2d_RCShU5YzMBbvIJiB0ss4SwCtw"
        }
        url = self.urlBetBase + leagueformat + "?markets=soccer.total_goals"
        response = requests.get(url, headers=headers)
        print(response.status_code)

        events = response.json()["events"]

        gamebets = []
        print(f"DB DB \n{self.db}")
        for event in events:
            if event["home"] is None:
                continue
            gameondb = self.db[(self.db["Home Team"] == nameMap[league][event["home"]["name"]]) & (
                        self.db["Away Team"] == nameMap[league][event["away"]["name"]])]
            oddsraw = event["markets"]["soccer.total_goals"]["submarkets"]["period=ft"]["selections"]
            oddselab = [oddsraw[i]["price"] for i in range(len(oddsraw))]

            gameobj = Game(gameondb["dateEvent"].iloc[0], gameondb["Home Team"].iloc[0], gameondb["Away Team"].iloc[0],
                           oddselab, league)
            print(gameobj)
            gamebets.append(gameobj)
        return gamebets




    def get_fixture(self):
        print("Fix")
        headers = {
            "accept": "application/json",
            "X-API-Key": "eyJhbGciOiJSUzI1NiIsImtpZCI6Img4LThRX1YwZnlUVHRPY2ZXUWFBNnV2bktjcnIyN1YzcURzQ2Z4bE44MGMiLCJ0eXAiOiJKV1QifQ.eyJhY2Nlc3NfdGllciI6ImFmZmlsaWF0ZSIsImV4cCI6MjA3ODMzNDc0NCwiaWF0IjoxNzYyOTc0NzQ0LCJqdGkiOiI1ZWIwNGZjNS0xMjhiLTRhNGEtOTMyNS03Nzk3M2IwYjFmOWQiLCJzdWIiOiIxN2U0ZDk4MS1jODA1LTRkZDMtYmVmYi01NzhjNTkwNWMwY2EiLCJ0ZW5hbnQiOiJjbG91ZGJldCIsInV1aWQiOiIxN2U0ZDk4MS1jODA1LTRkZDMtYmVmYi01NzhjNTkwNWMwY2EifQ.leilGTjGj7zcxFC9zmsUAsK0UAezmGw9aZZrdFHtqtmO821nm4jr7HmqBVgtKzUTPEGpj10JPZVAjf-yr-F83iVLHQrclei-V-q56gxww8GPDd2ns8TMtOfU7SmWgiRzAa7e3wbFwurN9OgmIX-wYo6WvvBPPEdHWi2JesIORGyC8JwIW4f3O8pCcnCOvts2cE9sjO_WoocX-rW9a11EtgfgYST_JvmcvcXoA-Wt7BB3wjOXHuleYY2jT1vwjvlNTQFKPcRdzls_z2EhkUE6BJmpqsfGdNfNje7pYp3zqBzW0Q_lFkZuUZ1j3s2d_RCShU5YzMBbvIJiB0ss4SwCtw"
        }
        url = "https://sports-api.cloudbet.com/pub/v2/odds/fixtures?sport=soccer&from=1763022545&to=1765614545&players=false&limit=10000"
        response = requests.get(url, headers=headers)
        print(response.status_code)
        with open("mega.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(response.json(), indent=4))





if __name__ == "__main__":
    api = BetAPI()
    api.get_request("Serie B")

