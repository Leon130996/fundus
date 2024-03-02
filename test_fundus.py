import logging

from fundus.logging import basic_logger
from src.fundus import Crawler, PublisherCollection

publisher = PublisherCollection.us.OccupyDemocrats
crawler = Crawler(publisher)
basic_logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(f"fundus.log", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
basic_logger.addHandler(file_handler)
for article in crawler.crawl(max_articles=20, only_complete=False):
    print(article.title)
    print(article.plaintext)
    print(article.html.responded_url)
    print(article.authors)
    print(article.topics)
    print("\n")
