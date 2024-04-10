from dataclasses import dataclass
import datetime
from typing import List
from argparse import ArgumentError
from abc import ABC, abstractmethod
from enum import Enum


class Language(Enum, str):
    english = "en"
    german = "de"


@dataclass
class NewsArticle:
    """
    Struct for desired news article query result
    """

    title: str
    URL: str
    last_updated: datetime
    relevancy_score: float


class NewsBackend(ABC):
    """
    Entity performing webscraping for recent articles on a freetext topic.
    """

    @staticmethod
    @abstractmethod
    def _fetch_for_topic(
        topic: str, max_num_articles: int, updated_after: datetime, lang: Language
    ) -> List[NewsArticle]:
        """
        Interface definition for querying the web for relevant articles given a freetext topic.

        Args:
            topic : Topic to query the web for
            max_num_articles : The total number of articles to return
            updated_after : Date after which article must have been modified to ensure recency
            lang: language to perform search query in (English or German)
        """

    @staticmethod
    def fetch_for_topic(
        topic: str, max_num_articles: int, updated_after: datetime, lang: Language
    ) -> List[NewsArticle]:
        """
        Public API for querying the web for recent relevant news articles given a freetext topic

        Args:
            topic : Topic to query the web for
            max_num_articles : The total number of articles to return
            updated_after : Date after which article must have been modified to ensure recency
            lang: language to perform search query in (English or German)
        """

        if updated_after > datetime.date.today:
            raise ArgumentError("Cannot query future news articles.")
        if len(topic) > 1e3:
            raise ArgumentError("Query is too long.")
        #TODO: I don't think I need this anymore
        # languages = ["en", "de"]
        # if lang != languages:
        #     raise ArgumentError("Sorry, search is restricted to English and German results.")

        # delegate to implementations after arg checks:
        return NewsBackend._fetch_for_topic(
            topic, max_num_articles, updated_after, lang
        )
