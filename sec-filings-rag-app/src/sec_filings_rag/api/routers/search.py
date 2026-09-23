from fastapi import APIRouter

from sec_filings_rag.api.deps import get_search_service
from sec_filings_rag.api.models.search import SearchRequest, SearchResponse

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search(request: SearchRequest):
    return get_search_service().query(request.query, request.limit)
