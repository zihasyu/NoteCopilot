"""笔记检索 MCP Server

提供实验记录、论文笔记的搜索和检索功能。
"""

import logging
import functools
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from fastmcp import FastMCP

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("NoteSearch_MCP_Server")

mcp = FastMCP("NoteSearch")


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


# 模拟笔记数据库
MOCK_NOTES_DB = {
    "exp_001": {
        "note_id": "exp_001",
        "title": "LLM微调实验记录 - LoRA方法",
        "type": "experiment",
        "tags": ["LLM", "LoRA", "fine-tuning", "transformers"],
        "created_at": "2024-03-15 10:00:00",
        "updated_at": "2024-03-20 15:30:00",
        "content": """## LLM微调实验记录

### 实验目标
使用LoRA方法对Llama-2-7b进行微调，提升在中文问答任务上的表现。

### 实验参数
- 基础模型: Llama-2-7b-hf
- 微调方法: LoRA
- rank: 16
- alpha: 32
- learning_rate: 2e-4
- batch_size: 4
- epochs: 3

### 实验结果
- 训练loss从2.34下降到0.89
- 验证集准确率提升12%
- GPU显存占用: 14GB
"""
    },
    "exp_002": {
        "note_id": "exp_002",
        "title": "RAG系统性能优化实验",
        "type": "experiment",
        "tags": ["RAG", "向量检索", "Milvus", "性能优化"],
        "created_at": "2024-03-18 09:00:00",
        "updated_at": "2024-03-22 16:00:00",
        "content": """## RAG系统性能优化实验

### 实验目标
优化RAG系统的检索延迟和召回率。

### 实验方法
1. 对比不同embedding模型
2. 调整向量索引参数
3. 优化分块策略

### 关键发现
- text-embedding-v2 比 v1 召回率提升8%
- 分块大小从500改为800，检索质量提升
- HNSW索引参数: ef=128, M=16 是最佳平衡点
"""
    },
    "paper_001": {
        "note_id": "paper_001",
        "title": "Attention Is All You Need - 论文笔记",
        "type": "paper",
        "tags": ["Transformer", "Attention", "NLP", "经典论文"],
        "created_at": "2024-02-10 14:00:00",
        "updated_at": "2024-02-15 10:30:00",
        "content": """## Attention Is All You Need

### 核心贡献
1. 提出Transformer架构，完全基于注意力机制
2. 摒弃RNN和CNN，实现并行计算
3. 在机器翻译任务上达到SOTA

### 关键创新点
- **Multi-Head Attention**: 多头注意力机制，捕获不同子空间信息
- **Positional Encoding**: 引入位置编码，保持序列顺序信息
- **Self-Attention**: 自注意力机制，建立全局依赖关系

### 实验结果
- WMT 2014英德翻译: BLEU=28.4
- WMT 2014英法翻译: BLEU=41.8
- 训练时间显著缩短
""",
        "citations": ["Vaswani et al., 2017"],
        "related_work": ["RNN", "LSTM", "Seq2Seq"]
    },
    "paper_002": {
        "note_id": "paper_002",
        "title": "LoRA: Low-Rank Adaptation - 论文笔记",
        "type": "paper",
        "tags": ["LoRA", "PEFT", "LLM", "参数高效微调"],
        "created_at": "2024-03-01 11:00:00",
        "updated_at": "2024-03-05 17:00:00",
        "content": """## LoRA: Low-Rank Adaptation of Large Language Models

### 核心思想
通过低秩矩阵来近似参数更新，大幅减少微调所需参数量。

### 方法
- 冻结预训练模型参数
- 在Transformer层注入可训练的低秩矩阵
- 训练参数仅为原始模型的0.1%

### 优势
1. 显存占用降低70%
2. 训练速度提升3倍
3. 模型部署时可合并权重，无推理延迟

### 适用场景
- 消费级GPU微调大模型
- 多任务适配器切换
- 模型个性化定制
""",
        "citations": ["Hu et al., 2021"],
        "related_work": ["Adapter", "Prompt Tuning", "BitFit"]
    }
}


@mcp.tool()
@log_tool_call
def search_notes(
    query: str,
    note_type: Optional[str] = None,
    tags: Optional[List[str]] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """搜索笔记库中的实验记录和论文笔记

    Args:
        query: 搜索关键词
        note_type: 笔记类型筛选 (experiment/paper/all)
        tags: 标签筛选
        date_from: 开始日期 (YYYY-MM-DD)
        date_to: 结束日期 (YYYY-MM-DD)
        limit: 返回结果数量限制

    Returns:
        搜索结果列表
    """
    results = []

    for note_id, note in MOCK_NOTES_DB.items():
        # 类型筛选
        if note_type and note_type != "all" and note["type"] != note_type:
            continue

        # 标签筛选
        if tags and not any(tag in note["tags"] for tag in tags):
            continue

        # 日期筛选
        note_date = note["created_at"][:10]
        if date_from and note_date < date_from:
            continue
        if date_to and note_date > date_to:
            continue

        # 关键词匹配（标题和内容）
        score = 0
        query_lower = query.lower()

        if query_lower in note["title"].lower():
            score += 10
        if query_lower in note["content"].lower():
            score += 5
        if any(query_lower in tag.lower() for tag in note["tags"]):
            score += 3

        if score > 0 or not query:
            results.append({
                "note_id": note_id,
                "title": note["title"],
                "type": note["type"],
                "tags": note["tags"],
                "created_at": note["created_at"],
                "score": score,
                "preview": note["content"][:200] + "..." if len(note["content"]) > 200 else note["content"]
            })

    # 按相关度排序
    results.sort(key=lambda x: x["score"], reverse=True)

    return {
        "total": len(results),
        "query": query,
        "results": results[:limit]
    }


@mcp.tool()
@log_tool_call
def get_note_detail(note_id: str) -> Dict[str, Any]:
    """获取笔记详细内容

    Args:
        note_id: 笔记ID

    Returns:
        笔记完整内容
    """
    note = MOCK_NOTES_DB.get(note_id)
    if not note:
        return {
            "error": f"笔记不存在: {note_id}",
            "available_notes": list(MOCK_NOTES_DB.keys())
        }

    return {
        "note_id": note_id,
        "title": note["title"],
        "type": note["type"],
        "tags": note["tags"],
        "created_at": note["created_at"],
        "updated_at": note["updated_at"],
        "content": note["content"],
        "citations": note.get("citations", []),
        "related_work": note.get("related_work", [])
    }


@mcp.tool()
@log_tool_call
def list_recent_notes(
    days: int = 7,
    note_type: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """获取最近更新的笔记列表

    Args:
        days: 最近多少天
        note_type: 笔记类型筛选
        limit: 返回数量限制

    Returns:
        笔记列表
    """
    cutoff_date = datetime.now() - timedelta(days=days)

    results = []
    for note_id, note in MOCK_NOTES_DB.items():
        note_updated = datetime.strptime(note["updated_at"], "%Y-%m-%d %H:%M:%S")

        if note_updated < cutoff_date:
            continue

        if note_type and note["type"] != note_type:
            continue

        results.append({
            "note_id": note_id,
            "title": note["title"],
            "type": note["type"],
            "updated_at": note["updated_at"],
            "preview": note["content"][:150] + "..."
        })

    results.sort(key=lambda x: x["updated_at"], reverse=True)

    return {
        "total": len(results),
        "days": days,
        "notes": results[:limit]
    }


@mcp.tool()
@log_tool_call
def get_related_notes(note_id: str, limit: int = 5) -> Dict[str, Any]:
    """获取相关笔记推荐

    Args:
        note_id: 参考笔记ID
        limit: 返回数量

    Returns:
        相关笔记列表
    """
    source_note = MOCK_NOTES_DB.get(note_id)
    if not source_note:
        return {"error": f"笔记不存在: {note_id}"}

    # 基于标签相似度计算相关性
    results = []
    source_tags = set(source_note["tags"])

    for nid, note in MOCK_NOTES_DB.items():
        if nid == note_id:
            continue

        common_tags = source_tags & set(note["tags"])
        if common_tags:
            results.append({
                "note_id": nid,
                "title": note["title"],
                "type": note["type"],
                "common_tags": list(common_tags),
                "similarity_score": len(common_tags)
            })

    results.sort(key=lambda x: x["similarity_score"], reverse=True)

    return {
        "source_note": note_id,
        "related_notes": results[:limit]
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8003, path="/mcp")
