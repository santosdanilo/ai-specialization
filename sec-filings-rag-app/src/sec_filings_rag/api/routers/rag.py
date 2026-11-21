from typing import Annotated

from fastapi import APIRouter, Depends

from sec_filings_rag.api.deps import get_rag_service
from sec_filings_rag.api.models.rag import RAGRequest, RAGResponse
from sec_filings_rag.api.services.rag import RAGService

router = APIRouter()


@router.post("/rag", response_model=RAGResponse)
def rag(
    request: RAGRequest,
    rag_service: Annotated[RAGService, Depends(get_rag_service)],
):
    return rag_service.generate_answer(request.query, request.limit)
