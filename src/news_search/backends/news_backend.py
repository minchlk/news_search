from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Dict, List
from datetime import datetime
from dataclasses import dataclass


class Language(str, Enum):
    """
    Enum for currently supported languages
    """

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


class NewsBackend(metaclass=ABCMeta):
    """
    Entity performing webscraping for recent articles on a freetext topic.
    """

    @staticmethod
    @abstractmethod
    def get_required_args() -> Dict[str, str]:
        """
        Since classes might need arguments to be instantiated, they may
        announce them here as dictionary between argument names and short
        descriptions
        """

    @abstractmethod
    def _fetch_for_topic(
        self,
        topic: str,
        max_num_articles: int,
        updated_after: datetime,
        language: Language,
    ) -> List[NewsArticle]:
        """
        Interface definition for querying the web for relevant articles given a freetext topic.

        Args:
            topic : Topic to query the web for
            max_num_articles : The total number of articles to return
            updated_after : Date after which article must have been modified to ensure recency
            lang: language to perform search query in (English or German)
        """

    def fetch_for_topic(
        self,
        topic: str,
        max_num_articles: int,
        updated_after: datetime,
        language: Language,
    ) -> List[NewsArticle]:
        """
        Public API for querying the web for recent relevant news articles given a freetext topic

        Args:
            topic : Topic to query the web for
            max_num_articles : The total number of articles to return
            updated_after : Date after which article must have been modified to ensure recency
            lang: language to perform search query in (English or German)
        """

        if updated_after > datetime.now():
            raise ValueError("Cannot query future news articles.")
        if len(topic) > 1e3:
            raise ValueError("Query is too long.")

        # delegate to implementations after arg checks:
        return self._fetch_for_topic(
            topic=topic,
            max_num_articles=max_num_articles,
            updated_after=updated_after,
            language=language,
        )
