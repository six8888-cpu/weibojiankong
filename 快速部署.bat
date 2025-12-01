@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ================================
echo   网页监控系统 - Linux部署工具
echo ================================
echo.

REM 获取服务器信息
set /p SERVER_IP="请输入服务器IP地址: "
set /p SERVER_USER="请输入SSH用户名 (默认root): "
if "%SERVER_USER%"=="" set SERVER_USER=root

echo.
echo 服务器信息：
echo - IP: %SERVER_IP%
echo - 用户: %SERVER_USER%
echo - 安装路径: /opt/web-monitor
echo.
set /p CONFIRM="确认开始部署？(y/n): "
if /i not "%CONFIRM%"=="y" (
    echo 已取消部署
    pause
    exit /b
)

echo.
echo ================================
echo 第1步: 压缩项目文件
echo ================================

REM 删除旧的压缩包
if exist web-monitor.tar.gz del web-monitor.tar.gz

REM 创建临时目录
if exist temp_deploy rmdir /s /q temp_deploy
mkdir temp_deploy

REM 复制文件（排除不需要的）
echo 正在复制文件...
xcopy /Y /Q app.py temp_deploy\
xcopy /Y /Q database.py temp_deploy\
xcopy /Y /Q monitor.py temp_deploy\
xcopy /Y /Q telegram_bot.py temp_deploy\
xcopy /Y /Q requirements.txt temp_deploy\
xcopy /Y /Q install.sh temp_deploy\
xcopy /Y /Q start.sh temp_deploy\
xcopy /Y /Q .gitignore temp_deploy\
xcopy /Y /Q README.md temp_deploy\
xcopy /Y /Q README_CN.md temp_deploy\
xcopy /Y /Q DEPLOY.md temp_deploy\
xcopy /Y /Q LINUX_DEPLOY.md temp_deploy\
if exist config.example.yaml xcopy /Y /Q config.example.yaml temp_deploy\
xcopy /E /Y /Q templates temp_deploy\templates\

echo.
echo ================================
echo 第2步: 上传到服务器
echo ================================
echo.
echo 正在上传文件到 %SERVER_USER%@%SERVER_IP%...
echo （首次连接需要输入密码）
echo.

scp -r temp_deploy %SERVER_USER%@%SERVER_IP%:/tmp/web-monitor

if errorlevel 1 (
    echo.
    echo ❌ 上传失败！请检查：
    echo 1. 服务器IP地址是否正确
    echo 2. SSH用户名和密码是否正确
    echo 3. 网络连接是否正常
    pause
    rmdir /s /q temp_deploy
    exit /b 1
)

echo ✅ 文件上传成功！

REM 清理临时目录
rmdir /s /q temp_deploy

echo.
echo ================================
echo 第3步: 在服务器上安装
echo ================================
echo.
echo 正在连接服务器执行安装...
echo.

ssh %SERVER_USER%@%SERVER_IP% "
echo '开始安装...';
sudo mkdir -p /opt/web-monitor;
sudo cp -r /tmp/web-monitor/* /opt/web-monitor/;
sudo chown -R %SERVER_USER%:%SERVER_USER% /opt/web-monitor;
cd /opt/web-monitor;
chmod +x install.sh start.sh;
echo '';
echo '=================================';
echo '准备运行安装脚本...';
echo '这将需要5-10分钟时间';
echo '=================================';
echo '';
sudo ./install.sh;
"

if errorlevel 1 (
    echo.
    echo ⚠️  安装过程可能遇到问题
    echo.
    echo 请手动SSH登录服务器继续：
    echo ssh %SERVER_USER%@%SERVER_IP%
    echo cd /opt/web-monitor
    echo sudo ./install.sh
    echo.
    pause
    exit /b 1
)

echo.
echo ================================
echo ✅ 部署完成！
echo ================================
echo.
echo 🌐 访问地址: http://%SERVER_IP%:9527
echo.
echo 📝 后续操作：
echo 1. 访问Web界面
echo 2. 配置Telegram
echo 3. 添加监控网址和关键词
echo 4. 启动监控
echo.
echo 🔧 管理命令：
echo - 查看状态: ssh %SERVER_USER%@%SERVER_IP% "sudo systemctl status web-monitor"
echo - 查看日志: ssh %SERVER_USER%@%SERVER_IP% "sudo journalctl -u web-monitor -f"
echo - 重启服务: ssh %SERVER_USER%@%SERVER_IP% "sudo systemctl restart web-monitor"
echo.
pause

