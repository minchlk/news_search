import datetime
from typing import List
import requests

from newsapi import NewsApiClient
from news_search.news_backend import NewsBackend, NewsArticle, Language



class NewsApiBackend(NewsBackend):
    """
    Class to implement NewsApiClient to scrape recent news articles.

    Initially tested with api.get_everything because we could specify a date, but 
    api.get_top_headlines only returns the most recent relevant articles.
    """

    def __init__(self, api_key : str):
        self.api_key = api_key

    def _fetch_for_topic(
        topic: str,
        max_num_articles: int,
        updated_after: datetime,
        lang: Language,
    ) -> List[NewsArticle]:
        # Start a session using the api key, and grab everything since we want to sort by relevancy
        with requests.Session() as session:
            api = NewsApiClient(api_key, session)
            all_results = api.get_top_headlines(q=topic, language=lang)
            
            # api.get_everything(
            #     q=topic,
            #     language=lang,
            #     from_param=datetime.datetime.today,
            #     to=updated_after,
            #     sort_by="relevancy"
            # )

            list_of_articles = all_results["articles"]  # list of dicts

            articles = []
            for article in list_of_articles[:max_num_articles]:
                title = article.get("title")
                URL = article.get("url")
                last_updated = article.get("publishedAt")
                relevancy_score = 0
                if title and URL and last_updated:
                    article.append(NewsArticle(title, URL, last_updated, relevancy_score))

        return articles
