@echo off
title A21 Startup
set BASE=%~dp0

echo Starting A21 services...
echo.

echo [1/4] Neo4j...
start "Neo4j" cmd /c "cd /d %BASE%neo4j\neo4j-community-2026.02.3\bin && neo4j.bat console"

echo [2/4] llama-server...
start "llama" cmd /c "cd /d %BASE%llama.cpp && llama-server.exe -m %BASE%model\qwen2.5-1.5b-instruct-q4_k_m.gguf -c 2048 -t 4 --host 127.0.0.1 --port 8082 --mlock"

echo [3/4] Backend + Vosk...
start "Backend" cmd /c "cd /d %BASE%backend && call conda activate a21 && start Vosk python tools\vosk_http.py && uvicorn main:app --host 127.0.0.1 --port 8000"

echo [4/4] Frontend...
start "Frontend" cmd /c "cd /d %BASE%frontend && npm run dev"

echo.
echo Wait 15-20s, then open http://localhost:5173
echo Neo4j:7474 llama:8082 vosk:8765 backend:8000 frontend:5173
pause
