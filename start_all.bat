@echo off
chcp 65001 >nul 2>&1
title A21 Startup
set BASE=%~dp0

echo ========================================
echo  A21 Ship Diagnosis System - Starting
echo ========================================
echo.

echo [1/5] Starting Neo4j...
start "Neo4j" /D "%BASE%neo4j\neo4j-community-2026.02.3\bin" cmd /c "neo4j.bat console"
echo        Waiting 15s...
timeout /t 15 /nobreak >nul

echo [2/5] Starting llama-server (port 8082)...
start "llama" /D "%BASE%llama.cpp" cmd /c "llama-server.exe -m %BASE%model\qwen2.5-1.5b-instruct-q4_k_m.gguf -c 2048 -t 4 --host 127.0.0.1 --port 8082 --mlock"
echo        Waiting 10s...
timeout /t 10 /nobreak >nul

echo [3/5] Starting Vosk (port 8765)...
start "Vosk" /D "%BASE%backend" cmd /c "call conda activate a21 && python tools\vosk_http.py"
echo        Waiting 5s...
timeout /t 5 /nobreak >nul

echo [4/5] Starting Backend (port 8000)...
start "Backend" /D "%BASE%backend" cmd /c "call conda activate a21 && uvicorn main:app --host 127.0.0.1 --port 8000"
timeout /t 5 /nobreak >nul

echo [5/5] Starting Frontend (port 5173)...
start "Frontend" /D "%BASE%frontend" cmd /c "npm run dev"

echo.
echo ========================================
echo  All services starting...
echo.
echo   Neo4j:    http://localhost:7474
echo   llama:    http://localhost:8082
echo   Vosk:     http://localhost:8765
echo   Backend:  http://localhost:8000/docs
echo   Frontend: http://localhost:5173
echo ========================================
pause
