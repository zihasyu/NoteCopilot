from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection
from langchain_openai import OpenAIEmbeddings
from .config import Config

class VectorService:
    def __init__(self):
        # 初始化 Milvus 连接
        connections.connect(
            alias="default",
            host=Config.MILVUS_HOST,
            port=Config.MILVUS_PORT
        )
        
        # 初始化嵌入模型
        self.embeddings = OpenAIEmbeddings(
            model=Config.EMBEDDING_MODEL,
            api_key=Config.OPENAI_API_KEY
        )
        
        # 创建或获取集合
        self.collection = self._create_collection()
    
    def _create_collection(self):
        # 定义字段
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=Config.EMBEDDING_DIM),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="metadata", dtype=DataType.JSON)
        ]
        
        # 创建模式
        schema = CollectionSchema(fields=fields, description="LangChain RAG Collection")
        
        # 创建或获取集合
        collection = Collection(name=Config.MILVUS_COLLECTION, schema=schema, using="default")
        
        # 创建索引
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128}
        }
        collection.create_index("embedding", index_params)
        
        return collection
    
    def embed_text(self, text):
        """将文本转换为向量"""
        return self.embeddings.embed_query(text)
    
    def insert(self, texts, metadatas):
        """插入文本和元数据到向量数据库"""
        # 生成嵌入向量
        embeddings = self.embeddings.embed_documents(texts)
        
        # 准备数据
        data = [
            embeddings,
            texts,
            metadatas
        ]
        
        # 插入数据
        self.collection.insert(data)
        self.collection.flush()
    
    def search(self, query, top_k=3):
        """搜索相似文本"""
        # 生成查询向量
        query_embedding = self.embed_text(query)
        
        # 搜索参数
        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10}
        }
        
        # 执行搜索
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["text", "metadata"]
        )
        
        # 处理结果
        search_results = []
        for hits in results:
            for hit in hits:
                search_results.append({
                    "text": hit.entity.get("text"),
                    "metadata": hit.entity.get("metadata"),
                    "distance": hit.distance
                })
        
        return search_results
