import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastembed import LateInteractionTextEmbedding, SparseTextEmbedding, TextEmbedding
from qdrant_client import QdrantClient, models

from training.rrf_reranking.utils.edgar_client import EdgarClient
from training.rrf_reranking.utils.semantic_chunker import SemanticChunker

APP_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = APP_ROOT.parents[3]
DENSE_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "financial"
SPARSE_MODEL_NAME = "Qdrant/bm25"
COLBERT_MODEL_NAME = "colbert-ir/colbertv2.0"
MAX_TOKENS = 300


def main() -> None:
    load_dotenv(WORKSPACE_ROOT / ".env")

    qdrant = QdrantClient(
        url=os.getenv("QDRANT_API_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
    )

    qdrant.delete_collection(COLLECTION_NAME)
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            "dense": models.VectorParams(
                size=384,
                distance=models.Distance.COSINE,
            ),
            "colbert": models.VectorParams(
                size=128,
                distance=models.Distance.COSINE,
                multivector_config=models.MultiVectorConfig(
                    comparator=models.MultiVectorComparator.MAX_SIM,
                ),
            ),
        },
        sparse_vectors_config={"sparse": models.SparseVectorParams()},
    )

    edgar = EdgarClient(os.getenv("EDGAR_CLIENT_EMAIL"))

    data_10k = edgar.fetch_filing_data("AAPL", "10-K")
    text_10k = edgar.get_combined_text(data_10k)

    data_10q = edgar.fetch_filing_data("AAPL", "10-Q")
    text_10q = edgar.get_combined_text(data_10q)

    chunker = SemanticChunker(max_tokens=MAX_TOKENS)

    all_chunks = []

    for data, text in [(data_10k, text_10k), (data_10q, text_10q)]:
        chunks = chunker.create_chunks(text)
        for chunk in chunks:
            all_chunks.append({"text": chunk, "metadata": data["metadata"]})

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

        qdrant.upload_points(
            collection_name=COLLECTION_NAME, points=points, batch_size=5
        )

    query_text = "what are the main financial risks?"
    query_dense_embedding = next(iter(dense_model.query_embed([query_text]))).tolist()
    query_sparse_embedding = next(
        iter(sparse_model.query_embed([query_text]))
    ).as_object()
    query_colbert_embedding = next(
        iter(colbert_model.query_embed([query_text]))
    ).tolist()

    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=[
            {
                "prefetch": [
                    {"query": query_dense_embedding, "using": "dense", "limit": 10},
                    {"query": query_sparse_embedding, "using": "sparse", "limit": 10},
                ],
                "query": models.FusionQuery(fusion=models.Fusion.RRF),
                "limit": 20,
            },
            {},
        ],
        query=query_colbert_embedding,
        using="colbert",
        limit=3,
        with_payload=True,
    )

    max_score = max(result.score for result in results.points)
    for r in results.points:
        normalized_score = r.score / max_score
        print(f"Score: {normalized_score}")
        print(f"Texto: {r.payload['text'][:100]}...")
        print("-" * 80)


if __name__ == "__main__":
    main()
