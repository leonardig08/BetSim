import datetime
from OddApi import Scraper
import asyncio, os

async def main():
    scraper = Scraper()
    await scraper.get_request("Serie A")

def testData():
    time = datetime.datetime.now()
    print(time)

# asyncio.run(main())
#testData()
for i in os.listdir("bets"):
    print(i[(len(i)-3):])
