# NoteCopilot

An intelligent notes assistant built with **LangGraph + Milvus + MCP**, implementing Plan-Execute-Replan Agent workflow for experiment records retrieval, paper notes enhancement, and blog uploading.

## Architecture Overview

```
User Query
    |
    v
+-------------------+      +-------------------+      +-------------------+
|  Plan-Execute-    |----->|   Milvus RAG      |----->|   MCP Tools       |
|  Replan Agent     |      |   (Vector Search) |      |   (search/        |
|   (LangGraph)     |      |                   |      |    enhance/       |
+---------+---------+      +-------------------+      |    upload)        |
          |                                           +-------------------+
          v
+-------------------+
|  Checkpointer     |
|  (SQLite)         |  <-- Persistent conversation memory
+-------------------+
```

## Core Components

### 1. Plan-Execute-Replan Agent (`core/agent.py`)

**Workflow:**
1. **Planner**: Breaks user request into executable steps
2. **Executor**: Runs each step (search/enhance/upload)
3. **Replan**: Re-evaluates plan if needed
4. **Responder**: Generates final answer

**State Persistence:** Uses LangGraph's SqliteSaver for long-term memory across sessions.

### 2. Milvus RAG System (`core/rag.py`)

**Pipeline:**
```
Markdown Files -> Chunking -> BGE Embedding -> Milvus Vector DB
                                      |
User Query -> Embedding -> ANN Search -> Retrieved Context
```

- **Chunking**: Paragraph-based with 500 char limit
- **Embedding**: BAAI/bge-large-zh-v1.5 (Chinese-optimized)
- **Index**: IVF_FLAT with L2 distance

### 3. MCP Tool Layer (`mcp_tools/`)

Implements Model Context Protocol for tool standardization:
- `search_notes`: RAG retrieval from vector DB
- `enhance_notes`: LLM-powered content enhancement
- `upload_blog`: Blog publishing interface

### 4. Checkpointer (`checkpointer/sqlite.py`)

- Stores conversation state per thread_id
- Enables multi-turn context retention
- Supports resuming previous sessions

## Windows Scripts Guide

### Quick Start Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `start.bat` | **One-click setup + run** | First time or clean start |
| `stop.bat` | Stop all services | Shut down gracefully |
| `reset.bat` | **Delete all data** | Start fresh (careful!) |

### Usage Scripts

| Script | Purpose | Example |
|--------|---------|---------|
| `run.bat chat` | Interactive chat with Agent | `run.bat chat` |
| `run.bat search` | Direct RAG search only | `run.bat search` |
| `run.bat mcp` | MCP server mode | `run.bat mcp` |
| `ingest.bat` | Re-index notes folder | After adding new .md files |

### Setup Scripts (Usually not needed directly)

| Script | Purpose |
|--------|---------|
| `setup.bat` | Install dependencies + start Docker |

## Quick Start

### Prerequisites

- Python 3.10+
- Docker Desktop
- Git

### Step 1: Clone and Enter Directory

```bash
git clone https://github.com/zihasyu/NoteCopilot.git
cd NoteCopilot
```

### Step 2: One-Click Start

```bash
start.bat
```

This will:
1. Create Python virtual environment (`.venv/`)
2. Install all dependencies
3. Start Milvus in Docker
4. Create `.env` file (you'll add API keys)
5. Import notes from `notes/` folder
6. Launch chat mode

### Step 3: Add API Keys

When Notepad opens with `.env`, add:

```env
# Option 1: Aliyun DashScope (Tongyi Qianwen)
DASHSCOPE_API_KEY=your-key-here

# Option 2: Kimi (Moonshot)
KIMI_API_KEY=your-key-here

# Optional: Change model
LLM_MODEL=qwen-max  # or kimi model name
```

Save and close Notepad, the chat will continue.

## Usage Modes

### Mode 1: Chat Mode (Agent + RAG)

```bash
run.bat chat
```

**Features:**
- Natural language queries
- Automatic RAG retrieval
- Multi-turn conversations with memory
- Plan-Execute-Replan workflow

**Example Session:**
```
[default] > find my experiments about LLM fine-tuning

[INFO] Processing...

[Response]
I found your experiment record from March 15, 2024. You tested LoRA fine-tuning on Qwen-7B-Chat with 10k Chinese dialogue samples. Results showed BLEU improved from 0.32 to 0.45.

[Sources]
  - notes/example-experiment.md (score: 0.23)

[default] > summarize it for my blog

[INFO] Processing...

[Response]
Here's a blog-ready summary of your LoRA fine-tuning experiment...
```

**Built-in Commands:**
| Command | Action |
|---------|--------|
| `/new <name>` | Create new conversation thread |
| `/history` | List all conversation threads |
| `/quit` | Exit program |

### Mode 2: Search Mode (RAG Only)

```bash
run.bat search
```

**Features:**
- Direct vector search
- Shows raw retrieval results
- No LLM processing
- Faster for simple lookups

**Example:**
```
[Search] > RLHF

[Results] Found 3 matches:

--- Result 1 ---
Source: notes/paper-llm-survey.md
Score: 0.1567
Content: RLHF: Reinforcement Learning from Human Feedback is the core alignment method...

--- Result 2 ---
Source: notes/paper-llm-survey.md
Score: 0.2034
Content: Key techniques: Pre-training, SFT, RLHF...
```

### Mode 3: MCP Server Mode

```bash
run.bat mcp
```

**Purpose:** Integrate with Claude Desktop or other MCP clients.

**Setup in Claude Desktop:**
1. Open Claude Desktop Settings
2. Add MCP server with command: `C:ull/path	oun.bat mcp`
3. Restart Claude

## Managing Notes

### Adding New Notes

1. Copy `.md` files to `notes/` folder
2. Run: `ingest.bat`
3. New notes are immediately searchable

### Notes Structure

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

### Re-indexing

If you modify existing notes:
```bash
# Option 1: Just re-index
reset.bat    # Warning: deletes all data
start.bat

# Option 2: Incremental (not implemented, use Option 1)
```

## Services

After `start.bat`, these services are available:

| Service | URL | Purpose |
|---------|-----|---------|
| Milvus | `localhost:19530` | Vector database |
| Attu UI | `http://localhost:8000` | Milvus web GUI |
| MinIO | `localhost:9000` | Object storage |

**View vectors in Attu:**
1. Open http://localhost:8000
2. Connect to `localhost:19530`
3. Browse `notes` collection

## Resume Mapping

| Resume Bullet | Implementation File | Key Function |
|--------------|---------------------|--------------|
| LangGraph Plan-Execute-Replan Agent | `core/agent.py` | `_build_graph()` - 4-node workflow |
| Docker Milvus + RAG | `core/rag.py` + `docker-compose.yml` | `ingest_notes()` + `search()` |
| MCP Tool Layer | `mcp_tools/tools.py` | `@mcp.tool()` decorators |
| Checkpointer Memory | `checkpointer/sqlite.py` | `SqliteSaver` + `ConversationMemory` |

## Troubleshooting

### "Python not found"
Install Python 3.10+ and check "Add to PATH"

### "Docker not found"
Install Docker Desktop and ensure it's running

### Milvus connection failed
```bash
# Check if Milvus is running
docker ps

# If not, restart
docker-compose down
docker-compose up -d

# Wait 30s, then retry
```

### No results in search
```bash
# Check if notes were ingested
ingest.bat

# Check notes folder has .md files
dir notes\*.md /s
```

### API errors
1. Check `.env` file has valid API key
2. Verify API key has credits
3. Try switching between DashScope and Kimi

## Project Structure

```
NoteCopilot/
├── core/                    # LangGraph Agent core
│   ├── state.py            # Agent state definitions
│   ├── rag.py              # Milvus RAG implementation
│   └── agent.py            # Plan-Execute-Replan Agent
├── mcp_tools/              # MCP Tool layer
│   ├── tools.py            # Tool definitions
│   └── server.py           # MCP server
├── checkpointer/           # State persistence
│   └── sqlite.py           # SQLite checkpointer
├── notes/                  # Your markdown notes
├── checkpoints/            # Conversation history
├── .venv/                  # Python environment
├── docker-compose.yml      # Milvus deployment
├── requirements.txt        # Python dependencies
├── *.bat                   # Windows scripts
└── README.md               # This file
```

## License

MIT License - Open source at https://github.com/zihasyu/NoteCopilot
