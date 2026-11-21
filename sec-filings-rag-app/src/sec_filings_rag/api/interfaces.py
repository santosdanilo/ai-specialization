from typing import Any, Protocol, runtime_checkable
from collections.abc import Iterable

from sec_filings_rag.api.models.search import SearchResponse


@runtime_checkable
class Embedder(Protocol):
    def query_embed(self, texts: Iterable[str]) -> Iterable[Any]: ...

    def passage_embed(self, texts: Iterable[str]) -> Iterable[Any]: ...


@runtime_checkable
class QueryEmbeddingService(Protocol):
    def embedded_query(self, query: str) -> tuple[Any, Any, Any]: ...


@runtime_checkable
class SearchServiceProtocol(Protocol):
    def query(
        self, query: str, limit: int = 3, filter: dict[str, Any] | None = None
    ) -> SearchResponse: ...


class ChatCompletion(Protocol):
    def create(self, **kwargs: Any) -> Any: ...


@runtime_checkable
class ChatClient(Protocol):
    """Sync LLM client exposing ``chat.completions.create``."""

    chat: ChatCompletion


@runtime_checkable
class AsyncChatClient(Protocol):
    """Async LLM client exposing ``await chat.completions.create(...)``."""

    chat: ChatCompletion


@runtime_checkable
class TickerExtractorProtocol(Protocol):
    def extract_ticker(self, query: str) -> str | None: ...
