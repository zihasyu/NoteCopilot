# NoteCopilot

> 基于 LangGraph 的智能笔记助手 - Plan-Execute-Replan Agent 实现实验记录检索、论文笔记增强生成、个人博客上传

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-latest-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/zihasyu/NoteCopilot)

## ✨ 核心特性

- 🤖 **智能任务编排** - 基于 LangGraph 的 Plan-Execute-Replan 协作流
- 📚 **实验记录检索** - 从 Markdown 笔记库中智能检索实验记录
- 📝 **论文笔记增强** - 自动生成摘要、优化格式、推荐相关论文
- 🌐 **博客自动发布** - 一键生成模板、预览效果、上传至个人博客
- 🔍 **RAG 知识库** - Milvus 向量数据库 + 文档分块与 Embedding
- 🔌 **MCP 工具集成** - 标准化 Tool 接入层，支持工具扩展
- 💾 **对话状态持久** - Checkpointer 实现长程多轮交互上下文记忆

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                        NoteCopilot                              │
│                   (FastAPI + LangGraph)                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Planner    │→│   Executor   │→│  Replanner   │         │
│  │  (制定计划)   │  │  (执行步骤)   │  │  (重规划)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         ↑                                    │                  │
│         └────────────────────────────────────┘                  │
├─────────────────────────────────────────────────────────────────┤
│                      MCP Tool Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  NoteSearch  │  │PaperEnhance  │  │ BlogUpload   │         │
│  │  笔记检索     │  │ 论文增强     │  │ 博客发布     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
├─────────────────────────────────────────────────────────────────┤
│                        RAG Layer                                │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Milvus Vector DB  +  Markdown Chunking  +  Embedding  │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ 技术栈

- **框架**: FastAPI + LangGraph + LangChain
- **LLM**: 阿里云 DashScope (通义千问)
- **向量库**: Milvus (Docker 部署)
- **工具协议**: MCP (Model Context Protocol)
- **状态持久**: LangGraph MemorySaver (Checkpointer)

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Docker Desktop
- 阿里云 DashScope API Key ([获取地址](https://dashscope.aliyun.com/))

### 安装和启动

#### 1. 克隆项目

```bash
git clone https://github.com/zihasyu/NoteCopilot.git
cd NoteCopilot
```

#### 2. 安装依赖

```bash
# 使用 uv（推荐，更快）
pip install uv
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .

# 或使用 pip
pip install -e .
```

#### 3. 配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env，填入你的 DASHSCOPE_API_KEY
vim .env
```

#### 4. 启动服务

**Windows:**
```powershell
.\start-windows.bat
```

**Linux/macOS:**
```bash
make start
```

**手动启动:**
```bash
# 1. 启动 Milvus
docker compose -f vector-database.yml up -d

# 2. 启动 MCP 服务（各开一个新终端）
python mcp_servers/note_search_server.py
python mcp_servers/paper_enhance_server.py
python mcp_servers/blog_upload_server.py

# 3. 启动主服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 9900

# 4. 上传示例笔记到向量库
python -c "import requests, os, time; [requests.post('http://localhost:9900/api/upload', files={'file': open(f'notes/{dir}/{f}', 'rb')}) or time.sleep(1) for dir in ['experiments', 'papers'] for f in os.listdir(f'notes/{dir}') if f.endswith('.md')]"
```

### 访问服务

- **Web 界面**: http://localhost:9900
- **API 文档**: http://localhost:9900/docs

## 📡 API 接口

### 核心接口

| 功能 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 智能助手 | POST | `/api/assist` | Plan-Execute-Replan 任务执行（流式） |
| 普通对话 | POST | `/api/chat` | 一次性返回 |
| 流式对话 | POST | `/api/chat_stream` | SSE 流式输出 |
| 文件上传 | POST | `/api/upload` | 上传 Markdown 文档到向量库 |
| 健康检查 | GET | `/api/health` | 服务状态检查 |

### 使用示例

```bash
# 实验记录检索
curl -X POST "http://localhost:9900/api/assist" \
  -H "Content-Type: application/json" \
  -d '{"session_id":"session-123", "query":"搜索LoRA相关实验记录"}' \
  --no-buffer

# 论文笔记增强
curl -X POST "http://localhost:9900/api/assist" \
  -H "Content-Type: application/json" \
  -d '{"session_id":"session-124", "query":"帮我增强Attention Is All You Need的论文笔记，生成结构化摘要"}' \
  --no-buffer

# 博客发布
curl -X POST "http://localhost:9900/api/assist" \
  -H "Content-Type: application/json" \
  -d '{"session_id":"session-125", "query":"将LoRA实验记录整理成博客文章并发布"}' \
  --no-buffer
```

## 📁 项目结构

```
NoteCopilot/
├── app/                                    # 应用核心
│   ├── __init__.py
│   ├── main.py                             # FastAPI 应用入口
│   ├── config.py                           # 配置管理
│   ├── api/                                # API 路由层
│   │   ├── chat.py                         # 对话接口
│   │   ├── aiops.py                        # NoteCopilot 助手接口
│   │   ├── file.py                         # 文件上传接口
│   │   └── health.py                       # 健康检查
│   ├── services/                           # 业务服务层
│   │   ├── aiops_service.py                # Plan-Execute-Replan 服务
│   │   ├── rag_agent_service.py            # RAG Agent
│   │   ├── vector_store_manager.py         # 向量存储管理
│   │   └── ...
│   ├── agent/                              # Agent 模块
│   │   ├── mcp_client.py                   # MCP 客户端
│   │   └── aiops/                          # Plan-Execute-Replan 核心
│   │       ├── planner.py                  # 计划制定器
│   │       ├── executor.py                 # 步骤执行器
│   │       ├── replanner.py                # 重规划器
│   │       └── state.py                    # 状态定义
│   ├── tools/                              # Agent 工具集
│   │   └── knowledge_tool.py               # RAG 知识检索
│   └── core/                               # 核心组件
│       ├── llm_factory.py                  # LLM 工厂
│       └── milvus_client.py                # Milvus 客户端
├── mcp_servers/                            # MCP 工具服务
│   ├── note_search_server.py               # 笔记检索服务 (8003)
│   ├── paper_enhance_server.py             # 论文增强服务 (8004)
│   └── blog_upload_server.py               # 博客上传服务 (8005)
├── notes/                                  # 示例笔记库
│   ├── experiments/                        # 实验记录
│   │   ├── llm-lora-finetuning.md
│   │   └── rag-performance-optimization.md
│   └── papers/                             # 论文笔记
│       ├── attention-is-all-you-need.md
│       └── lora-low-rank-adaptation.md
├── static/                                 # Web 前端
├── vector-database.yml                     # Milvus Docker Compose
├── pyproject.toml                          # 项目配置
└── README.md                               # 项目说明
```

## 🎯 Plan-Execute-Replan 工作流

```
用户输入查询
    ↓
┌─────────────┐
│   Planner   │  制定执行计划（基于可用工具）
└─────────────┘
    ↓
┌─────────────┐
│   Executor  │  执行计划中的第一个步骤
│  (调用工具)  │
└─────────────┘
    ↓
┌─────────────┐
│  Replanner  │  评估执行结果
│             │  → continue: 继续执行
│             │  → replan:   调整计划
│             │  → respond:  生成最终响应
└─────────────┘
    ↓
循环执行直到生成最终响应
```

## 🔧 配置说明

通过 `.env` 文件配置：

```bash
# 阿里云 DashScope 配置（必填）
DASHSCOPE_API_KEY=your-api-key
DASHSCOPE_MODEL=qwen-max
DASHSCOPE_EMBEDDING_MODEL=text-embedding-v4

# Milvus 配置
MILVUS_HOST=localhost
MILVUS_PORT=19530

# RAG 配置
RAG_TOP_K=3
CHUNK_MAX_SIZE=800
CHUNK_OVERLAP=100

# MCP 服务配置
MCP_NOTE_SEARCH_URL=http://localhost:8003/mcp
MCP_PAPER_ENHANCE_URL=http://localhost:8004/mcp
MCP_BLOG_UPLOAD_URL=http://localhost:8005/mcp
```

## 📝 MCP 工具服务

### NoteSearch Server (端口 8003)

**功能**: 实验记录和论文笔记搜索

| 工具 | 说明 |
|------|------|
| `search_notes` | 关键词搜索笔记 |
| `get_note_detail` | 获取笔记详情 |
| `list_recent_notes` | 获取最近更新 |
| `get_related_notes` | 相关笔记推荐 |

### PaperEnhance Server (端口 8004)

**功能**: 论文笔记增强和格式化

| 工具 | 说明 |
|------|------|
| `generate_paper_summary` | 生成结构化摘要 |
| `enhance_note_format` | 优化笔记格式 |
| `suggest_related_papers` | 推荐相关论文 |
| `generate_citation_format` | 生成引用格式 |
| `analyze_experiment_data` | 分析实验数据 |

### BlogUpload Server (端口 8005)

**功能**: 博客文章发布管理

| 工具 | 说明 |
|------|------|
| `upload_blog_post` | 发布博客文章 |
| `update_blog_post` | 更新博客文章 |
| `generate_blog_template` | 生成博客模板 |
| `preview_blog_post` | 预览博客效果 |
| `get_published_stats` | 发布统计信息 |

## 🐛 常见问题

### Milvus 连接失败

```bash
# 检查 Milvus 状态
docker ps | grep milvus

# 重启 Milvus
docker compose -f vector-database.yml restart
```

### MCP 服务无法连接

```bash
# 检查端口占用
# Windows:
netstat -ano | findstr :8003
# Linux/macOS:
lsof -i :8003

# 重新启动 MCP 服务
python mcp_servers/note_search_server.py
```

## 📚 参考资源

- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [LangGraph Plan-Execute 教程](https://langchain-ai.github.io/langgraph/tutorials/plan-and-execute/)
- [MCP 协议](https://modelcontextprotocol.io/)
- [Milvus 文档](https://milvus.io/docs)
- [阿里云 DashScope](https://dashscope.aliyun.com/)

## 📄 许可证

[MIT License](LICENSE)

作者: [zihasyu](https://github.com/zihasyu)

开源地址: https://github.com/zihasyu/NoteCopilot
