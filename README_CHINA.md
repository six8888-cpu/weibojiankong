# 🔍 网页监控系统 - 中国服务器优化版

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个功能强大的网页监控系统，支持关键词检测、Telegram通知、反爬虫绕过，特别针对中国服务器环境进行了优化。

## ✨ 主要特性

### 🎯 核心功能
- ✅ **网页监控** - 定时检测网页内容变化
- ✅ **关键词检测** - 支持精确匹配和模糊匹配
- ✅ **Telegram通知** - 实时推送监控结果
- ✅ **反爬虫绕过** - 使用Playwright模拟真实浏览器
- ✅ **可视化界面** - 美观的Web管理界面
- ✅ **数据持久化** - SQLite数据库存储

### 🚀 中国服务器优化
- ✅ **代理支持** - 网页端直接配置Telegram代理（HTTP/SOCKS5）
- ✅ **国内镜像** - 支持使用阿里云等国内镜像加速
- ✅ **长时间运行优化** - 内存管理、自动垃圾回收
- ✅ **日志自动清理** - 超过5条自动清空，防止日志堆积
- ✅ **健康检查** - 实时监控系统资源使用情况
- ✅ **进程管理** - 支持systemd、Gunicorn等生产环境部署
- ✅ **一键安装** - 自动化安装脚本，简化部署流程

## 📦 快速开始

### 方式一：一键安装（推荐）

```bash
# 下载项目
git clone <你的仓库地址>
cd <项目目录>

# 运行一键安装脚本
chmod +x install_china.sh
./install_china.sh

# 启动服务
./start.sh
```

### 方式二：Docker部署（即将支持）

```bash
docker pull your-image:latest
docker run -d -p 9527:9527 your-image:latest
```

### 方式三：手动安装

```bash
# 1. 安装依赖（使用国内镜像）
pip3 install -r requirements_china.txt -i https://mirrors.aliyun.com/pypi/simple/

# 2. 安装Playwright浏览器
python3 -m playwright install chromium

# 3. 初始化数据库
python3 -c "from database import Database; db = Database(); db.init_db()"

# 4. 启动服务
python3 app.py
```

## 🎨 界面预览

访问 `http://服务器IP:9527` 即可看到美观的管理界面：

- **监控列表** - 管理所有监控网址
- **关键词管理** - 配置检测关键词
- **监控日志** - 查看历史记录
- **Telegram配置** - 设置机器人和代理

## 📡 Telegram配置指南

### 1. 创建Telegram机器人

```
1. 在Telegram中搜索 @BotFather
2. 发送 /newbot 创建机器人
3. 按提示设置名称，获取 Bot Token
```

### 2. 获取Chat ID

```
1. 创建一个Telegram群组
2. 将机器人添加到群组
3. 在群组中发送任意消息
4. 访问：https://api.telegram.org/bot你的TOKEN/getUpdates
5. 找到 "chat":{"id":-1001234567890}
6. 复制这个负数ID
```

### 3. 配置代理（中国服务器必需）

在网页界面的"Telegram配置"页面填写：

```
代理地址示例：
- HTTP代理：http://127.0.0.1:7890
- SOCKS5代理：socks5://127.0.0.1:1080
```

常用代理软件：
- **V2Ray/Xray** - 本地端口通常为 1080 (SOCKS5) 或 10809 (HTTP)
- **Clash** - 本地端口通常为 7890 (HTTP) 或 7891 (SOCKS5)
- **Shadowsocks** - 本地端口通常为 1080

## 🔧 生产环境部署

### 使用Gunicorn（推荐）

```bash
chmod +x start_production.sh
./start_production.sh
```

### 使用systemd（开机自启）

```bash
# 安装服务
sudo mv /tmp/webmonitor.service /etc/systemd/system/
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start webmonitor
sudo systemctl enable webmonitor

# 查看状态
sudo systemctl status webmonitor
```

### 使用screen/tmux（简单方式）

```bash
# screen
screen -S webmonitor
python3 app.py
# Ctrl+A, D 退出

# tmux
tmux new -s webmonitor
python3 app.py
# Ctrl+B, D 退出
```

## 🔍 系统监控

### 查看日志

```bash
# 应用日志
tail -f monitor.log

# 系统服务日志
sudo journalctl -u webmonitor -f
```

### 健康检查

访问 API 端点：
```bash
curl http://localhost:9527/api/health
```

返回示例：
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "monitor_running": true,
    "urls_count": 5,
    "system": {
      "memory": {"rss_mb": 120.5, "percent": 15.2},
      "cpu": {"percent": 5.3},
      "uptime": {"formatted": "2天 5小时 30分钟"}
    }
  }
}
```

## 📊 性能优化

### 1. 自动日志清理

- ✅ 每次监控任务后自动清理
- ✅ 默认保留最新5条记录
- ✅ 可在网页端手动清理
- ✅ 防止日志无限增长

### 2. 内存管理

- ✅ 自动垃圾回收（GC）
- ✅ 内存使用监控
- ✅ 超过阈值自动优化
- ✅ Gunicorn worker自动重启

### 3. 数据库优化

```bash
# 定期优化数据库
sqlite3 monitor.db "VACUUM;"
sqlite3 monitor.db "ANALYZE;"
```

### 4. 系统资源限制

systemd配置：
- 内存限制：500MB
- CPU限制：50%

## 🛠️ 配置说明

### 监控配置

```python
# 在Web界面配置：
- 网址URL：要监控的网页地址
- 检查间隔：建议≥300秒（避免被封）
- 关键词：支持多个关键词
- 匹配模式：精确匹配 / 模糊匹配
```

### 高级配置

编辑 `config.example.yaml` 并重命名为 `config.yaml`：

```yaml
# 监控配置
monitor:
  default_interval: 300  # 默认检查间隔
  max_concurrent: 3      # 最大并发数
  timeout: 30            # 超时时间

# 浏览器配置
browser:
  headless: true
  user_agent: "..."
  locale: zh-CN
```

## 🐛 故障排查

### 问题1：Telegram发送失败

```bash
# 检查代理
curl -x http://127.0.0.1:7890 https://api.telegram.org

# 查看日志
tail -f monitor.log
```

### 问题2：内存占用过高

```bash
# 使用Gunicorn
./start_production.sh

# 查看资源
htop
```

### 问题3：端口被占用

```bash
# 查看端口
netstat -tlnp | grep 9527

# 修改端口（在app.py中）
app.run(host='0.0.0.0', port=你的端口, debug=False)
```

## 📝 更新日志

### v2.0 - 中国服务器优化版

#### 新增功能
- ✅ 网页端配置Telegram代理
- ✅ 日志自动清理（超过5条）
- ✅ 系统健康监控
- ✅ 内存自动管理
- ✅ 一键安装脚本
- ✅ Gunicorn生产部署
- ✅ systemd服务支持

#### 性能优化
- ✅ 数据库连接池
- ✅ 自动垃圾回收
- ✅ 守护线程优化
- ✅ 资源使用监控

#### 中国优化
- ✅ 国内镜像源支持
- ✅ 代理配置简化
- ✅ 部署文档完善
- ✅ 故障排查指南

## 🔒 安全建议

1. **修改默认端口**
2. **配置防火墙规则**
3. **设置IP白名单**（可选）
4. **使用Nginx反向代理**
5. **定期备份数据库**

## 📚 相关文档

- [完整部署指南](deploy_china.md)
- [API文档](API.md)（待补充）
- [常见问题](FAQ.md)（待补充）

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 开源协议

本项目采用 MIT 协议开源，详见 [LICENSE](LICENSE) 文件。

## 📮 联系方式

- Issues: [GitHub Issues](https://github.com/your-repo/issues)
- Email: your-email@example.com

## ⭐ Star History

如果这个项目对你有帮助，请给个Star⭐支持一下！

---

**特别提醒**：
1. 中国服务器使用Telegram**必须**配置代理
2. 推荐使用systemd管理服务，保证稳定运行
3. 定期检查日志和系统资源使用情况
4. 合理设置监控间隔，避免对目标网站造成压力

**祝您使用愉快！** 🎉
