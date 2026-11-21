from types import SimpleNamespace

import pytest
from qdrant_client import models

from sec_filings_rag.api.config.settings import Settings
from sec_filings_rag.vector_store import (
    QdrantVectorStore,
    VectorStore,
    create_vector_store,
)


class FakeQdrantClient:
    def __init__(self, points=None):
        self.points = points if points is not None else []
        self.query_calls: list[dict] = []
        self.upload_calls: list[dict] = []
        self.deleted: list[str] = []
        self.created: list[dict] = []
        self.indexed: list[dict] = []

    def query_points(self, **kwargs):
        self.query_calls.append(kwargs)
        return SimpleNamespace(points=self.points)

    def upload_points(self, **kwargs):
        self.upload_calls.append(kwargs)

    def delete_collection(self, collection_name, **kwargs):
        self.deleted.append(collection_name)

    def create_collection(self, **kwargs):
        self.created.append(kwargs)

    def create_payload_index(self, **kwargs):
        self.indexed.append(kwargs)


def make_store(points=None):
    client = FakeQdrantClient(points=points)
    store = QdrantVectorStore(client=client, collection_name="test-collection")
    return store, client


def make_qdrant_point(score, text, metadata=None):
    return SimpleNamespace(
        score=score, payload={"text": text, "metadata": metadata or {"ticker": "AAPL"}}
    )


class TestSearch:
    def test_returns_scored_hits(self):
        store, _ = make_store(
            points=[
                make_qdrant_point(4.0, "hi"),
                make_qdrant_point(2.0, "lo"),
            ]
        )

        hits = store.search(dense=[0.1], sparse={}, colbert=[[0.0]], limit=2)

        assert [(h.score, h.text, h.metadata) for h in hits] == [
            (4.0, "hi", {"ticker": "AAPL"}),
            (2.0, "lo", {"ticker": "AAPL"}),
        ]

    def test_empty(self):
        store, _ = make_store(points=[])
        assert store.search(dense=[0.1], sparse={}, colbert=[[0.0]]) == []

    def test_hybrid_prefetch_shape(self):
        store, client = make_store()

        store.search(
            dense=[0.1, 0.2],
            sparse={"indices": [1], "values": [1.0]},
            colbert=[[0.0]],
            limit=5,
            filter={"ticker": "AAPL", "form_type": "10-K"},
        )

        call = client.query_calls[0]
        assert call["collection_name"] == "test-collection"
        assert call["using"] == "colbert"
        assert call["limit"] == 5
        assert call["query"] == [[0.0]]
        assert call["with_payload"] is True

        dense_prefetch, colbert_prefetch = call["prefetch"]
        inner = dense_prefetch["prefetch"]
        assert inner[0] == {"query": [0.1, 0.2], "using": "dense", "limit": 10}
        assert inner[1] == {
            "query": {"indices": [1], "values": [1.0]},
            "using": "sparse",
            "limit": 10,
        }
        assert isinstance(dense_prefetch["query"], models.FusionQuery)
        assert dense_prefetch["query"].fusion == models.Fusion.RRF
        assert colbert_prefetch == {}

        assert call["query_filter"] == {
            "must": [
                {"key": "metadata.ticker", "match": {"value": "AAPL"}},
                {"key": "metadata.form_type", "match": {"value": "10-K"}},
            ]
        }

    def test_no_filter(self):
        store, client = make_store()
        store.search(dense=[0.1], sparse={}, colbert=[[0.0]])
        assert client.query_calls[0]["query_filter"] is None


class TestReset:
    def test_deletes_and_recreates_collection(self):
        store, client = make_store()

        store.reset()

        assert client.deleted == ["test-collection"]
        vectors_config = client.created[0]["vectors_config"]
        assert set(vectors_config) == {"dense", "colbert"}
        assert client.created[0]["sparse_vectors_config"] == {
            "sparse": models.SparseVectorParams()
        }


class TestUpsert:
    def test_converts_records_to_points(self):
        store, client = make_store()

        count = store.upsert(
            [
                {"text": "a", "metadata": {"ticker": "AAPL"}, "vectors": {"dense": [1.0], "sparse": {"indices": [0], "values": [1.0]}, "colbert": [[1.0]]}},
                {"text": "b", "metadata": {"ticker": "MSFT"}, "vectors": {"dense": [2.0], "sparse": {"indices": [1], "values": [1.0]}, "colbert": [[2.0]]}},
            ]
        )

        assert count == 2
        upload = client.upload_calls[0]
        assert upload["collection_name"] == "test-collection"
        assert upload["batch_size"] == 5

        points = upload["points"]
        assert len(points) == 2
        assert all(isinstance(p.id, str) for p in points)
        assert points[0].payload == {"text": "a", "metadata": {"ticker": "AAPL"}}
        assert set(points[0].vector) == {"dense", "sparse", "colbert"}

    def test_empty(self):
        store, client = make_store()
        assert store.upsert([]) == 0
        assert client.upload_calls[0]["points"] == []


class TestEnsureFilterIndex:
    def test_creates_keyword_payload_index(self):
        store, client = make_store()

        store.ensure_filter_index("ticker")

        assert client.indexed == [
            {
                "collection_name": "test-collection",
                "field_name": "metadata.ticker",
                "field_schema": models.PayloadSchemaType.KEYWORD,
            }
        ]


class TestFactory:
    def test_default_provider_is_qdrant(self):
        settings = Settings(
            qdrant_api_url="https://fake",
            qdrant_api_key="k",
            llm_api_key="k",
        )

        store = create_vector_store(settings)

        assert isinstance(store, QdrantVectorStore)
        assert isinstance(store, VectorStore)
        assert store.collection_name == settings.collection_name

    def test_unknown_provider_raises(self):
        settings = Settings(
            qdrant_api_url="http://fake",
            qdrant_api_key="k",
            llm_api_key="k",
            vector_store_provider="pinecone",
        )

        with pytest.raises(ValueError, match="pinecone"):
            create_vector_store(settings)
