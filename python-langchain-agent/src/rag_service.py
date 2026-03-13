from langchain_community.chat_models import ChatDashScope
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from .vector_service import VectorService
from .config import Config

class RagService:
    def __init__(self):
        # 初始化向量服务
        self.vector_service = VectorService()
        
        # 初始化LLM
        self.llm = ChatDashScope(
            model=Config.QWEN_MODEL,
            dashscope_api_key=Config.DASHSCOPE_API_KEY
        )
        
        # 创建检索器
        self.retriever = self._create_retriever()
        
        # 创建RAG链
        self.rag_chain = self._create_rag_chain()
    
    def _create_retriever(self):
        """创建自定义检索器"""
        class CustomRetriever:
            def __init__(self, vector_service):
                self.vector_service = vector_service
            
            def get_relevant_documents(self, query):
                """获取相关文档"""
                results = self.vector_service.search(query)
                # 转换为LangChain文档格式
                from langchain.schema import Document
                documents = []
                for result in results:
                    doc = Document(
                        page_content=result["text"],
                        metadata=result["metadata"]
                    )
                    documents.append(doc)
                return documents
        
        return CustomRetriever(self.vector_service)
    
    def _create_rag_chain(self):
        """创建RAG链"""
        # 定义提示模板
        prompt_template = """
        你是一个智能助手，需要根据提供的上下文回答用户的问题。
        
        上下文信息：
        {context}
        
        用户问题：
        {question}
        
        请基于上下文信息，提供一个详细、准确的回答。
        如果上下文信息不足以回答问题，请明确说明。
        """
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # 创建RAG链
        rag_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": prompt}
        )
        
        return rag_chain
    
    def add_document(self, text, metadata=None):
        """添加文档到向量数据库"""
        if metadata is None:
            metadata = {}
        self.vector_service.insert([text], [metadata])
    
    def query(self, question):
        """使用RAG回答问题"""
        result = self.rag_chain.invoke({"query": question})
        return result["result"]
