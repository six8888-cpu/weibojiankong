#!/bin/bash
# 香港服务器 - 一键安装SOCKS5代理服务
# 使用gost实现，轻量级高性能

echo "============================================"
echo "   SOCKS5代理服务器 - 一键安装脚本"
echo "============================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检测系统类型
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo -e "${RED}无法检测系统类型${NC}"
    exit 1
fi

echo -e "${YELLOW}检测到系统: $OS${NC}"

# 设置代理端口和认证（可自定义）
SOCKS5_PORT=1080
SOCKS5_USER="proxy"
SOCKS5_PASS=$(openssl rand -base64 12)  # 随机生成密码

echo ""
echo -e "${BLUE}代理配置：${NC}"
echo -e "  端口: ${GREEN}$SOCKS5_PORT${NC}"
echo -e "  用户名: ${GREEN}$SOCKS5_USER${NC}"
echo -e "  密码: ${GREEN}$SOCKS5_PASS${NC}"
echo ""

# 安装gost
echo -e "${YELLOW}[1/4] 安装gost...${NC}"

# 检测系统架构
ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
    GOST_ARCH="amd64"
elif [ "$ARCH" = "aarch64" ]; then
    GOST_ARCH="arm64"
else
    GOST_ARCH="amd64"
fi

# 下载gost
GOST_VERSION="2.11.5"
DOWNLOAD_URL="https://github.com/ginuerzh/gost/releases/download/v${GOST_VERSION}/gost-linux-${GOST_ARCH}-${GOST_VERSION}.gz"

echo "下载gost..."
wget -q --show-progress $DOWNLOAD_URL -O gost.gz || {
    echo -e "${RED}下载失败，尝试备用地址...${NC}"
    wget -q --show-progress "https://ghproxy.com/${DOWNLOAD_URL}" -O gost.gz || {
        echo -e "${RED}下载失败，请检查网络${NC}"
        exit 1
    }
}

gunzip gost.gz
chmod +x gost
sudo mv gost /usr/local/bin/

echo -e "${GREEN}✓ gost安装成功${NC}"

# 创建配置文件
echo -e "${YELLOW}[2/4] 创建配置文件...${NC}"

sudo mkdir -p /etc/gost

cat > /tmp/gost.json << EOF
{
    "ServeNodes": [
        "socks5://${SOCKS5_USER}:${SOCKS5_PASS}@:${SOCKS5_PORT}"
    ]
}
EOF

sudo mv /tmp/gost.json /etc/gost/config.json

echo -e "${GREEN}✓ 配置文件创建成功${NC}"

# 创建systemd服务
echo -e "${YELLOW}[3/4] 创建systemd服务...${NC}"

cat > /tmp/gost.service << EOF
[Unit]
Description=Gost SOCKS5 Proxy
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/gost -C /etc/gost/config.json
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/gost.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gost
sudo systemctl start gost

echo -e "${GREEN}✓ systemd服务已创建并启动${NC}"

# 配置防火墙
echo -e "${YELLOW}[4/4] 配置防火墙...${NC}"

if command -v firewall-cmd &> /dev/null; then
    # CentOS/RHEL
    sudo firewall-cmd --permanent --add-port=${SOCKS5_PORT}/tcp
    sudo firewall-cmd --reload
    echo -e "${GREEN}✓ firewalld防火墙已配置${NC}"
elif command -v ufw &> /dev/null; then
    # Ubuntu/Debian
    sudo ufw allow ${SOCKS5_PORT}/tcp
    echo -e "${GREEN}✓ ufw防火墙已配置${NC}"
else
    echo -e "${YELLOW}⚠ 未检测到防火墙，请手动开放端口 ${SOCKS5_PORT}${NC}"
fi

# 检查服务状态
sleep 2
if systemctl is-active --quiet gost; then
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}   SOCKS5代理服务安装成功！${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "${BLUE}服务器信息：${NC}"
    SERVER_IP=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')
    echo -e "  IP地址: ${GREEN}${SERVER_IP}${NC}"
    echo ""
    echo -e "${BLUE}代理配置：${NC}"
    echo -e "  协议: ${GREEN}SOCKS5${NC}"
    echo -e "  地址: ${GREEN}${SERVER_IP}${NC}"
    echo -e "  端口: ${GREEN}${SOCKS5_PORT}${NC}"
    echo -e "  用户名: ${GREEN}${SOCKS5_USER}${NC}"
    echo -e "  密码: ${GREEN}${SOCKS5_PASS}${NC}"
    echo ""
    echo -e "${BLUE}完整代理地址（复制使用）：${NC}"
    echo -e "${GREEN}socks5://${SOCKS5_USER}:${SOCKS5_PASS}@${SERVER_IP}:${SOCKS5_PORT}${NC}"
    echo ""
    echo -e "${BLUE}管理命令：${NC}"
    echo "  启动: sudo systemctl start gost"
    echo "  停止: sudo systemctl stop gost"
    echo "  重启: sudo systemctl restart gost"
    echo "  状态: sudo systemctl status gost"
    echo "  日志: sudo journalctl -u gost -f"
    echo ""
    echo -e "${YELLOW}⚠️  重要：请保存好用户名和密码！${NC}"
    echo ""
    
    # 保存配置到文件
    cat > ~/socks5_proxy_info.txt << INFOEOF
SOCKS5代理服务器信息
====================
服务器IP: ${SERVER_IP}
端口: ${SOCKS5_PORT}
用户名: ${SOCKS5_USER}
密码: ${SOCKS5_PASS}

完整代理地址:
socks5://${SOCKS5_USER}:${SOCKS5_PASS}@${SERVER_IP}:${SOCKS5_PORT}

测试命令:
curl -x socks5://${SOCKS5_USER}:${SOCKS5_PASS}@${SERVER_IP}:${SOCKS5_PORT} https://api.telegram.org

在中国服务器使用:
export http_proxy=socks5://${SOCKS5_USER}:${SOCKS5_PASS}@${SERVER_IP}:${SOCKS5_PORT}
export https_proxy=socks5://${SOCKS5_USER}:${SOCKS5_PASS}@${SERVER_IP}:${SOCKS5_PORT}
INFOEOF
    
    echo -e "${GREEN}✓ 配置信息已保存到: ~/socks5_proxy_info.txt${NC}"
else
    echo -e "${RED}✗ 服务启动失败，请检查日志: sudo journalctl -u gost -n 50${NC}"
    exit 1
fi
