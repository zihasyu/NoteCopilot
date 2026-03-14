"""聊天API - 提供对话接口"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.rag_agent_service import rag_agent_service

router = APIRouter(prefix="/api/chat", tags=["聊天"])


class ChatRequest(BaseModel):
    """聊天请求模型"""
    question: str


class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str


@router.post("/query", response_model=ChatResponse)
async def query_chat(request: ChatRequest):
    """
    使用 Agent 回答问题
    
    Args:
        request: 聊天请求
        
    Returns:
        ChatResponse: 聊天响应
    """
    try:
        result = rag_agent_service.query(request.question)
        return ChatResponse(response=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
