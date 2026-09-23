from fastapi import APIRouter

from sec_filings_rag.api.deps import get_rag_service
from sec_filings_rag.api.models.rag import RAGRequest, RAGResponse

router = APIRouter()


@router.post("/rag", response_model=RAGResponse)
def rag(request: RAGRequest):
    return get_rag_service().generate_answer(request.query, request.limit)
