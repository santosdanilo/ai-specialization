import uuid
from typing import Any

from qdrant_client import QdrantClient, models

from sec_filings_rag.vector_store.base import ScoredHit, VectorRecord


class QdrantVectorStore:
    """Qdrant adapter: owns all Qdrant-specific fusion/schema/payload details."""

    def __init__(
        self,
        client: QdrantClient,
        collection_name: str,
        dense_vector_size: int,
        colbert_vector_size: int,
    ):
        self.client = client
        self.collection_name = collection_name
        self.dense_vector_size = dense_vector_size
        self.colbert_vector_size = colbert_vector_size

    @staticmethod
    def _build_filter(filter: dict[str, Any] | None = None) -> dict | None:
        if not filter:
            return None

        must_conditions = []
        for key, value in filter.items():
            must_conditions.append(
                {"key": f"metadata.{key}", "match": {"value": value}}
            )

        return {"must": must_conditions}

    def search(
        self,
        *,
        dense: Any,
        sparse: Any,
        colbert: Any,
        limit: int = 3,
        filter: dict[str, Any] | None = None,
    ) -> list[ScoredHit]:
        results = self.client.query_points(
            collection_name=self.collection_name,
            prefetch=[
                {
                    "prefetch": [
                        {"query": dense, "using": "dense", "limit": 10},
                        {"query": sparse, "using": "sparse", "limit": 10},
                    ],
                    "query": models.FusionQuery(fusion=models.Fusion.RRF),
                    "limit": 15,
                },
                {},
            ],
            query=colbert,
            using="colbert",
            limit=limit,
            query_filter=self._build_filter(filter),
            with_payload=True,
        )
        return [
            ScoredHit(
                score=point.score,
                text=point.payload["text"],
                metadata=point.payload["metadata"],
            )
            for point in results.points
        ]

    def reset(self) -> None:
        self.client.delete_collection(self.collection_name)
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config={
                "dense": models.VectorParams(
                    size=self.dense_vector_size,
                    distance=models.Distance.COSINE,
                ),
                "colbert": models.VectorParams(
                    size=self.colbert_vector_size,
                    distance=models.Distance.COSINE,
                    multivector_config=models.MultiVectorConfig(
                        comparator=models.MultiVectorComparator.MAX_SIM,
                    ),
                ),
            },
            sparse_vectors_config={"sparse": models.SparseVectorParams()},
        )

    def upsert(self, records: list[VectorRecord]) -> int:
        points = [
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector={
                    "dense": record["vectors"]["dense"],
                    "sparse": record["vectors"]["sparse"],
                    "colbert": record["vectors"]["colbert"],
                },
                payload={"text": record["text"], "metadata": record["metadata"]},
            )
            for record in records
        ]
        self.client.upload_points(
            collection_name=self.collection_name, points=points, batch_size=5
        )
        return len(points)

    def ensure_filter_index(self, field: str) -> None:
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name=f"metadata.{field}",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )
