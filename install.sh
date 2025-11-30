#!/bin/bash

# Twitter监控系统 - CentOS一键安装脚本
# 适用于 CentOS 7/8/9

echo "=========================================="
echo "  Twitter监控系统 - 一键安装脚本"
echo "=========================================="
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用root权限运行此脚本"
    echo "使用命令: sudo bash install.sh"
    exit 1
fi

# 检测CentOS版本
if [ -f /etc/centos-release ]; then
    CENTOS_VERSION=$(cat /etc/centos-release | grep -oE '[0-9]+' | head -1)
    echo "✅ 检测到 CentOS $CENTOS_VERSION"
else
    echo "⚠️  未检测到CentOS系统，但仍将尝试安装..."
fi

# 更新系统
echo ""
echo "📦 更新系统包..."
yum update -y

# 安装必要工具
echo ""
echo "🔧 安装必要工具..."
yum install -y curl wget git

# 安装Node.js 20.x LTS
echo ""
echo "📦 安装 Node.js 20.x LTS..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
    yum install -y nodejs
    echo "✅ Node.js 安装完成"
    node -v
    npm -v
else
    echo "✅ Node.js 已安装"
    node -v
    npm -v
fi

# 安装PM2
echo ""
echo "📦 安装 PM2 进程管理器..."
if ! command -v pm2 &> /dev/null; then
    npm install -g pm2
    echo "✅ PM2 安装完成"
else
    echo "✅ PM2 已安装"
fi

# 创建应用目录
APP_DIR="/opt/twitter-monitor"
echo ""
echo "📁 设置应用目录: $APP_DIR"

if [ -d "$APP_DIR" ]; then
    echo "⚠️  目录已存在，将备份旧版本..."
    mv "$APP_DIR" "${APP_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
fi

mkdir -p "$APP_DIR"
cd "$APP_DIR"

# 克隆代码
echo ""
echo "📥 下载项目代码..."
git clone https://github.com/six8888-cpu/twitter-monitor.git .

# 安装依赖
echo ""
echo "📦 安装项目依赖..."
npm install

# 配置防火墙
echo ""
echo "🔥 配置防火墙规则..."
if command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-port=3000/tcp
    firewall-cmd --reload
    echo "✅ 防火墙端口 3000 已开放"
else
    echo "⚠️  未检测到firewalld，请手动开放3000端口"
fi

# 创建启动脚本
echo ""
echo "📝 创建系统服务..."

cat > /etc/systemd/system/twitter-monitor.service << 'EOF'
[Unit]
Description=Twitter Monitor Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/twitter-monitor
ExecStart=/usr/bin/node /opt/twitter-monitor/server.js
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=twitter-monitor
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

echo ""
echo "=========================================="
echo "  ✅ 安装完成！"
echo "=========================================="
echo ""
echo "📋 使用说明："
echo ""
echo "1️⃣  启动服务："
echo "   systemctl start twitter-monitor"
echo ""
echo "2️⃣  设置开机自启："
echo "   systemctl enable twitter-monitor"
echo ""
echo "3️⃣  查看服务状态："
echo "   systemctl status twitter-monitor"
echo ""
echo "4️⃣  查看日志："
echo "   journalctl -u twitter-monitor -f"
echo ""
echo "5️⃣  重启服务："
echo "   systemctl restart twitter-monitor"
echo ""
echo "6️⃣  停止服务："
echo "   systemctl stop twitter-monitor"
echo ""
echo "=========================================="
echo "  🌐 访问Web界面"
echo "=========================================="
echo ""
echo "打开浏览器访问："
echo "http://你的服务器IP:3000"
echo ""
echo "如果使用本机访问："
echo "http://localhost:3000"
echo ""
echo "=========================================="
echo "  ⚙️  配置系统"
echo "=========================================="
echo ""
echo "1. 访问Web界面"
echo "2. 点击'系统配置' -> '显示'"
echo "3. 填入以下信息："
echo "   - RapidAPI Key (从 rapidapi.com 获取)"
echo "   - Telegram Bot Token (从 @BotFather 获取)"
echo "   - Telegram Chat ID (从 @userinfobot 获取)"
echo "4. 保存配置并测试"
echo "5. 添加要监控的Twitter用户"
echo ""
echo "=========================================="
echo "  📚 更多帮助"
echo "=========================================="
echo ""
echo "项目地址: https://github.com/six8888-cpu/twitter-monitor"
echo "安装目录: $APP_DIR"
echo ""
echo "现在启动服务？[y/n]"
read -r start_now

if [ "$start_now" = "y" ] || [ "$start_now" = "Y" ]; then
    echo ""
    echo "🚀 启动服务..."
    systemctl start twitter-monitor
    systemctl enable twitter-monitor
    sleep 2
    systemctl status twitter-monitor
    echo ""
    echo "✅ 服务已启动并设置为开机自启！"
    echo "🌐 现在可以访问: http://$(hostname -I | awk '{print $1}'):3000"
else
    echo ""
    echo "稍后可以使用以下命令启动服务："
    echo "systemctl start twitter-monitor"
fi

echo ""
echo "=========================================="
echo "  🎉 安装完成，祝使用愉快！"
echo "=========================================="

