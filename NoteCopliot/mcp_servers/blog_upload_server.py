"""个人博客上传 MCP Server

提供博客文章发布、更新、管理等功能。
"""

import logging
import functools
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from fastmcp import FastMCP

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BlogUpload_MCP_Server")

mcp = FastMCP("BlogUpload")

# 模拟博客存储
MOCK_BLOG_DB = {}
BLOG_PUBLISHED_LIST = []


def log_tool_call(func):
    """装饰器：记录工具调用的日志"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        method_name = func.__name__
        logger.info(f"=" * 80)
        logger.info(f"调用方法: {method_name}")
        if kwargs:
            try:
                params_str = json.dumps(kwargs, ensure_ascii=False, indent=2)
            except (TypeError, ValueError):
                params_str = str(kwargs)
            logger.info(f"参数信息:\n{params_str}")
        else:
            logger.info("参数信息: 无")
        try:
            result = func(*args, **kwargs)
            logger.info(f"返回状态: SUCCESS")
            if isinstance(result, dict):
                summary = {k: v if not isinstance(v, (list, dict)) else f"<{type(v).__name__} with {len(v)} items>"
                          for k, v in list(result.items())[:5]}
                logger.info(f"返回结果摘要: {json.dumps(summary, ensure_ascii=False)}")
            else:
                logger.info(f"返回结果: {result}")
            logger.info(f"=" * 80)
            return result
        except Exception as e:
            logger.error(f"返回状态: ERROR")
            logger.error(f"错误信息: {str(e)}")
            logger.error(f"=" * 80)
            raise
    return wrapper


@mcp.tool()
@log_tool_call
def upload_blog_post(
    title: str,
    content: str,
    tags: List[str],
    category: str = "技术",
    summary: Optional[str] = None,
    cover_image: Optional[str] = None,
    publish: bool = True
) -> Dict[str, Any]:
    """上传/发布博客文章

    Args:
        title: 文章标题
        content: 文章内容（Markdown格式）
        tags: 文章标签
        category: 文章分类
        summary: 文章摘要（可选，自动从内容生成）
        cover_image: 封面图片URL（可选）
        publish: 是否立即发布

    Returns:
        发布结果
    """
    post_id = f"post_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    created_at = datetime.now().isoformat()

    # 自动生成摘要
    if not summary:
        summary = content[:150] + "..." if len(content) > 150 else content

    blog_post = {
        "post_id": post_id,
        "title": title,
        "content": content,
        "summary": summary,
        "tags": tags,
        "category": category,
        "cover_image": cover_image,
        "created_at": created_at,
        "updated_at": created_at,
        "status": "published" if publish else "draft",
        "views": 0,
        "likes": 0
    }

    MOCK_BLOG_DB[post_id] = blog_post

    if publish:
        BLOG_PUBLISHED_LIST.append({
            "post_id": post_id,
            "title": title,
            "published_at": created_at,
            "url": f"https://zihasyu.github.io/blog/{post_id}"
        })

    return {
        "success": True,
        "post_id": post_id,
        "title": title,
        "status": "published" if publish else "draft",
        "url": f"https://zihasyu.github.io/blog/{post_id}" if publish else None,
        "message": f"文章《{title}》{'发布成功' if publish else '保存为草稿'}"
    }


@mcp.tool()
@log_tool_call
def update_blog_post(
    post_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    tags: Optional[List[str]] = None,
    category: Optional[str] = None
) -> Dict[str, Any]:
    """更新已发布的博客文章

    Args:
        post_id: 文章ID
        title: 新标题（可选）
        content: 新内容（可选）
        tags: 新标签（可选）
        category: 新分类（可选）

    Returns:
        更新结果
    """
    if post_id not in MOCK_BLOG_DB:
        return {
            "success": False,
            "error": f"文章不存在: {post_id}"
        }

    post = MOCK_BLOG_DB[post_id]

    if title:
        post["title"] = title
    if content:
        post["content"] = content
    if tags:
        post["tags"] = tags
    if category:
        post["category"] = category

    post["updated_at"] = datetime.now().isoformat()

    return {
        "success": True,
        "post_id": post_id,
        "title": post["title"],
        "updated_at": post["updated_at"],
        "message": f"文章《{post['title']}》更新成功"
    }


@mcp.tool()
@log_tool_call
def list_blog_posts(
    status: str = "all",
    category: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """获取博客文章列表

    Args:
        status: 文章状态 (all/published/draft)
        category: 分类筛选（可选）
        limit: 返回数量限制

    Returns:
        文章列表
    """
    posts = []

    for post_id, post in MOCK_BLOG_DB.items():
        if status != "all" and post["status"] != status:
            continue
        if category and post["category"] != category:
            continue

        posts.append({
            "post_id": post_id,
            "title": post["title"],
            "summary": post["summary"],
            "tags": post["tags"],
            "category": post["category"],
            "status": post["status"],
            "created_at": post["created_at"],
            "updated_at": post["updated_at"]
        })

    posts.sort(key=lambda x: x["updated_at"], reverse=True)

    return {
        "total": len(posts),
        "status_filter": status,
        "posts": posts[:limit]
    }


@mcp.tool()
@log_tool_call
def generate_blog_template(
    template_type: str = "tech",
    title: Optional[str] = None
) -> Dict[str, Any]:
    """生成博客文章模板

    Args:
        template_type: 模板类型 (tech/research/tutorial)
        title: 文章标题（可选）

    Returns:
        博客模板
    """
    templates = {
        "tech": {
            "frontmatter": """---
title: {title}
date: {date}
tags: [技术, AI, LLM]
category: 技术
cover:
---""",
            "structure": [
                "## 背景介绍",
                "## 问题定义",
                "## 解决方案",
                "## 实现细节",
                "## 实验结果",
                "## 总结与展望"
            ],
            "tips": [
                "使用代码块展示关键代码",
                "添加架构图说明系统结构",
                "提供可运行的示例"
            ]
        },
        "research": {
            "frontmatter": """---
title: {title}
date: {date}
tags: [论文解读, AI, 深度学习]
category: 论文笔记
---""",
            "structure": [
                "## 论文概述",
                "## 研究背景",
                "## 核心方法",
                "## 实验设置",
                "## 主要结果",
                "## 个人思考"
            ],
            "tips": [
                "对比相关工作的差异",
                "分析方法的优缺点",
                "思考可能的应用场景"
            ]
        },
        "tutorial": {
            "frontmatter": """---
title: {title}
date: {date}
tags: [教程, 入门, 实践]
category: 教程
---""",
            "structure": [
                "## 目标读者",
                "## 前置知识",
                "## 环境准备",
                "## 详细步骤",
                "## 常见问题",
                "## 进阶资源"
            ],
            "tips": [
                "提供清晰的步骤编号",
                "包含预期输出示例",
                "添加故障排查指南"
            ]
        }
    }

    template = templates.get(template_type, templates["tech"])
    date_str = datetime.now().strftime("%Y-%m-%d")

    return {
        "template_type": template_type,
        "frontmatter": template["frontmatter"].format(
            title=title or "文章标题",
            date=date_str
        ),
        "structure": template["structure"],
        "writing_tips": template["tips"],
        "example": f"""{template["frontmatter"].format(title=title or "示例文章", date=date_str)}

{chr(10).join(template["structure"])}

## 参考资源
- [相关链接1]
- [相关链接2]
"""
    }


@mcp.tool()
@log_tool_call
def preview_blog_post(
    title: str,
    content: str,
    tags: List[str]
) -> Dict[str, Any]:
    """预览博客文章效果

    Args:
        title: 文章标题
        content: 文章内容
        tags: 文章标签

    Returns:
        预览信息
    """
    # 计算阅读时间（平均200字/分钟）
    word_count = len(content)
    read_time = max(1, word_count // 200)

    # 统计信息
    code_blocks = content.count("```")
    headers = content.count("##")
    images = content.count("![")
    links = content.count("](http")

    return {
        "title": title,
        "word_count": word_count,
        "estimated_read_time": f"{read_time} 分钟",
        "statistics": {
            "code_blocks": code_blocks // 2,  # 每个代码块有开始和结束
            "headers": headers,
            "images": images,
            "links": links
        },
        "tags": tags,
        "suggestions": [
            "建议添加封面图片提升视觉效果",
            "使用目录帮助读者快速导航" if headers > 3 else "",
            "添加相关文章推荐" if links == 0 else ""
        ],
        "preview_url": f"https://zihasyu.github.io/preview/draft_{datetime.now().strftime('%H%M%S')}"
    }


@mcp.tool()
@log_tool_call
def get_published_stats() -> Dict[str, Any]:
    """获取博客发布统计

    Returns:
        发布统计信息
    """
    total_posts = len(MOCK_BLOG_DB)
    published = sum(1 for p in MOCK_BLOG_DB.values() if p["status"] == "published")
    drafts = total_posts - published

    categories = {}
    for post in MOCK_BLOG_DB.values():
        cat = post["category"]
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "total_posts": total_posts,
        "published": published,
        "drafts": drafts,
        "category_distribution": categories,
        "github_repo": "https://github.com/zihasyu/zihasyu.github.io",
        "site_url": "https://zihasyu.github.io"
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8005, path="/mcp")
