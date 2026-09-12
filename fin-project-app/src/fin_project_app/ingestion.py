import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastembed import TextEmbedding, SparseTextEmbedding, LateInteractionTextEmbedding
from qdrant_client import QdrantClient, models

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = PROJECT_ROOT.parent
FILE_PATH = PROJECT_ROOT / "AAPL_10-K_1A_temp.md"
DENSE_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "financial"
SPARSE_MODEL_NAME = "Qdrant/bm25"
COLBERT_MODEL_NAME = "colbert-ir/colbertv2.0"


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

    content = FILE_PATH.read_text(encoding="utf-8")
    paragraphs = content.split("\n\n")
    chunks = [
        paragraph.strip() for paragraph in paragraphs if len(paragraph.strip()) > 50
    ]

    dense_model = TextEmbedding(DENSE_MODEL_NAME)
    sparse_model = SparseTextEmbedding(SPARSE_MODEL_NAME)
    colbert_model = LateInteractionTextEmbedding(COLBERT_MODEL_NAME)

    points = []
    for chunk in chunks:
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
            payload={"text": chunk, "source": str(FILE_PATH)},
        )
        points.append(point)

        qdrant.upload_points(collection_name=COLLECTION_NAME, points=points)

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
