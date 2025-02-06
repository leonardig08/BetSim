import datetime
from OddApi import Scraper
import asyncio

async def main():
    scraper = Scraper()
    await scraper.get_request("Serie A")

def testData():
    time = datetime.datetime.now()
    print(time)

# asyncio.run(main())
testData()