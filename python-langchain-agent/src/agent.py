from langchain.agents import AgentType, initialize_agent, Tool
from langchain_openai import ChatOpenAI
from .rag_service import RagService
from .config import Config

class AgentService:
    def __init__(self):
        # 初始化LLM
        self.llm = ChatOpenAI(
            model="gpt-4",
            api_key=Config.OPENAI_API_KEY
        )
        
        # 初始化RAG服务
        self.rag_service = RagService()
        
        # 创建工具
        self.tools = self._create_tools()
        
        # 初始化Agent
        self.agent = self._create_agent()
    
    def _create_tools(self):
        """创建工具列表"""
        tools = [
            Tool(
                name="RAG查询",
                func=self.rag_service.query,
                description="用于回答需要基于文档知识的问题。当用户的问题需要专业知识或具体信息时使用。"
            ),
            Tool(
                name="添加文档",
                func=self.rag_service.add_document,
                description="用于向知识库中添加新的文档。当需要更新知识库时使用。"
            )
        ]
        return tools
    
    def _create_agent(self):
        """创建Agent"""
        agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        return agent
    
    def run(self, query):
        """运行Agent处理查询"""
        result = self.agent.run(query)
        return result
