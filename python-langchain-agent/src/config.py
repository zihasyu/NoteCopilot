import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # DashScope 配置
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    
    # Milvus 配置
    MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
    MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
    MILVUS_COLLECTION = os.getenv("MILVUS_COLLECTION", "langchain_rag")
    
    # Qwen 配置
    QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen2.5-7b-instruct")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")
    
    # 向量维度（根据模型选择）
    EMBEDDING_DIM = 1536  # text-embedding-v3 的维度
