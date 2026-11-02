import os
from pathlib import Path

from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

APP_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = APP_ROOT.parents[3]
COLLECTION_NAME = "financial"

load_dotenv(WORKSPACE_ROOT / ".env")

qdrant = QdrantClient(
    url=os.getenv("QDRANT_API_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

fields_to_index = [
    "metadata.ticker",
    "metadata.form_type",
    "metadata.source",
]

for field_name in fields_to_index:
    qdrant.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name=field_name,
        field_schema=models.PayloadSchemaType.KEYWORD,
    )
    print(f"Qdrant: Index created for field {field_name}")
