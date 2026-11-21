from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from sec_filings_rag.api.deps import get_agent_service
from sec_filings_rag.api.models.agent import AgentRequest, AgentResponse
from sec_filings_rag.api.services.agent import AgentService

router = APIRouter()


@router.post("/agent", response_model=AgentResponse)
async def agent(
    request: AgentRequest,
    agent_service: Annotated[AgentService, Depends(get_agent_service)],
):
    try:
        return await agent_service.analyze(request.query, request.limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
