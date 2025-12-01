#!/bin/bash

# 微博监控系统一键安装脚本 - 适配中国服务器
# 支持 Ubuntu/Debian/CentOS 系统

set -e

echo "=========================================="
echo "   微博监控系统 - 一键安装脚本"
echo "   适配中国服务器环境"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检测操作系统
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        echo -e "${RED}无法检测操作系统${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} 检测到操作系统: $OS $VER"
}

# 检查root权限
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        echo -e "${YELLOW}提示: 某些操作可能需要root权限，建议使用 sudo${NC}"
    fi
}

# 更新系统
update_system() {
    echo ""
    echo "步骤 1/7: 更新系统软件包..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        sudo apt-get update -y
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
        sudo yum update -y
    fi
    
    echo -e "${GREEN}✓${NC} 系统更新完成"
}

# 安装Python3
install_python() {
    echo ""
    echo "步骤 2/7: 检查Python环境..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        echo -e "${GREEN}✓${NC} Python已安装: $PYTHON_VERSION"
    else
        echo "正在安装Python3..."
        if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
            sudo apt-get install -y python3 python3-pip python3-venv
        elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
            sudo yum install -y python3 python3-pip
        fi
        echo -e "${GREEN}✓${NC} Python3安装完成"
    fi
}

# 安装Chrome和ChromeDriver
install_chrome() {
    echo ""
    echo "步骤 3/7: 安装Chrome浏览器..."
    
    if command -v google-chrome &> /dev/null; then
        echo -e "${GREEN}✓${NC} Chrome已安装"
    else
        if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
            echo "正在安装Chrome..."
            wget -q -O /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
            sudo apt-get install -y /tmp/google-chrome.deb || sudo dpkg -i /tmp/google-chrome.deb
            sudo apt-get install -f -y
            rm /tmp/google-chrome.deb
            echo -e "${GREEN}✓${NC} Chrome安装完成"
        elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]]; then
            echo "正在安装Chrome..."
            wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
            sudo yum install -y google-chrome-stable_current_x86_64.rpm
            rm google-chrome-stable_current_x86_64.rpm
            echo -e "${GREEN}✓${NC} Chrome安装完成"
        fi
    fi
    
    # 安装Chrome依赖
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        sudo apt-get install -y fonts-liberation libasound2 libatk-bridge2.0-0 \
            libatk1.0-0 libatspi2.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 \
            libgtk-3-0 libnspr4 libnss3 libwayland-client0 libxcomposite1 \
            libxdamage1 libxfixes3 libxkbcommon0 libxrandr2 xdg-utils
    fi
}

# 创建虚拟环境
create_venv() {
    echo ""
    echo "步骤 4/7: 创建Python虚拟环境..."
    
    if [ -d "venv" ]; then
        echo -e "${YELLOW}虚拟环境已存在，跳过创建${NC}"
    else
        python3 -m venv venv
        echo -e "${GREEN}✓${NC} 虚拟环境创建完成"
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
}

# 安装Python依赖
install_dependencies() {
    echo ""
    echo "步骤 5/7: 安装Python依赖包..."
    echo "使用国内镜像源加速下载..."
    
    # 升级pip并使用清华镜像源
    pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
    
    # 安装依赖包
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    
    echo -e "${GREEN}✓${NC} Python依赖安装完成"
}

# 配置文件
configure() {
    echo ""
    echo "步骤 6/7: 配置系统..."
    
    # 检查配置文件
    if [ ! -f "config.yaml" ]; then
        echo -e "${YELLOW}config.yaml 不存在，请确保已正确配置${NC}"
    fi
    
    # 创建日志目录
    mkdir -p logs
    
    # 设置执行权限
    chmod +x start.sh stop.sh
    
    echo -e "${GREEN}✓${NC} 系统配置完成"
}

# 创建systemd服务
create_service() {
    echo ""
    echo "步骤 7/7: 创建系统服务..."
    
    CURRENT_DIR=$(pwd)
    CURRENT_USER=$(whoami)
    
    # 创建systemd服务文件
    sudo tee /etc/systemd/system/weibo-monitor.service > /dev/null <<EOF
[Unit]
Description=Weibo Monitor Web Service
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin"
ExecStart=$CURRENT_DIR/venv/bin/python $CURRENT_DIR/web_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # 重载systemd
    sudo systemctl daemon-reload
    
    echo -e "${GREEN}✓${NC} 系统服务创建完成"
    echo ""
    echo -e "${GREEN}服务管理命令：${NC}"
    echo "  启动服务: sudo systemctl start weibo-monitor"
    echo "  停止服务: sudo systemctl stop weibo-monitor"
    echo "  重启服务: sudo systemctl restart weibo-monitor"
    echo "  查看状态: sudo systemctl status weibo-monitor"
    echo "  开机自启: sudo systemctl enable weibo-monitor"
    echo "  查看日志: sudo journalctl -u weibo-monitor -f"
}

# 显示配置指南
show_config_guide() {
    echo ""
    echo "=========================================="
    echo "   安装完成！"
    echo "=========================================="
    echo ""
    echo -e "${YELLOW}⚠️  下一步操作：${NC}"
    echo ""
    echo "1. 编辑配置文件 config.yaml:"
    echo "   nano config.yaml 或 vim config.yaml"
    echo ""
    echo "2. 配置Telegram Bot Token和Chat ID"
    echo "   - 获取Bot Token: 在Telegram搜索 @BotFather"
    echo "   - 获取Chat ID: 在Telegram搜索 @userinfobot"
    echo ""
    echo "3. 设置要监控的关键词"
    echo ""
    echo "4. 启动服务（选择一种）："
    echo "   方式1（推荐）: sudo systemctl start weibo-monitor"
    echo "   方式2: ./start.sh"
    echo ""
    echo "5. 设置开机自启（可选）："
    echo "   sudo systemctl enable weibo-monitor"
    echo ""
    echo "6. 访问Web管理界面："
    echo "   http://你的服务器IP:5000"
    echo ""
    echo "   如需外网访问，请在config.yaml中修改："
    echo "   web:"
    echo "     host: \"0.0.0.0\"  # 允许外网访问"
    echo "     port: 5000"
    echo ""
    echo "   并开放防火墙端口："
    echo "   sudo ufw allow 5000  (Ubuntu/Debian)"
    echo "   sudo firewall-cmd --add-port=5000/tcp --permanent (CentOS)"
    echo "   sudo firewall-cmd --reload (CentOS)"
    echo ""
    echo "7. 查看服务状态："
    echo "   sudo systemctl status weibo-monitor"
    echo ""
    echo "8. 查看实时日志："
    echo "   sudo journalctl -u weibo-monitor -f"
    echo ""
    echo "=========================================="
}

# 主函数
main() {
    detect_os
    check_root
    update_system
    install_python
    install_chrome
    create_venv
    install_dependencies
    configure
    create_service
    show_config_guide
}

# 运行主函数
main

