@echo off
chcp 65001 >nul
echo ================================
echo   部署到Linux服务器
echo ================================
echo.

REM 请修改以下配置
set SERVER_USER=root
set SERVER_IP=your-server-ip
set SERVER_PATH=/opt/web-monitor

echo 请修改此文件中的服务器配置：
echo SERVER_USER=%SERVER_USER%
echo SERVER_IP=%SERVER_IP%
echo SERVER_PATH=%SERVER_PATH%
echo.
pause

echo 正在压缩文件...
tar -czf web-monitor.tar.gz ^
    --exclude=venv ^
    --exclude=__pycache__ ^
    --exclude=*.db ^
    --exclude=*.log ^
    --exclude=.git ^
    app.py database.py monitor.py telegram_bot.py ^
    requirements.txt install.sh start.sh start.bat ^
    .gitignore config.example.yaml ^
    templates README.md README_CN.md DEPLOY.md LINUX_DEPLOY.md

echo.
echo 正在上传到服务器...
scp web-monitor.tar.gz %SERVER_USER%@%SERVER_IP%:/tmp/

echo.
echo 文件已上传！请在服务器上执行以下命令：
echo.
echo ssh %SERVER_USER%@%SERVER_IP%
echo sudo mkdir -p %SERVER_PATH%
echo cd %SERVER_PATH%
echo sudo tar -xzf /tmp/web-monitor.tar.gz
echo sudo chmod +x install.sh start.sh
echo sudo ./install.sh
echo.
pause

