from typing import TYPE_CHECKING

from sec_filings_rag.vector_store.base import ScoredHit, VectorRecord, VectorStore
from sec_filings_rag.vector_store.qdrant_store import QdrantVectorStore

if TYPE_CHECKING:
    from sec_filings_rag.api.config.settings import Settings

__all__ = [
    "QdrantVectorStore",
    "ScoredHit",
    "VectorRecord",
    "VectorStore",
    "create_vector_store",
]


def create_vector_store(settings: "Settings") -> VectorStore:
    """Factory switching on ``settings.vector_store_provider`` (default: qdrant)."""
    provider = settings.vector_store_provider
    if provider == "qdrant":
        from qdrant_client import QdrantClient

        return QdrantVectorStore(
            client=QdrantClient(
                url=settings.qdrant_api_url,
                api_key=settings.qdrant_api_key,
            ),
            collection_name=settings.collection_name,
        )
    raise ValueError(
        f"Unknown vector store provider: {provider!r} "
        "(expected one of: 'qdrant')"
    )
