from collections.abc import Callable
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

from sec_filings_rag.ingestion.interfaces import NewsSource  # noqa: F401 (re-export for typing)


def Ticker(ticker: str, count: int = 10) -> SimpleNamespace:
    """Return ticker news in yfinance's former ``Ticker.news`` format.

    Yahoo's endpoint used by ``yf.Ticker(ticker).news`` currently returns 404.
    ``yf.Search`` still provides news, but uses a different article schema.
    Adapt its results here so existing ingestion code can keep consuming them.
    """
    import yfinance as yf

    articles = yf.Search(ticker, news_count=count).news
    news = []

    for article in articles:
        # Search results are flat dictionaries; accept nested content too so
        # this adapter remains compatible if yfinance changes its payload.
        content = article.get("content", article)
        title = content.get("title")
        canonical_url = content.get("canonicalUrl") or {}
        url = canonical_url.get("url") or content.get("link")
        if not title or not url:
            continue

        published = content.get("pubDate") or content.get("providerPublishTime")
        if isinstance(published, (int, float)):
            published = datetime.fromtimestamp(published, tz=timezone.utc).isoformat()

        news.append(
            {
                "id": article.get("id") or content.get("uuid"),
                "content": {
                    "contentType": content.get("contentType", "STORY"),
                    "title": title,
                    "pubDate": published,
                    "canonicalUrl": {"url": url},
                },
            }
        )

    return SimpleNamespace(news=news)


class NewsClient:
    """Fetches and extracts news articles for a ticker.

    ``news_fetcher``, ``url_fetcher`` and ``text_extractor`` are required and
    injected so parsing/filtering can be tested offline. Use
    ``load_news_client()`` to build the real yfinance/trafilatura-backed
    instance.
    """

    def __init__(
        self,
        news_fetcher: Callable[..., SimpleNamespace],
        url_fetcher: Callable[[str], Any],
        text_extractor: Callable[[Any], Any],
    ):
        self._news_fetcher = news_fetcher
        self._url_fetcher = url_fetcher
        self._text_extractor = text_extractor

    def fetch_news(self, ticker: str, max_stories: int = 10) -> list[dict[str, any]]:
        data = self._news_fetcher(ticker, count=max_stories)
        news = data.news

        news_data = []
        for item in news[:max_stories]:
            content = item.get("content", {})
            content_type = content.get("contentType")
            if content_type != "STORY":
                continue

            canonical_url = content.get("canonicalUrl", {})
            title = content.get("title")
            date = content.get("pubDate")
            url = canonical_url.get("url")

            if not url or "finance.yahoo.com" not in url:
                continue

            downloaded = self._url_fetcher(url)
            text_content = self._text_extractor(downloaded)
            if text_content:
                metadata = {
                    "ticker": ticker,
                    "title": title,
                    "url": url,
                    "date": date,
                    "source": "yahoo_finance",
                }
                news_data.append(
                    {
                        "text": text_content,
                        "metadata": metadata,
                    }
                )

        return news_data


def load_news_client() -> NewsClient:
    """Build the real NewsClient backed by yfinance and trafilatura."""
    import trafilatura

    return NewsClient(
        news_fetcher=Ticker,
        url_fetcher=trafilatura.fetch_url,
        text_extractor=trafilatura.extract,
    )
