# Twitter监控系统 - 一键安装指南

## 📦 CentOS/RHEL 一键安装

### 安装命令

```bash
curl -fsSL https://raw.githubusercontent.com/six8888-cpu/twitter-monitor/main/install.sh | sudo bash
```

### 安装完成后

1. **访问Web界面**
   ```
   http://你的服务器IP:3000
   ```

2. **配置系统**
   - 点击 "系统配置" → "显示"
   - 填入 RapidAPI Key
   - 填入 Telegram Bot Token
   - 填入 Telegram Chat ID
   - 保存配置

3. **添加监控用户**
   - 在 "添加监控用户" 输入Twitter用户名
   - 点击 "添加"
   - 选择监控选项（新推文、回复、置顶、转发）

4. **开始监控**
   - 系统会自动每5分钟检查一次
   - 也可点击 "立即检查" 手动触发

## 🔧 服务管理命令

```bash
# 启动服务
systemctl start twitter-monitor

# 停止服务
systemctl stop twitter-monitor

# 重启服务
systemctl restart twitter-monitor

# 查看状态
systemctl status twitter-monitor

# 查看日志
journalctl -u twitter-monitor -f

# 开机自启
systemctl enable twitter-monitor
```

## 📋 获取API密钥

### RapidAPI Key
1. 访问：https://rapidapi.com/davethebeast/api/twitter241
2. 注册并订阅（有免费套餐）
3. 复制 API Key

### Telegram Bot Token
1. 在Telegram搜索：@BotFather
2. 发送：`/newbot`
3. 按提示创建机器人
4. 保存返回的Token

### Telegram Chat ID
1. 在Telegram搜索：@userinfobot
2. 发送任意消息
3. 机器人返回你的Chat ID

## 🆘 故障排查

### 查看日志
```bash
journalctl -u twitter-monitor -f
```

### 运行调试脚本
```bash
cd /opt/twitter-monitor
bash debug.sh
```

### 重置数据
```bash
# 清空监控用户
echo '[]' > /opt/twitter-monitor/data/monitored_users.json

# 清空缓存
echo '{}' > /opt/twitter-monitor/data/cache.json

# 重启服务
systemctl restart twitter-monitor
```

## 📞 支持

- GitHub: https://github.com/six8888-cpu/twitter-monitor
- 问题反馈: https://github.com/six8888-cpu/twitter-monitor/issues

