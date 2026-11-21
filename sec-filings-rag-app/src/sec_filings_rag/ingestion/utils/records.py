from typing import Any

from sec_filings_rag.vector_store import VectorRecord


def build_records(
    chunk_items: list[dict[str, Any]],
    embedding_service: Any,
) -> list[VectorRecord]:
    """Embed ``[{"text", "metadata"}, ...]`` into DB-agnostic vector records.

    ``embedding_service`` must implement ``embed_passages(texts)`` returning a
    vector dict per text (see api.services.embeddings.EmbeddingService).
    """
    texts = [item["text"] for item in chunk_items]
    vectors = embedding_service.embed_passages(texts)

    return [
        {
            "text": item["text"],
            "metadata": item["metadata"],
            "vectors": vector,
        }
        for item, vector in zip(chunk_items, vectors)
    ]
