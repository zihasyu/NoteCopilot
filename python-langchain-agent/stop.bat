@echo off
chcp 65001 >nul
echo ====================================
echo 停止 LangChain Agent 服务
echo ====================================
echo.

echo [1/2] 停止 Milvus 向量数据库...
docker compose -f vector-database.yml down
echo [成功] Milvus 已停止
echo.

echo [2/2] 清理完成
echo.
echo ====================================
echo 服务已停止
echo ====================================
pause
