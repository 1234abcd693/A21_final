@echo off
chcp 65001 >nul
echo ========================================
echo  A21 船舶故障诊断系统 - 开发环境启动
echo ========================================
echo.

set BASE=%~dp0

REM 启动 Neo4j
echo [1/5] 启动 Neo4j...
start "Neo4j" /D "%BASE%neo4j\neo4j-community-2026.02.3\bin" cmd /c "neo4j.bat console"
echo       等待 Neo4j 就绪 (15秒)...
timeout /t 15 /nobreak >nul

REM 启动 llama-server (端口8082, 避免冲突)
echo [2/5] 启动 llama-server (端口 8082)...
start "llama-server" /D "%BASE%llama.cpp" cmd /c "llama-server.exe -m %BASE%model\qwen2.5-1.5b-instruct-q4_k_m.gguf -c 2048 -t 4 --host 127.0.0.1 --port 8082 --mlock"
echo       等待 llama-server 就绪 (10秒)...
timeout /t 10 /nobreak >nul

REM 启动 whisper-server
echo [3/5] 启动 whisper-server (端口 8081)...
start "whisper-server" /D "%BASE%whisper.cpp\Release" cmd /c "whisper-server.exe -m %BASE%model\ggml-base.bin --host 127.0.0.1 --port 8081"
timeout /t 3 /nobreak >nul

REM 启动 FastAPI 后端 (需要 conda 环境)
echo [4/5] 启动后端 (端口 8000)...
start "FastAPI" /D "%BASE%backend" cmd /c "call conda activate a21 && uvicorn main:app --host 127.0.0.1 --port 8000"
timeout /t 5 /nobreak >nul

REM 启动前端
echo [5/5] 启动前端 (端口 5173)...
start "Vue" /D "%BASE%frontend" cmd /c "npm run dev"

echo.
echo ========================================
echo  所有服务启动中...
echo.
echo   Neo4j:         http://localhost:7474
echo   llama-server:  http://localhost:8082
echo   whisper:       http://localhost:8081
echo   后端 API:       http://localhost:8000/docs
echo   前端:           http://localhost:5173
echo ========================================
echo.
pause
