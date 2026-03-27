"""
NoteCopilot 请求和响应模型
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class NoteCopilotRequest(BaseModel):
    """NoteCopilot 智能笔记助手请求"""

    session_id: Optional[str] = Field(
        default="default",
        description="会话ID，用于追踪对话历史"
    )

    query: Optional[str] = Field(
        default="",
        description="用户查询/任务描述，例如：搜索LoRA实验记录、生成论文摘要、发布博客文章"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session-123",
                "query": "搜索LoRA相关实验记录并生成博客文章"
            }
        }


class NoteSearchResult(BaseModel):
    """笔记搜索结果"""
    note_id: str
    title: str
    type: str
    tags: List[str]
    score: float
    preview: str


class AssistResponse(BaseModel):
    """智能助手响应（非流式）"""

    code: int = 200
    message: str = "success"
    data: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "success",
                "data": {
                    "status": "completed",
                    "task": "搜索LoRA实验记录",
                    "result": {
                        "found_notes": 2,
                        "notes": [
                            {"note_id": "exp_001", "title": "LLM微调实验记录 - LoRA方法"}
                        ]
                    }
                }
            }
        }
