@echo off
chcp 65001 >nul
echo ========================================
echo  A21 船舶故障诊断系统 - 开发环境启动
echo ========================================
echo.

set BASE=%~dp0

REM 启动 Neo4j（使用自带 JRE）
echo [1/4] 启动 Neo4j...
start "Neo4j" cmd /c "cd %BASE%neo4j\neo4j-community-2026.02.3\bin && neo4j.bat console"
timeout /t 12 /nobreak >nul

REM 启动 llama-server
echo [2/4] 启动 llama-server...
start "llama-server" cmd /c "cd %BASE%llama.cpp && llama-server.exe -m %BASE%model\qwen2.5-1.5b-instruct-q4_k_m.gguf -c 2048 -t 4 --host 127.0.0.1 --port 8080 --mlock"
timeout /t 5 /nobreak >nul

REM 启动 FastAPI 后端
echo [3/4] 启动后端...
start "FastAPI" cmd /c "cd %BASE%backend && uvicorn main:app --reload --host 127.0.0.1 --port 8000"
timeout /t 3 /nobreak >nul

REM 启动前端
echo [4/4] 启动前端...
start "Vue" cmd /c "cd %BASE%frontend && npm run dev"

echo.
echo ========================================
echo  所有服务已启动！
echo.
echo   Neo4j:        http://localhost:7474
echo   llama-server: http://localhost:8080
echo   后端 API:      http://localhost:8000/docs
echo   前端:          http://localhost:5173
echo ========================================
echo.
pause
