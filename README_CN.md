# 🔍 微博关键词监控系统 - Web版

一个功能强大的微博监控工具，支持Web界面管理，关键词模糊匹配，Telegram实时通知。

## ✨ 特点

- 🌐 **Web管理界面** - 美观的可视化管理面板
- 🎯 **关键词管理** - Web界面添加/删除/编辑关键词，支持模糊匹配
- 📱 **Telegram通知** - 实时推送匹配的微博内容  
- 🤖 **智能反爬** - 使用undetected-chromedriver绕过检测
- ⚡ **高频监控** - 1分钟检查一次（可配置）
- 📊 **实时监控** - 查看监控状态、日志、统计数据
- 🔄 **自动去重** - 避免重复通知
- 🚀 **一键部署** - 适配香港/海外服务器

## 📸 界面预览

Web管理界面包含：
- 监控状态面板（运行状态、检查次数、匹配次数）
- 关键词管理（添加、编辑、删除）
- 配置管理（微博地址、Telegram配置、检查间隔）
- 实时日志查看
- 一键启动/停止监控

## 🚀 快速部署（香港服务器）

### 一键安装

```bash
# 1. 克隆代码
git clone <仓库地址> && cd weibo-monitor

# 2. 运行安装脚本
chmod +x install.sh && ./install.sh

# 3. 编辑配置
nano config.yaml

# 4. 启动服务
sudo systemctl start weibo-monitor
sudo systemctl enable weibo-monitor

# 5. 开放端口
sudo ufw allow 5000
```

### 访问管理界面

```
http://你的服务器IP:5000
```

详细部署文档：[DEPLOY.md](DEPLOY.md)  
快速开始：[QUICKSTART.md](QUICKSTART.md)

## 📦 项目结构

```
weibo-monitor/
├── web_server.py           # Web服务器（Flask后端）
├── weibo_monitor.py        # 监控核心逻辑
├── config.yaml             # 配置文件
├── requirements.txt        # Python依赖
├── install.sh             # 一键安装脚本
├── start.sh               # 启动脚本
├── stop.sh                # 停止脚本
├── restart.sh             # 重启脚本
├── templates/
│   └── index.html         # Web前端界面
├── static/                # 静态资源
├── logs/                  # 日志目录
└── README.md             # 说明文档
```

## ⚙️ 配置说明

### config.yaml

```yaml
# 监控地址
weibo_url: "https://weibo.com/u/2656274875"

# 关键词（也可在Web界面管理）
keywords:
  - "关键词1"
  - "关键词2"

# Telegram配置
telegram:
  bot_token: "你的TOKEN"
  chat_id: "你的CHAT_ID"
  proxy_url: ""  # 香港服务器留空

# 监控设置
monitor:
  check_interval: 1  # 分钟
  headless: true     # 无头模式
  
# Web服务器
web:
  host: "0.0.0.0"   # 允许外网访问
  port: 5000
```

## 🎯 使用方法

### 1. Web界面管理（推荐）

访问 `http://服务器IP:5000`，在界面中：

1. **添加关键词**：在"关键词管理"区域输入关键词并添加
2. **编辑关键词**：点击"编辑"按钮修改
3. **删除关键词**：点击"删除"按钮移除
4. **启动监控**：点击"启动监控"按钮
5. **查看日志**：实时查看运行日志

### 2. 命令行管理

```bash
# 启动
sudo systemctl start weibo-monitor

# 停止  
sudo systemctl stop weibo-monitor

# 重启
sudo systemctl restart weibo-monitor

# 查看状态
sudo systemctl status weibo-monitor

# 查看日志
sudo journalctl -u weibo-monitor -f
```

## 📱 Telegram配置

### 创建Bot

1. Telegram搜索 `@BotFather`
2. 发送 `/newbot`
3. 按提示设置名称
4. 获取Token

### 获取Chat ID

1. Telegram搜索 `@userinfobot`  
2. 点击Start
3. 获取你的ID

## 🔧 API接口

后端提供RESTful API：

```
GET  /api/config           # 获取配置
POST /api/config           # 更新配置
GET  /api/keywords         # 获取关键词列表
POST /api/keywords         # 添加关键词
PUT  /api/keywords/<id>    # 更新关键词
DELETE /api/keywords/<id>  # 删除关键词
POST /api/monitor/start    # 启动监控
POST /api/monitor/stop     # 停止监控
GET  /api/monitor/status   # 获取状态
GET  /api/logs             # 获取日志
POST /api/test/telegram    # 测试Telegram
```

## 🛠️ 技术栈

- **后端**: Python + Flask
- **前端**: 原生JavaScript + CSS3
- **爬虫**: Selenium + undetected-chromedriver
- **解析**: BeautifulSoup4
- **通知**: python-telegram-bot
- **调度**: schedule

## 🔒 安全建议

1. 使用防火墙限制端口访问
2. 配置Nginx反向代理+SSL
3. 定期更新依赖包
4. 不要暴露敏感配置

## 📊 系统要求

- **系统**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **内存**: 最低1GB，推荐2GB+
- **CPU**: 1核心+
- **硬盘**: 5GB+
- **网络**: 能访问微博和Telegram

## 🐛 故障排查

### 服务无法启动

```bash
# 查看日志
sudo journalctl -u weibo-monitor -n 50

# 手动测试
source venv/bin/activate
python web_server.py
```

### Chrome驱动问题

```bash
pip uninstall undetected-chromedriver
pip install undetected-chromedriver
```

### Web界面无法访问

1. 检查服务状态：`sudo systemctl status weibo-monitor`
2. 检查端口：`sudo netstat -tlnp | grep 5000`
3. 检查防火墙：`sudo ufw status`
4. 检查安全组（云服务器）

详细排查见：[DEPLOY.md](DEPLOY.md#故障排查)

## 📝 更新日志

### v2.0.0 (2025-12-01)
- ✨ 新增Web管理界面
- ✨ 支持在线管理关键词
- ✨ 实时监控状态查看
- ✨ 在线日志查看
- 🎯 优化为1分钟检查间隔
- 🚀 一键部署脚本
- 📱 Telegram代理支持

### v1.0.0
- 基础监控功能
- 命令行配置

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## ⚠️ 免责声明

本工具仅供学习交流使用，请遵守微博使用条款，不要过度频繁访问。使用者需自行承担使用风险。

---

**Made with ❤️ for monitoring Weibo**

