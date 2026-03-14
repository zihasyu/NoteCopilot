# 使用说明

## 架构说明

本项目是一个基于 LangChain 的 RAG Agent 系统，包含以下核心组件：

### 1. 向量数据库（Milvus）
- **作用**：存储文档的向量表示，支持相似性搜索
- **运行方式**：Docker 容器
- **端口**：19530（Milvus）、9000/9001（MinIO 管理界面）
- **必须启动**：是

### 2. Python 应用
- **作用**：实现 RAG Agent 的核心逻辑
- **运行方式**：Python 脚本或 FastAPI 服务
- **端口**：8000（API 服务）
- **必须启动**：是

### 3. LLM 服务（DashScope）
- **作用**：提供大语言模型能力
- **运行方式**：云端 API
- **必须配置**：API Key

## 使用流程

### 第一步：启动向量数据库

**Windows 用户**：
```bash
# 双击运行
start.bat

# 或命令行运行
.\start.bat
```

**Linux/Mac 用户**：
```bash
# 启动 Milvus
docker compose -f vector-database.yml up -d

# 查看状态
docker compose -f vector-database.yml ps
```

**验证启动成功**：
```bash
# 检查容器状态
docker ps

# 应该看到以下容器运行中：
# - milvus-standalone
# - milvus-etcd
# - milvus-minio
```

### 第二步：配置 API Key

编辑 `.env` 文件：
```bash
# 设置您的 DashScope API Key
DASHSCOPE_API_KEY=sk-your-api-key-here
```

**获取 API Key**：
1. 访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/)
2. 开通服务并创建 API Key
3. 复制 API Key 到 `.env` 文件

### 第三步：安装依赖

**首次运行需要创建虚拟环境**：
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 第四步：运行测试

**方式一：脚本测试（推荐）**
```bash
# Windows
.venv\Scripts\python.exe simple_demo.py

# Linux/Mac
python simple_demo.py
```

**测试流程**：
1. 连接到 Milvus
2. 添加示例文档到向量数据库
3. 启动交互式对话
4. 输入问题测试 RAG 功能

**方式二：API 服务**
```bash
# Windows
.venv\Scripts\python.exe -m uvicorn app.main:app --reload

# Linux/Mac
python -m uvicorn app.main:app --reload
```

**访问 API 文档**：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 第五步：停止服务

**Windows 用户**：
```bash
# 双击运行
stop.bat

# 或命令行运行
.\stop.bat
```

**Linux/Mac 用户**：
```bash
# 停止 Milvus
docker compose -f vector-database.yml down
```

## 常见问题

### 1. Milvus 启动失败
**原因**：Docker 未运行或端口被占用

**解决方案**：
```bash
# 检查 Docker 状态
docker ps

# 检查端口占用
netstat -ano | findstr "19530"

# 重启 Docker Desktop
```

### 2. 连接 Milvus 失败
**原因**：Milvus 未完全启动

**解决方案**：
```bash
# 等待 15-30 秒后重试
# 或检查 Milvus 日志
docker logs milvus-standalone
```

### 3. API Key 无效
**原因**：未配置或配置错误

**解决方案**：
1. 检查 `.env` 文件是否存在
2. 确认 API Key 格式正确
3. 确认 API Key 有效且有余额

### 4. 依赖安装失败
**原因**：网络问题或 Python 版本不兼容

**解决方案**：
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 确认 Python 版本（需要 3.8+）
python --version
```

## 性能优化

### 1. 向量数据库优化
- 调整 `CHUNK_MAX_SIZE` 和 `CHUNK_OVERLAP` 参数
- 根据文档大小调整分块策略
- 定期清理不需要的向量数据

### 2. LLM 调用优化
- 调整 `RAG_TOP_K` 参数控制检索文档数量
- 选择合适的模型（qwen-max vs qwen-turbo）
- 启用流式输出提高响应速度

### 3. 内存优化
- 使用批量处理减少 API 调用
- 合理设置向量维度
- 定期清理会话历史

## 扩展开发

### 添加新工具
在 `app/tools/` 目录创建新工具：
```python
from langchain_core.tools import tool

@tool
def my_new_tool(query: str) -> str:
    """工具描述"""
    # 实现逻辑
    return result
```

### 添加新 API
在 `app/api/` 目录创建新接口：
```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/my", tags=["我的API"])

@router.post("/endpoint")
async def my_endpoint():
    # 实现逻辑
    return {"result": "success"}
```

### 添加新服务
在 `app/services/` 目录创建新服务：
```python
class MyNewService:
    def __init__(self):
        # 初始化逻辑
        pass
    
    def do_something(self):
        # 实现逻辑
        pass

# 全局单例
my_new_service = MyNewService()
```

## 监控和日志

### 查看日志
```bash
# Milvus 日志
docker logs milvus-standalone

# 应用日志（如果配置了日志文件）
tail -f logs/app.log
```

### 健康检查
```bash
# 检查 Milvus 状态
curl http://localhost:9091/healthz

# 检查 API 状态
curl http://localhost:8000/api/health/
```

## 生产部署

### Docker 部署
```bash
# 构建镜像
docker build -t langchain-agent .

# 运行容器
docker run -d -p 8000:8000 --env-file .env langchain-agent
```

### Kubernetes 部署
参考 `k8s/` 目录中的部署配置文件。

### 性能调优
- 使用 Gunicorn 或 Uvicorn 多进程
- 配置 Nginx 反向代理
- 启用 Redis 缓存
- 使用连接池管理数据库连接
