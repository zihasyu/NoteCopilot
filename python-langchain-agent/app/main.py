"""主应用文件 - FastAPI 应用入口"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import config
from app.api import chat, document, health
from app.core.milvus_client import milvus_manager

# 创建 FastAPI 应用
app = FastAPI(
    title=config.app_name,
    version=config.app_version,
    description="基于 LangChain 的智能 Agent 系统"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router)
app.include_router(document.router)
app.include_router(health.router)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    print(f"启动 {config.app_name} v{config.app_version}")
    
    # 连接到 Milvus
    try:
        milvus_manager.connect()
        print("Milvus 连接成功")
    except Exception as e:
        print(f"Milvus 连接失败: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print("关闭应用...")
    
    # 关闭 Milvus 连接
    try:
        milvus_manager.close()
        print("Milvus 连接已关闭")
    except Exception as e:
        print(f"关闭 Milvus 连接失败: {e}")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": config.app_name,
        "version": config.app_version,
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config.host,
        port=config.port,
        reload=config.debug
    )
