# 🔍 网页监控系统

一个功能强大的网页监控系统，支持反爬虫绕过、关键词检测和Telegram实时通知。

## ✨ 功能特点

- 🚀 **反爬虫绕过**：使用Playwright无头浏览器，模拟真实用户行为，绕过Cloudflare等反爬虫机制
- 🔑 **关键词监控**：支持多关键词、模糊匹配和精确匹配
- 📱 **Telegram通知**：检测到关键词时即时推送Telegram消息
- 🌐 **Web管理界面**：现代化的Web界面，轻松管理监控任务
- ⏰ **定时监控**：自动定时检查网页变化
- 📊 **监控日志**：详细记录每次监控结果
- 🖥️ **跨平台支持**：支持Windows和Linux系统

## 🎯 反爬虫技术

本项目采用以下反爬虫绕过技术（参考 [bypass-cloudflare](https://github.com/bright-cn/bypass-cloudflare)）：

1. **无头浏览器**：使用Playwright模拟真实Chrome浏览器
2. **反检测脚本**：覆盖`navigator.webdriver`等检测特征
3. **请求头伪造**：设置真实的User-Agent、Referer等HTTP头
4. **行为模拟**：模拟真实用户的滚动、等待等行为
5. **浏览器指纹**：配置真实的浏览器指纹信息

## 📦 安装部署

### Windows系统

1. **安装Python**（3.8或更高版本）
   - 下载：https://www.python.org/downloads/
   - 安装时勾选"Add Python to PATH"

2. **下载项目**
```bash
git clone <repository_url>
cd web-monitor
```

3. **运行启动脚本**
```bash
start.bat
```

脚本会自动：
- 创建虚拟环境
- 安装依赖包
- 安装Playwright浏览器
- 启动Web服务

### Linux系统

#### 方法一：自动安装（推荐）

```bash
# 下载项目
git clone <repository_url>
cd web-monitor

# 运行安装脚本
chmod +x install.sh
./install.sh
```

安装脚本会自动：
- 安装系统依赖
- 安装Python和pip
- 创建虚拟环境
- 安装Python依赖
- 安装Playwright浏览器
- 可选：创建systemd服务

#### 方法二：手动安装

```bash
# 1. 安装系统依赖
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装Python依赖
pip install -r requirements.txt

# 4. 安装Playwright浏览器
playwright install chromium
playwright install-deps chromium

# 5. 启动应用
python3 app.py
```

### 使用systemd服务（Linux）

创建服务文件后：

```bash
# 启动服务
sudo systemctl start web-monitor

# 停止服务
sudo systemctl stop web-monitor

# 查看状态
sudo systemctl status web-monitor

# 开机自启
sudo systemctl enable web-monitor

# 查看日志
sudo journalctl -u web-monitor -f
```

## 🚀 快速开始

### 1. 启动系统

**Windows:**
```bash
start.bat
```

**Linux:**
```bash
chmod +x start.sh
./start.sh
```

### 2. 访问Web界面

打开浏览器访问：http://localhost:5000

### 3. 配置Telegram通知（发送到群组）

#### 创建机器人
1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 创建新机器人
3. 按提示设置名称，获取 **Bot Token**

#### 获取群组Chat ID

**方法1：通过API获取（推荐）**
1. 在Telegram创建一个群组
2. 将你的机器人添加到群组中
3. 在群组中 @你的机器人 发送任意消息
4. 浏览器访问：`https://api.telegram.org/bot你的BOT_TOKEN/getUpdates`
5. 在返回的JSON中查找：`"chat":{"id":-1001234567890}`
6. 复制这个**负数ID**（包括负号）

**方法2：使用辅助机器人**
1. 在Telegram搜索 `@getidsbot` 或 `@RawDataBot`
2. 将机器人添加到你的群组
3. 机器人会自动显示群组Chat ID

**重要说明：**
- ✅ 群组Chat ID是**负数**（如：-1001234567890）
- ✅ 个人Chat ID是**正数**（如：123456789）  
- ✅ 确保机器人有发送消息权限

#### 保存配置
1. 在Web界面的"Telegram配置"选项卡填入：
   - Bot Token
   - Chat ID（**群组ID包括负号**）
2. 点击"测试连接"验证配置

### 4. 添加监控网址

1. 切换到"监控列表"选项卡
2. 点击"添加监控网址"
3. 填写网址信息：
   - **网址名称**：便于识别的名称
   - **网址URL**：要监控的完整URL
   - **检查间隔**：每次检查的间隔时间（秒）

### 5. 添加关键词

1. 切换到"关键词管理"选项卡
2. 点击"添加关键词"
3. 选择要监控的网址
4. 输入关键词
5. 选择匹配方式：
   - **模糊匹配**（推荐）：只要包含关键词即可
   - **精确匹配**：匹配完整单词

### 6. 启动监控

点击顶部状态栏的"启动监控"按钮，系统会：
- 每5分钟自动执行一次监控任务
- 检查所有启用的监控网址
- 发现关键词时发送Telegram通知
- 记录监控日志

也可以点击"立即执行"手动触发一次监控。

## 📖 使用说明

### 监控列表

- **添加网址**：添加要监控的网页
- **启用/禁用**：控制是否监控某个网址
- **删除**：删除监控网址（会同时删除相关关键词）

### 关键词管理

- **添加关键词**：为网址添加监控关键词
- **模糊匹配**：检测内容中是否包含关键词（不区分大小写）
- **精确匹配**：精确匹配完整单词
- **删除关键词**：点击关键词标签上的 ×

### 监控日志

- 显示最近50条监控记录
- 可以看到：
  - 监控时间
  - 监控的网址
  - 检测到的关键词
  - 监控状态（找到/未找到）

### Telegram配置

- **Bot Token**：Telegram机器人令牌
- **Chat ID**：接收通知的用户ID
- **保存配置**：保存Telegram配置
- **测试连接**：发送测试消息验证配置

## 🔧 配置文件

可以通过`.env`文件配置系统参数：

```bash
# 复制示例配置
cp .env.example .env

# 编辑配置
vim .env
```

配置项：
- `FLASK_HOST`: Web服务监听地址（默认：0.0.0.0）
- `FLASK_PORT`: Web服务端口（默认：5000）
- `DATABASE_PATH`: 数据库文件路径（默认：monitor.db）
- `LOG_LEVEL`: 日志级别（默认：INFO）

## 📁 项目结构

```
web-monitor/
├── app.py                 # Flask主应用
├── database.py            # 数据库管理
├── monitor.py             # 监控模块（反爬虫）
├── telegram_bot.py        # Telegram通知
├── requirements.txt       # Python依赖
├── .env.example          # 配置示例
├── .gitignore            # Git忽略文件
├── start.sh              # Linux启动脚本
├── start.bat             # Windows启动脚本
├── install.sh            # Linux安装脚本
├── README.md             # 说明文档
├── templates/
│   └── index.html        # Web界面
└── monitor.db            # SQLite数据库（自动创建）
```

## 🛠️ 技术栈

### 后端
- **Flask**: Web框架
- **APScheduler**: 任务调度
- **Playwright**: 无头浏览器（反爬虫）
- **SQLite**: 数据库
- **aiohttp**: 异步HTTP客户端

### 前端
- **原生HTML/CSS/JavaScript**
- **现代化响应式设计**
- **无需额外依赖**

## 🔒 反爬虫实现细节

### Playwright配置

```python
# 启动参数
args=[
    '--disable-blink-features=AutomationControlled',  # 禁用自动化特征
    '--disable-dev-shm-usage',
    '--no-sandbox',
    '--disable-setuid-sandbox',
]

# 浏览器上下文
viewport={'width': 1920, 'height': 1080}
user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...'
locale='zh-CN'
timezone_id='Asia/Shanghai'
```

### 反检测脚本

```javascript
// 覆盖webdriver检测
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});

// 模拟真实浏览器环境
window.chrome = { runtime: {} };

// 覆盖其他检测特征
navigator.plugins = [1, 2, 3, 4, 5];
navigator.languages = ['zh-CN', 'zh', 'en-US', 'en'];
```

### 行为模拟

```python
# 等待页面加载
await page.goto(url, wait_until='networkidle')
await asyncio.sleep(2)

# 模拟滚动
await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
await asyncio.sleep(1)
```

## ❓ 常见问题

### 1. Playwright安装失败

**问题**：安装Playwright浏览器时出错

**解决**：
```bash
# 手动安装
playwright install chromium

# Linux还需要安装系统依赖
playwright install-deps chromium
```

### 2. 无法访问某些网站

**问题**：某些网站仍然无法访问或被检测为机器人

**解决**：
- 检查网站是否需要代理
- 尝试增加等待时间
- 检查网站是否需要登录
- 某些网站的反爬虫机制特别强，可能需要更高级的绕过方案

### 3. Telegram通知不工作

**问题**：配置了Telegram但收不到通知

**解决**：
1. 确认Bot Token和Chat ID正确
2. 确保机器人已启动（向机器人发送 `/start`）
3. 点击"测试连接"验证配置
4. 检查网络是否能访问Telegram API

### 4. 监控不运行

**问题**：点击启动监控后没有反应

**解决**：
1. 确认至少添加了一个监控网址
2. 确认监控网址处于启用状态
3. 确认已添加关键词
4. 查看监控日志了解详情
5. 检查 `monitor.log` 文件

### 5. 内存占用过高

**问题**：长时间运行后内存占用很高

**解决**：
- 减少同时监控的网址数量
- 增加检查间隔时间
- 定期重启服务

## 📝 开发建议

### 添加代理支持

在 `monitor.py` 中修改浏览器配置：

```python
context = await self.browser.new_context(
    proxy={
        'server': 'http://proxy.example.com:8080',
        'username': 'user',
        'password': 'pass'
    }
)
```

### 自定义检查逻辑

在 `monitor.py` 的 `check_url` 方法中添加自定义逻辑：

```python
async def check_url(self, url_data: Dict):
    # 自定义处理逻辑
    content = await self.fetch_page_content(url)
    
    # 例如：提取特定元素
    soup = BeautifulSoup(content, 'html.parser')
    title = soup.find('h1').text
```

### 添加更多通知方式

创建新的通知模块，例如 `email_notifier.py`：

```python
class EmailNotifier:
    def send_email(self, subject, message):
        # 实现邮件发送
        pass
```

## 📄 许可证

本项目仅供学习和个人使用。使用时请遵守目标网站的robots.txt和服务条款。

## 🙏 致谢

- 反爬虫技术参考：[bypass-cloudflare](https://github.com/bright-cn/bypass-cloudflare)
- Playwright无头浏览器：[Playwright](https://playwright.dev/)

## 📮 联系方式

如有问题或建议，请提交Issue。

---

**注意**：请负责任地使用本工具，遵守网站的使用条款和相关法律法规。过度频繁的请求可能会给目标网站造成负担。

