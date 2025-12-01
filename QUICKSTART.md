# ⚡ 快速开始 - 5分钟部署指南

适用于香港/海外服务器的快速部署

## 📋 前置要求

- Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- Root或sudo权限
- 服务器可访问外网

## 🚀 三步部署

### 第一步：上传代码

```bash
cd /opt
git clone <你的仓库> weibo-monitor
cd weibo-monitor
```

### 第二步：一键安装

```bash
chmod +x install.sh
./install.sh
```

等待安装完成（约5-10分钟）

### 第三步：配置并启动

1. 编辑配置：
```bash
nano config.yaml
```

2. 修改以下内容：
```yaml
telegram:
  bot_token: "替换为你的Token"
  chat_id: "替换为你的ChatID"
```

3. 启动服务：
```bash
sudo systemctl start weibo-monitor
sudo systemctl enable weibo-monitor
```

4. 开放端口：
```bash
sudo ufw allow 5000  # Ubuntu
# 或
sudo firewall-cmd --add-port=5000/tcp --permanent && sudo firewall-cmd --reload  # CentOS
```

## ✅ 访问系统

浏览器打开：`http://你的服务器IP:5000`

在Web界面中可以：
- 添加监控关键词
- 启动/停止监控
- 查看实时日志
- 修改配置

## 🎯 完成！

系统已经开始监控，发现关键词会自动发送Telegram通知。

详细文档见：[DEPLOY.md](DEPLOY.md)
