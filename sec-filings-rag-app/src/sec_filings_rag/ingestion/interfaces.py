from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Chunker(Protocol):
    def create_chunks(self, text_content: str) -> list[str]: ...


@runtime_checkable
class FilingSource(Protocol):
    def fetch_filing_data(self, ticker: str, form_type: str) -> dict[str, Any]: ...

    def get_combined_text(self, data: dict) -> str: ...


@runtime_checkable
class NewsSource(Protocol):
    def fetch_news(
        self, ticker: str, max_stories: int = 10
    ) -> list[dict[str, Any]]: ...


@runtime_checkable
class PassageEmbeddingService(Protocol):
    def embedded_query(self, query: str) -> tuple[Any, Any, Any]: ...

    def embed_passages(self, texts: list[str]) -> list[dict[str, Any]]: ...
