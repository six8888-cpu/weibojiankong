#!/bin/bash

# 网页监控系统 - Linux启动脚本

echo "================================"
echo "   网页监控系统启动脚本"
echo "================================"

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到Python3，请先安装Python 3.8或更高版本"
    exit 1
fi

echo "检测到Python版本："
python3 --version

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo ""
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo ""
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo ""
echo "安装Python依赖..."
pip install -r requirements.txt

# 安装Playwright浏览器
echo ""
echo "安装Playwright浏览器..."
playwright install chromium

# 启动应用
echo ""
echo "================================"
echo "启动监控系统..."
echo "================================"
echo ""
echo "Web界面地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务"
echo ""

python3 app.py

