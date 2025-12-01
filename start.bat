@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ================================
echo    网页监控系统启动脚本
echo ================================

REM 检查Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到Python，请先安装Python 3.8或更高版本
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 检测到Python版本：
python --version

REM 创建虚拟环境
if not exist "venv" (
    echo.
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo.
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo.
echo 安装Python依赖...
pip install -r requirements.txt

REM 安装Playwright浏览器
echo.
echo 安装Playwright浏览器...
playwright install chromium

REM 启动应用
echo.
echo ================================
echo 启动监控系统...
echo ================================
echo.
echo Web界面地址: http://localhost:9527
echo 按 Ctrl+C 停止服务
echo.

python app.py

pause

