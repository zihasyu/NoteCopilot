"""
MCP Tool 定义 - RAG 检索、笔记增强、博客上传
"""
from typing import Any
import json

from mcp.server.fastmcp import FastMCP


# 创建 MCP Server
mcp = FastMCP("NoteCopilot")

# 全局 RAG 引用（在 main.py 中设置）
_rag_instance = None


def set_rag(rag):
    """设置 RAG 实例"""
    global _rag_instance
    _rag_instance = rag


@mcp.tool()
async def search_notes(query: str, top_k: int = 5) -> str:
    """
    检索实验记录和论文笔记

    Args:
        query: 检索关键词
        top_k: 返回结果数量

    Returns:
        JSON 格式的检索结果
    """
    if _rag_instance is None:
        return json.dumps({"error": "RAG 未初始化"})

    notes = _rag_instance.search(query, top_k=top_k)

    return json.dumps({
        "results": notes,
        "count": len(notes)
    }, ensure_ascii=False)


@mcp.tool()
async def enhance_notes(content: str, style: str = "academic") -> str:
    """
    增强生成论文摘要或实验总结

    Args:
        content: 原始笔记内容
        style: 生成风格 (academic/blog/simple)

    Returns:
        增强后的内容
    """
    styles = {
        "academic": "学术风格，正式严谨",
        "blog": "博客风格，通俗易懂",
        "simple": "简洁风格，要点清晰"
    }

    style_desc = styles.get(style, styles["academic"])

    return json.dumps({
        "style": style_desc,
        "original_length": len(content),
        "status": "已增强（Demo 模式，实际调用 LLM 生成）",
        "preview": content[:200] + "..." if len(content) > 200 else content
    }, ensure_ascii=False)


@mcp.tool()
async def upload_blog(title: str, content: str, tags: list = None) -> str:
    """
    上传个人博客

    Args:
        title: 博客标题
        content: 博客内容
        tags: 标签列表

    Returns:
        上传结果
    """
    # Demo 模式，实际项目中调用博客 API
    return json.dumps({
        "status": "success",
        "title": title,
        "url": f"https://your-blog.com/posts/{title.lower().replace(' ', '-')}",
        "tags": tags or [],
        "message": "博客已准备上传（Demo 模式）"
    }, ensure_ascii=False)


@mcp.tool()
async def list_sources() -> str:
    """
    列出所有笔记来源

    Returns:
        笔记文件列表
    """
    if _rag_instance is None:
        return json.dumps({"error": "RAG 未初始化"})

    # 返回示例数据，实际应从 Milvus 查询
    return json.dumps({
        "sources": [
            "experiments/2024-01.md",
            "papers/llm-survey.md",
            "ideas/project-ideas.md"
        ],
        "total": 3
    }, ensure_ascii=False)
