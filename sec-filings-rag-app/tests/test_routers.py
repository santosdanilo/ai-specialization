import pytest
import test_agent_service as agent_fixtures  # reuse fake models
from conftest import FakeSearchService
from fastapi.testclient import TestClient
from sec_filings_rag.api.deps import (
    get_agent_service,
    get_rag_service,
    get_search_service,
)
from sec_filings_rag.api.models.agent import AgentResponse
from sec_filings_rag.api.models.rag import RAGResponse
from sec_filings_rag.main import app


@pytest.fixture
def client():
    app.dependency_overrides.clear()
    yield TestClient(app)
    app.dependency_overrides.clear()


class FakeRAGService:
    def __init__(self):
        self.calls = []

    def generate_answer(self, query, limit=3):
        self.calls.append((query, limit))
        return RAGResponse(query=query, answer="fake answer", metadata=[])


class FakeAgentService:
    def __init__(self, error=None):
        self.error = error

    async def analyze(self, query, limit=3):
        if self.error:
            raise ValueError(self.error)
        return AgentResponse(
            query=query,
            ticker="AAPL",
            fundamental_analysis=agent_fixtures.FUNDAMENTAL,
            momentum_analysis=agent_fixtures.MOMENTUM,
            sentiment_analysis=agent_fixtures.SENTIMENT,
            final_recommendation=agent_fixtures.RECOMMENDATION,
        )


def test_search_endpoint_uses_overridden_dependency(client):
    fake = FakeSearchService()
    app.dependency_overrides[get_search_service] = lambda: fake

    response = client.post("/search", json={"query": "risks", "limit": 2})

    assert response.status_code == 200
    assert response.json()["results"][0]["text"] == "chunk one"
    assert fake.calls == [("risks", 2, None)]


def test_rag_endpoint_uses_overridden_dependency(client):
    fake = FakeRAGService()
    app.dependency_overrides[get_rag_service] = lambda: fake

    response = client.post("/rag", json={"query": "risks?"})

    assert response.status_code == 200
    assert response.json()["answer"] == "fake answer"
    assert fake.calls == [("risks?", 3)]


def test_agent_endpoint_success(client):
    app.dependency_overrides[get_agent_service] = lambda: FakeAgentService()

    response = client.post("/agent", json={"query": "how is apple?"})

    assert response.status_code == 200
    assert response.json()["ticker"] == "AAPL"
    assert response.json()["final_recommendation"]["action"] == "BUY"


def test_agent_endpoint_bad_request_when_no_ticker(client):
    app.dependency_overrides[get_agent_service] = lambda: FakeAgentService(
        error="Could not extract a valid ticker symbol from the query"
    )

    response = client.post("/agent", json={"query": "what is the weather?"})

    assert response.status_code == 400
    assert "ticker" in response.json()["detail"]


def test_root(client):
    assert client.get("/").json() == {"status": "ok"}
