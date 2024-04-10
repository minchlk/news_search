import csv
import re
from typing import List, Tuple, Counter, Union
from heapq import nlargest
from string import punctuation
from pathlib import Path
from datetime import datetime
import spacy
from spacy.lang.de.stop_words import STOP_WORDS as GERMAN_STOPWORDS
from spacy.lang.en.stop_words import STOP_WORDS as ENGLISH_STOPWORDS

from news_search.backends import Language, NewsArticle, NewsBackend


class NewsScraper:
    """
    Class to scrape the web for recent and relevant news articles, and summarize titles.
    """

    def __init__(
        self,
        backend: NewsBackend,
        save_on_fetch: bool = True,
        language: Language = Language.english,
    ):
        self.backend = backend
        self.save_on_fetch = save_on_fetch
        self.language = language

    def fetch_summary_and_named_entities(
        self,
        topic: str,
        max_num_articles: int,
        updated_after: datetime,
        outfile: Union[str, Path] = None,
    ) -> Tuple[str, List[str]]:
        """
        Fetch relevant recent articles for a topic and return a summary and list of named entities.

        Args:
            topic : Topic to query the web for
            max_num_articles : The total number of articles to return
            updated_after : Date after which article must have been modified to ensure recency

        Returns:
            summarized_articles : A summary of the most relevant news article headlines
            named_entities : A list of the named entities mentioned in the headlines, sorted by frequency
        """
        
        # Query the backend and return the 15 most recent/relevant news articles
        articles = self.backend.fetch_for_topic(
            topic, max_num_articles, updated_after, self.language
        )

        # Load the appropriate model and stop words
        match self.language:
            case Language.english:
                nlp = spacy.load("en_core_web_md")
                stopwords = ENGLISH_STOPWORDS
            case Language.german:
                nlp = spacy.load("de_core_news_md")
                stopwords = GERMAN_STOPWORDS

        # Sort the articles based on how relevant they are to the query using spacy's similarity score
        relevance_sorted_newsarticles = self.rate_relevance(topic, nlp, articles)

        # Generate a summary based on the headlines of the news articles
        summarized_articles = self.generate_summary(
            nlp, 
            stopwords,
            articles
        )

        # Create a list of the entities named in the articles headlines, sorted by frequency
        sorted_entities = self.return_named_entities(nlp, articles)

        # Save articles titles, URLs, and publication dates to a csv file
        if self.save_on_fetch:
            self.save_articles(articles=relevance_sorted_newsarticles, outfile=outfile)

        return summarized_articles, sorted_entities
    
    def rate_relevance(self, topic: str, nlp, articles: List[NewsArticle]):
        """
        Determine the relevance of a news article to the given query.

        Args:
            topic: The query given by the user
            nlp: The spacy model
            articles : A list of NewsArticle objects

        Returns:
            A list of NewsArticle objects with newly created relevance score, sorted by score
        """
        # Create a spacy Doc to compare the query with the headlines
        query_doc = nlp(topic)
        
        # Iteratively compare each headline with the query, and save the similarity score
        for article in articles:
            headline = article.title
            headline_doc = nlp(headline)
            similarity_score = headline_doc.similarity(query_doc)
            article.relevancy_score = similarity_score

        # Sort articles by similarity score
        relevance_sorted_newsarticles = sorted(
            articles, key=lambda x: x.relevancy_score, reverse=True
        )

        return relevance_sorted_newsarticles

    def generate_summary(self, nlp, stopwords, articles: List[NewsArticle]) -> str:
        """
        Generate a summary from a list of article headlines.

        Args:
            nlp: nlp: The spacy model
            stopwords : The spacy stopwords specific to the query language
            articles : A list of NewsArticle objects

        Returns:
            summary : A brief summary of the headlines
        """
        headlines = [article.title for article in articles]
        headline_str = " ".join(headlines)
        headline_doc = nlp(headline_str)

        freq_of_word=dict()

        # Preprocessing
        for word in headline_doc:
            if word.text.lower() not in list(stopwords):
                if word.text.lower() not in punctuation:
                    if word.text not in freq_of_word.keys():
                        freq_of_word[word.text] = 1
                    else:
                        freq_of_word[word.text] += 1

        # Normalize word frequency
        max_freq = max(freq_of_word.values())
        for word in freq_of_word.keys():
            freq_of_word[word]=freq_of_word[word]/max_freq

        # Sentence weighting
        sent_tokens = [sent for sent in headline_doc.sents]
        sent_scores = dict()
        for sent in sent_tokens:
            for word in sent:
                if word.text.lower() in freq_of_word.keys():
                    if sent not in sent_scores.keys():
                        sent_scores[sent]=freq_of_word[word.text.lower()]
                    else:
                        sent_scores[sent]+=freq_of_word[word.text.lower()]

        # Return a selection of the most important headline tokens
        len_tokens = int(len(sent_tokens)*0.2)
        summary = nlargest(n=len_tokens, iterable=sent_scores, key=sent_scores.get)

        final_summary = [word.text for word in summary]
        summary = ' '.join(final_summary)

        return summary

    def return_named_entities(self, nlp, articles: List[NewsArticle]):
        """
        Identifies all named entities in article title and returns them in a list sorted by frequency.

        Args:
            nlp : The spacy model
            articles : A list of NewsArticle objects

        Returns:
            sorted_entities : A list of named entities, sorted by frequency
        """
        headlines = [article.title for article in articles]
        headline_str = " ".join(headlines)
        headline_doc = nlp(headline_str)

        named_entities = []
        for ent in headline_doc.ents:
            if ent.label_ in ["PERSON", "ORG", "GPE", "PER"]:
                named_entities.append(ent)

        entity_counts = {}
        for entity in named_entities:
            ent_text = entity.text
            if ent_text in entity_counts:
                entity_counts[ent_text] += 1
            else:
                entity_counts[ent_text] = 1

        sorted_entities = sorted(
            entity_counts.items(), key=lambda x: x[1], reverse=True
        )
        # Leave this here just in case 
        final = []
        for entity, count in sorted_entities:
            final.append(entity)
            #print(f"{entity}: {count}")

        return final

    def save_articles(self, articles: List[NewsArticle], outfile: Path):
        """
        Save articles to a csv file.

        Args:
            articles : A list of NewsArticle objects
            outfile : Path to the output file
        """
        # Specify where to save the search results
        outfile.parent.mkdir(exist_ok=True, parents=True)

        with open(outfile, "w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["title", "URL", "publication_date", "relevancy_score"])
            for article in articles:
                writer.writerow([article.title, article.URL, article.last_updated, article.relevancy_score])
