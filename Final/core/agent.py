"""
LangGraph Plan-Execute-Replan Agent 协作流
实现：实验记录检索、论文笔记增强生成、个人博客上传
"""
import os
import json
from typing import List, Literal, Optional
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from .state import AgentState
from .rag import NoteRAG


class NoteCopilotAgent:
    """Plan-Execute-Replan Agent"""

    def __init__(self, rag: NoteRAG, checkpointer=None):
        self.rag = rag
        self.checkpointer = checkpointer

        # 支持阿里云百炼 (通义千问) 或 Kimi API
        base_url = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("KIMI_API_KEY")
        model = os.getenv("LLM_MODEL", "qwen-max")

        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=0.7
        )

        # 构建 Graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """构建 Plan-Execute-Replan 工作流"""
        workflow = StateGraph(AgentState)

        # 添加节点
        workflow.add_node("planner", self._planner)
        workflow.add_node("executor", self._executor)
        workflow.add_node("replan", self._replan)
        workflow.add_node("responder", self._responder)

        # 设置入口
        workflow.set_entry_point("planner")

        # 添加边
        workflow.add_edge("planner", "executor")
        workflow.add_conditional_edges(
            "executor",
            self._should_replan,
            {
                "replan": "replan",
                "respond": "responder"
            }
        )
        workflow.add_edge("replan", "executor")
        workflow.add_edge("responder", END)

        return workflow.compile(checkpointer=self.checkpointer)

    def _planner(self, state: AgentState) -> dict:
        """规划阶段：分解任务"""
        prompt = f"""你是一个科研助手。请将用户请求分解为可执行的步骤。

可用工具：
1. search_notes(query) - 检索实验记录和论文笔记
2. enhance_notes(content) - 增强生成论文摘要或实验总结
3. upload_blog(title, content) - 上传个人博客

用户请求: {state['input']}

请以 JSON 格式返回执行计划，每个步骤包含工具名称和参数：
{{
    "plan": [
        "search_notes: 检索相关实验记录",
        "enhance_notes: 基于检索结果生成增强内容",
        ...
    ]
}}"""

        response = self.llm.invoke([SystemMessage(content=prompt)])

        try:
            plan_data = json.loads(response.content)
            plan = plan_data.get("plan", [])
        except:
            # 解析失败时创建简单计划
            plan = ["search_notes: 检索相关笔记", "enhance_notes: 增强生成内容"]

        return {
            "plan": plan,
            "current_step": plan[0] if plan else None,
            "past_steps": [],
            "replan_needed": False
        }

    def _executor(self, state: AgentState) -> dict:
        """执行阶段：执行当前步骤"""
        step = state["current_step"]
        if not step:
            return {"replan_needed": False}

        # 解析工具调用
        if "search_notes" in step.lower():
            # 提取查询关键词
            query = state["input"]
            notes = self.rag.search(query, top_k=3)
            result = f"检索到 {len(notes)} 条相关笔记"
            retrieved = notes

        elif "enhance_notes" in step.lower():
            # 基于检索结果增强生成
            context = "\n\n".join([
                f"[来自 {n['source']}]\n{n['content']}"
                for n in state.get("retrieved_notes", [])
            ])
            prompt = f"""基于以下笔记内容，生成一份增强的实验报告或论文摘要：

{context}

用户需求: {state['input']}
"""
            response = self.llm.invoke([HumanMessage(content=prompt)])
            result = response.content
            retrieved = state.get("retrieved_notes", [])

        elif "upload_blog" in step.lower():
            # 模拟博客上传
            title = f"笔记整理 - {datetime.now().strftime('%Y-%m-%d')}"
            content = state.get("past_steps", [])[-1][1] if state.get("past_steps") else ""
            # 实际项目中这里调用博客 API
            result = f"博客 '{title}' 已准备上传（Demo 模式）"
            retrieved = state.get("retrieved_notes", [])

        else:
            result = "未知步骤"
            retrieved = state.get("retrieved_notes", [])

        # 更新已执行步骤
        past_steps = state.get("past_steps", []) + [(step, result)]

        # 获取下一步
        plan = state.get("plan", [])
        current_idx = plan.index(step) if step in plan else -1
        next_step = plan[current_idx + 1] if current_idx >= 0 and current_idx + 1 < len(plan) else None

        return {
            "past_steps": past_steps,
            "current_step": next_step,
            "retrieved_notes": retrieved,
            "replan_needed": False
        }

    def _replan(self, state: AgentState) -> dict:
        """重新规划阶段"""
        prompt = f"""基于已执行的结果，重新评估计划：

原始请求: {state['input']}
已执行步骤: {state['past_steps']}

请判断是否需要调整计划，以 JSON 格式返回：
{{
    "replan_needed": true/false,
    "new_steps": ["步骤1", "步骤2", ...]
}}"""

        response = self.llm.invoke([SystemMessage(content=prompt)])

        try:
            data = json.loads(response.content)
            replan_needed = data.get("replan_needed", False)
            new_steps = data.get("new_steps", [])
        except:
            replan_needed = False
            new_steps = []

        if replan_needed and new_steps:
            return {
                "plan": new_steps,
                "current_step": new_steps[0],
                "replan_needed": False
            }

        return {"replan_needed": False}

    def _responder(self, state: AgentState) -> dict:
        """生成最终响应"""
        history = "\n\n".join([
            f"步骤: {step}\n结果: {result}"
            for step, result in state.get("past_steps", [])
        ])

        prompt = f"""基于以下执行历史，生成最终回答：

{history}

请以清晰、专业的方式总结结果。"""

        response = self.llm.invoke([HumanMessage(content=prompt)])

        return {"response": response.content}

    def _should_replan(self, state: AgentState) -> Literal["replan", "respond"]:
        """判断是否继续执行或重新规划"""
        if state.get("replan_needed"):
            return "replan"

        if state.get("current_step"):
            return "replan"  # 还有步骤要执行

        return "respond"

    def invoke(self, query: str, thread_id: str = None) -> dict:
        """执行查询"""
        config = {"configurable": {"thread_id": thread_id or "default"}}

        result = self.graph.invoke({
            "input": query,
            "thread_id": thread_id or "default"
        }, config=config)

        return result

    def get_state(self, thread_id: str) -> Optional[dict]:
        """获取对话状态（用于长程多轮交互）"""
        config = {"configurable": {"thread_id": thread_id}}
        return self.graph.get_state(config)
