@echo off
chcp 65001 >nul
echo 🚀 Skill Orchestrator - 环境初始化脚本 (Windows)
echo ================================================

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未找到。请先安装 Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python 已就绪

REM 安装依赖
echo.
echo 📦 正在安装 Python 依赖...
pip install jieba -q
if errorlevel 1 (
    echo ⚠️  pip 安装失败，请尝试以管理员身份运行或手动安装。
) else (
    echo ✅ 依赖安装完成
)

REM 检查 npx
where npx >nul 2>&1
if errorlevel 1 (
    echo.
    echo ⚠️  npx (Node.js) 未找到。find-skills 功能将受限。
    echo    如需完整功能，请安装 Node.js: https://nodejs.org/
) else (
    echo ✅ npx (Node.js) 已就绪
)

REM 创建目录
echo.
echo 📁 初始化必要目录...
if not exist logs mkdir logs
if not exist output mkdir output

echo.
echo ================================================
echo ✅ 初始化完成！
echo.
echo 使用方法: python scripts\run.py "你的请求"
pause
