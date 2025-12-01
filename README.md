# 微博关键词监控程序

这是一个自动监控指定微博用户主页的Python脚本，当检测到包含特定关键词的微博时，会通过Telegram发送通知提醒。

## 功能特点

- ✅ 自动监控指定微博用户的最新内容
- ✅ 支持多个关键词监控
- ✅ 通过Telegram Bot发送实时通知
- ✅ 使用无头浏览器绕过反爬机制
- ✅ 自动去重，避免重复通知
- ✅ 可配置检查间隔
- ✅ 完整的日志记录

## 系统要求

- Python 3.7+
- Google Chrome 浏览器
- 稳定的网络连接

## 安装步骤

### 1. 克隆或下载项目

```bash
# 进入项目目录
cd weibo-monitor
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置Telegram Bot

#### 3.1 创建Telegram Bot

1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 按照提示设置Bot名称和用户名
4. 创建成功后，BotFather会给你一个Token，类似：`1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
5. 保存这个Token

#### 3.2 获取Chat ID

1. 在Telegram中搜索 `@userinfobot`
2. 点击开始（Start）
3. Bot会返回你的用户信息，其中包含你的Chat ID
4. 保存这个Chat ID（是一个数字，可能是正数或负数）

**或者使用以下方法：**

1. 先给你的Bot发送任意一条消息
2. 在浏览器中访问：`https://api.telegram.org/bot<你的BOT_TOKEN>/getUpdates`
3. 在返回的JSON中找到 `"chat":{"id":123456789}` 的部分
4. 这个id就是你的Chat ID

### 4. 配置程序

编辑 `config.yaml` 文件：

```yaml
# 要监控的微博用户页面URL
weibo_url: "https://weibo.com/u/2656274875"

# 关键词列表（根据你的需求修改）
keywords:
  - "关键词1"
  - "关键词2"
  - "关键词3"

# Telegram 配置
telegram:
  bot_token: "你的BOT_TOKEN"  # 替换为你的Token
  chat_id: "你的CHAT_ID"      # 替换为你的Chat ID

# 监控设置
monitor:
  check_interval: 5          # 检查间隔（分钟）
  headless: true             # 是否使用无头模式
  page_load_timeout: 30      # 页面加载超时时间（秒）
  notified_file: "notified_weibo.txt"  # 已通知记录文件
```

## 使用方法

### 启动监控

```bash
python weibo_monitor.py
```

### 后台运行（Linux/Mac）

```bash
nohup python weibo_monitor.py > output.log 2>&1 &
```

### 后台运行（Windows）

1. 创建一个批处理文件 `start_monitor.bat`：

```batch
@echo off
pythonw weibo_monitor.py
```

2. 双击运行，或者添加到开机启动项

### 停止监控

- 前台运行：按 `Ctrl+C`
- 后台运行：找到进程并终止

```bash
# Linux/Mac
ps aux | grep weibo_monitor.py
kill <PID>

# Windows
tasklist | findstr python
taskkill /PID <PID> /F
```

## 配置说明

### 关键词设置

在 `config.yaml` 中的 `keywords` 部分添加你想监控的关键词：

```yaml
keywords:
  - "重要通知"
  - "紧急"
  - "特别提醒"
  - "限时"
```

- 支持中文、英文、数字、符号
- 大小写敏感
- 只要微博内容包含任意一个关键词就会触发通知

### 监控频率

```yaml
monitor:
  check_interval: 5  # 每5分钟检查一次
```

- 建议设置为 3-10 分钟
- 不建议设置太频繁，以免被微博限制
- 根据实际需求调整

### 无头模式

```yaml
monitor:
  headless: true  # true: 后台运行不显示浏览器窗口
                  # false: 显示浏览器窗口（用于调试）
```

## 日志文件

程序运行时会生成以下文件：

- `weibo_monitor.log` - 运行日志
- `notified_weibo.txt` - 已通知的微博ID记录

## 常见问题

### 1. Chrome浏览器版本不匹配

**错误信息：** `SessionNotCreatedException: Message: session not created`

**解决方法：**
- 更新Chrome浏览器到最新版本
- 或者指定ChromeDriver版本

### 2. 无法访问微博

**可能原因：**
- 网络连接问题
- 微博反爬机制
- 页面结构变化

**解决方法：**
- 检查网络连接
- 增加 `page_load_timeout` 时间
- 关闭无头模式查看实际页面情况

### 3. Telegram通知发送失败

**检查项：**
- Bot Token是否正确
- Chat ID是否正确
- 是否已经给Bot发送过消息（激活Bot）
- 网络是否能访问Telegram

### 4. 未检测到关键词

**检查项：**
- 关键词拼写是否正确
- 是否区分大小写
- 微博内容是否真的包含关键词
- 查看日志文件确认是否正确获取到微博内容

## 技术说明

### 反爬机制应对

程序使用了以下技术来应对微博的反爬机制：

1. **undetected-chromedriver** - 隐藏Selenium自动化特征
2. **浏览器指纹伪装** - 设置真实的User-Agent
3. **随机延迟** - 模拟人类浏览行为
4. **无头模式** - 减少资源消耗

### 数据提取

- 使用Selenium加载动态内容
- BeautifulSoup解析HTML
- 多种选择器兼容不同页面结构

## 注意事项

1. **合规使用**：请遵守微博的使用条款，不要过度频繁地访问
2. **个人用途**：本程序仅供个人学习和使用
3. **隐私保护**：不要分享你的Bot Token和Chat ID
4. **适度监控**：建议监控间隔不要小于3分钟

## 更新日志

### v1.0.0 (2025-12-01)
- 首次发布
- 支持微博关键词监控
- Telegram通知功能
- 反爬机制应对

## 许可证

MIT License

## 技术支持

如有问题，请检查日志文件 `weibo_monitor.log` 查看详细错误信息。

---

**免责声明**：本工具仅供学习交流使用，使用者需自行承担使用风险。
