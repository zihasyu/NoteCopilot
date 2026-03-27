"""
MCP Server 启动器
基于 MCP 协议构建 Tool 接入层
"""
import asyncio
import sys

from .tools import mcp, set_rag


def start_mcp_server(rag_instance, transport: str = "stdio"):
    """
    启动 MCP Server

    Args:
        rag_instance: NoteRAG 实例
        transport: 传输方式 (stdio/sse)
    """
    set_rag(rag_instance)

    if transport == "stdio":
        mcp.run(transport='stdio')
    else:
        mcp.run(transport='sse', port=8001)


async def handle_client(rag_instance, reader, writer):
    """处理 MCP 客户端连接（SSE 模式）"""
    set_rag(rag_instance)
    addr = writer.get_extra_info('peername')
    print(f"MCP 客户端连接: {addr}")

    try:
        while True:
            data = await reader.read(4096)
            if not data:
                break

            # 简单 echo 示例，实际应解析 MCP 协议
            writer.write(data)
            await writer.drain()

    except asyncio.CancelledError:
        pass
    finally:
        writer.close()
        await writer.wait_closed()
        print(f"MCP 客户端断开: {addr}")
