from qdrant_client import QdrantClient, models

from sec_filings_rag.api.models.search import SearchResponse, SearchResult
from sec_filings_rag.api.services.embeddings import EmbeddingService
from typing import Any


class SearchService:
    def __init__(
        self,
        qdrant_api_url: str,
        qdrant_api_key: str,
        collection_name: str,
    ):
        self.qdrant = QdrantClient(
            url=qdrant_api_url,
            api_key=qdrant_api_key,
        )
        self.collection_name = collection_name
        self.embedding_service = EmbeddingService()

    def _build_qdrant_filter(self, filter: dict[str, Any] | None = None) -> dict | None:
        if not filter:
            return None

        must_conditions = []
        for key, value in filter.items():
            must_conditions.append(
                {"key": f"metadata.{key}", "match": {"value": value}}
            )

        return {"must": must_conditions}

    def query(self, query: str, limit: int = 3, filter: dict[str, Any] | None = None):
        query_dense_embedding, query_sparse_embedding, query_colbert_embedding = (
            self.embedding_service.embedded_query(
                query=query,
            )
        )

        query_filter = self._build_qdrant_filter(filter)

        results = self.qdrant.query_points(
            collection_name=self.collection_name,
            prefetch=[
                {
                    "prefetch": [
                        {
                            "query": query_dense_embedding,
                            "using": "dense",
                            "limit": 10,
                        },
                        {
                            "query": query_sparse_embedding,
                            "using": "sparse",
                            "limit": 10,
                        },
                    ],
                    "query": models.FusionQuery(
                        fusion=models.Fusion.RRF,
                    ),
                    "limit": 15,
                },
                {},
            ],
            query=query_colbert_embedding,
            using="colbert",
            limit=limit,
            query_filter=query_filter,
            with_payload=True,
        )
        max_score = max(result.score for result in results.points)

        search_results = [
            SearchResult(
                score=result.score / max_score,
                text=result.payload["text"],
                metadata=result.payload["metadata"],
            )
            for result in results.points
        ]
        return SearchResponse(
            results=search_results,
        )
