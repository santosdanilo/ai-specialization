import asyncio
from types import SimpleNamespace

from conftest import FakeSearchService
from sec_filings_rag.api.config.prompts import SENTIMENT_QUERY_TEMPLATE
from sec_filings_rag.api.models.agent import (
    FinalRecommendation,
    FundamentalAnalysis,
    MomentumAnalysis,
    SentimentAnalysis,
)
from sec_filings_rag.api.services.agent import AgentService

FUNDAMENTAL = FundamentalAnalysis(
    overall_investment_thesis="strong",
    investment_grade="A",
    confidence_score=0.9,
    key_strengths=["a", "b", "c"],
    key_concerns=["d", "e", "f"],
    recommendation="buy",
)
MOMENTUM = MomentumAnalysis(
    overall_momentum="positive",
    momentum_strength="strong",
    key_momentum_drivers=["a", "b"],
    momentum_risks=["c", "d"],
    short_term_outlook="bullish",
    momentum_score=0.8,
)
SENTIMENT = SentimentAnalysis(
    sentiment_score=0.7,
    sentiment_direction="Positive",
    key_news_themes=["earnings"],
    recent_catalysts=["launch"],
    market_outlook="good",
)
RECOMMENDATION = FinalRecommendation(
    action="BUY",
    confidence=0.85,
    rationale="all green",
    key_risks=["r1"],
    key_opportunities=["o1"],
    time_horizon="Long-term",
)

RESPONSES = {
    FundamentalAnalysis: FUNDAMENTAL,
    MomentumAnalysis: MOMENTUM,
    SentimentAnalysis: SENTIMENT,
    FinalRecommendation: RECOMMENDATION,
}


class FakeAsyncClient:
    def __init__(self):
        self.calls: list[dict] = []

    class _Completions:
        def __init__(self, outer):
            self.outer = outer

        async def create(self, **kwargs):
            self.outer.calls.append(kwargs)
            return RESPONSES[kwargs["response_model"]]

    @property
    def chat(self):
        return SimpleNamespace(completions=self._Completions(self))


class FakeTickerExtractor:
    def __init__(self, ticker="AAPL"):
        self.ticker = ticker

    def extract_ticker(self, query):
        return self.ticker


def make_agent(settings, search_service=None, ticker="AAPL"):
    search_service = search_service or FakeSearchService()
    client = FakeAsyncClient()
    service = AgentService(
        search_service=search_service,
        llm_client=client,
        ticker_extractor=FakeTickerExtractor(ticker),
        settings=settings,
    )
    return service, search_service, client


class TestAnalyze:
    def test_full_pipeline(self, settings):
        service, search_service, client = make_agent(settings)

        response = asyncio.run(service.analyze("how is apple?", limit=4))

        assert response.ticker == "AAPL"
        assert response.fundamental_analysis is FUNDAMENTAL
        assert response.momentum_analysis is MOMENTUM
        assert response.sentiment_analysis is SENTIMENT
        assert response.final_recommendation is RECOMMENDATION

        # 4 fundamental + 3 momentum + one search per char of the sentiment
        # query string (original _run_queries behavior) + 1 sentiment query
        sentiment_query = SENTIMENT_QUERY_TEMPLATE.format(ticker="AAPL")
        assert len(search_service.calls) == 4 + 3 + len(sentiment_query) + 1
        # three stream analyses + one aggregation
        assert len(client.calls) == 4

    def test_uses_injected_llm_model(self, settings):
        service, _, client = make_agent(settings)
        asyncio.run(service.analyze("how is apple?"))
        assert all(call["model"] == "test-model" for call in client.calls)

    def test_fundamental_and_momentum_filters(self, settings):
        service, search_service, _ = make_agent(settings)
        asyncio.run(service.analyze("how is apple?"))

        form_types = {
            call[2]["form_type"]
            for call in search_service.calls
            if call[2] and "form_type" in call[2]
        }
        sources = {
            call[2]["source"]
            for call in search_service.calls
            if call[2] and "source" in call[2]
        }
        assert form_types == {"10-K", "10-Q"}
        assert sources == {"yahoo_finance"}

    def test_aggregation_prompt_includes_stream_outputs(self, settings):
        service, _, client = make_agent(settings)
        asyncio.run(service.analyze("how is apple?"))

        aggregation_prompt = client.calls[-1]["messages"][0]["content"]
        assert FUNDAMENTAL.overall_investment_thesis in aggregation_prompt
        assert RECOMMENDATION is RESPONSES[FinalRecommendation]

    def test_missing_ticker_raises_value_error(self, settings):
        service, _, _ = make_agent(settings, ticker=None)
        try:
            asyncio.run(service.analyze("what is the weather?"))
        except ValueError as e:
            assert "ticker" in str(e).lower()
        else:
            raise AssertionError("expected ValueError")
