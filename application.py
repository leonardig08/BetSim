import os
import json
import datetime
from api import OddApi
from textual.app import App, ComposeResult
from textual.containers import VerticalGroup, HorizontalGroup, VerticalScroll, Grid, Center
from textual.widgets import Header, Label, Rule, LoadingIndicator, TabbedContent, TabPane, Select, Button, Collapsible, Input
from textual.screen import Screen, ModalScreen
from textual.widget import Widget
from asset import stringText, cssText
from textual import work
from dataclasses import dataclass, asdict
from textual.reactive import reactive

scraper = OddApi.Scraper()

betTypes = ["1x2", "Under/Over"]



leaguesDict = {"gamesItalia": ["Serie A"],
               "gamesUefa": ["Champions League", "Europa League", "Conference League"],
               "gamesInghilterra": ["Premier League"],
               "gamesGermania": ["Bundesliga"],
               "gamesSpagna": ["La Liga"]}



databaseGame = {}

class WarningDialogDefault(ModalScreen):
    def __init__(self, warningMessage: str):
        self.warningMessage = warningMessage
        super().__init__()
    def compose(self):
        yield Grid(
            Label(self.warningMessage),
            Button("OK", variant="warning")
        )
    def on_button_pressed(self, event: Button.Pressed):
        self.app.pop_screen()

class SplashScreen(Screen):
    def compose(self):
        with VerticalGroup():
            yield Label(stringText, id="labelTitoletto")
            yield Rule(line_style="thick")
            yield LoadingIndicator()

class GameObject(Widget):
    def __init__(self, gameObject, id=None, not1x2=False, prepress=None):
        super().__init__(id=id)
        self.game = gameObject
        self.rendermode = not1x2
        self.prepress = prepress
    def compose(self):
        if self.rendermode:
            with HorizontalGroup():
                with VerticalGroup(id="groupGameDetail"):
                    yield Label(f"{self.game.home} - {self.game.away}")
                    yield Label(f"{self.game.date}  ||  {self.game.time}", id="labelData")
                with HorizontalGroup(id="oddGroup"):
                    index = 0
                    btts = []
                    for i in ["Under", "Over"]:
                        with VerticalGroup(id=f"odd{i}"):
                            yield Label(i.upper(), id="labelUnit")
                            yield Rule(line_style="solid", id="ruleUnit")
                            btts.append(Button(self.game.odds[index], "primary", name=f"{self.game.home}/{self.game.away}/{i}"))
                            yield btts[index]
                        index += 1
                    if self.prepress is not None:
                        btts[self.prepress].variant = "success"
        else:
            with HorizontalGroup():
                with VerticalGroup(id="groupGameDetail"):
                    yield Label(f"{self.game.home} - {self.game.away}")
                    yield Label(f"{self.game.date}  ||  {self.game.time}", id="labelData")
                with HorizontalGroup(id="oddGroup"):
                    index = 0
                    btts = []
                    for i in ["1", "x", "2"]:
                        with VerticalGroup(id=f"odd{i}"):
                            yield Label(i.upper(), id="labelUnit")
                            yield Rule(line_style="solid", id="ruleUnit")
                            btts.append(Button(self.game.odds[index], "primary", name=f"{self.game.home}/{self.game.away}/{i}"))
                            yield btts[index]
                        index += 1
                    if self.prepress is not None:
                        btts[self.prepress].variant = "success"
                    
    def placeHolder(self):
        pass
    def on_button_pressed(self, event: Button.Pressed):
        button = event.button
        data = button.name.split("/")
        self.app.query_one("MainAppScreen").add_bet(self.game, data[2], button.name, self.rendermode)

class TicketObject(Widget):
    def __init__(self, betObject, index,  id = None):
        super().__init__(id=id)
        self.value = float(betObject[0])
        self.bet = betObject[1]
        self.index = index
        self.multodds = None
        
    def compose(self):
        associate = {
                            "1": 0,
                            "x": 1,
                            "2": 2,
                            "Under": 0,
                            "Over": 1
                        }
        with Collapsible(title=f"Scheda numero {self.index}"):
            self.time = datetime.datetime.now()
            mappa_mesi = ["Gennaio", "Febbraio", "Marzo", "Aprile",
                "Maggio", "Giugno", "Luglio", "Agosto",
                "Settembre", "Ottobre", "Novembre", "Dicembre"]
            print(self.bet)
            scommesseVinte = []
            self.multodds = 1
            states = []
            for id, selected in self.bet.items():
                game = selected[0]
                data = game.date
                data = data.split(" ")
                print(data)
                time = game.time
                time = time.split(":")
                print(time)
                gameTime = datetime.datetime(int(data[2]), mappa_mesi.index(data[1]) + 1, int(data[0]), int(time[0]), int(time[1]))
                gameString = None
                state = None
                if gameTime > self.time:
                    state = 0
                elif self.time + datetime.timedelta(minutes=120)  > gameTime:
                    state = 1
                elif self.time  > gameTime:
                    state = 2
                gameString = ["Partita non ancora iniziata","Partita finita","Partita in corso"][state]
                score = None
                oddSelected = selected[1]
                if state == 1:
                    for i in databaseGame[game.league]:
                        if game.home == i["HomeTeam"] and game.away == i["AwayTeam"]:
                            if i["HomeTeamScore"] != None and i["AwayTeamScore"] != None:
                                score = [i["HomeTeamScore"], i["AwayTeamScore"]]
                scoreString = "Risultato non presente" if score == None else f"{score[0]}-{score[1]}"
                
                wonBet = None
                if score is not None:
                    match oddSelected:
                        case "1":
                            if score[0] > score[1]:
                                wonBet = True
                            else: wonBet = False
                        case "x":
                            if score[0] == score[1]:
                                wonBet = True 
                            else: wonBet = False
                        case "2":
                            if score[0] < score[1]:
                                wonBet = True 
                            else: wonBet = False
                        case "Under":
                            if score[0]+score[1] < 2.5:
                                wonBet = True 
                            else: wonBet = False
                        case "Over":
                            if score[0]+score[1] > 2.5:
                                wonBet = True 
                            else: wonBet = False

                match wonBet:
                    case True:
                        emoji = ":green_circle:"
                    case False:
                        emoji = ":red_circle:"
                    case _:
                        emoji = ":yellow_circle:"
                scommesseVinte.append(wonBet)
                states.append(state)
                self.multodds *= float(game.odds[associate[oddSelected]])
                with Collapsible(title=f"{game.home} - {game.away} || {game.date} {game.time} || {gameString} || {emoji}"):
                    yield Label(f"Selezionata: {oddSelected}\nQuotazione: {game.odds[associate[oddSelected]]}\nRisultato: {scoreString}")
            with HorizontalGroup(id="internalGroupCash"):
                disableButton = not all(scommesseVinte)
                lostBet = False
                if False in scommesseVinte:
                    lostBet = True

                if not disableButton and not lostBet:
                    statoScommessa = "Vinta"
                elif not lostBet:
                    statoScommessa = "In corso"
                else:
                    statoScommessa = "Persa"
                yield Label(f"Valore scheda €{self.value}\nGuadagno potenziale €{round(self.value * self.multodds, 2)}\nStato: {statoScommessa}", id="labelValue")
                if not lostBet:
                    yield Button("Cash out", "success", id="cashOutButton", disabled=disableButton)
                else: yield Button("Elimina Scommessa", "error", id="removeBetButton")
    def on_button_pressed(self, event: Button.Pressed):
        contentId = event.button.id
        print(contentId)
        if contentId == "cashOutButton":
            print("cash")
            cash = round(self.value * self.multodds, 2)
            self.app.query_one(MainAppScreen).balance += cash
        elif contentId == "removeBetButton":
            print("elimina")
            try:
                os.remove(f"bets/{self.index}.bet")
            except FileNotFoundError:
                pass
            self.remove()





class MainAppScreen(Screen):
    balance = reactive(0)
    def compose(self):
        self.odd_cache = {}
        self.rejectIndex = 0
        self.current_bet = {}
        self.old_nation="Italia"
        self.old_bet = "1x2"
        yield Header(True)
        yield Center(Label("Soldi: ???", id="balanceLab"))
        with TabbedContent(id = "tabNation"):
            with TabPane("Italia"):
                selectLeague = Select.from_values(["Serie A"], prompt="Lega selezionata", allow_blank=False, id="selectItalia")
                selectOdd = Select.from_values(betTypes, prompt="Tipo scommessa", allow_blank=False, id="betItalia")
                with HorizontalGroup():
                    yield selectLeague
                    yield selectOdd
                yield VerticalScroll(id="gamesItalia")
            with TabPane("UEFA"):
                selectLeague = Select.from_values(["Champions League","Europa League","Conference League"], prompt="Lega selezionata", allow_blank=False, id="selectUefa")
                selectOdd = Select.from_values(betTypes, prompt="Tipo scommessa", allow_blank=False, id="betUefa")
                with HorizontalGroup():
                    yield selectLeague
                    yield selectOdd
                yield VerticalScroll(id="gamesUefa")
            with TabPane("Inghilterra"):
                selectLeague = Select.from_values(["Premier League"], prompt="Lega selezionata", allow_blank=False, id="selectInghilterra")
                selectOdd = Select.from_values(betTypes, prompt="Tipo scommessa", allow_blank=False, id="betInghilterra")
                with HorizontalGroup():
                    yield selectLeague
                    yield selectOdd
                yield VerticalScroll(id="gamesInghilterra")
            with TabPane("Germania"):
                selectLeague = Select.from_values(["Bundesliga"], prompt="Lega selezionata", allow_blank=False, id="selectGermania")
                selectOdd = Select.from_values(betTypes, prompt="Tipo scommessa", allow_blank=False, id="betGermania")
                with HorizontalGroup():
                    yield selectLeague
                    yield selectOdd
                yield VerticalScroll(id="gamesGermania")
            with TabPane("Spagna"):
                selectLeague = Select.from_values(["La Liga"], prompt="Lega selezionata", allow_blank=False, id="selectSpagna")
                selectOdd = Select.from_values(betTypes, prompt="Tipo scommessa", allow_blank=False, id="betSpagna")
                with HorizontalGroup():
                    yield selectLeague
                    yield selectOdd
                yield VerticalScroll(id="gamesSpagna")
            with TabPane("Scheda"):
                yield Label("La tua scheda", id="titleScheda")
                with VerticalScroll(id="ticketGroup"):
                    for game, selectedBet in self.current_bet:
                        with Collapsible(title=f"{game.home} - {game.away} || {game.date} {game.time}"):
                                yield Label(f"Selezionata: {selectedBet}\nQuotazione: {game[selectedBet]}")
                with HorizontalGroup(id="GroupBuy"):
                    yield Label("Costo €")
                    yield Input(placeholder="Soldi", type="number", id="soldiInput")
                    yield Button("Compra la scommessa", variant="success", id="buyButton")
            with TabPane("Risultati"):
                yield Label("Schede Acquistate", id="titleResult")
                with HorizontalGroup():
                    yield Center(Button("Ricarica schede", "primary", id="reloadBet"))
                    yield Center(Button("Ricarica risultati", "primary", id="reloadDb"))
                yield VerticalScroll(id="resultTicketGroup")
        self.call_later(self.clear_cache)
        self.call_after_refresh(self.load_money)
    def load_money(self):
        if os.path.exists("data/balance.enc"):
            with open("data/balance.enc", "r", encoding="utf-8") as f:
                tempbalance = json.loads(f.read())
        else:
            tempbalance = 0
            with open("data/balance.enc", "w", encoding="utf-8") as f:
                f.write(json.dumps(tempbalance))
        self.balance = tempbalance
    def watch_balance(self, newmoney):
        self.query_one("#balanceLab").update(f"Soldi: {newmoney}")
        print("Saving ",newmoney)
        with open("data/balance.enc", "w", encoding="utf-8") as f:
                f.write(json.dumps(newmoney))
    async def reload_bets(self):
        bets = []
        if not os.path.exists("bets"):
            return
        for i in os.listdir("bets"):
            print(f"loading {i}")
            bet = []
            with open("bets/"+i, "r", encoding="utf-8") as f:
                singlebet = json.loads(f.read())
                money = singlebet[0]
                bet.append(money)
                
                temp = {}
                for id, value in singlebet[1].items():
                    value[0] = OddApi.Game(**value[0])
                    temp[id] = [value[0], value[1]]
                bet.append(temp)
            bets.append(bet)
        group = self.query_one("#resultTicketGroup")
        await group.remove_children()
        print(bets)
        inde = 0
        for betObject in bets:
            print(f"betCaricata{bets.index(betObject)}")
            group.mount(TicketObject(betObject, inde, id=f"betCaricata{inde}"))
            inde += 1
    def reload_ticket(self):
        print(self.current_bet)
        group = self.query_one("#ticketGroup")
        group.remove_children()
        print(self.current_bet)
        for gamelul, selectedBet in self.current_bet.items():
                        print(selectedBet)
                        game = selectedBet[0] 
                        associate = {
                            "1": 0,
                            "x": 1,
                            "2": 2,
                            "Under": 0,
                            "Over": 1
                        }
                        group.mount(Collapsible(Label(f"Selezionata: {selectedBet[1]}\nQuotazione: {game.odds[associate[selectedBet[1]]]}"), title=f"{game.home} - {game.away} || {game.date} {game.time}"))
    def clear_cache(self):
        self.odd_cache = {}
    async def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated):
        nation = event.tab.label_text
        if nation == "Risultati":
            await self.reload_bets()
            return
        elif nation == "Scheda":
            self.reload_ticket()
            return
        else:
            print("Tab Activated ", nation, "--", self.old_nation)
            if nation == self.old_nation:
                return
            else:
                self.old_nation = nation
            match nation:
                case "Italia":
                    league = "Serie A"
                    containerName = "gamesItalia"
                case "UEFA":
                    league = "Champions League"
                    containerName = "gamesUefa"
                case "Inghilterra":
                    league = "Premier League"
                    containerName = "gamesInghilterra"
                case "Germania":
                    league = "Bundesliga"
                    containerName = "gamesGermania"
                case "Spagna":
                    league = "La Liga"
                    containerName = "gamesSpagna"
            self.update_games(league, containerName)
    async def on_select_changed(self, event: Select.Changed):
        if "bet" in event.select.id:
            betType = event.value
            if betType == self.old_bet:
                return
            else:
                self.old_bet = betType
            id = event.select.id
            nation = id.removeprefix("bet")
            select = "select"+nation
            bettype = event.select.parent.query_one("#bet"+nation).value
            league = event.select.parent.query_one("#"+select).value
            for key,value in leaguesDict.items():
                if league in value:
                    container = key
            print(league, container)
            underover = False
            match betType:
                case "1x2":
                    underover = False
                case "Under/Over":
                    underover = True
            self.query_one(f"#{container}").set_loading(True)
            self.update_games(league, container, underover)
            self.query_one(f"#{container}").set_loading(False)
                    


        else:
            league = event.value
            print(league, self.rejectIndex)
            if league != "Serie A" and self.rejectIndex < len(leaguesDict)-1:
                print("Rejecting ", league)
                self.rejectIndex += 1
                return
            print("Getting ", league)
            
            for key,value in leaguesDict.items():
                if league in value:
                    container = key
            print(league, container)
            self.query_one(f"#{container}").set_loading(True)
            self.update_games(league, container)
            self.query_one(f"#{container}").set_loading(False)
    @work()
    async def update_games(self, league, containerName, underover = False):
        print("Doing ",underover)
        
        self.query_one(f"#{containerName}").set_loading(True)
        keyleague = league+"uo" if underover else league
        if keyleague in self.odd_cache.keys():
            odds = self.odd_cache[keyleague]
        else:
            if underover:
                odds = await scraper.get_other_bet(league)
                self.odd_cache[league+"uo"] = odds
            else:
                odds = await scraper.get_request(league)
                self.odd_cache[league] = odds
        await self.query_one(f"#{containerName}").remove_children()
        print(odds)
        print(self.current_bet)
        if odds == []:
            self.query_one(f"#{containerName}").mount(Label("Nessuna Partita disponibile,  appena disponibili appariranno qui"))
        else:
            for gameData in odds:
                if underover:
                    odder = None
                    if f"{gameData.home}{gameData.away}{gameData.date}" in self.current_bet:
                        odder = ["Under", "Over"].index(self.current_bet[f"{gameData.home}{gameData.away}{gameData.date}"][1])
                    print(odder)
                    self.query_one(f"#{containerName}").mount(GameObject(gameData, id=f"{gameData.home.replace(" ", "").replace(".", "")}_{gameData.away.replace(" ", "").replace(".", "")}_uo", not1x2=True, prepress=odder))
                else:
                    odder = None
                    if f"{gameData.home}{gameData.away}{gameData.date}" in self.current_bet:
                        odder = ["1", "x", "2"].index(self.current_bet[f"{gameData.home}{gameData.away}{gameData.date}"][1])
                    print(odder)
                    self.query_one(f"#{containerName}").mount(GameObject(gameData, id=f"{gameData.home.replace(" ", "").replace(".", "")}_{gameData.away.replace(" ", "").replace(".", "")}", prepress=odder))
        self.query_one(f"#{containerName}").set_loading(False)
    def add_bet(self, game, odd, buttonid, underover):
        print(self.current_bet)
        if f"{game.home}{game.away}{game.date}" in self.current_bet.keys():
            if self.current_bet[f"{game.home}{game.away}{game.date}"][1] != odd:
                self.current_bet[f"{game.home}{game.away}{game.date}"] = [game, odd]
                for button in self.query_one(f"#{game.home.replace(" ", "").replace(".", "")}_{game.away.replace(" ", "").replace(".", "")}" if not underover else f"#{game.home.replace(" ", "").replace(".", "")}_{game.away.replace(" ", "").replace(".", "")}_uo").query("Button"):
                    button.variant = "primary"
                self.query_one(f"#{game.home.replace(" ", "").replace(".", "")}_{game.away.replace(" ", "").replace(".", "")}" if not underover else f"#{game.home.replace(" ", "").replace(".", "")}_{game.away.replace(" ", "").replace(".", "")}_uo").query_one(f"#odd{odd}").query_one("Button").variant = "success"
            else:
                self.current_bet.pop(f"{game.home}{game.away}{game.date}")
                for button in self.query_one(f"#{game.home.replace(" ", "").replace(".", "")}_{game.away.replace(" ", "").replace(".", "")}" if not underover else f"#{game.home.replace(" ", "").replace(".", "")}_{game.away.replace(" ", "").replace(".", "")}_uo").query("Button"): #.replace(" ", "").replace(".", "")
                    button.variant = "primary"
        else:
            self.current_bet[f"{game.home}{game.away}{game.date}"] = [game, odd]
            self.query_one(f"#{game.home.replace(" ", "").replace(".", "")}_{game.away.replace(" ", "").replace(".", "")}" if not underover else f"#{game.home.replace(" ", "").replace(".", "")}_{game.away.replace(" ", "").replace(".", "")}_uo").query_one(f"#odd{odd}").query_one("Button").variant = "success"

    async def on_button_pressed(self, event: Button.Pressed):
        button = event.button
        print(button.id)
        if button.id == "buyButton":
            moneyValue = round(float(self.query_one("#soldiInput").value), 2)
            if moneyValue == 0 or moneyValue is None:
                self.app.push_screen(WarningDialogDefault("Inserisci un valore di soldi con cui piazzare la scommessa, diverso da 0!"))
                return
            self.saveBet(moneyValue)
        elif button.id == "reloadBet":
            await self.reload_bets()
        elif button.id == "reloadDb":
            self.reload_db()

    @work(thread=True)
    def reload_db(self):
        for id, values in leaguesDict.items():
            for i in values:
                databaseGame[i] = scraper.cacheDB(i)


    def saveBet(self, money):
        index = 0
        if len(self.current_bet) == 0:
            self.app.push_screen(WarningDialogDefault("Non puoi piazzare una scommessa vuota!"))
            return
        if money > self.balance:
            self.app.push_screen(WarningDialogDefault("Soldi insufficienti per piazzare la scommessa!"))
            return
        else:
            self.balance -= money
        if os.path.exists("bets"):
            for file in os.listdir("bets"):
                num = int(file.removesuffix(".bet"))
                if num >= index:
                    index = num + 1
        else:
            os.mkdir("bets")
            index = 0
        with open(f"bets/{index}.bet", "w", encoding="utf-8") as f:
            bettowrite = {}
            for id, value in self.current_bet.items():
                print(value[0])
                game = asdict(value[0])
                odd = value[1]
                bettowrite[id] = [game, odd]
                
            bet = [money, bettowrite]
            content = json.dumps(bet, indent=4)
            f.write(content)
        
        

class BetSim(App):
    CSS_PATH = "main.tcss"
    
    def compose(self):
        yield Header(show_clock=True)
        self.push_screen(SplashScreen())
        self.odd_data = None
        self.dataLoaded = False
        
        self.call_later(self.load_data)
    
    def load_main_screen(self):
        if self.dataLoaded:
            self.pop_screen()
            self.push_screen(MainAppScreen())

    @work(thread=True)
    def load_data(self):
        for id, values in leaguesDict.items():
            for i in values:
                databaseGame[i] = scraper.cacheDB(i)
        self.dataLoaded = True
        print(databaseGame)
        self.call_from_thread(self.load_main_screen)
        
    
            

        
if __name__ == "__main__":
    app = BetSim()
    app.run()


