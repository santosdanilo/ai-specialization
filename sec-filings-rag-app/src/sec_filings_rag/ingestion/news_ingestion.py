import argparse

from sec_filings_rag.ingestion.utils.news_client import load_news_client
from sec_filings_rag.ingestion.utils.records import build_records
from sec_filings_rag.ingestion.utils.simple_chunker import load_simple_chunker
from sec_filings_rag.ingestion.utils.ticker_validator import parse_ticker

MAX_TOKENS = 300


def collect_chunk_items(news_client, chunker, ticker: str, max_stories: int = 10):
    chunk_items = []
    for article in news_client.fetch_news(ticker, max_stories=max_stories):
        for chunk in chunker.create_chunks(article["text"]):
            chunk_items.append(
                {"text": chunk, "metadata": article["metadata"]}
            )
    return chunk_items


def ingest_news(
    store,
    news_client,
    chunker,
    embedding_service,
    ticker: str,
    max_stories: int = 10,
) -> int:
    """Fetch news, chunk, embed and upsert. Returns number of records."""
    chunk_items = collect_chunk_items(news_client, chunker, ticker, max_stories)
    records = build_records(chunk_items, embedding_service)
    return store.upsert(records)


def main() -> None:
    from sec_filings_rag.api.config.settings import get_settings
    from sec_filings_rag.api.services.embeddings import load_embedding_service
    from sec_filings_rag.vector_store import create_vector_store

    parser = argparse.ArgumentParser(description="Ingest stock news into Qdrant")
    parser.add_argument(
        "ticker",
        type=parse_ticker,
        help="Stock ticker, e.g. 'AAPL'",
    )
    ticker = parser.parse_args().ticker

    settings = get_settings()
    store = create_vector_store(settings)
    news_client = load_news_client()
    chunker = load_simple_chunker(settings.dense_model_name, max_tokens=MAX_TOKENS)
    embedding_service = load_embedding_service(settings)

    count = ingest_news(
        store=store,
        news_client=news_client,
        chunker=chunker,
        embedding_service=embedding_service,
        ticker=ticker,
    )
    print(f"Ingested {count} news chunks for {ticker}")


if __name__ == "__main__":
    main()
