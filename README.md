# News Search Engine

The News Search Engine takes user queries and returns the most recent news articles in either English or German by order of relevance. The top 15 articles are saved to a ```.csv``` file, where the user can find the article title, URL, publication date and relevancy score for their specific query. Additionally, the News Search Engine returns a list of the named entities mentioned in the news article headlines, sorted by frequency, and a summary of the returned news articles headlines.

The News Search Engine has the option to use one of two APIs: GoogleNews or NewsAPI. Keep in mind that while using NewsAPI for your search, you will need to provide an api-key, which you can get from **[NewsAPI](https://newsapi.org/docs/get-started)** directly. 


## How to install and run

First create a virtual environment

```bash
python3.10 -m venv .venv  # Or choose whatever interpreter you wish
source .venv/bin/activate 
# If you are on windows: venv\Scripts\activate
```

Then install the dependencies, either only for running the project
or including development dependencies (such as linters and formatters)

```bash
# Minimum install to run
pip install .

# Extensive install including development tools
pip install ".[dev]"

# Then you'll also want to install the spacy language models
python -m spacy download en_core_web_md
python -m spacy download de_core_news_md
```

After the local install of the `news_search` library, you can use the cli
like so:

```bash
python cli.py "Example Search Query" en GoogleNewsBackend
python cli.py <topic> <language> <backend>
```
