from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .agent import AgentService
from .rag_service import RagService
import os
import glob

app = FastAPI(title="LangChain Agent API")

# 初始化服务
agent_service = AgentService()
rag_service = RagService()

# 定义请求模型
class QueryRequest(BaseModel):
    query: str

class DocumentRequest(BaseModel):
    text: str
    metadata: dict = {}

# 加载文档的函数
def load_documents():
    """从docs目录加载文档"""
    docs_dir = "docs"
    if not os.path.exists(docs_dir):
        return []
    
    documents = []
    for file_path in glob.glob(f"{docs_dir}/*.md"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                documents.append({
                    "text": content,
                    "metadata": {"source": file_path}
                })
        except Exception as e:
            print(f"Error loading document {file_path}: {e}")
    
    return documents

# 启动时加载文档
@app.on_event("startup")
async def startup_event():
    print("Loading documents...")
    documents = load_documents()
    for doc in documents:
        rag_service.add_document(doc["text"], doc["metadata"])
    print(f"Loaded {len(documents)} documents")

# API端点
@app.post("/query")
async def query_agent(request: QueryRequest):
    """使用Agent回答问题"""
    try:
        result = agent_service.run(request.query)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add-document")
async def add_document(request: DocumentRequest):
    """添加文档到知识库"""
    try:
        rag_service.add_document(request.text, request.metadata)
        return {"message": "Document added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}
