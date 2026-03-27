
# NoteCopilot

一个基于 **LangGraph + Milvus(RAG) + MCP** 构建的智能笔记助手，实现了“规划-执行-反思”（Plan-Execute-Replan）的 Agent 工作流，用于实验记录检索、论文笔记增强和博客上传。[English](./README.md)

## 架构概览

```
用户查询
    |
    v
+-------------------+      +-------------------+      +-------------------+
|  规划-执行-反思    |----->|   Milvus RAG      |----->|    MCP 工具       |
|  Agent (LangGraph)|      |   (向量检索)       |      |   (搜索/增强/     |
|                   |      |                   |      |    上传)          |
+---------+---------+      +-------------------+      +-------------------+
          |
          v
+-------------------+
|    检查点模块      |
|    (SQLite)       |  <-- 持久化会话记忆
+-------------------+
```

## 核心组件

### 1. 规划-执行-反思 Agent (agent.py)

**工作流:**
1.  **规划器 (Planner)**: 将用户请求分解为可执行的步骤。
2.  **执行器 (Executor)**: 运行每个步骤（如搜索、增强、上传）。
3.  **反思 (Replan)**: 如果需要，重新评估计划。
4.  **响应器 (Responder)**: 生成最终答案。

**状态持久化:** 使用 LangGraph 的 `SqliteSaver` 实现跨会话的长期记忆。

### 2. Milvus RAG 系统 (rag.py)

**处理流程:**
```
Markdown 文件 -> 文本分块 -> BGE 嵌入 -> Milvus 向量数据库
                                    |
用户查询 -> 嵌入 -> 近似最近邻搜索 -> 检索到的上下文
```

-   **文本分块**: 基于段落，限制 500 字符。
-   **嵌入模型**: BAAI/bge-large-zh-v1.5 (中文优化模型)。
-   **索引**: IVF_FLAT，使用 L2 距离计算。

### 3. MCP 工具层 (mcp_tools)

实现模型上下文协议（Model Context Protocol）以标准化工具：
-   `search_notes`: 从向量数据库进行 RAG 检索。
-   `enhance_notes`: 由大语言模型驱动的内容增强。
-   `upload_blog`: 博客发布接口。

### 4. 检查点模块 (sqlite.py)

-   为每个 `thread_id` 存储会话状态。
-   支持多轮对话的上下文保持。
-   支持恢复之前的会话。

## Windows 脚本指南

### 快速启动脚本

| 脚本 | 用途 | 何时使用 |
|---|---|---|
| start.bat | **一键安装并运行** | 首次使用或全新启动 |
| stop.bat | 停止所有服务 | 正常关闭程序 |
| reset.bat | **删除所有数据** | 需要从零开始时（请谨慎操作！） |

### 功能使用脚本

| 脚本 | 用途 | 示例 |
|---|---|---|
| `run.bat chat` | 与 Agent 进行交互式聊天 | `run.bat chat` |
| `run.bat search` | 仅执行直接的 RAG 搜索 | `run.bat search` |
| `run.bat mcp` | 启动 MCP 服务器模式 | `run.bat mcp` |
| ingest.bat | 重新索引 notes 文件夹 | 添加了新的 `.md` 文件后 |

### 安装脚本 (通常不需要直接运行)

| 脚本 | 用途 |
|---|---|
| setup.bat | 安装依赖并启动 Docker |

## 快速开始

### 环境要求

-   Python 3.10+
-   Docker Desktop
-   Git

### 步骤 1: 克隆并进入目录

```bash
git clone https://github.com/zihasyu/NoteCopilot.git
cd NoteCopilot
```

### 步骤 2: 一键启动

```bash
start.bat
```

此脚本将自动完成以下操作:
1.  创建 Python 虚拟环境 (.venv)。
2.  安装所有依赖项。
3.  在 Docker 中启动 Milvus。
4.  创建 .env 文件（你需要稍后填入 API 密钥）。
5.  从 notes 文件夹导入笔记。
6.  启动聊天模式。

### 步骤 3: 添加 API 密钥

当记事本自动打开 .env 文件后，填入你的 API 密钥：

```env
# 选项 1: 阿里云百炼 (通义千问)
DASHSCOPE_API_KEY=你的密钥

# 选项 2: Kimi (月之暗面)
KIMI_API_KEY=你的密钥

# 可选: 更换模型
LLM_MODEL=qwen-max  # 或 kimi 的模型名称
```

保存并关闭记事本，程序将继续运行。

## 使用模式

### 模式 1: 聊天模式 (Agent + RAG)

```bash
run.bat chat
```

**功能:**
-   自然语言查询。
-   自动进行 RAG 检索。
-   带记忆的多轮对话。
-   规划-执行-反思工作流。

**示例会话:**
```
[default] > 找到我关于大模型微调的实验

[INFO] 正在处理...

[Response]
我找到了您在2024年3月15日的实验记录。您在Qwen-7B-Chat上测试了LoRA微调，使用了1万条中文对话样本。结果显示BLEU从0.32提升到了0.45。

[Sources]
  - notes/example-experiment.md (score: 0.23)

[default] > 帮我为博客总结一下

[INFO] 正在处理...

[Response]
这是为您准备的关于LoRA微调实验的博客摘要...
```

**内置命令:**
| 命令 | 操作 |
|---|---|
| `/new <名称>` | 创建一个新的会话线程 |
| `/history` | 列出所有会话线程 |
| `/quit` | 退出程序 |

### 模式 2: 搜索模式 (仅 RAG)

```bash
run.bat search
```

**功能:**
-   直接进行向量搜索。
-   显示原始检索结果。
-   无大语言模型处理。
-   对于简单查找速度更快。

**示例:**
```
[Search] > RLHF

[Results] 找到 3 个匹配项:

--- 结果 1 ---
来源: notes/paper-llm-survey.md
分数: 0.1567
内容: RLHF: 基于人类反馈的强化学习是核心的对齐方法...

--- 结果 2 ---
来源: notes/paper-llm-survey.md
分数: 0.2034
内容: 关键技术: 预训练, SFT, RLHF...
```

### 模式 3: MCP 服务器模式

```bash
run.bat mcp
```

**用途:** 与 Claude Desktop 或其他 MCP 客户端集成。

**在 Claude Desktop 中设置:**
1.  打开 Claude Desktop 设置。
2.  添加 MCP 服务器，命令为: `C:\完整路径\run.bat mcp`。
3.  重启 Claude。

## 管理笔记

### 添加新笔记

1.  将 `.md` 文件复制到 notes 文件夹。
2.  运行: ingest.bat。
3.  新笔记将立即可被搜索。

### 笔记结构

```
notes/
├── experiments/
│   ├── 2024-03-lora-finetune.md
│   └── 2024-04-rag-eval.md
├── papers/
│   ├── llm-survey.md
│   └── attention-is-all-you-need.md
└── ideas/
    └── project-ideas.md
```

### 重新索引

如果你修改了现有笔记：
```bash
# 方案 1: 完全重建索引
reset.bat    # 警告: 这会删除所有数据
start.bat

# 方案 2: 增量更新 (暂未实现, 请使用方案 1)
```

## 服务

运行 start.bat 后，以下服务将可用：

| 服务 | URL | 用途 |
|---|---|---|
| Milvus | `localhost:19530` | 向量数据库 |
| Attu UI | `http://localhost:8000` | Milvus 网页管理界面 |
| MinIO | `localhost:9000` | 对象存储 |

**在 Attu 中查看向量:**
1.  打开 http://localhost:8000。
2.  连接到 `localhost:19530`。
3.  浏览 notes collection。

## 简历亮点映射

| 简历技能点 | 实现文件 | 关键函数 |
|---|---|---|
| LangGraph 规划-执行-反思 Agent | agent.py | `_build_graph()` - 4节点工作流 |
| Docker Milvus + RAG | rag.py + docker-compose.yml | `ingest_notes()` + `search()` |
| MCP 工具层 | tools.py | `@mcp.tool()` 装饰器 |
| 检查点记忆模块 | sqlite.py | `SqliteSaver` + `ConversationMemory` |

## 问题排查

### "Python not found" (找不到 Python)
安装 Python 3.10+ 并勾选 "Add to PATH"。

### "Docker not found" (找不到 Docker)
安装 Docker Desktop 并确保它正在运行。

### Milvus 连接失败
```bash
# 检查 Milvus 是否在运行
docker ps

# 如果没有，重启它
docker-compose down
docker-compose up -d

# 等待 30 秒后重试
```

### 搜索没有结果
```bash
# 检查笔记是否已导入
ingest.bat

# 检查 notes 文件夹中是否有 .md 文件
dir notes\*.md /s
```

### API 错误
1.  检查 .env 文件中是否有有效的 API 密钥。
2.  确认 API 密钥账户有足够余额。
3.  尝试在百炼和 Kimi 之间切换。

## 项目结构

```
NoteCopilot/
├── core/                    # LangGraph Agent 核心
│   ├── state.py            # Agent 状态定义
│   ├── rag.py              # Milvus RAG 实现
│   └── agent.py            # 规划-执行-反思 Agent
├── mcp_tools/              # MCP 工具层
│   ├── tools.py            # 工具定义
│   └── server.py           # MCP 服务器
├── checkpointer/           # 状态持久化
│   └── sqlite.py           # SQLite 检查点模块
├── notes/                  # 你的 Markdown 笔记
├── checkpoints/            # 会话历史记录
├── .venv/                  # Python 虚拟环境
├── docker-compose.yml      # Milvus 部署文件
├── requirements.txt        # Python 依赖
├── *.bat                   # Windows 脚本
└── README.md               # 本文件
```
