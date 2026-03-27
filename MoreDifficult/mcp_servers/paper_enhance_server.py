"""论文笔记增强 MCP Server

提供论文笔记的自动增强、格式化、生成摘要等功能。
"""

import logging
import functools
import json
from typing import Dict, Any, Optional, List
from fastmcp import FastMCP

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("PaperEnhance_MCP_Server")

mcp = FastMCP("PaperEnhance")


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
def generate_paper_summary(
    title: str,
    content: str,
    summary_length: str = "medium"
) -> Dict[str, Any]:
    """根据论文内容生成结构化摘要

    Args:
        title: 论文标题
        content: 论文内容或关键段落
        summary_length: 摘要长度 (short/medium/long)

    Returns:
        结构化摘要
    """
    length_config = {
        "short": {"background": 50, "method": 80, "results": 50, "conclusion": 40},
        "medium": {"background": 100, "method": 150, "results": 100, "conclusion": 80},
        "long": {"background": 200, "method": 300, "results": 200, "conclusion": 150}
    }

    config = length_config.get(summary_length, length_config["medium"])

    # 提取关键词（模拟）
    keywords = _extract_keywords(content)

    return {
        "title": title,
        "structured_summary": {
            "background": f"论文针对{title.split()[0] if title else '该领域'}的研究挑战...",
            "method": "作者提出了新的方法论，通过创新性技术解决问题...",
            "results": "实验表明该方法在多个基准数据集上取得显著提升...",
            "conclusion": "该研究为相关领域提供了新的思路和方法..."
        },
        "keywords": keywords,
        "key_contributions": [
            "提出了一种新的方法框架",
            "在标准数据集上验证了有效性",
            "提供了理论分析和实验证明"
        ],
        "suitable_for": ["快速了解论文核心", "文献综述参考", "相关研究对比"]
    }


@mcp.tool()
@log_tool_call
def enhance_note_format(
    content: str,
    note_type: str = "paper"
) -> Dict[str, Any]:
    """优化笔记格式，增强可读性

    Args:
        content: 原始笔记内容
        note_type: 笔记类型 (paper/experiment)

    Returns:
        格式化后的笔记
    """
    templates = {
        "paper": {
            "sections": ["摘要", "核心贡献", "方法", "实验", "总结", "相关论文"],
            "suggestions": [
                "使用##标记主要章节",
                "使用###标记子章节",
                "添加关键公式用$$包裹",
                "添加引用链接"
            ]
        },
        "experiment": {
            "sections": ["实验目标", "实验设置", "实验结果", "分析与讨论", "下一步计划"],
            "suggestions": [
                "使用表格展示对比结果",
                "添加实验参数配置",
                "记录环境信息",
                "添加可视化图表"
            ]
        }
    }

    template = templates.get(note_type, templates["paper"])

    return {
        "original_length": len(content),
        "enhanced_content": content,  # 实际应用中会进行格式优化
        "suggested_structure": template["sections"],
        "formatting_suggestions": template["suggestions"],
        "markdown_tips": [
            "使用 `- [ ]` 创建待办事项",
            "使用 `> ` 添加引用块",
            "使用 `**粗体**` 强调重点",
            "使用代码块展示代码"
        ]
    }


@mcp.tool()
@log_tool_call
def suggest_related_papers(
    topic: str,
    keywords: List[str],
    limit: int = 5
) -> Dict[str, Any]:
    """根据主题推荐相关论文

    Args:
        topic: 研究主题
        keywords: 关键词列表
        limit: 返回数量

    Returns:
        推荐论文列表
    """
    # 模拟论文数据库
    paper_db = {
        "transformer": [
            {"title": "BERT: Pre-training of Deep Bidirectional Transformers", "authors": "Devlin et al.", "year": 2019},
            {"title": "GPT-3: Language Models are Few-Shot Learners", "authors": "Brown et al.", "year": 2020},
        ],
        "lora": [
            {"title": "Parameter-Efficient Transfer Learning for NLP", "authors": "Houlsby et al.", "year": 2019},
            {"title": "The Power of Scale for Parameter-Efficient Prompt Tuning", "authors": "Lester et al.", "year": 2021},
        ],
        "rag": [
            {"title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP", "authors": "Lewis et al.", "year": 2020},
            {"title": "Dense Passage Retrieval for Open-Domain QA", "authors": "Karpukhin et al.", "year": 2020},
        ]
    }

    results = []
    query_lower = topic.lower()

    for category, papers in paper_db.items():
        if query_lower in category or any(kw.lower() in category for kw in keywords):
            results.extend(papers)

    return {
        "topic": topic,
        "keywords": keywords,
        "recommended_papers": results[:limit],
        "search_suggestions": [
            f"https://scholar.google.com/scholar?q={'+'.join(topic.split())}",
            f"https://arxiv.org/search/?query={'+'.join(keywords)}&searchtype=all"
        ]
    }


@mcp.tool()
@log_tool_call
def generate_citation_format(
    title: str,
    authors: List[str],
    year: int,
    venue: Optional[str] = None,
    style: str = "apa"
) -> Dict[str, Any]:
    """生成标准引用格式

    Args:
        title: 论文标题
        authors: 作者列表
        year: 发表年份
        venue: 发表会议/期刊
        style: 引用格式 (apa/mla/ieee/chicago)

    Returns:
        各种格式的引用
    """
    author_str = ", ".join(authors)

    formats = {
        "apa": f"{author_str} ({year}). {title}. {venue or 'Preprint'}.",
        "mla": f"{authors[0] if authors else 'Unknown'}. \"{title}.\" {venue or 'arXiv preprint'}, {year}.",
        "ieee": f"{author_str}, \"{title},\" {venue or 'arXiv preprint'}, {year}.",
        "chicago": f"{author_str}. \"{title}.\" {venue or 'Preprint'}, {year}."
    }

    return {
        "requested_style": style,
        "citation": formats.get(style, formats["apa"]),
        "all_formats": formats,
        "bibtex": f"""@article{{cite_key,
  title={{ {title} }},
  author={{ {author_str} }},
  year={{ {year} }},
  journal={{ {venue or 'arXiv preprint'} }}
}}"""
    }


def _extract_keywords(content: str) -> List[str]:
    """提取关键词（简化版）"""
    common_terms = [
        "transformer", "attention", "bert", "gpt", "llm",
        "fine-tuning", "lora", "rag", "embedding", "vector",
        "training", "inference", "optimization", "deep learning"
    ]
    content_lower = content.lower()
    return [term for term in common_terms if term in content_lower][:5]


@mcp.tool()
@log_tool_call
def analyze_experiment_data(
    experiment_type: str,
    metrics: Dict[str, List[float]],
    baseline: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """分析实验数据，生成分析报告

    Args:
        experiment_type: 实验类型
        metrics: 指标数据
        baseline: 基线数据

    Returns:
        分析结果
    """
    analysis = {
        "experiment_type": experiment_type,
        "summary": {},
        "improvements": [],
        "suggestions": []
    }

    for metric_name, values in metrics.items():
        if values:
            import statistics
            analysis["summary"][metric_name] = {
                "mean": round(statistics.mean(values), 4),
                "std": round(statistics.stdev(values), 4) if len(values) > 1 else 0,
                "min": round(min(values), 4),
                "max": round(max(values), 4)
            }

            if baseline and metric_name in baseline:
                baseline_val = baseline[metric_name]
                current_val = statistics.mean(values)
                improvement = ((current_val - baseline_val) / baseline_val * 100
                             if baseline_val != 0 else 0)
                analysis["improvements"].append({
                    "metric": metric_name,
                    "baseline": baseline_val,
                    "current": round(current_val, 4),
                    "improvement": f"{improvement:+.2f}%"
                })

    analysis["suggestions"] = [
        "建议增加更多对比实验",
        "考虑进行统计显著性检验",
        "记录更多中间过程数据"
    ]

    return analysis


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8004, path="/mcp")
