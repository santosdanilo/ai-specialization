from fastapi import APIRouter, HTTPException

from sec_filings_rag.api.deps import get_search_service
from sec_filings_rag.api.models.agent import AgentRequest, AgentResponse
from sec_filings_rag.api.services.agent import AgentService

router = APIRouter()

agent_service = AgentService(search_service=get_search_service())


@router.post("/agent", response_model=AgentResponse)
async def agent(request: AgentRequest):
    try:
        return await agent_service.analyze(request.query, request.limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
