"""测试 RAG 文档检索功能"""

import asyncio
from app.core.milvus_client import milvus_manager
from app.services.vector_store_manager import vector_store_manager
from app.config import config

async def test_retrieve():
    print("=" * 60)
    print("Testing NoteCopilot RAG")
    print("=" * 60)

    # 1. 连接 Milvus
    print("\n[1] Connecting to Milvus...")
    try:
        milvus_manager.connect()
        print("[OK] Milvus connected")
    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        return

    # 2. 获取向量存储
    print("\n[2] Getting vector store...")
    try:
        vector_store = vector_store_manager.get_vector_store()
        print("[OK] Vector store ready")
    except Exception as e:
        print(f"[ERROR] Failed to get vector store: {e}")
        return

    # 3. 测试检索
    test_queries = [
        "LoRA",
        "实验记录",
        "论文笔记",
        "RAG",
        "Transformer"
    ]

    print("\n[3] Testing document retrieval:")
    for query in test_queries:
        print(f"\n  Query: '{query}'")
        try:
            retriever = vector_store.as_retriever(search_kwargs={"k": 3})
            docs = await asyncio.to_thread(retriever.invoke, query)

            if docs:
                print(f"  [OK] Found {len(docs)} documents:")
                for i, doc in enumerate(docs, 1):
                    source = doc.metadata.get("_file_name", "unknown")
                    preview = doc.page_content[:100].replace("\n", " ")
                    print(f"    {i}. {source}")
                    print(f"       Preview: {preview}...")
            else:
                print(f"  [WARN] No documents found")
        except Exception as e:
            print(f"  [ERROR] {e}")

    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_retrieve())
