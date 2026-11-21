from types import SimpleNamespace

from conftest import FakeSearchService
from sec_filings_rag.api.services.rag import RAGService


class FakeChatClient:
    def __init__(self, answer="42"):
        self.answer = answer
        self.calls: list[dict] = []

    class _Completions:
        def __init__(self, outer):
            self.outer = outer

        def create(self, **kwargs):
            self.outer.calls.append(kwargs)
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(message=SimpleNamespace(content=self.outer.answer))
                ]
            )

    @property
    def chat(self):
        return SimpleNamespace(completions=self._Completions(self))


def make_rag(settings):
    search_service = FakeSearchService()
    client = FakeChatClient(answer="the answer")
    service = RAGService(
        search_service=search_service, llm_client=client, settings=settings
    )
    return service, search_service, client


class TestGenerateAnswer:
    def test_returns_answer_and_metadata(self, settings):
        service, _, _ = make_rag(settings)

        response = service.generate_answer("what are the risks?")

        assert response.answer == "the answer"
        assert response.query == "what are the risks?"
        assert response.metadata == [
            {"ticker": "AAPL", "score": 1.0},
            {"ticker": "AAPL", "score": 0.5},
        ]

    def test_prompt_contains_context_and_query(self, settings):
        service, _, client = make_rag(settings)

        service.generate_answer("what are the risks?", limit=7)

        assert client.calls[0]["model"] == "test-model"
        prompt = client.calls[0]["messages"][0]["content"]
        assert "chunk one" in prompt and "chunk two" in prompt
        assert "what are the risks?" in prompt

    def test_search_service_receives_query_and_limit(self, settings):
        service, search_service, _ = make_rag(settings)
        service.generate_answer("q", limit=2)
        assert search_service.calls == [("q", 2, None)]
