# MCP 服务器说明

NoteCopilot 使用 MCP (Model Context Protocol) 协议构建了三个核心工具服务：

## 服务列表

### 1. NoteSearch Server (端口 8003)

**功能**：实验记录和论文笔记的搜索与检索

**主要工具**：
- `search_notes` - 搜索笔记库中的实验记录和论文笔记
- `get_note_detail` - 获取笔记详细内容
- `list_recent_notes` - 获取最近更新的笔记列表
- `get_related_notes` - 获取相关笔记推荐

**启动方式**：
```bash
python mcp_servers/note_search_server.py
```

### 2. PaperEnhance Server (端口 8004)

**功能**：论文笔记增强和格式化

**主要工具**：
- `generate_paper_summary` - 根据论文内容生成结构化摘要
- `enhance_note_format` - 优化笔记格式，增强可读性
- `suggest_related_papers` - 根据主题推荐相关论文
- `generate_citation_format` - 生成标准引用格式
- `analyze_experiment_data` - 分析实验数据，生成分析报告

**启动方式**：
```bash
python mcp_servers/paper_enhance_server.py
```

### 3. BlogUpload Server (端口 8005)

**功能**：个人博客文章上传和管理

**主要工具**：
- `upload_blog_post` - 上传/发布博客文章
- `update_blog_post` - 更新已发布的博客文章
- `list_blog_posts` - 获取博客文章列表
- `generate_blog_template` - 生成博客文章模板
- `preview_blog_post` - 预览博客文章效果
- `get_published_stats` - 获取博客发布统计

**启动方式**：
```bash
python mcp_servers/blog_upload_server.py
```

## 快速启动

使用启动脚本一键启动所有 MCP 服务：

**Windows:**
```powershell
.\start-windows.bat
```

**Linux/macOS:**
```bash
make start
```

## MCP 协议说明

MCP (Model Context Protocol) 是 Anthropic 推出的开放协议，用于标准化 AI 模型与外部工具的交互。NoteCopilot 通过 MCP 实现：

- 标准化的工具发现和调用
- 类型安全的参数传递
- 可扩展的工具生态
- 与 LangChain/LangGraph 无缝集成

## 配置说明

MCP 服务器地址在 `app/config.py` 中配置：

```python
mcp_note_search_url: str = "http://localhost:8003/mcp"
mcp_paper_enhance_url: str = "http://localhost:8004/mcp"
mcp_blog_upload_url: str = "http://localhost:8005/mcp"
```
