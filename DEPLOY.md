# 部署指南

## 🚀 Linux服务器部署

### 1. 准备服务器

推荐配置：
- CPU: 1核+
- 内存: 1GB+
- 系统: Ubuntu 20.04+ / Debian 10+ / CentOS 7+
- Python: 3.8+

### 2. 上传代码

```bash
# 方法1：使用git
git clone <repository_url> /opt/web-monitor
cd /opt/web-monitor

# 方法2：使用scp上传
scp -r web-monitor/ user@server:/opt/web-monitor
```

### 3. 运行安装脚本

```bash
cd /opt/web-monitor
chmod +x install.sh
sudo ./install.sh
```

安装脚本会询问是否创建systemd服务，选择 `y`。

### 4. 启动服务

```bash
# 启动服务
sudo systemctl start web-monitor

# 查看状态
sudo systemctl status web-monitor

# 开机自启
sudo systemctl enable web-monitor
```

### 5. 配置防火墙

```bash
# UFW防火墙
sudo ufw allow 5000/tcp

# firewalld防火墙
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload

# iptables
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
```

### 6. 访问服务

在浏览器中访问：`http://服务器IP:5000`

## 🔒 使用Nginx反向代理

### 1. 安装Nginx

```bash
sudo apt update
sudo apt install nginx
```

### 2. 创建配置文件

```bash
sudo nano /etc/nginx/sites-available/web-monitor
```

添加以下内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 修改为你的域名

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. 启用配置

```bash
sudo ln -s /etc/nginx/sites-available/web-monitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. 配置HTTPS（可选）

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

## 🐳 使用Docker部署（可选）

### 1. 创建Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装Playwright浏览器
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

# 暴露端口
EXPOSE 5000

# 启动应用
CMD ["python", "app.py"]
```

### 2. 创建docker-compose.yml

```yaml
version: '3.8'

services:
  web-monitor:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./monitor.db:/app/monitor.db
      - ./monitor.log:/app/monitor.log
    restart: always
    environment:
      - FLASK_HOST=0.0.0.0
      - FLASK_PORT=5000
```

### 3. 构建并运行

```bash
docker-compose up -d
```

## 📊 监控和维护

### 查看日志

```bash
# systemd服务日志
sudo journalctl -u web-monitor -f

# 应用日志
tail -f /opt/web-monitor/monitor.log

# Docker日志
docker-compose logs -f
```

### 重启服务

```bash
# systemd
sudo systemctl restart web-monitor

# Docker
docker-compose restart
```

### 备份数据

```bash
# 备份数据库
cp /opt/web-monitor/monitor.db /backup/monitor.db.$(date +%Y%m%d)

# 定时备份（添加到crontab）
0 2 * * * cp /opt/web-monitor/monitor.db /backup/monitor.db.$(date +\%Y\%m\%d)
```

## 🔧 性能优化

### 1. 使用Gunicorn

```bash
# 安装gunicorn
pip install gunicorn

# 启动（4个工作进程）
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

修改systemd服务文件：

```ini
[Service]
ExecStart=/opt/web-monitor/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 2. 调整监控频率

- 根据实际需求调整检查间隔
- 避免同时监控过多网址
- 错峰执行不同网址的监控

### 3. 数据库维护

```bash
# 定期清理旧日志
sqlite3 monitor.db "DELETE FROM monitor_logs WHERE created_at < datetime('now', '-30 days');"

# 优化数据库
sqlite3 monitor.db "VACUUM;"
```

## 🔐 安全建议

1. **修改默认端口**
   - 在`.env`中设置非5000端口

2. **使用防火墙**
   - 只开放必要的端口
   - 限制访问来源IP

3. **使用HTTPS**
   - 通过Nginx配置SSL证书

4. **定期更新**
   - 更新Python依赖包
   - 更新系统软件包

5. **限制访问**
   - 配置HTTP基本认证
   - 或使用VPN访问

## 📱 远程访问

### 方法1：使用域名

1. 购买域名
2. 配置DNS解析到服务器IP
3. 配置Nginx反向代理
4. 配置SSL证书

### 方法2：使用内网穿透

使用frp、ngrok等工具实现内网穿透。

### 方法3：使用VPN

通过VPN连接到服务器所在网络。

## 🆘 故障排查

### 服务无法启动

```bash
# 查看详细错误
sudo systemctl status web-monitor
sudo journalctl -u web-monitor -n 50

# 检查端口占用
sudo netstat -tlnp | grep 5000

# 手动启动测试
cd /opt/web-monitor
source venv/bin/activate
python app.py
```

### 内存不足

```bash
# 查看内存使用
free -h

# 重启服务释放内存
sudo systemctl restart web-monitor

# 增加swap空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 浏览器启动失败

```bash
# 重新安装Playwright浏览器
source venv/bin/activate
playwright install chromium
playwright install-deps chromium
```

---

如有其他问题，请查看日志文件或提交Issue。

