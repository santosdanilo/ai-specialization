"""Composition root: the only module that knows about concrete implementations.

Everything else receives collaborators via constructors; tests override these
providers (or use ``app.dependency_overrides``) with fakes.
"""

from functools import lru_cache

from sec_filings_rag.api.config.company_mappings import COMPANY_TICKER_MAPPINGS
from sec_filings_rag.api.config.settings import get_settings
from sec_filings_rag.api.services.agent import AgentService
from sec_filings_rag.api.services.embeddings import (
    EmbeddingService,
    load_embedding_service,
)
from sec_filings_rag.api.services.groq_compat import create_groq_client
from sec_filings_rag.api.services.rag import RAGService
from sec_filings_rag.api.services.search import SearchService
from sec_filings_rag.api.services.ticker_extractor import TickerExtractor
from sec_filings_rag.vector_store import VectorStore, create_vector_store


@lru_cache
def get_vector_store() -> VectorStore:
    return create_vector_store(get_settings())


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return load_embedding_service(get_settings())


@lru_cache
def get_search_service() -> SearchService:
    return SearchService(
        store=get_vector_store(),
        embedding_service=get_embedding_service(),
    )


@lru_cache
def get_llm_client():
    """Sync instructor-parsed LLM client."""
    import instructor

    settings = get_settings()
    client = create_groq_client(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        fallback_models=settings.llm_fallback_models,
    )
    return instructor.from_groq(client=client, mode=instructor.Mode.JSON)


@lru_cache
def get_plain_llm_client():
    """Sync plain chat client (no structured output)."""
    settings = get_settings()
    return create_groq_client(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        fallback_models=settings.llm_fallback_models,
    )


@lru_cache
def get_async_llm_client():
    """Async instructor-parsed LLM client."""
    import instructor

    settings = get_settings()
    client = create_groq_client(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        fallback_models=settings.llm_fallback_models,
        async_client=True,
    )
    return instructor.from_groq(client=client, mode=instructor.Mode.JSON)


@lru_cache
def get_ticker_extractor() -> TickerExtractor:
    return TickerExtractor(
        client=get_llm_client(),
        settings=get_settings(),
        mappings=COMPANY_TICKER_MAPPINGS,
    )


@lru_cache
def get_rag_service() -> RAGService:
    return RAGService(
        search_service=get_search_service(),
        llm_client=get_plain_llm_client(),
        settings=get_settings(),
    )


@lru_cache
def get_agent_service() -> AgentService:
    return AgentService(
        search_service=get_search_service(),
        llm_client=get_async_llm_client(),
        ticker_extractor=get_ticker_extractor(),
        settings=get_settings(),
    )
