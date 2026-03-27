"""
Plan-Execute-Replan Agent 状态定义
"""
from typing import List, Optional, Annotated
from typing_extensions import TypedDict
import operator


class NoteSource(TypedDict):
    """笔记来源"""
    source: str
    content: str
    score: float


class AgentState(TypedDict):
    """Agent 状态"""
    # 用户输入
    input: str

    # Plan 阶段
    plan: List[str]

    # 执行结果
    past_steps: Annotated[List[tuple], operator.add]

    # 当前执行的步骤
    current_step: Optional[str]

    # RAG 检索结果
    retrieved_notes: List[NoteSource]

    # 最终响应
    response: Optional[str]

    # 对话历史（用于 Checkpointer）
    thread_id: str

    # 是否需要 replan
    replan_needed: bool
