# Python LangChain Agent Project

这是一个基于LangChain框架的Python项目，实现了MCP（Model, Compute, Platform）架构和RAG（Retrieval-Augmented Generation）功能，使用通义千问作为LLM。

## 项目结构

```
python-langchain-agent/
├── requirements.txt      # 项目依赖
├── .env                 # 环境变量配置
├── docs/                # 文档目录
├── app/                # 应用代码目录
│   ├── __init__.py
│   ├── main.py         # FastAPI 应用入口
│   ├── config.py       # 配置管理
│   ├── agent/          # Agent 相关模块
│   ├── api/            # API 接口
│   │   ├── __init__.py
│   │   ├── chat.py     # 聊天接口
│   │   ├── document.py # 文档管理接口
│   │   └── health.py   # 健康检查接口
│   ├── core/           # 核心模块
│   │   ├── __init__.py
│   │   ├── llm_factory.py      # LLM 工厂
│   │   └── milvus_client.py    # Milvus 客户端
│   ├── models/         # 数据模型
│   ├── services/       # 服务层
│   │   ├── __init__.py
│   │   ├── document_splitter_service.py  # 文档分割服务
│   │   ├── rag_agent_service.py          # RAG Agent 服务
│   │   ├── vector_embedding_service.py   # 向量嵌入服务
│   │   ├── vector_search_service.py      # 向量搜索服务
│   │   └── vector_store_manager.py       # 向量存储管理器
│   ├── tools/          # 工具模块
│   │   ├── __init__.py
│   │   ├── knowledge_tool.py  # 知识检索工具
│   │   └── time_tool.py       # 时间工具
│   └── utils/          # 工具函数
└── README.md           # 项目说明
```

## 功能特性

1. **向量数据库集成**：使用Milvus作为向量存储，支持高效的相似度搜索
2. **RAG能力**：结合检索和生成，提供基于文档的智能回答
3. **Agent系统**：使用LangChain的Agent框架，支持工具调用
4. **文档分割**：智能文档分割，支持Markdown和普通文本
5. **API接口**：提供RESTful API接口
6. **模块化设计**：清晰的分层结构，便于扩展和维护

## 快速开始

### 方式一：使用脚本测试（推荐用于学习和测试）

1. **启动 Milvus 向量数据库**
   ```bash
   # Windows
   start.bat
   
   # 或手动启动
   docker compose -f vector-database.yml up -d
   ```

2. **配置环境变量**
   编辑 `.env` 文件，设置您的 DashScope API Key：
   ```
   DASHSCOPE_API_KEY=your-dashscope-api-key
   ```

3. **运行测试脚本**
   ```bash
   # Windows
   .venv\Scripts\python.exe simple_demo.py
   
   # Linux/Mac
   python simple_demo.py
   ```

4. **停止服务**
   ```bash
   # Windows
   stop.bat
   
   # 或手动停止
   docker compose -f vector-database.yml down
   ```

### 方式二：使用 API 服务（推荐用于生产环境）

1. **启动服务**
   ```bash
   # Windows
   start.bat
   
   # 启动 API 服务
   .venv\Scripts\python.exe -m uvicorn app.main:app --reload
   ```

2. **访问 API 文档**
   打开浏览器访问：`http://localhost:8000/docs`

3. **测试接口**
   - 使用 Swagger UI 测试
   - 或使用 Postman/curl 测试

## 技术栈

- Python 3.8+
- LangChain 框架
- 通义千问 API (DashScope)
- Milvus 向量数据库
- FastAPI
- Pydantic

## 架构设计

本项目参考了Template_python的优秀架构设计，实现了以下模块化结构：

### 核心模块 (Core)
- **LLM Factory**: 使用OpenAI兼容模式调用DashScope，便于切换模型提供商
- **Milvus Client**: 管理Milvus连接和Collection，支持自动创建和索引

### 服务层 (Services)
- **Document Splitter**: 智能文档分割，支持Markdown标题分割和文本分块
- **Vector Embedding**: 实现LangChain标准Embeddings接口
- **Vector Search**: 从Milvus中搜索相似向量
- **Vector Store Manager**: 管理文档的向量化和存储
- **RAG Agent**: 基于LangChain的智能代理

### 工具层 (Tools)
- **Knowledge Tool**: 从向量数据库中检索相关信息
- **Time Tool**: 获取当前时间信息

### API层 (API)
- **Chat API**: 提供对话接口
- **Document API**: 提供文档管理接口
- **Health API**: 提供系统健康状态接口

## 安装与配置

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   编辑 `.env` 文件，填写您的API密钥和配置信息：
   ```
   # DashScope API Key
   DASHSCOPE_API_KEY=your-dashscope-api-key
   
   # 应用配置
   APP_NAME=LangChainAgent
   APP_VERSION=1.0.0
   DEBUG=true
   HOST=0.0.0.0
   PORT=8000
   
   # Milvus Configuration
   MILVUS_HOST=localhost
   MILVUS_PORT=19530
   MILVUS_TIMEOUT=10000
   
   # Qwen Configuration
   QWEN_MODEL=qwen-max
   DASHSCOPE_EMBEDDING_MODEL=text-embedding-v3
   
   # RAG Configuration
   RAG_TOP_K=3
   RAG_MODEL=qwen-max
   
   # Document Chunk Configuration
   CHUNK_MAX_SIZE=800
   CHUNK_OVERLAP=100
   ```

3. **启动Milvus服务**
   确保Milvus服务已经启动并运行在配置的主机和端口上。

4. **添加文档**
   将您的文档放入 `docs` 目录，支持 `.md` 格式的文件。

## 使用方法

### 启动API服务

```bash
uvicorn app.main:app --reload
```

API接口将在 `http://localhost:8000` 可用，可访问 `http://localhost:8000/docs` 查看API文档。

### API接口说明

#### 1. 聊天接口
- `POST /api/chat/query`: 使用Agent回答问题

#### 2. 文档管理接口
- `POST /api/documents/add`: 添加文档到知识库
- `POST /api/documents/upload`: 上传文档文件到知识库
- `DELETE /api/documents/clear`: 清空知识库
- `GET /api/documents/count`: 获取知识库中的文档数量

#### 3. 健康检查接口
- `GET /api/health/`: 系统健康检查

### 核心功能

1. **添加文档**：通过API添加文档到知识库
2. **查询问题**：通过API使用Agent回答问题
3. **RAG查询**：自动检索相关文档并生成回答
4. **文档分割**：智能分割文档，提高检索效果

## 扩展与定制

- **添加新工具**：在 `app/tools` 目录中创建新的工具模块
- **添加新服务**：在 `app/services` 目录中创建新的服务模块
- **更换模型**：在 `.env` 文件中修改 `QWEN_MODEL` 配置
- **调整向量数据库**：在 `app/core/milvus_client.py` 中修改向量数据库相关代码
- **扩展API**：在 `app/api` 目录中添加新的API端点

## MCP架构说明

- **Model**：使用通义千问模型作为核心AI模型
- **Compute**：LangChain框架提供计算能力，包括RAG、Agent等
- **Platform**：Python应用和FastAPI提供运行平台和接口

## 设计特点

1. **模块化设计**：清晰的分层结构，各模块职责明确
2. **可扩展性**：易于添加新的工具、服务和API接口
3. **类型安全**：使用Pydantic进行数据验证
4. **配置管理**：使用Pydantic Settings进行类型安全的配置管理
5. **错误处理**：完善的异常处理和日志记录
6. **性能优化**：批量处理、连接池等优化措施

## 注意事项

- 需要有效的DashScope API密钥
- 需要运行中的Milvus服务
- 首次运行时会自动创建Milvus集合和索引
- 支持Markdown和普通文本文档的自动分割
- 文档分割会自动合并过小的分片，提高检索效果
