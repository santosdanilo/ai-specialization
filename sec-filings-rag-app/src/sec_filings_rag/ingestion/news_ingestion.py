import argparse
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastembed import LateInteractionTextEmbedding, SparseTextEmbedding, TextEmbedding
from qdrant_client import QdrantClient, models

from sec_filings_rag.ingestion.utils.news_client import NewsClient
from sec_filings_rag.ingestion.utils.simple_chunker import SimpleChunker
from sec_filings_rag.ingestion.utils.ticker_validator import parse_ticker

APP_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = APP_ROOT.parents[3]
DENSE_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "financial"
SPARSE_MODEL_NAME = "Qdrant/bm25"
COLBERT_MODEL_NAME = "colbert-ir/colbertv2.0"
MAX_TOKENS = 300


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest stock news into Qdrant")
    parser.add_argument(
        "ticker",
        type=parse_ticker,
        help="Stock ticker, e.g. 'AAPL'",
    )
    ticker = parser.parse_args().ticker

    load_dotenv(WORKSPACE_ROOT / ".env")

    qdrant = QdrantClient(
        url=os.getenv("QDRANT_API_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
    )

    news_client = NewsClient()

    news_data = news_client.fetch_news(ticker, max_stories=10)

    chunker = SimpleChunker(max_tokens=MAX_TOKENS)

    all_chunks = []
    for article in news_data:
        chunks = chunker.create_chunks(article["text"])
        for chunk in chunks:
            all_chunks.append(
                {
                    "text": chunk,
                    "metadata": article["metadata"],
                }
            )

    dense_model = TextEmbedding(DENSE_MODEL_NAME)
    sparse_model = SparseTextEmbedding(SPARSE_MODEL_NAME)
    colbert_model = LateInteractionTextEmbedding(COLBERT_MODEL_NAME)

    points = []
    for chunk_data in all_chunks:
        chunk = chunk_data["text"]
        metadata = chunk_data["metadata"]

        dense_embedding = next(iter(dense_model.passage_embed([chunk]))).tolist()
        sparse_embedding = next(iter(sparse_model.passage_embed([chunk]))).as_object()
        colbert_embedding = next(iter(colbert_model.passage_embed([chunk]))).tolist()

        point = models.PointStruct(
            id=str(uuid.uuid4()),
            vector={
                "dense": dense_embedding,
                "sparse": sparse_embedding,
                "colbert": colbert_embedding,
            },
            payload={"text": chunk, "metadata": metadata},
        )
        points.append(point)

    qdrant.upload_points(collection_name=COLLECTION_NAME, points=points, batch_size=5)


if __name__ == "__main__":
    main()
