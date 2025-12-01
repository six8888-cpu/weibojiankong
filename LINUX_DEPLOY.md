# Linux服务器部署指南

## 快速部署步骤

### 1️⃣ 上传代码到服务器

```bash
# 方法1：使用git（推荐）
cd /opt
git clone <你的仓库地址> web-monitor
cd web-monitor

# 方法2：使用scp上传
# 在本地Windows执行：
scp -r D:\cursor\1 user@your-server:/opt/web-monitor
```

### 2️⃣ 运行自动安装脚本

```bash
cd /opt/web-monitor
chmod +x install.sh
sudo ./install.sh
```

安装脚本会自动：
- ✅ 安装Python 3和依赖
- ✅ 创建虚拟环境
- ✅ 安装所有Python包
- ✅ 安装Playwright浏览器
- ✅ 创建systemd服务（可选）

### 3️⃣ 启动服务

```bash
# 方法1：使用systemd服务（推荐）
sudo systemctl start web-monitor
sudo systemctl enable web-monitor  # 开机自启
sudo systemctl status web-monitor

# 方法2：手动启动
./start.sh
```

### 4️⃣ 配置防火墙

```bash
# 开放5000端口
sudo ufw allow 5000/tcp
# 或
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

### 5️⃣ 访问Web界面

```
http://your-server-ip:5000
```

---

## 详细部署步骤

### 一、准备服务器环境

**系统要求：**
- Ubuntu 20.04+ / Debian 10+ / CentOS 7+
- 1GB+ 内存
- 1核+ CPU
- 至少500MB可用磁盘空间

### 二、上传项目文件

#### 选项A：使用git（推荐）

1. 先在GitHub/Gitee创建仓库
2. 在Windows本地推送代码：

```bash
cd D:\cursor\1
git init
git add .
git commit -m "Initial commit"
git remote add origin <你的仓库地址>
git push -u origin main
```

3. 在Linux服务器拉取：

```bash
cd /opt
sudo git clone <你的仓库地址> web-monitor
sudo chown -R $USER:$USER web-monitor
cd web-monitor
```

#### 选项B：使用scp直接上传

在Windows PowerShell中：

```powershell
# 压缩文件（先压缩可以加快传输）
Compress-Archive -Path D:\cursor\1\* -DestinationPath D:\web-monitor.zip

# 上传到服务器
scp D:\web-monitor.zip user@your-server-ip:/tmp/

# 然后SSH登录服务器解压
ssh user@your-server-ip
cd /opt
sudo mkdir web-monitor
sudo chown $USER:$USER web-monitor
cd web-monitor
unzip /tmp/web-monitor.zip
```

#### 选项C：使用SFTP工具

推荐使用：
- **WinSCP**（Windows）
- **FileZilla**
- **XShell + XFTP**

直接拖拽上传整个文件夹到 `/opt/web-monitor`

### 三、运行自动安装脚本

```bash
cd /opt/web-monitor
chmod +x install.sh start.sh

# 运行安装（会询问是否创建systemd服务）
sudo ./install.sh
```

安装过程需要5-10分钟，主要时间花在下载Playwright浏览器上。

**安装过程中会询问：**
```
是否创建systemd服务？(y/n)
```

推荐选择 `y`，这样可以：
- 开机自动启动
- 服务崩溃自动重启
- 使用systemctl管理

### 四、启动应用

#### 方法1：使用systemd服务（推荐）

```bash
# 启动服务
sudo systemctl start web-monitor

# 查看状态
sudo systemctl status web-monitor

# 开机自启
sudo systemctl enable web-monitor

# 查看实时日志
sudo journalctl -u web-monitor -f

# 停止服务
sudo systemctl stop web-monitor

# 重启服务
sudo systemctl restart web-monitor
```

#### 方法2：手动启动

```bash
cd /opt/web-monitor
./start.sh
```

按 `Ctrl+C` 停止。

### 五、配置防火墙

#### Ubuntu/Debian (ufw)

```bash
# 检查防火墙状态
sudo ufw status

# 开放5000端口
sudo ufw allow 5000/tcp

# 如果防火墙未启用
sudo ufw enable
```

#### CentOS/RHEL (firewalld)

```bash
# 检查防火墙状态
sudo firewall-cmd --state

# 开放5000端口
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload

# 查看开放的端口
sudo firewall-cmd --list-ports
```

#### 云服务器安全组

如果使用阿里云、腾讯云、AWS等，还需要在控制台配置安全组规则：
- 添加入站规则
- 协议：TCP
- 端口：5000
- 来源：0.0.0.0/0（或指定IP）

### 六、验证部署

```bash
# 检查应用是否运行
ps aux | grep python

# 检查端口是否监听
netstat -tlnp | grep 5000
# 或
ss -tlnp | grep 5000

# 测试本地访问
curl http://localhost:5000

# 查看日志
tail -f /opt/web-monitor/monitor.log
```

### 七、访问Web界面

在浏览器中访问：
```
http://your-server-ip:5000
```

你应该能看到熟悉的监控界面，之前的配置需要重新添加。

---

## 进阶配置

### 1. 使用Nginx反向代理

#### 安装Nginx

```bash
sudo apt update
sudo apt install nginx
```

#### 创建配置文件

```bash
sudo nano /etc/nginx/sites-available/web-monitor
```

添加以下内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 改成你的域名或IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### 启用配置

```bash
sudo ln -s /etc/nginx/sites-available/web-monitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

现在可以通过 `http://your-domain.com` 访问（不需要端口号）。

### 2. 配置HTTPS（SSL证书）

#### 使用Let's Encrypt免费证书

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书并自动配置Nginx
sudo certbot --nginx -d your-domain.com

# 测试自动续期
sudo certbot renew --dry-run
```

### 3. 数据库备份

#### 创建备份脚本

```bash
nano /opt/web-monitor/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/web-monitor/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp /opt/web-monitor/monitor.db $BACKUP_DIR/monitor_$DATE.db

# 只保留最近30天的备份
find $BACKUP_DIR -name "monitor_*.db" -mtime +30 -delete
```

```bash
chmod +x /opt/web-monitor/backup.sh
```

#### 添加到crontab

```bash
crontab -e
```

添加一行（每天凌晨2点备份）：
```
0 2 * * * /opt/web-monitor/backup.sh
```

### 4. 监控日志管理

#### 清理旧日志

```bash
# 手动清理30天前的日志
sqlite3 /opt/web-monitor/monitor.db "DELETE FROM monitor_logs WHERE created_at < datetime('now', '-30 days');"

# 优化数据库
sqlite3 /opt/web-monitor/monitor.db "VACUUM;"
```

#### 自动清理（添加到crontab）

```bash
crontab -e
```

添加（每周日凌晨3点清理）：
```
0 3 * * 0 sqlite3 /opt/web-monitor/monitor.db "DELETE FROM monitor_logs WHERE created_at < datetime('now', '-30 days'); VACUUM;"
```

---

## 故障排查

### 应用无法启动

```bash
# 查看详细日志
sudo journalctl -u web-monitor -n 100

# 手动启动查看错误
cd /opt/web-monitor
source venv/bin/activate
python app.py
```

### 端口被占用

```bash
# 查看占用5000端口的进程
sudo lsof -i :5000

# 杀死进程
sudo kill -9 <PID>
```

### 浏览器启动失败

```bash
# 重新安装Playwright
cd /opt/web-monitor
source venv/bin/activate
playwright install chromium
playwright install-deps chromium
```

### 内存不足

```bash
# 创建swap空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久启用
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 无法访问Web界面

```bash
# 检查服务状态
sudo systemctl status web-monitor

# 检查端口
sudo netstat -tlnp | grep 5000

# 检查防火墙
sudo ufw status
sudo firewall-cmd --list-ports

# 测试本地访问
curl http://localhost:5000
```

---

## 性能优化

### 1. 使用Gunicorn（生产环境）

```bash
# 安装gunicorn
source venv/bin/activate
pip install gunicorn

# 启动（4个工作进程）
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

修改systemd服务文件：
```bash
sudo nano /etc/systemd/system/web-monitor.service
```

修改 `ExecStart` 行：
```ini
ExecStart=/opt/web-monitor/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

```bash
sudo systemctl daemon-reload
sudo systemctl restart web-monitor
```

### 2. 调整监控频率

根据实际需求在Web界面调整检查间隔：
- 新闻网站：300-600秒
- 电商网站：600-1800秒
- 公告页面：1800-3600秒

### 3. 限制资源使用

编辑systemd服务：
```bash
sudo nano /etc/systemd/system/web-monitor.service
```

添加资源限制：
```ini
[Service]
MemoryMax=512M
CPUQuota=50%
```

---

## 维护命令

```bash
# 查看服务状态
sudo systemctl status web-monitor

# 查看实时日志
sudo journalctl -u web-monitor -f

# 重启服务
sudo systemctl restart web-monitor

# 更新代码
cd /opt/web-monitor
git pull
sudo systemctl restart web-monitor

# 查看应用日志
tail -f /opt/web-monitor/monitor.log

# 查看数据库
sqlite3 /opt/web-monitor/monitor.db
.tables
SELECT * FROM monitor_urls;
.quit

# 备份数据库
cp /opt/web-monitor/monitor.db ~/monitor_backup_$(date +%Y%m%d).db
```

---

## 安全建议

1. **修改默认端口**：在 `.env` 文件中设置
2. **使用防火墙**：只开放必要端口
3. **配置HTTPS**：使用SSL证书加密传输
4. **定期更新**：更新系统和Python包
5. **限制访问**：通过Nginx配置IP白名单或HTTP认证

---

## 总结

完成以上步骤后，你的网页监控系统就成功部署到Linux服务器了！

**下一步：**
1. 访问 `http://your-server-ip:5000`
2. 重新配置Telegram
3. 添加监控网址和关键词
4. 启动监控任务

有问题随时查看日志：
```bash
sudo journalctl -u web-monitor -f
```

