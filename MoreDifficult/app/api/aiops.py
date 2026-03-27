"""
NoteCopilot 智能笔记助手接口
"""

import json
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from loguru import logger

from app.models.aiops import NoteCopilotRequest
from app.services.aiops_service import notecopilot_service

router = APIRouter()


@router.post("/assist")
async def assist_stream(request: NoteCopilotRequest):
    """
    NoteCopilot 智能笔记助手接口（流式 SSE）

    **功能说明：**
    - 基于 Plan-Execute-Replan 模式进行智能任务处理
    - 支持实验记录检索、论文笔记增强、博客发布等功能
    - 流式返回任务执行过程和结果

    **SSE 事件类型：**

    1. `status` - 状态更新
       ```json
       {
         "type": "status",
         "stage": "planning",
         "message": "正在制定执行计划..."
       }
       ```

    2. `plan` - 计划制定完成
       ```json
       {
         "type": "plan",
         "stage": "plan_created",
         "message": "执行计划已制定，共 5 个步骤",
         "plan": ["步骤1: ...", "步骤2: ..."]
       }
       ```

    3. `step_complete` - 步骤执行完成
       ```json
       {
         "type": "step_complete",
         "stage": "step_executed",
         "message": "步骤执行完成 (2/5)",
         "current_step": "搜索相关笔记",
         "remaining_steps": 3
       }
       ```

    4. `report` - 最终结果
       ```json
       {
         "type": "report",
         "stage": "final_report",
         "message": "任务执行完成",
         "report": "# 任务执行结果\\n..."
       }
       ```

    5. `complete` - 任务完成
       ```json
       {
         "type": "complete",
         "stage": "task_complete",
         "message": "任务执行完成",
         "result": {...}
       }
       ```

    **使用示例：**
    ```bash
    curl -X POST "http://localhost:9900/api/assist" \\
      -H "Content-Type: application/json" \\
      -d '{"session_id": "session-123", "query": "搜索LoRA相关实验记录"}' \\
      --no-buffer
    ```

    Args:
        request: NoteCopilot 请求

    Returns:
        SSE 事件流
    """
    session_id = request.session_id or "default"
    query = request.query or "帮助整理笔记"
    logger.info(f"[会话 {session_id}] 收到 NoteCopilot 请求: {query}")

    async def event_generator():
        try:
            async for event in notecopilot_service.assist(user_input=query, session_id=session_id):
                # 发送事件
                yield {
                    "event": "message",
                    "data": json.dumps(event, ensure_ascii=False)
                }

                # 如果是完成或错误事件，结束流
                if event.get("type") in ["complete", "error"]:
                    break

            logger.info(f"[会话 {session_id}] NoteCopilot 流式响应完成")

        except Exception as e:
            logger.error(f"[会话 {session_id}] NoteCopilot 流式响应异常: {e}", exc_info=True)
            yield {
                "event": "message",
                "data": json.dumps({
                    "type": "error",
                    "stage": "exception",
                    "message": f"任务执行异常: {str(e)}"
                }, ensure_ascii=False)
            }

    return EventSourceResponse(event_generator())
