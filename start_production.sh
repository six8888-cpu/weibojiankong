#!/bin/bash
# 生产环境启动脚本（使用Gunicorn）

echo "启动网页监控系统（生产模式）..."

# 检查gunicorn是否安装
if ! command -v gunicorn &> /dev/null; then
    echo "正在安装gunicorn..."
    pip3 install gunicorn -i https://mirrors.aliyun.com/pypi/simple/
fi

# 创建日志目录
mkdir -p logs

# 启动参数
WORKERS=2                    # 工作进程数（建议：CPU核心数 * 2 + 1）
THREADS=4                    # 每个进程的线程数
TIMEOUT=120                  # 超时时间（秒）
MAX_REQUESTS=1000            # 每个worker处理的最大请求数（防止内存泄漏）
MAX_REQUESTS_JITTER=100      # 随机抖动，避免所有worker同时重启
GRACEFUL_TIMEOUT=30          # 优雅关闭超时时间

# 启动Gunicorn
gunicorn app:app \
    --bind 0.0.0.0:9527 \
    --workers $WORKERS \
    --threads $THREADS \
    --timeout $TIMEOUT \
    --max-requests $MAX_REQUESTS \
    --max-requests-jitter $MAX_REQUESTS_JITTER \
    --graceful-timeout $GRACEFUL_TIMEOUT \
    --worker-class sync \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    --pid /tmp/webmonitor.pid \
    --daemon

if [ $? -eq 0 ]; then
    echo "✓ 服务已启动（后台运行）"
    echo "  访问地址：http://服务器IP:9527"
    echo "  进程ID文件：/tmp/webmonitor.pid"
    echo "  访问日志：logs/access.log"
    echo "  错误日志：logs/error.log"
    echo ""
    echo "停止服务："
    echo "  kill \$(cat /tmp/webmonitor.pid)"
else
    echo "✗ 服务启动失败，请检查错误日志"
    exit 1
fi
