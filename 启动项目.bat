@echo off
chcp 65001 >nul
title 电商智能客服系统

echo ========================================
echo  电商智能客服系统 - 启动脚本
echo ========================================
echo.

:: 检查 .env 文件
if not exist backend\.env (
    echo [错误] backend\.env 文件不存在！
    echo 请从 backend\.env.example 复制并配置 API Key
    pause
    exit /b 1
)

:: 启动后端
echo [1/2] 启动后端服务...
start "Backend" cmd /c "cd backend && C:\Users\Administrator\AppData\Local\Programs\Python\Python313\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

:: 等待后端启动
echo 等待后端启动...
timeout /t 3 /nobreak >nul

:: 启动前端
echo [2/2] 启动前端服务...
start "Frontend" cmd /c "cd frontend && npm run dev"

echo.
echo ========================================
echo  系统启动中...
echo  后端地址: http://localhost:8000
echo  前端地址: http://localhost:3000
echo  文档: http://localhost:8000/docs
echo ========================================
echo.
echo 按任意键关闭所有服务...
pause >nul

:: 关闭服务
taskkill /f /fi "WINDOWTITLE eq Backend" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq Frontend" >nul 2>&1

echo 服务已关闭。
