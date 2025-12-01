#!/bin/bash
# 中国服务器一键安装脚本（使用虚拟环境）

echo "======================================"
echo "  网页监控系统 - 中国服务器安装脚本  "
echo "======================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Python版本
echo -e "${YELLOW}[1/8] 检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误：未找到Python3，正在安装...${NC}"
    sudo yum install -y python3 python3-pip
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✓ Python版本: $PYTHON_VERSION${NC}"

# 创建虚拟环境
echo -e "${YELLOW}[2/8] 创建Python虚拟环境...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ 虚拟环境创建成功${NC}"
else
    echo -e "${GREEN}✓ 虚拟环境已存在${NC}"
fi

# 激活虚拟环境
source venv/bin/activate

# 升级pip（使用国内镜像）
echo -e "${YELLOW}[3/8] 升级pip（使用阿里云镜像）...${NC}"
pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ --quiet

# 安装依赖
echo -e "${YELLOW}[4/8] 安装Python依赖（使用阿里云镜像）...${NC}"
echo "这可能需要几分钟时间，请耐心等待..."
pip install -r requirements_china.txt -i https://mirrors.aliyun.com/pypi/simple/

if [ $? -ne 0 ]; then
    echo -e "${RED}错误：依赖安装失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python依赖已安装${NC}"

# 安装Playwright浏览器（使用国内镜像）
echo -e "${YELLOW}[5/8] 安装Playwright浏览器...${NC}"
echo "提示：如果下载速度慢，请配置代理环境变量 HTTP_PROXY 和 HTTPS_PROXY"
python -m playwright install chromium

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}警告：Playwright浏览器安装可能失败，如需使用反爬功能请手动安装${NC}"
fi

# 初始化数据库
echo -e "${YELLOW}[6/8] 初始化数据库...${NC}"
python -c "from database import Database; db = Database(); db.init_db()"
echo -e "${GREEN}✓ 数据库已初始化${NC}"

# 退出虚拟环境
deactivate

# 创建启动脚本
echo -e "${YELLOW}[7/8] 创建启动脚本...${NC}"
cat > start.sh << 'STARTEOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python app.py
STARTEOF

chmod +x start.sh

cat > start_production.sh << 'PRODEOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

if ! command -v gunicorn &> /dev/null; then
    echo "安装gunicorn..."
    pip install gunicorn -i https://mirrors.aliyun.com/pypi/simple/
fi

mkdir -p logs

gunicorn app:app \
    --bind 0.0.0.0:9527 \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --graceful-timeout 30 \
    --worker-class sync \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    --pid /tmp/webmonitor.pid \
    --daemon

if [ $? -eq 0 ]; then
    echo "✓ 服务已启动（后台运行）"
    echo "  访问地址：http://服务器IP:9527"
    echo "停止服务：kill \$(cat /tmp/webmonitor.pid)"
fi
PRODEOF

chmod +x start_production.sh
echo -e "${GREEN}✓ 启动脚本已创建${NC}"

# 创建systemd服务文件
echo -e "${YELLOW}[8/8] 创建systemd服务（可选）...${NC}"
cat > /tmp/webmonitor.service << EOF
[Unit]
Description=Web Monitor Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$(pwd)/venv/bin/python $(pwd)/app.py
Restart=always
RestartSec=10

# 资源限制（防止内存泄漏）
MemoryLimit=500M
CPUQuota=50%

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ systemd服务文件已创建在 /tmp/webmonitor.service${NC}"
echo ""
echo -e "${YELLOW}如需安装为系统服务，请执行：${NC}"
echo "  sudo mv /tmp/webmonitor.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable webmonitor"
echo "  sudo systemctl start webmonitor"
echo ""

# 设置权限
chmod +x start.sh

echo ""
echo -e "${GREEN}======================================"
echo "       安装完成！"
echo "======================================${NC}"
echo ""
echo "启动方式："
echo "  1. 开发模式：./start.sh"
echo "  2. 生产模式：./start_production.sh"
echo "  3. 系统服务：sudo systemctl start webmonitor"
echo ""
echo "访问地址：http://服务器IP:9527"
echo ""
echo -e "${YELLOW}重要提示：${NC}"
echo "  - 如果使用Telegram，请在网页端配置代理地址"
echo "  - 推荐使用 screen 或 tmux 保持程序后台运行"
echo "  - 服务器需要开放9527端口"
echo ""
echo -e "${GREEN}祝您使用愉快！${NC}"
