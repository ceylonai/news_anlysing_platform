import asyncio
import re
import motor.motor_asyncio
import requests
from bs4 import BeautifulSoup
from ceylon import CeylonAIAgent
import datetime

source_agent = CeylonAIAgent()


@source_agent.register("source_agent", number_of_agents=1)
class SourceAgent:

    def __init__(self):
        self.source = "https://cryptonews.com/"
        self.base_pattern = r"^(\/|https:\/\/cryptonews\.com\/).*"
        self.article_pattern = r"^(\/|https:\/\/cryptonews\.com\/\/news\/).*"

        self.client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')

        self.db = self.client['news_analysing_db']
        # select the database and collection

    @source_agent.init()
    async def setup_method(self):
        self.db.articles.create_index("link", unique=True)

    @source_agent.processor("article_agent")
    async def on_new_link(self, message):
        pass

    @source_agent.background("source_reader")
    async def source_reader(self):
        while True:
            page_link = self.source  # We will get only home page links
            response = requests.get(page_link)
            soup = BeautifulSoup(response.content, "html.parser")
            link_details = soup.find_all("a")
            for link_dtm in link_details:
                text = f"{link_dtm.text}".strip()
                link = f"{link_dtm.get('href')}".strip()
                if text and text != "" and link and link != "":

                    if not re.match(self.base_pattern, link):
                        continue
                    if not link.startswith("https://") or not link.startswith("http://"):
                        link = f"{self.source}{link}"
                    if not re.match(self.article_pattern, link):
                        continue

                    await self.insert_link_to_db(link, text)

            await asyncio.sleep(10 * 60)

    async def insert_link_to_db(self, link, text):
        if await self.db.articles.count_documents({"link": link}) == 0:
            id = await self.db.articles.insert_one({
                "type": "article",
                "source": self.source,
                "title": text,
                "link": link,
                "is_visited": False,
                "is_analysed": False,
                "is_sentiment_analysed": False,
                "sentiment": None,
                "sentiment_score": None,
                "sentiment_magnitude": None,
                "meta": {
                    "keywords": [],
                    "description": None,
                    "image": None,
                    "author": None,
                    "published_date": None
                },
                "created_at": datetime.datetime.utcnow(),
                "updated_at": datetime.datetime.utcnow()
            })
            print(f"Inserted {id.inserted_id} to db")
