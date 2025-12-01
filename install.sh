#!/bin/bash

# 网页监控系统 - Linux安装脚本

set -e  # 遇到错误立即退出

echo "================================"
echo "   网页监控系统安装脚本"
echo "================================"

# 检测Linux发行版
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
    echo "检测到系统: $PRETTY_NAME"
else
    echo "无法检测系统类型"
    OS="unknown"
fi

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then 
    echo "警告：不建议以root用户运行此脚本"
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 更新系统
echo ""
echo "1. 更新系统软件包..."

if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
    sudo apt update
    INSTALL_CMD="sudo apt install -y"
    PYTHON_PKG="python3 python3-pip python3-venv"
elif [[ "$OS" == "centos" ]] || [[ "$OS" == "rhel" ]]; then
    sudo yum update -y
    INSTALL_CMD="sudo yum install -y"
    PYTHON_PKG="python3 python3-pip"
else
    echo "警告：未知的系统类型，假设使用apt"
    sudo apt update
    INSTALL_CMD="sudo apt install -y"
    PYTHON_PKG="python3 python3-pip python3-venv"
fi

# 安装Python3和pip
echo ""
echo "2. 安装Python3和pip..."
$INSTALL_CMD $PYTHON_PKG

# 安装Playwright依赖
echo ""
echo "3. 安装Playwright浏览器依赖..."
if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
    $INSTALL_CMD \
        libnss3 \
        libnspr4 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdrm2 \
        libdbus-1-3 \
        libxkbcommon0 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        libgbm1 \
        libpango-1.0-0 \
        libcairo2 \
        libasound2 \
        libatspi2.0-0
elif [[ "$OS" == "centos" ]] || [[ "$OS" == "rhel" ]]; then
    $INSTALL_CMD \
        nss \
        nspr \
        atk \
        at-spi2-atk \
        cups-libs \
        libdrm \
        dbus-libs \
        libxkbcommon \
        libXcomposite \
        libXdamage \
        libXfixes \
        libXrandr \
        mesa-libgbm \
        pango \
        cairo \
        alsa-lib
fi

# 创建虚拟环境
echo ""
echo "4. 创建Python虚拟环境..."
python3 -m venv venv

# 激活虚拟环境
echo ""
echo "5. 激活虚拟环境..."
source venv/bin/activate

# 安装Python依赖
echo ""
echo "6. 安装Python依赖包..."
pip install --upgrade pip
pip install -r requirements.txt

# 安装Playwright浏览器
echo ""
echo "7. 安装Playwright浏览器..."
playwright install chromium

# 创建systemd服务（可选）
echo ""
read -p "是否创建systemd服务？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    CURRENT_DIR=$(pwd)
    SERVICE_FILE="/etc/systemd/system/web-monitor.service"
    
    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Web Monitor Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin"
ExecStart=$CURRENT_DIR/venv/bin/python $CURRENT_DIR/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    echo ""
    echo "systemd服务已创建"
    echo "启动服务：sudo systemctl start web-monitor"
    echo "开机自启：sudo systemctl enable web-monitor"
    echo "查看状态：sudo systemctl status web-monitor"
    echo "查看日志：sudo journalctl -u web-monitor -f"
fi

echo ""
echo "================================"
echo "安装完成！"
echo "================================"
echo ""
echo "启动方法："
echo "1. 手动启动: ./start.sh"
echo "2. systemd服务: sudo systemctl start web-monitor"
echo ""
echo "访问地址: http://localhost:5000"
echo ""

