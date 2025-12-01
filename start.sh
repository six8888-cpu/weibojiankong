#!/bin/bash

# 微博监控系统启动脚本

echo "=========================================="
echo "   启动微博监控系统"
echo "=========================================="

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "错误: 虚拟环境不存在，请先运行 ./install.sh"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查配置文件
if [ ! -f "config.yaml" ]; then
    echo "错误: 配置文件 config.yaml 不存在"
    exit 1
fi

# 检查是否已经在运行
if [ -f "weibo_monitor.pid" ]; then
    PID=$(cat weibo_monitor.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "警告: 服务已在运行中 (PID: $PID)"
        echo "如需重启，请先运行 ./stop.sh"
        exit 1
    else
        rm weibo_monitor.pid
    fi
fi

# 启动服务
echo "正在启动Web服务器..."
nohup python web_server.py > logs/server.log 2>&1 &
echo $! > weibo_monitor.pid

sleep 2

# 检查是否启动成功
if ps -p $(cat weibo_monitor.pid) > /dev/null 2>&1; then
    echo "✓ 服务启动成功！"
    echo ""
    echo "访问地址: http://localhost:5000"
    echo "查看日志: tail -f logs/server.log"
    echo "停止服务: ./stop.sh"
    echo ""
else
    echo "✗ 服务启动失败，请检查日志"
    cat logs/server.log
    exit 1
fi

