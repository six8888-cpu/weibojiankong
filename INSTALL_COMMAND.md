# 🚀 Linux服务器一键安装命令

## 方式一：复制粘贴运行（最简单）

直接在Linux服务器执行以下命令：

```bash
cd /opt && git clone https://github.com/six8888-cpu/twitter-monitor.git weibo-monitor && cd weibo-monitor && chmod +x install.sh && ./install.sh
```

## 方式二：分步执行

```bash
# 1. 进入目录
cd /opt

# 2. 克隆代码
git clone https://github.com/six8888-cpu/twitter-monitor.git weibo-monitor

# 3. 进入项目
cd weibo-monitor

# 4. 运行安装
chmod +x install.sh
./install.sh
```

## 安装完成后启动

```bash
# 1. 启动服务
sudo systemctl start weibo-monitor
sudo systemctl enable weibo-monitor

# 2. 开放防火墙端口
sudo ufw allow 5000

# 3. 查看状态
sudo systemctl status weibo-monitor
```

## 访问Web界面配置

```
http://你的服务器IP:5000
```

### 在Web界面中完成配置（推荐）

1. **配置微博地址**
   - 在"监控配置"区域输入微博用户页面地址
   - 点击"保存配置"

2. **配置Telegram**（必须）
   - 在"Telegram配置"区域输入：
     - Bot Token（从 @BotFather 获取）
     - Chat ID（从 @userinfobot 获取）
   - 点击"保存配置"
   - 点击"测试连接"确认配置正确

3. **添加关键词**
   - 在"关键词管理"区域输入要监控的关键词
   - 点击"添加关键词"

4. **启动监控**
   - 点击"启动监控"按钮
   - 查看实时日志确认运行正常

### 或命令行配置（可选）

如果更喜欢命令行：
```bash
nano config.yaml
# 修改telegram配置后重启服务
sudo systemctl restart weibo-monitor
```

## 常用命令

```bash
# 查看日志
sudo journalctl -u weibo-monitor -f

# 重启服务
sudo systemctl restart weibo-monitor

# 停止服务
sudo systemctl stop weibo-monitor
```

---

**仓库地址：** https://github.com/six8888-cpu/twitter-monitor

**⚠️ 重要提醒：** 
你的GitHub Token已在聊天中暴露，建议立即在GitHub设置中删除这个token并重新生成新的！
访问：https://github.com/settings/tokens

