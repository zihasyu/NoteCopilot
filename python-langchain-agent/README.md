# Python LangChain Agent Project

这是一个基于LangChain框架的Python项目，实现了MCP（Model, Compute, Platform）架构和RAG（Retrieval-Augmented Generation）功能。

## 项目结构

```
python-langchain-agent/
├── requirements.txt      # 项目依赖
├── .env                 # 环境变量配置
├── src/                # 源代码目录
│   ├── __init__.py
│   ├── config.py       # 配置管理
│   ├── vector_service.py  # 向量数据库服务
│   ├── rag_service.py    # RAG服务
│   ├── agent.py        # Agent服务
│   └── main.py         # 主应用
└── README.md           # 项目说明
```

## 功能特性

1. **向量数据库集成**：使用Milvus作为向量存储，支持高效的相似度搜索
2. **RAG能力**：结合检索和生成，提供基于文档的智能回答
3. **Agent系统**：使用LangChain的Agent框架，支持工具调用
4. **模块化设计**：清晰的分层结构，便于扩展和维护

## 技术栈

- Python 3.8+
- LangChain 框架
- OpenAI API
- Milvus 向量数据库

## 安装与配置

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   编辑 `.env` 文件，填写您的API密钥和配置信息：
   ```
   # OpenAI API Key
   OPENAI_API_KEY=your-openai-api-key
   
   # Milvus Configuration
   MILVUS_HOST=localhost
   MILVUS_PORT=19530
   MILVUS_COLLECTION=langchain_rag
   
   # Embedding Model
   EMBEDDING_MODEL=text-embedding-3-small
   ```

3. **启动Milvus服务**
   确保Milvus服务已经启动并运行在配置的主机和端口上。

## 使用方法

### 运行示例

```bash
python -m src.main
```

### 核心功能

1. **添加文档**：使用 `rag_service.add_document()` 方法向知识库添加文档
2. **查询问题**：使用 `agent.run()` 方法通过Agent回答问题
3. **RAG查询**：使用 `rag_service.query()` 方法直接进行RAG查询

## 扩展与定制

- **添加新工具**：在 `agent.py` 中添加新的Tool对象
- **更换嵌入模型**：在 `.env` 文件中修改 `EMBEDDING_MODEL` 配置
- **调整向量数据库**：在 `vector_service.py` 中修改向量数据库相关代码

## 注意事项

- 需要有效的OpenAI API密钥
- 需要运行中的Milvus服务
- 首次运行时会自动创建Milvus集合和索引
