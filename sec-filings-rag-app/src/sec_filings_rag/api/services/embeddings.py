from typing import Any

from sec_filings_rag.api.config.settings import Settings
from sec_filings_rag.api.interfaces import Embedder


class EmbeddingService:
    """Wraps three embedder models (dense, sparse, colbert).

    Models are injected so tests can pass lightweight fakes; use
    ``load_embedding_service()`` to build the real fastembed-backed instance.
    """

    def __init__(
        self,
        dense_model: Embedder,
        sparse_model: Embedder,
        colbert_model: Embedder,
    ):
        self.dense_model = dense_model
        self.sparse_model = sparse_model
        self.colbert_model = colbert_model

    def embedded_query(self, query: str):
        query_dense_embedding = next(
            iter(self.dense_model.query_embed([query]))
        ).tolist()

        query_sparse_embedding = next(
            iter(self.sparse_model.query_embed([query]))
        ).as_object()

        query_colbert_embedding = next(
            iter(self.colbert_model.query_embed([query]))
        ).tolist()

        return query_dense_embedding, query_sparse_embedding, query_colbert_embedding

    def embed_passages(self, texts: list[str]) -> list[dict[str, Any]]:
        """Return ``{"dense", "sparse", "colbert"}`` vectors per passage."""
        dense = [e.tolist() for e in self.dense_model.passage_embed(texts)]
        sparse = [e.as_object() for e in self.sparse_model.passage_embed(texts)]
        colbert = [e.tolist() for e in self.colbert_model.passage_embed(texts)]
        return [
            {"dense": d, "sparse": s, "colbert": c}
            for d, s, c in zip(dense, sparse, colbert)
        ]


def load_embedding_service(settings: Settings) -> EmbeddingService:
    from fastembed import (
        LateInteractionTextEmbedding,
        SparseTextEmbedding,
        TextEmbedding,
    )

    return EmbeddingService(
        dense_model=TextEmbedding(settings.dense_model_name),
        sparse_model=SparseTextEmbedding(settings.sparse_model_name),
        colbert_model=LateInteractionTextEmbedding(settings.colbert_model_name),
    )
