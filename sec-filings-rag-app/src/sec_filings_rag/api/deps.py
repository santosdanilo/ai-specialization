from functools import lru_cache

from sec_filings_rag.api.config.settings import settings
from sec_filings_rag.api.services.rag import RAGService
from sec_filings_rag.api.services.search import SearchService


@lru_cache
def get_search_service() -> SearchService:
    return SearchService(
        qdrant_api_url=settings.qdrant_api_url,
        qdrant_api_key=settings.qdrant_api_key,
        collection_name=settings.collection_name,
    )


@lru_cache
def get_rag_service() -> RAGService:
    return RAGService(
        search_service=get_search_service(),
    )
