"""向量存储管理器模块"""

from typing import List

from langchain_core.documents import Document
from pymilvus import Collection

from app.core.milvus_client import milvus_manager
from app.services.vector_embedding_service import vector_embedding_service


class VectorStoreManager:
    """向量存储管理器 - 负责文档的向量化和存储"""

    def __init__(self):
        """初始化向量存储管理器"""
        print("向量存储管理器初始化完成")

    def add_documents(self, documents: List[Document]) -> int:
        """
        添加文档到向量存储

        Args:
            documents: 文档列表

        Returns:
            int: 成功添加的文档数量

        Raises:
            RuntimeError: 添加失败时抛出
        """
        try:
            if not documents:
                print("文档列表为空，无需添加")
                return 0

            print(f"开始添加 {len(documents)} 个文档到向量存储")

            # 1. 提取文本内容
            texts = [doc.page_content for doc in documents]

            # 2. 批量生成嵌入向量
            embeddings = vector_embedding_service.embed_documents(texts)

            # 3. 获取 collection
            collection: Collection = milvus_manager.get_collection()

            # 4. 准备数据
            data = []
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                # 生成唯一ID
                doc_id = f"doc_{hash(doc.page_content)}_{i}"
                
                # 构建数据项
                data.append({
                    "id": doc_id,
                    "vector": embedding,
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                })

            # 5. 插入数据
            collection.insert(data)
            collection.flush()

            print(f"成功添加 {len(data)} 个文档到向量存储")
            return len(data)

        except Exception as e:
            print(f"添加文档到向量存储失败: {e}")
            raise RuntimeError(f"添加文档失败: {e}") from e

    def delete_documents(self, ids: List[str]) -> int:
        """
        从向量存储中删除文档

        Args:
            ids: 文档ID列表

        Returns:
            int: 成功删除的文档数量

        Raises:
            RuntimeError: 删除失败时抛出
        """
        try:
            if not ids:
                print("ID列表为空，无需删除")
                return 0

            print(f"开始删除 {len(ids)} 个文档")

            # 获取 collection
            collection: Collection = milvus_manager.get_collection()

            # 删除文档
            collection.delete(ids)

            print(f"成功删除 {len(ids)} 个文档")
            return len(ids)

        except Exception as e:
            print(f"删除文档失败: {e}")
            raise RuntimeError(f"删除文档失败: {e}") from e

    def clear_collection(self) -> bool:
        """
        清空向量存储

        Returns:
            bool: 是否成功

        Raises:
            RuntimeError: 清空失败时抛出
        """
        try:
            print("开始清空向量存储")

            # 获取 collection
            collection: Collection = milvus_manager.get_collection()

            # 删除所有数据
            collection.delete(expr="id != ''")
            collection.flush()

            print("成功清空向量存储")
            return True

        except Exception as e:
            print(f"清空向量存储失败: {e}")
            raise RuntimeError(f"清空向量存储失败: {e}") from e

    def get_document_count(self) -> int:
        """
        获取向量存储中的文档数量

        Returns:
            int: 文档数量

        Raises:
            RuntimeError: 查询失败时抛出
        """
        try:
            # 获取 collection
            collection: Collection = milvus_manager.get_collection()

            # 获取文档数量
            count = collection.num_entities

            print(f"向量存储中的文档数量: {count}")
            return count

        except Exception as e:
            print(f"获取文档数量失败: {e}")
            raise RuntimeError(f"获取文档数量失败: {e}") from e


# 全局单例
vector_store_manager = VectorStoreManager()
