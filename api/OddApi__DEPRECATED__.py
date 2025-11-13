import asyncio
import requests
import json
import os
from playwright.async_api import async_playwright
from dataclasses import dataclass, asdict
@dataclass
class Game:
    date : str
    time : str
    home : str
    away : str
    odds : str
    league: str
    def __post_init__(self):
        for odd in self.odds:
                float(odd)

listaDate = ["Gennaio", "Febbraio", "Marzo", "Aprile",
             "Maggio", "Giugno", "Luglio", "Agosto",
             "Settembre", "Ottobre", "Novembre", "Dicembre"]
apiKey = "40ce507ae65c49ee9d52fd74dbc52d24"


class Scraper():
    def __init__(self):
        self.linksCache = {}
        self.db = None
        self.translation = None
        self.teamMap = None

    def cacheDB(self, league):
        print("Caching ", league)
        link = None
        name = None
        match league:
            case "Serie A":
                link = "https://fixturedownload.com/feed/json/serie-a-2024"
                name = "it.json"
            case "Champions League":
                link = "https://fixturedownload.com/feed/json/champions-league-2024"
                name = "ucl.json"
            case "Europa League":
                link = "https://fixturedownload.com/feed/json/europa-league-2024"
                name = "uel.json"
            case "Conference League":
                link = "https://fixturedownload.com/feed/json/conference-league-2024"
                name = "ucr.json"
            case "Premier League":
                link = "https://fixturedownload.com/feed/json/epl-2024"
                name = "epl.json"
            case "Bundesliga":
                link = "https://fixturedownload.com/feed/json/bundesliga-2024"
                name = "bun.json"
            case "La Liga":
                link = "https://fixturedownload.com/feed/json/la-liga-2024"
                name = "liga.json"
            case _:
                raise Exception("Can't find league")
        if not os.path.exists("data"):
            os.mkdir("data")
        filename = f"data/{name}"
        print(link, " -- ", name)
        response = requests.get(link)
        response.raise_for_status()
        print(response.status_code)
        self.db = response.json()
        oldcontent = None
        print("Writing")
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
                if content != "":
                    oldcontent = json.loads(content)
        with open(filename, "w", encoding="utf-8") as f:
            if oldcontent != None:
                print("writing confirm")
                if oldcontent != response.json() and oldcontent != "":
                    print("written")
                    f.write(json.dumps(response.json(), indent=4))
            else:
                print("Writing none")
                f.write(json.dumps(response.json(), indent=4))
        with open("data/team_map.json", "r", encoding="utf-8") as f:
            readed = json.loads(f.read())
            self.teamMap = readed
        return response.json()



    async def get_other_bet(self, league):
        link = None
        print("Getting")
        match league:
            case "Serie A":
                link = "https://www.oddsportal.com/football/italy/serie-a/"
            case "Champions League":
                link = "https://www.oddsportal.com/football/europe/champions-league/"
            case "Europa League":
                link = "https://www.oddsportal.com/football/europe/europa-league/"
            case "Conference League":
                link = "https://www.oddsportal.com/football/europe/conference-league/"
            case "Premier League":
                link = "https://www.oddsportal.com/football/england/premier-league/"
            case "Bundesliga":
                link = "https://www.oddsportal.com/football/germany/bundesliga/"
            case "La Liga":
                link = "https://www.oddsportal.com/football/spain/laliga/"
            case _:
                raise Exception("Can't find league")
        self.cacheDB(league)
        gameLinks = []
        completeParsed = []
        rowData = []
        async def func(semaphore, browser, game):
            async with semaphore:
                retries = 2
                
                parsedDate = None
                driverFunc = await browser.new_page()
                await driverFunc.route("**/*", lambda route, request: 
                route.abort() if request.resource_type == "image" else route.continue_())
                for dbgame in self.db:
                    try:
                        if self.teamMap[league][dbgame["HomeTeam"]] == game[1] and self.teamMap[league][dbgame["AwayTeam"]] == game[3]:
                            rawDate = dbgame["DateUtc"]
                            rawDate = rawDate.split(" ")[0]
                            rawDate = rawDate.split("-")
                            parsedDate = f"{rawDate[2]} {listaDate[int(rawDate[1]) - 1]} {rawDate[0]}" 
                    except KeyError:
                        print(f"{dbgame["HomeTeam"]} ----- {game[1]}\n{dbgame["AwayTeam"]} ---- {game[3]}")
                gamelink = gameLinks[rowData.index(game)]
                await driverFunc.goto(gamelink, timeout=100000)
                for i in range(retries):
                    try:
                        listofodds = driverFunc.locator(".visible-links")
                        odds = []
                        li = listofodds.locator("li")
                        await li.nth(1).click()
                        print("Finito")
                        print("Waiting")
                        await driverFunc.wait_for_selector(".max-sm\\:h-auto", timeout=15000)
                        oddsRaw = driverFunc.locator("xpath=//*[contains(text(), '+2.5')]").first
                        oddsToGet = oddsRaw.locator("xpath=./../..")
                        over25 = await oddsToGet.locator(".border-black-main").all()
                        odds = [await elem.locator("p").text_content() for elem in over25]
                        print(odds)
                        try:
                            gameObject = Game(parsedDate, game[0], game[1], game[3], [odds[0], odds[1]], league)
                        except ValueError:
                            print("Quote non corrette")
                            await driverFunc.close()
                            return
                        
                        await driverFunc.close()
                        print("Closing")
                        return gameObject
                    except TimeoutError:
                        driverFunc.reload()
                        continue


        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=[
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage", 
            "--disable-extensions",
            "--disable-background-networking", 
            "--mute-audio" 
            ])
            page = await browser.new_page()
            await page.route("**/*", lambda route, request: 
               route.abort() if request.resource_type == "image" else route.continue_())
            print("Navigating")
            await page.goto(link)
            print("Getting")
            gameRows = await page.locator('//div[@class="group flex"]').all()
            for row in gameRows:
                gameLinks.append("https://oddsportal.com"+await row.locator("a.next-m\\:flex").get_attribute("href"))
            rowDataraw = [await row.inner_text() for row in gameRows]
            rowDataraw = [text.split("\n") for text in rowDataraw]
            for row in rowDataraw:
                rowParsed = []
                for item in row:
                    if item:
                        rowParsed.append(item)
                rowData.append(rowParsed[:len(rowParsed)-1])
            await page.close()
            semaphore = asyncio.Semaphore(7)
            tasks = [func(semaphore, browser, game) for game in rowData]
            completeParsed = await asyncio.gather(*tasks)
            await browser.close()
        print(completeParsed)
        for parsed in completeParsed:
            if not parsed:
                completeParsed.pop(completeParsed.index(parsed))
        return completeParsed

    async def get_request(self, league : str):

        link = None
        match league:
            case "Serie A":
                link = "https://www.oddsportal.com/football/italy/serie-a/"
            case "Champions League":
                link = "https://www.oddsportal.com/football/europe/champions-league/"
            case "Europa League":
                link = "https://www.oddsportal.com/football/europe/europa-league/"
            case "Conference League":
                link = "https://www.oddsportal.com/football/europe/conference-league/"
            case "Premier League":
                link = "https://www.oddsportal.com/football/england/premier-league/"
            case "Bundesliga":
                link = "https://www.oddsportal.com/football/germany/bundesliga/"
            case "La Liga":
                link = "https://www.oddsportal.com/football/spain/laliga/"
            case _:
                raise Exception("Can't find league")
        self.cacheDB(league)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=[
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-extensions",
            "--disable-background-networking",
            "--mute-audio"
        ])
            page = await browser.new_page()
            await page.route("**/*", lambda route, request: 
               route.abort() if request.resource_type == "image" else route.continue_())
            print("Navigating")
            await page.goto(link)
            print("Getting")
            gameRows = await page.locator('//div[@class="group flex"]').all()

            rowDataraw = [await row.inner_text() for row in gameRows]
            rowDataraw = [text.split("\n") for text in rowDataraw]
            rowData = []
            for row in rowDataraw:
                rowParsed = []
                for item in row:
                    if item:
                        rowParsed.append(item)
                rowData.append(rowParsed[:len(rowParsed)-1])
                        
            print(rowData)

            completeParsed = []

            for game in rowData:
                parsedDate = None
                for dbgame in self.db:
                    try:
                        if self.teamMap[league][dbgame["HomeTeam"]] == game[1] and self.teamMap[league][dbgame["AwayTeam"]] == game[3]:
                            rawDate = dbgame["DateUtc"]
                            rawDate = rawDate.split(" ")[0]
                            rawDate = rawDate.split("-")
                            parsedDate = f"{rawDate[2]} {listaDate[int(rawDate[1]) - 1]} {rawDate[0]}" 
                    except KeyError:
                        print(f"{dbgame["HomeTeam"]} ----- {game[1]}\n{dbgame["AwayTeam"]} ---- {game[3]}")
                try:
                    gameObject = Game(parsedDate, game[0], game[1], game[3], [game[4], game[5], game[6]], league)
                except ValueError:
                    print("Quote non corrette")
                    continue
                completeParsed.append(gameObject)
            await page.close()
            await browser.close()
        return completeParsed

