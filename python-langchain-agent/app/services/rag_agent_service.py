"""RAG Agent 服务 - 基于 LangChain 的智能代理"""

from typing import List

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from app.config import config
from app.core.llm_factory import llm_factory
from app.tools import get_current_time, retrieve_knowledge


class RagAgentService:
    """RAG Agent 服务 - 使用 LangChain + OpenAI 兼容模式"""

    def __init__(self):
        """初始化 RAG Agent 服务"""
        self.model_name = config.rag_model
        self.system_prompt = self._build_system_prompt()

        # 创建 LLM 实例
        self.model = llm_factory.create_chat_model(
            model=self.model_name,
            temperature=0.7,
            streaming=False,
        )

        # 定义基础工具
        self.tools = [retrieve_knowledge, get_current_time]

        # 创建 Agent
        self.agent = self._create_agent()

        print(f"RAG Agent 服务初始化完成, model={self.model_name}")

    def _create_agent(self) -> AgentExecutor:
        """创建 Agent"""
        # 定义提示模板
        prompt = PromptTemplate.from_template(
            self.system_prompt + "\n\n"
            "工具列表:\n{tools}\n\n"
            "工具名称: {tool_names}\n\n"
            "使用以下格式:\n"
            "Question: 你需要回答的输入问题\n"
            "Thought: 你应该始终思考要做什么\n"
            "Action: 要采取的行动，应该是 [{tool_names}] 中的一个\n"
            "Action Input: 行动的输入\n"
            "Observation: 行动的结果\n"
            "... (这个 Thought/Action/Action Input/Observation 可以重复 N 次)\n"
            "Thought: 我现在知道最终答案了\n"
            "Final Answer: 对原始输入问题的最终答案\n\n"
            "开始!\n\n"
            "Question: {input}\n"
            "Thought: {agent_scratchpad}"
        )

        # 创建 ReAct Agent
        agent = create_react_agent(
            llm=self.model,
            tools=self.tools,
            prompt=prompt,
        )

        # 创建 Agent 执行器
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
        )

        return agent_executor

    def _build_system_prompt(self) -> str:
        """
        构建系统提示词

        Returns:
            str: 系统提示词
        """
        return """你是一个专业的AI助手，能够使用多种工具来帮助用户解决问题。

工作原则:
1. 理解用户需求，选择合适的工具来完成任务
2. 当需要获取实时信息或专业知识时，主动使用相关工具
3. 基于工具返回的结果提供准确、专业的回答
4. 如果工具无法提供足够信息，请诚实地告知用户

回答要求:
- 保持友好、专业的语气
- 回答简洁明了，重点突出
- 基于事实，不编造信息
- 如有不确定的地方，明确说明

请根据用户的问题，灵活使用可用工具，提供高质量的帮助。"""

    def query(self, question: str) -> str:
        """
        处理用户问题

        Args:
            question: 用户问题

        Returns:
            str: 完整答案
        """
        try:
            print(f"RAG Agent 收到查询: {question}")

            # 调用 Agent
            result = self.agent.invoke({"input": question})

            # 提取最终答案
            answer = result.get("output", "")

            print(f"RAG Agent 查询完成")
            return answer

        except Exception as e:
            print(f"RAG Agent 查询失败: {e}")
            raise RuntimeError(f"查询失败: {e}") from e


# 全局单例
rag_agent_service = RagAgentService()
