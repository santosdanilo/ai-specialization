from functools import lru_cache

from fastapi import FastAPI

from sec_filings_rag.api.config.settings import settings
from sec_filings_rag.api.models import SearchRequest, SearchResponse
from sec_filings_rag.api.routes import router
from sec_filings_rag.api.services.search import SearchService

app = FastAPI(title="SEC Filings RAG")
app.include_router(router)


@lru_cache
def get_search_service() -> SearchService:
    return SearchService(
        qdrant_api_url=settings.qdrant_api_url,
        qdrant_api_key=settings.qdrant_api_key,
        collection_name=settings.collection_name,
    )


@app.post("/search", response_model=SearchResponse)
def search(request: SearchRequest):
    return get_search_service().query(request.query, request.limit)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
