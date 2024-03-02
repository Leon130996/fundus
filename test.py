from fundus import PublisherCollection, Crawler

crawler = Crawler(PublisherCollection.us.TheNewYorker)

for article in crawler.crawl(max_articles=50, only_complete=False):
	print(article.title)
	print(article.html.responded_url)
	print(article.plaintext)
	print(article.authors)
	print(article.topics)
	print("\n")