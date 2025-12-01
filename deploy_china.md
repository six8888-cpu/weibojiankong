# 中国服务器部署指南

## 🚀 快速部署

### 方式一：一键安装（推荐）

```bash
# 1. 克隆或上传项目到服务器
cd /opt
git clone <你的仓库地址>
cd <项目目录>

# 2. 运行一键安装脚本
chmod +x install_china.sh
./install_china.sh

# 3. 启动服务
./start.sh
```

### 方式二：手动安装

```bash
# 1. 安装Python依赖（使用国内镜像）
pip3 install -r requirements_china.txt -i https://mirrors.aliyun.com/pypi/simple/

# 2. 安装Playwright浏览器
python3 -m playwright install chromium

# 3. 初始化数据库
python3 -c "from database import Database; db = Database(); db.init_db()"

# 4. 启动服务
python3 app.py
```

## 📋 系统要求

- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- **Python**: 3.8+
- **内存**: 最低512MB，推荐1GB+
- **磁盘**: 500MB+
- **端口**: 9527（可在app.py中修改）

## 🔧 生产环境部署

### 使用Gunicorn（推荐）

```bash
# 启动生产服务
chmod +x start_production.sh
./start_production.sh

# 停止服务
kill $(cat /tmp/webmonitor.pid)
```

### 使用systemd（开机自启）

```bash
# 1. 安装服务
sudo mv /tmp/webmonitor.service /etc/systemd/system/
sudo systemctl daemon-reload

# 2. 启动服务
sudo systemctl start webmonitor
sudo systemctl enable webmonitor  # 开机自启

# 3. 查看状态
sudo systemctl status webmonitor

# 4. 查看日志
sudo journalctl -u webmonitor -f
```

### 使用screen或tmux（简单方式）

```bash
# 使用screen
screen -S webmonitor
python3 app.py
# 按 Ctrl+A 然后按 D 退出screen
# 恢复：screen -r webmonitor

# 使用tmux
tmux new -s webmonitor
python3 app.py
# 按 Ctrl+B 然后按 D 退出tmux
# 恢复：tmux attach -t webmonitor
```

## 🌐 Nginx反向代理（可选）

如果需要使用域名或80端口访问：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:9527;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持（如果未来需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

## 📡 Telegram代理配置

### 方式一：网页端配置（推荐）

1. 访问系统网页界面
2. 进入"Telegram配置"标签页
3. 填写代理地址，例如：
   - HTTP代理：`http://127.0.0.1:7890`
   - SOCKS5代理：`socks5://127.0.0.1:1080`

### 方式二：环境变量配置

```bash
# 设置系统代理
export HTTP_PROXY="http://127.0.0.1:7890"
export HTTPS_PROXY="http://127.0.0.1:7890"

# 启动应用
python3 app.py
```

### 常用代理软件

1. **V2Ray / Xray**
   ```bash
   # 安装
   bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)
   
   # 配置文件：/usr/local/etc/v2ray/config.json
   # 本地SOCKS端口：1080
   # 本地HTTP端口：10809
   ```

2. **Clash**
   ```bash
   # 下载
   wget https://github.com/Dreamacro/clash/releases/download/v1.18.0/clash-linux-amd64-v1.18.0.gz
   gunzip clash-linux-amd64-v1.18.0.gz
   chmod +x clash-linux-amd64-v1.18.0
   
   # 运行
   ./clash-linux-amd64-v1.18.0 -d .
   # 本地SOCKS端口：7891
   # 本地HTTP端口：7890
   ```

## 🔍 监控和维护

### 查看日志

```bash
# 应用日志
tail -f monitor.log

# 系统服务日志
sudo journalctl -u webmonitor -f

# Gunicorn日志
tail -f logs/error.log
tail -f logs/access.log
```

### 监控资源使用

```bash
# 查看进程
ps aux | grep python

# 查看内存使用
free -h

# 查看磁盘使用
df -h

# 实时监控
htop
```

### 数据库备份

```bash
# 备份数据库
cp monitor.db monitor.db.backup.$(date +%Y%m%d)

# 定时备份（添加到crontab）
0 2 * * * cp /path/to/monitor.db /path/to/backups/monitor.db.$(date +\%Y\%m\%d)
```

## ⚡ 性能优化

### 1. 日志自动清理

程序已内置日志自动清理功能：
- 每次监控任务执行后，自动清理旧日志
- 默认保留最新5条记录
- 也可在网页端手动清理

### 2. 数据库优化

```bash
# 定期优化数据库
sqlite3 monitor.db "VACUUM;"
sqlite3 monitor.db "ANALYZE;"
```

### 3. 系统资源限制

在systemd服务中已配置：
- 内存限制：500MB
- CPU限制：50%

### 4. Gunicorn自动重启

配置了`--max-requests 1000`，每处理1000个请求后自动重启worker，防止内存泄漏。

## 🔒 安全建议

1. **修改默认端口**
   ```python
   # 在app.py中修改
   app.run(host='0.0.0.0', port=你的端口, debug=False)
   ```

2. **使用防火墙**
   ```bash
   # UFW
   sudo ufw allow 9527/tcp
   sudo ufw enable
   
   # firewalld
   sudo firewall-cmd --permanent --add-port=9527/tcp
   sudo firewall-cmd --reload
   ```

3. **限制访问IP（可选）**
   ```python
   # 在app.py中添加IP白名单
   from flask import request, abort
   
   ALLOWED_IPS = ['your.ip.address']
   
   @app.before_request
   def limit_remote_addr():
       if request.remote_addr not in ALLOWED_IPS:
           abort(403)
   ```

## 🐛 故障排查

### 问题1：Telegram发送失败

**解决方案：**
1. 检查代理配置是否正确
2. 测试代理连接：`curl -x http://127.0.0.1:7890 https://api.telegram.org`
3. 查看日志：`tail -f monitor.log`

### 问题2：Playwright安装失败

**解决方案：**
```bash
# 方法1：配置代理
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
python3 -m playwright install chromium

# 方法2：手动下载
# 从国内镜像站下载浏览器文件，然后手动安装
```

### 问题3：服务无法启动

**解决方案：**
```bash
# 检查端口占用
netstat -tlnp | grep 9527

# 检查Python版本
python3 --version

# 检查依赖
pip3 list | grep -E "Flask|APScheduler"

# 查看详细错误
python3 app.py
```

### 问题4：内存占用过高

**解决方案：**
1. 使用Gunicorn替代Flask自带服务器
2. 配置systemd内存限制
3. 检查日志数量，及时清理
4. 减少监控URL数量或增加检查间隔

## 📞 技术支持

如遇到问题，请查看：
1. 日志文件：`monitor.log`
2. 系统日志：`sudo journalctl -u webmonitor`
3. Python错误：直接运行`python3 app.py`查看详细错误

## 🎯 最佳实践

1. ✅ 使用systemd管理服务
2. ✅ 配置Nginx反向代理
3. ✅ 定期备份数据库
4. ✅ 监控系统资源
5. ✅ 配置日志轮转
6. ✅ 使用代理访问Telegram
7. ✅ 设置合理的检查间隔（建议≥300秒）

---

部署完成后，访问 `http://服务器IP:9527` 开始使用！
