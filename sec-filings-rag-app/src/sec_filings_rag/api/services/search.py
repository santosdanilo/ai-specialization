from typing import Any

from sec_filings_rag.api.interfaces import QueryEmbeddingService
from sec_filings_rag.api.models.search import SearchResponse, SearchResult
from sec_filings_rag.vector_store import VectorStore


class SearchService:
    def __init__(
        self,
        store: VectorStore,
        embedding_service: QueryEmbeddingService,
    ):
        self.store = store
        self.embedding_service = embedding_service

    def query(self, query: str, limit: int = 3, filter: dict[str, Any] | None = None):
        query_dense_embedding, query_sparse_embedding, query_colbert_embedding = (
            self.embedding_service.embedded_query(
                query=query,
            )
        )

        hits = self.store.search(
            dense=query_dense_embedding,
            sparse=query_sparse_embedding,
            colbert=query_colbert_embedding,
            limit=limit,
            filter=filter,
        )

        if not hits:
            return SearchResponse(results=[])

        max_score = max(hit.score for hit in hits)

        search_results = [
            SearchResult(
                score=hit.score / max_score,
                text=hit.text,
                metadata=hit.metadata,
            )
            for hit in hits
        ]
        return SearchResponse(
            results=search_results,
        )
