#!/bin/bash

# 微博监控系统停止脚本

echo "=========================================="
echo "   停止微博监控系统"
echo "=========================================="

# 检查PID文件
if [ ! -f "weibo_monitor.pid" ]; then
    echo "未找到运行的服务"
    exit 0
fi

PID=$(cat weibo_monitor.pid)

# 检查进程是否存在
if ! ps -p $PID > /dev/null 2>&1; then
    echo "服务未运行"
    rm weibo_monitor.pid
    exit 0
fi

# 停止进程
echo "正在停止服务 (PID: $PID)..."
kill $PID

# 等待进程结束
sleep 2

# 强制停止（如果还在运行）
if ps -p $PID > /dev/null 2>&1; then
    echo "强制停止服务..."
    kill -9 $PID
fi

rm weibo_monitor.pid

echo "✓ 服务已停止"

