from langchain.agents import AgentType, initialize_agent, Tool
from langchain_community.chat_models import ChatDashScope
from .rag_service import RagService
from .config import Config
from .skills.document_skill import DocumentSkill

class AgentService:
    def __init__(self):
        # 初始化LLM
        self.llm = ChatDashScope(
            model=Config.QWEN_MODEL,
            dashscope_api_key=Config.DASHSCOPE_API_KEY
        )
        
        # 初始化RAG服务
        self.rag_service = RagService()
        
        # 初始化技能
        self.skills = self._init_skills()
        
        # 创建工具
        self.tools = self._create_tools()
        
        # 初始化Agent
        self.agent = self._create_agent()
    
    def _init_skills(self):
        """初始化技能"""
        skills = {
            "document": DocumentSkill(self.rag_service)
        }
        return skills
    
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
        
        # 添加技能中的工具
        for skill_name, skill in self.skills.items():
            tools.extend(skill.get_tools())
        
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
