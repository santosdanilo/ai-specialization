from typing import Annotated

from fastapi import APIRouter, Depends

from sec_filings_rag.api.deps import get_search_service
from sec_filings_rag.api.models.search import SearchRequest, SearchResponse
from sec_filings_rag.api.services.search import SearchService

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search(
    request: SearchRequest,
    search_service: Annotated[SearchService, Depends(get_search_service)],
):
    return search_service.query(request.query, request.limit, request.filter)
