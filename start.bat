@echo off
chcp 65001 >nul
echo ========================================
echo    微博监控程序启动
echo ========================================
echo.

python weibo_monitor.py

pause

