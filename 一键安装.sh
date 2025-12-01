#!/bin/bash

# 网页监控系统 - 一键安装脚本（从GitHub）

set -e

echo "================================"
echo "  网页监控系统 - 一键安装"
echo "================================"
echo ""

# GitHub仓库地址（需要替换）
REPO_URL="https://github.com/你的用户名/你的仓库名.git"

# 安装目录
INSTALL_DIR="/opt/web-monitor"

echo "1. 检查并安装必要工具..."
if ! command -v git &> /dev/null; then
    echo "正在安装git..."
    if [ -f /etc/debian_version ]; then
        sudo apt update
        sudo apt install -y git
    elif [ -f /etc/redhat-release ]; then
        sudo yum install -y git
    fi
fi

echo ""
echo "2. 克隆代码..."
if [ -d "$INSTALL_DIR" ]; then
    echo "目录已存在，正在更新..."
    cd $INSTALL_DIR
    sudo git pull
else
    echo "正在克隆仓库..."
    sudo git clone $REPO_URL $INSTALL_DIR
fi

echo ""
echo "3. 设置权限..."
sudo chown -R $USER:$USER $INSTALL_DIR

echo ""
echo "4. 进入安装目录..."
cd $INSTALL_DIR
chmod +x install.sh start.sh

echo ""
echo "5. 开始安装..."
sudo ./install.sh

echo ""
echo "================================"
echo "✅ 安装完成！"
echo "================================"
echo ""
echo "🌐 访问地址: http://$(curl -s ifconfig.me):9527"
echo ""
echo "📝 管理命令："
echo "  启动: sudo systemctl start web-monitor"
echo "  停止: sudo systemctl stop web-monitor"
echo "  状态: sudo systemctl status web-monitor"
echo "  日志: sudo journalctl -u web-monitor -f"
echo ""

