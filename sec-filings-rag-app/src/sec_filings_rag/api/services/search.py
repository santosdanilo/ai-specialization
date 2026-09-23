from qdrant_client import QdrantClient, models

from sec_filings_rag.api.models.search import SearchResponse, SearchResult
from sec_filings_rag.api.services.embeddings import EmbeddingService


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

    def query(self, query: str, limit: int = 3):
        query_dense_embedding, query_sparse_embedding, query_colbert_embedding = (
            self.embedding_service.embedded_query(
                query=query,
            )
        )

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
