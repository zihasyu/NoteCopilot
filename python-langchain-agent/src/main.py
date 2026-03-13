from .agent import AgentService

# 初始化Agent服务
agent_service = AgentService()

# 示例：添加文档到知识库
print("添加示例文档到知识库...")
agent_service.rag_service.add_document(
    "Milvus是一个开源的向量数据库，专为AI应用设计，支持高效的向量搜索和相似性匹配。",
    {"source": "技术文档", "topic": "向量数据库"}
)

agent_service.rag_service.add_document(
    "LangChain是一个用于构建LLM应用的框架，提供了丰富的组件和工具，简化了AI应用的开发。",
    {"source": "技术文档", "topic": "LLM框架"}
)

# 示例：使用Agent回答问题
print("\n测试Agent回答问题：")
query = "什么是Milvus？"
result = agent_service.run(query)
print(f"问题: {query}")
print(f"回答: {result}")

query = "LangChain有什么作用？"
result = agent_service.run(query)
print(f"\n问题: {query}")
print(f"回答: {result}")
