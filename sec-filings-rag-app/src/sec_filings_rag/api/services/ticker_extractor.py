from sec_filings_rag.api.config.company_mappings import TICKER_EXTRACTION_PROMPT
from sec_filings_rag.api.config.settings import Settings
from sec_filings_rag.api.interfaces import ChatClient
from sec_filings_rag.api.models.ticker_extractor import TickerResult


class TickerExtractor:
    def __init__(
        self,
        client: ChatClient,
        settings: Settings,
        mappings: dict[str, str],
    ):
        self.client = client
        self.settings = settings
        self.mappings = mappings

    def extract_ticker(self, query: str) -> str | None:
        query_lower = query.lower()
        for company_name, ticker in self.mappings.items():
            if company_name in query_lower:
                return ticker

        return self._extract_with_llm(query)

    def _extract_with_llm(self, query: str) -> str | None:
        prompt = TICKER_EXTRACTION_PROMPT.format(query=query)
        result = self.client.chat.completions.create(
            model=self.settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_model=TickerResult,
        )
        return result.ticker
