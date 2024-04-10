#!/usr/bin/env python3

import datetime
from typing import Dict
from pathlib import Path

import typer
import dateutil.relativedelta

from news_search import Language, NewsScraper
from news_search.backends import NewsBackend, NewsApiBackend, GoogleNewsBackend

# Map to match user input string with the respective backend
# classes to instantiate below.
backend_map = {
    "googlenews": GoogleNewsBackend,
    "newsapi": NewsApiBackend,
}

# NewsApiClient requires an API key, so we need to prompt for this
def query_for_args(args: Dict[str, str]) -> Dict[str, str]:
    user_choices = {}
    for arg, prompt in args.items():
        user_choices[arg] = typer.prompt(prompt)
    return user_choices

app = typer.Typer()

@app.command()
def run(
    topic: str,
    language: str = typer.Argument("en", help="Language for news articles"),
    backend: str = typer.Argument("NewsApi", help="Backend for fetching news articles"),
    max_num_articles: int = 15,
):
    backend = backend.lower()

    assert backend in backend_map, f"Backend {backend} unknown or unsupported!"
    backend_class = backend_map[backend]
    backend_args = backend_class.get_required_args()
    user_choices = query_for_args(backend_args) if backend_args else {}

    scraper = NewsScraper(
        backend=backend_class(**user_choices), language=Language(language)
    )
    outfile = Path(f"results/{topic.replace(' ', '_')}_summary.csv")

    summarized_articles, sorted_entities = scraper.fetch_summary_and_named_entities(
        topic,
        max_num_articles,
        updated_after=datetime.datetime.today()
        - dateutil.relativedelta.relativedelta(months=1),
        outfile=outfile,
    )

    print(
        "Here's your summary of the news articles: \n",
        summarized_articles,
        "\n",
        "\n",
        "These are the named entities from the headlines: \n",
        sorted_entities,
    )

    # Reprompting
    rerun = typer.confirm("Wanna rerun?")
    if rerun:
        new_topic = typer.prompt("Give me another topic")
        run(new_topic, language, backend, max_num_articles)


if __name__ == "__main__":
    app()
