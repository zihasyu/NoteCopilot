"""简单使用示例 - 直接调用核心功能"""

from app.services.rag_agent_service import rag_agent_service
from app.services.document_splitter_service import document_splitter_service
from app.services.vector_store_manager import vector_store_manager
from app.core.milvus_client import milvus_manager


def main():
    """主函数"""
    print("=" * 50)
    print("LangChain Agent 简单示例")
    print("=" * 50)
    
    # 1. 连接到 Milvus
    print("\n1. 连接到 Milvus...")
    try:
        milvus_manager.connect()
        print("✓ Milvus 连接成功")
    except Exception as e:
        print(f"✗ Milvus 连接失败: {e}")
        return
    
    # 2. 添加示例文档
    print("\n2. 添加示例文档...")
    sample_docs = [
        """# Python 编程语言
        
Python是一种高级编程语言，以其简洁清晰的语法而闻名。
它支持多种编程范式，包括面向对象、命令式、函数式和过程式编程。

## 特点
- 简单易学
- 开源免费
- 丰富的库
- 跨平台
""",
        """# LangChain 框架

LangChain是一个用于构建LLM应用的框架。
它提供了丰富的组件和工具，简化了AI应用的开发。

## 核心组件
- LLM接口
- 向量存储
- Agent
- Chain
"""
    ]
    
    for i, doc in enumerate(sample_docs, 1):
        documents = document_splitter_service.split_document(doc, f"sample_{i}.md")
        count = vector_store_manager.add_documents(documents)
        print(f"✓ 添加文档 {i}: {count} 个分片")
    
    # 3. 查询示例
    print("\n3. 开始对话 (输入 'quit' 退出)...")
    print("-" * 50)
    
    while True:
        try:
            question = input("\n你的问题: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("再见！")
                break
            
            if not question:
                continue
            
            print("\n思考中...")
            answer = rag_agent_service.query(question)
            print(f"\n回答: {answer}")
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n错误: {e}")
    
    # 4. 关闭连接
    print("\n4. 关闭连接...")
    milvus_manager.close()
    print("✓ 连接已关闭")


if __name__ == "__main__":
    main()
