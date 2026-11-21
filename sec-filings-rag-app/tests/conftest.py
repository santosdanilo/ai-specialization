from types import SimpleNamespace

import pytest

from sec_filings_rag.api.config.settings import Settings
from sec_filings_rag.api.models.search import SearchResponse, SearchResult
from sec_filings_rag.vector_store import ScoredHit


@pytest.fixture
def settings() -> Settings:
    return Settings(
        qdrant_api_url="http://fake",
        qdrant_api_key="fake-key",
        llm_api_key="fake-llm",
        llm_model="test-model",
        llm_fallback_models="fallback-model",
    )


class FakeEmbeddingService:
    """Stands in for EmbeddingService without loading any model."""

    def __init__(self):
        self.query_calls: list[str] = []
        self.passage_calls: list[list[str]] = []

    def embedded_query(self, query: str):
        self.query_calls.append(query)
        return [0.1, 0.2], {"indices": [1, 2], "values": [1.0, 1.0]}, [[0.0], [0.1]]

    def embed_passages(self, texts: list[str]):
        self.passage_calls.append(texts)
        return [
            {"dense": [0.5] * 3, "sparse": {"indices": [0], "values": [1.0]}, "colbert": [[1.0]]}
            for _ in texts
        ]


class FakeVectorStore:
    def __init__(self, hits: list[ScoredHit] | None = None):
        self.hits = hits if hits is not None else []
        self.search_calls: list[dict] = []
        self.upserted: list = []
        self.reset_calls = 0
        self.indexed_fields: list[str] = []

    def search(self, *, dense, sparse, colbert, limit=3, filter=None):
        self.search_calls.append(
            {
                "dense": dense,
                "sparse": sparse,
                "colbert": colbert,
                "limit": limit,
                "filter": filter,
            }
        )
        return list(self.hits)

    def reset(self):
        self.reset_calls += 1

    def upsert(self, records):
        self.upserted.extend(records)
        return len(records)

    def ensure_filter_index(self, field):
        self.indexed_fields.append(field)


def make_hit(score: float, text: str, metadata: dict | None = None) -> ScoredHit:
    return ScoredHit(score=score, text=text, metadata=metadata or {"ticker": "AAPL"})


class FakeSearchService:
    def __init__(self, results: list[SearchResult] | None = None):
        self.results = results if results is not None else [
            SearchResult(score=1.0, text="chunk one", metadata={"ticker": "AAPL"}),
            SearchResult(score=0.5, text="chunk two", metadata={"ticker": "AAPL"}),
        ]
        self.calls: list[tuple] = []

    def query(self, query: str, limit: int = 3, filter: dict | None = None):
        self.calls.append((query, limit, filter))
        return SearchResponse(results=list(self.results))


class ExplodingClient:
    """LLM client stub that fails loudly if a test hits the LLM path."""

    class _Completions:
        def create(self, *args, **kwargs):
            raise AssertionError("LLM should not have been called")

    chat = SimpleNamespace(completions=_Completions())
