import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = PROJECT_ROOT.parent
FILE_PATH = PROJECT_ROOT / "AAPL_10-K_1A_temp.md"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "financial"


def main() -> None:
    load_dotenv(WORKSPACE_ROOT / ".env")

    qdrant = QdrantClient(
        url=os.getenv("QDRANT_API_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
    )

    qdrant.delete_collection(COLLECTION_NAME)
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=384,
            distance=models.Distance.COSINE,
        ),
    )

    content = FILE_PATH.read_text(encoding="utf-8")
    paragraphs = content.split("\n\n")
    chunks = [paragraph.strip() for paragraph in paragraphs if len(paragraph.strip()) > 50]

    model = TextEmbedding(MODEL_NAME)

    points = []
    for chunk in chunks:
        embedding = list(model.passage_embed([chunk]))[0].tolist()
        point = models.PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={"text": chunk, "source": str(FILE_PATH)},
        )
        points.append(point)

        qdrant.upload_points(collection_name=COLLECTION_NAME, points=points)


if __name__ == "__main__":
    main()
