# Re-export to allow for simpler imports such as
# from news_search.backends import GoogleNewsBackend
from news_search.backends.news_api import NewsApiBackend
from news_search.backends.google_news import GoogleNewsBackend
from news_search.backends.news_backend import Language, NewsArticle, NewsBackend
