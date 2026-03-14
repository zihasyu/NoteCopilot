"""健康检查API - 提供系统健康状态接口"""

from fastapi import APIRouter

from app.core.milvus_client import milvus_manager

router = APIRouter(prefix="/api/health", tags=["健康检查"])


@router.get("/")
async def health_check():
    """
    系统健康检查
    
    Returns:
        dict: 系统健康状态
    """
    # 检查 Milvus 连接状态
    milvus_healthy = milvus_manager.health_check()
    
    return {
        "status": "healthy" if milvus_healthy else "unhealthy",
        "milvus": "connected" if milvus_healthy else "disconnected",
    }
