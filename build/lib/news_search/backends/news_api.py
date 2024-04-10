from typing import Dict, List
from datetime import date, datetime

import requests
from newsapi import NewsApiClient

from news_search.backends.news_backend import Language, NewsArticle, NewsBackend


class NewsApiBackend(NewsBackend):
    """
    Class to implement NewsApiClient to scrape recent news articles.

    Initially tested with api.get_everything because we could specify a date, but
    api.get_top_headlines only returns the most recent relevant articles.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    @staticmethod
    def get_required_args() -> Dict[str, str]:
        return {
            "api_key": (
                "Please enter your api key; "
                + "you can get an api key here: "
                + "https://newsapi.org/docs/get-started "
            )
        }

    def _fetch_for_topic(
        self,
        topic: str,
        max_num_articles: int,
        updated_after: datetime,
        language: Language,
    ) -> List[NewsArticle]:
        # Start a session using the api key, and grab everything since we want to sort by relevancy
        with requests.Session() as session:
            api = NewsApiClient(self.api_key, session)
            all_results = api.get_everything(
                q=topic,
                language=language,
                from_param=updated_after,
                to=date.today(),
                sort_by="relevancy"
            )

            #api.get_top_headlines(q=topic, language=language)
            list_of_articles = all_results["articles"]  # list of dicts

            articles = []
            for article in list_of_articles[:max_num_articles]:
                title = article.get("title")
                URL = article.get("url")
                last_updated = article.get("publishedAt")
                relevancy_score = 0
                if title and URL and last_updated:
                    articles.append(NewsArticle(title, URL, last_updated, relevancy_score)
                    )

        return articles
