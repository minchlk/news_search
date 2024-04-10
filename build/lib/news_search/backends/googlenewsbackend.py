from typing import List
from datetime import datetime

import GoogleNews
from news_search.news_backend import NewsBackend, NewsArticle, Language


class GoogleNewsBackend(NewsBackend):
    """
    Class to implement GoogleNews API to scrape recent news articles.

    Does not always return the max_num_articles, and certain functions are blocked, 
    which makes this the inferior of the two backends.
    """

    def _fetch_for_topic(
        topic: str, max_num_articles: int, updated_after: datetime, lang: Language
    ) -> List[NewsArticle]:
        # GoogleNews does not seem to like .get_news(), so we'll use .search() instead
        gn = GoogleNews(lang=lang, start=updated_after, end=datetime.today)
        gn.search(topic)

        # iterate through results and create NewsArticle objects with relevancy score
        articles = []
        for _ in range(max_num_articles):
            article = gn.results()[_]
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
