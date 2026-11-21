import argparse

from sec_filings_rag.ingestion.utils.edgar_client import load_edgar_client
from sec_filings_rag.ingestion.utils.records import build_records
from sec_filings_rag.ingestion.utils.semantic_chunker import load_semantic_chunker
from sec_filings_rag.ingestion.utils.ticker_validator import parse_ticker

FORM_TYPES = ["10-K", "10-Q"]


def collect_chunk_items(edgar, chunker, ticker: str, form_types=FORM_TYPES):
    chunk_items = []
    for form_type in form_types:
        data = edgar.fetch_filing_data(ticker, form_type)
        text = edgar.get_combined_text(data)
        for chunk in chunker.create_chunks(text):
            chunk_items.append({"text": chunk, "metadata": data["metadata"]})
    return chunk_items


def ingest_filings(
    store,
    edgar,
    chunker,
    embedding_service,
    ticker: str,
    form_types=FORM_TYPES,
) -> int:
    """Fetch filings, chunk, embed and upsert. Returns number of records."""
    chunk_items = collect_chunk_items(edgar, chunker, ticker, form_types)
    records = build_records(chunk_items, embedding_service)
    return store.upsert(records)


def main() -> None:
    from sec_filings_rag.api.config.settings import get_settings
    from sec_filings_rag.api.services.embeddings import load_embedding_service
    from sec_filings_rag.api.services.search import SearchService
    from sec_filings_rag.vector_store import create_vector_store

    parser = argparse.ArgumentParser(description="Ingest SEC filings into Qdrant")
    parser.add_argument(
        "ticker",
        type=parse_ticker,
        help="Stock ticker, e.g. 'AAPL'",
    )
    ticker = parser.parse_args().ticker

    settings = get_settings()
    store = create_vector_store(settings)
    edgar = load_edgar_client(settings.edgar_client_email)
    chunker = load_semantic_chunker(settings)
    embedding_service = load_embedding_service(settings)

    store.reset()

    count = ingest_filings(
        store=store,
        edgar=edgar,
        chunker=chunker,
        embedding_service=embedding_service,
        ticker=ticker,
    )
    print(f"Ingested {count} chunks for {ticker}")

    search_service = SearchService(
        store=store, embedding_service=embedding_service
    )
    response = search_service.query("what are the main financial risks?", limit=3)
    for result in response.results:
        print(f"Score: {result.score}")
        print(f"Texto: {result.text[:100]}...")
        print("-" * 80)


if __name__ == "__main__":
    main()
