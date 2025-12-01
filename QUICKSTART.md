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

### 第三步：启动服务

```bash
# 启动服务
sudo systemctl start weibo-monitor
sudo systemctl enable weibo-monitor

# 开放端口
sudo ufw allow 5000  # Ubuntu
# 或
sudo firewall-cmd --add-port=5000/tcp --permanent && sudo firewall-cmd --reload  # CentOS
```

## ✅ Web界面配置

浏览器打开：`http://你的服务器IP:5000`

**必须在Web界面完成以下配置：**

1. **配置Telegram**（必须）
   - 获取Bot Token: Telegram搜索 `@BotFather`，发送 `/newbot`
   - 获取Chat ID: Telegram搜索 `@userinfobot`，点击Start
   - 在"Telegram配置"填入Token和Chat ID
   - 点击"保存配置"
   - 点击"测试连接"验证

2. **添加关键词**
   - 在"关键词管理"输入关键词
   - 点击"添加关键词"

3. **启动监控**
   - 点击"启动监控"按钮
   - 查看日志确认运行正常

## 🎯 完成！

系统已经开始监控，发现关键词会自动发送Telegram通知。

详细文档见：[DEPLOY.md](DEPLOY.md)
