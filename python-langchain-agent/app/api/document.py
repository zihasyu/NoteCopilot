"""文档API - 提供文档管理接口"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from pathlib import Path
import os

from app.services.document_splitter_service import document_splitter_service
from app.services.vector_store_manager import vector_store_manager

router = APIRouter(prefix="/api/documents", tags=["文档管理"])


class DocumentRequest(BaseModel):
    """文档请求模型"""
    text: str
    file_path: str = ""


class DocumentResponse(BaseModel):
    """文档响应模型"""
    message: str
    count: int


@router.post("/add", response_model=DocumentResponse)
async def add_document(request: DocumentRequest):
    """
    添加文档到知识库
    
    Args:
        request: 文档请求
        
    Returns:
        DocumentResponse: 文档响应
    """
    try:
        # 分割文档
        documents = document_splitter_service.split_document(
            request.text, request.file_path
        )
        
        # 添加到向量存储
        count = vector_store_manager.add_documents(documents)
        
        return DocumentResponse(
            message="文档添加成功",
            count=count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    上传文档文件到知识库
    
    Args:
        file: 上传的文件
        
    Returns:
        DocumentResponse: 文档响应
    """
    try:
        # 读取文件内容
        content = await file.read()
        text = content.decode("utf-8")
        
        # 分割文档
        documents = document_splitter_service.split_document(
            text, file.filename or ""
        )
        
        # 添加到向量存储
        count = vector_store_manager.add_documents(documents)
        
        return DocumentResponse(
            message=f"文件 {file.filename} 上传成功",
            count=count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear", response_model=DocumentResponse)
async def clear_documents():
    """
    清空知识库
    
    Returns:
        DocumentResponse: 文档响应
    """
    try:
        vector_store_manager.clear_collection()
        return DocumentResponse(
            message="知识库已清空",
            count=0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/count")
async def get_document_count():
    """
    获取知识库中的文档数量
    
    Returns:
        dict: 文档数量信息
    """
    try:
        count = vector_store_manager.get_document_count()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
