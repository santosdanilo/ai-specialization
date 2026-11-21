from conftest import FakeEmbeddingService, FakeVectorStore, make_hit
from sec_filings_rag.api.services.search import SearchService


def make_service(hits=None):
    store = FakeVectorStore(hits=hits)
    embedder = FakeEmbeddingService()
    service = SearchService(store=store, embedding_service=embedder)
    return service, store, embedder


class TestQuery:
    def test_empty_results(self):
        service, _, _ = make_service(hits=[])
        response = service.query("anything")
        assert response.results == []

    def test_scores_normalized_by_max(self):
        hits = [make_hit(2.0, "high"), make_hit(1.0, "low")]
        service, _, _ = make_service(hits=hits)

        response = service.query("anything", limit=5)

        assert [r.score for r in response.results] == [1.0, 0.5]
        assert [r.text for r in response.results] == ["high", "low"]

    def test_passes_embedded_vectors_and_filter_to_store(self):
        hits = [make_hit(1.0, "hit")]
        service, store, embedder = make_service(hits=hits)

        service.query("risk factors", limit=2, filter={"ticker": "AAPL"})

        assert embedder.query_calls == ["risk factors"]
        call = store.search_calls[0]
        assert call["dense"] == [0.1, 0.2]
        assert call["sparse"] == {"indices": [1, 2], "values": [1.0, 1.0]}
        assert call["colbert"] == [[0.0], [0.1]]
        assert call["limit"] == 2
        assert call["filter"] == {"ticker": "AAPL"}
