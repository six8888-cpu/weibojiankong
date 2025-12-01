# 香港服务器一键部署指南

本指南将帮助你在香港服务器上快速部署微博监控系统。

## 🚀 一键安装

### 1. 上传代码到服务器

```bash
# 方式1: 使用Git（推荐）
cd /opt
git clone <你的仓库地址> weibo-monitor
cd weibo-monitor

# 方式2: 使用SCP上传
# 在本地执行：
scp -r ./* root@你的服务器IP:/opt/weibo-monitor/
```

### 2. 运行一键安装脚本

```bash
cd /opt/weibo-monitor
chmod +x install.sh
./install.sh
```

安装脚本将自动：
- ✅ 检测操作系统
- ✅ 更新系统软件包
- ✅ 安装Python3和pip
- ✅ 安装Chrome浏览器
- ✅ 创建Python虚拟环境
- ✅ 安装所有依赖包（使用国内镜像加速）
- ✅ 创建systemd系统服务

### 3. 配置系统

编辑配置文件：
```bash
nano config.yaml
```

**必须配置的项：**

```yaml
# 微博地址
weibo_url: "https://weibo.com/u/2656274875"

# 关键词（在Web界面也可以管理）
keywords:
  - "你的关键词1"
  - "你的关键词2"

# Telegram配置
telegram:
  bot_token: "你的BOT_TOKEN"  # 从 @BotFather 获取
  chat_id: "你的CHAT_ID"      # 从 @userinfobot 获取
```

### 4. 启动服务

**方式1：使用systemd（推荐，开机自启）**
```bash
sudo systemctl start weibo-monitor
sudo systemctl enable weibo-monitor  # 开机自启
sudo systemctl status weibo-monitor  # 查看状态
```

**方式2：使用启动脚本**
```bash
chmod +x start.sh stop.sh restart.sh
./start.sh
```

### 5. 访问Web管理界面

打开浏览器访问：
```
http://你的服务器IP:5000
```

在Web界面中可以：
- ✅ 实时查看监控状态
- ✅ 添加/删除/修改关键词
- ✅ 修改配置
- ✅ 启动/停止监控
- ✅ 查看运行日志
- ✅ 测试Telegram连接

### 6. 开放防火墙端口

**Ubuntu/Debian:**
```bash
sudo ufw allow 5000
sudo ufw reload
```

**CentOS:**
```bash
sudo firewall-cmd --add-port=5000/tcp --permanent
sudo firewall-cmd --reload
```

**云服务器：**
还需要在云服务商的控制台安全组中开放5000端口

## 📱 获取Telegram配置

### 创建Telegram Bot

1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 按提示设置Bot名称和用户名
4. 获取Bot Token（格式：`1234567890:ABCdef...`）

### 获取Chat ID

1. 在Telegram中搜索 `@userinfobot`
2. 点击"Start"
3. 获取你的Chat ID（一串数字）

或者：
1. 给你的Bot发送一条消息
2. 访问：`https://api.telegram.org/bot<你的TOKEN>/getUpdates`
3. 找到JSON中的chat id

## 🔧 常用命令

### systemd服务管理

```bash
# 启动服务
sudo systemctl start weibo-monitor

# 停止服务
sudo systemctl stop weibo-monitor

# 重启服务
sudo systemctl restart weibo-monitor

# 查看状态
sudo systemctl status weibo-monitor

# 开机自启
sudo systemctl enable weibo-monitor

# 取消自启
sudo systemctl disable weibo-monitor

# 查看日志
sudo journalctl -u weibo-monitor -f

# 查看最近100行日志
sudo journalctl -u weibo-monitor -n 100
```

### 手动启动方式

```bash
# 启动
./start.sh

# 停止
./stop.sh

# 重启
./restart.sh

# 查看日志
tail -f logs/server.log
tail -f weibo_monitor.log
```

## 📊 监控检查

### 检查服务是否正常运行

```bash
# 方式1
sudo systemctl status weibo-monitor

# 方式2
ps aux | grep web_server.py

# 方式3
curl http://localhost:5000
```

### 检查端口是否监听

```bash
sudo netstat -tlnp | grep 5000
# 或
sudo ss -tlnp | grep 5000
```

### 测试Telegram连接

在Web界面中点击"测试连接"按钮，或运行：
```bash
source venv/bin/activate
python -c "
from telegram import Bot
bot = Bot(token='你的TOKEN')
bot.send_message(chat_id='你的CHAT_ID', text='测试消息')
"
```

## 🔍 故障排查

### 服务无法启动

1. 查看详细日志：
```bash
sudo journalctl -u weibo-monitor -n 50 --no-pager
```

2. 检查配置文件：
```bash
python -c "import yaml; print(yaml.safe_load(open('config.yaml')))"
```

3. 手动测试：
```bash
source venv/bin/activate
python web_server.py
```

### Chrome驱动问题

如果出现ChromeDriver错误：
```bash
# 卸载旧版本
pip uninstall undetected-chromedriver

# 重新安装
pip install undetected-chromedriver
```

### Telegram发送失败

1. 检查Token和Chat ID是否正确
2. 确认已给Bot发送过消息
3. 香港服务器通常不需要代理
4. 检查网络连接：`curl https://api.telegram.org`

### Web界面无法访问

1. 检查服务是否运行
2. 检查防火墙设置
3. 检查云服务商安全组
4. 检查config.yaml中host是否为"0.0.0.0"

## 📦 更新系统

```bash
# 停止服务
sudo systemctl stop weibo-monitor

# 更新代码（如果使用Git）
git pull

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt -U

# 重启服务
sudo systemctl start weibo-monitor
```

## 🔒 安全建议

1. **使用防火墙**：只开放必要的端口
2. **使用HTTPS**：配置Nginx反向代理+SSL证书
3. **设置访问密码**：可以用Nginx添加Basic Auth
4. **定期更新**：保持系统和依赖包最新
5. **备份配置**：定期备份config.yaml和notified_weibo.txt

## 🌐 Nginx反向代理（可选）

如果想使用域名+HTTPS访问：

```nginx
server {
    listen 80;
    server_name monitor.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

然后使用Let's Encrypt配置SSL：
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d monitor.yourdomain.com
```

## 💡 性能优化

### 调整监控间隔

在config.yaml中修改：
```yaml
monitor:
  check_interval: 1  # 分钟，根据需求调整
```

### 使用无头模式

```yaml
monitor:
  headless: true  # 后台运行，节省资源
```

### 限制日志大小

```bash
# 编辑systemd服务
sudo systemctl edit weibo-monitor

# 添加：
[Service]
StandardOutput=journal
StandardError=journal
```

## 📞 技术支持

- 查看README.md了解更多功能
- 查看日志文件排查问题
- 检查config.yaml配置是否正确

---

**提示**：首次部署建议先手动启动测试，确认无误后再配置systemd服务。

