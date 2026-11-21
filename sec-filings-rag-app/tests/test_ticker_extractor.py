from types import SimpleNamespace

from conftest import ExplodingClient
from sec_filings_rag.api.config.company_mappings import COMPANY_TICKER_MAPPINGS
from sec_filings_rag.api.models.ticker_extractor import TickerResult
from sec_filings_rag.api.services.ticker_extractor import TickerExtractor


class FakeStructuredClient:
    def __init__(self, result):
        self.result = result
        self.calls: list[dict] = []

    class _Completions:
        def __init__(self, outer):
            self.outer = outer

        def create(self, **kwargs):
            self.outer.calls.append(kwargs)
            return self.outer.result

    @property
    def chat(self):
        return SimpleNamespace(completions=self._Completions(self))


def make_extractor(client, mappings=COMPANY_TICKER_MAPPINGS):
    from sec_filings_rag.api.config.settings import Settings

    settings = Settings(llm_api_key="k", llm_model="test-model")
    return TickerExtractor(client=client, settings=settings, mappings=mappings)


class TestStaticMapping:
    def test_known_company_never_calls_llm(self):
        extractor = make_extractor(ExplodingClient())
        assert extractor.extract_ticker("How is Apple doing?") == "AAPL"

    def test_mapping_is_case_insensitive(self):
        extractor = make_extractor(ExplodingClient())
        assert extractor.extract_ticker("TELL ME ABOUT NVIDIA") == "NVDA"

    def test_custom_mappings(self):
        extractor = make_extractor(ExplodingClient(), mappings={"ibm": "IBM"})
        assert extractor.extract_ticker("what about ibm?") == "IBM"


class TestLLMFallback:
    def test_unknown_company_uses_llm(self):
        client = FakeStructuredClient(SimpleNamespace(ticker="DIS"))
        extractor = make_extractor(client)

        result = extractor.extract_ticker("How is Disney doing?")

        assert result == "DIS"
        assert len(client.calls) == 1
        assert client.calls[0]["model"] == "test-model"
        assert client.calls[0]["response_model"] is TickerResult

    def test_llm_none_result_propagates(self):
        client = FakeStructuredClient(SimpleNamespace(ticker="NONE"))
        extractor = make_extractor(client)
        assert extractor.extract_ticker("what is the weather?") == "NONE"
