from typing import Dict, List
from datetime import date, datetime

from GoogleNews import GoogleNews

from news_search.backends.news_backend import Language, NewsArticle, NewsBackend


class GoogleNewsBackend(NewsBackend):
    """
    Class to implement GoogleNews API to scrape recent news articles.

    Does not always return the max_num_articles, and certain functions are blocked,
    which makes this the inferior of the two backends.
    """

    def __init__(self):
        pass

    @staticmethod
    def get_required_args() -> Dict[str, str]:
        return {}

    def _fetch_for_topic(
        self,
        topic: str,
        max_num_articles: int,
        updated_after: datetime,
        language: Language,
    ) -> List[NewsArticle]:

        start = updated_after.strftime("%m/%d/%Y")
        end = date.today().strftime("%m/%d/%Y")
        gn = GoogleNews(lang=language, start=start, end=end)
        gn.get_news(topic)

        # iterate through results and create NewsArticle objects with relevancy score
        articles = []
        for article in gn.results()[:max_num_articles]:
            articles.append(
                NewsArticle(
                    title=article["title"],
                    URL=article["link"],
                    last_updated=article["date"],
                    relevancy_score=0,
                )
            )
        # clear result list before next search
        gn.clear()

        return articles
