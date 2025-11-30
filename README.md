# Twitter 监控系统

一个简洁高效的Twitter监控系统，实时监控指定用户的Twitter动态，并通过Telegram发送通知。

## ✨ 功能特点

- 🐦 **新推文通知** - 实时监控用户发布的新推文
- 💬 **回复通知** - 监控用户的回复动态
- 📌 **置顶推文通知** - 检测用户置顶推文的变化
- 🔄 **转发通知** - 监控用户的转发行为
- 📱 **Telegram通知** - 通过Telegram Bot实时推送通知
- 🎯 **多用户监控** - 支持同时监控多个Twitter用户
- ⚙️ **灵活配置** - 可自定义监控间隔和监控项目
- 🎨 **简洁界面** - 响应式设计，支持移动端访问

## 📋 前置要求

1. **Node.js** - 版本 14.x 或更高
2. **RapidAPI账号** - 用于访问Twitter API
3. **Telegram Bot** - 用于发送通知

## 🚀 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 获取必要的API密钥

#### RapidAPI Key
1. 访问 [Twitter241 API](https://rapidapi.com/davethebeast/api/twitter241)
2. 注册/登录RapidAPI账号
3. 订阅API（有免费套餐）
4. 复制你的RapidAPI Key

#### Telegram Bot配置
1. 在Telegram中找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称
4. 保存Bot Token（格式类似：`123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`）

#### 获取Telegram Chat ID
1. 在Telegram中找到 [@userinfobot](https://t.me/userinfobot)
2. 发送任意消息
3. 机器人会返回你的Chat ID

### 3. 启动服务器

```bash
npm start
```

或使用开发模式（自动重启）：

```bash
npm run dev
```

### 4. 访问Web界面

打开浏览器访问：http://localhost:3000

### 5. 配置系统

1. 点击"**系统配置**"右侧的"**显示**"按钮
2. 填入以下信息：
   - RapidAPI Key
   - Telegram Bot Token
   - Telegram Chat ID
   - 检查间隔（建议5-15分钟）
3. 点击"**保存配置**"
4. 点击"**测试Telegram**"验证配置是否正确

### 6. 添加监控用户

1. 在"**添加监控用户**"区域输入Twitter用户名（不含@）
2. 点击"**添加**"按钮
3. 在监控列表中可以选择监控项目：
   - ✅ 启用监控
   - 📝 新推文
   - 💬 回复
   - 📌 置顶
   - 🔄 转发

## 📁 项目结构

```
twitter-monitor/
├── server.js           # 后端服务器
├── package.json        # 项目配置
├── README.md          # 说明文档
├── public/            # 前端文件
│   ├── index.html     # 主页面
│   ├── style.css      # 样式文件
│   └── script.js      # 前端逻辑
└── data/              # 数据存储（自动创建）
    ├── config.json    # 系统配置
    ├── monitored_users.json  # 监控用户列表
    └── cache.json     # 数据缓存
```

## 🔧 配置说明

### 检查间隔
- 建议设置为 5-15 分钟
- 间隔太短可能触发API限制
- 间隔太长可能错过实时动态

### 监控选项
每个用户可以独立配置以下监控项：
- **启用监控**：总开关
- **新推文**：监控用户发布的新推文
- **回复**：监控用户的回复内容
- **置顶**：监控置顶推文的变化
- **转发**：监控用户转发的推文

## 📱 Telegram通知格式

### 新推文通知
```
🐦 新推文通知

👤 用户: @username
📝 内容: 推文内容...
🔗 链接: https://twitter.com/...
⏰ 时间: 2024-01-01 12:00:00
```

### 回复通知
```
💬 新回复通知

👤 用户: @username
📝 回复内容: 回复内容...
🔗 链接: https://twitter.com/...
⏰ 时间: 2024-01-01 12:00:00
```

### 置顶推文通知
```
📌 置顶推文变化通知

👤 用户: @username
🔗 新置顶推文: https://twitter.com/...
⏰ 检测时间: 2024-01-01 12:00:00
```

### 转发通知
```
🔄 转发推文通知

👤 用户: @username
📝 转发了: @original_user
💭 原文: 原推文内容...
🔗 链接: https://twitter.com/...
⏰ 时间: 2024-01-01 12:00:00
```

## ⚠️ 注意事项

1. **API限制**
   - RapidAPI的免费套餐有请求次数限制
   - 建议合理设置检查间隔
   - 监控用户不宜过多

2. **数据安全**
   - API密钥等敏感信息存储在本地
   - 建议不要将 `data/` 目录提交到版本控制
   - 定期备份 `data/` 目录

3. **首次运行**
   - 首次添加用户后，系统会初始化缓存
   - 初始化期间不会发送通知
   - 从第二次检查开始才会发送新动态通知

4. **服务器运行**
   - 需要保持服务器持续运行
   - 建议使用 PM2 或 systemd 管理进程
   - 可部署到云服务器实现24小时监控

## 🛠️ 高级部署

### 使用 PM2 部署（推荐）

```bash
# 安装 PM2
npm install -g pm2

# 启动应用
pm2 start server.js --name twitter-monitor

# 设置开机自启
pm2 startup
pm2 save

# 查看日志
pm2 logs twitter-monitor

# 重启应用
pm2 restart twitter-monitor
```

### 使用 Docker 部署

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

```bash
# 构建镜像
docker build -t twitter-monitor .

# 运行容器
docker run -d -p 3000:3000 -v $(pwd)/data:/app/data twitter-monitor
```

## 🐛 故障排除

### Telegram消息发送失败
- 检查Bot Token是否正确
- 检查Chat ID是否正确
- 确认已向Bot发送过消息（激活对话）

### API调用失败
- 检查RapidAPI Key是否正确
- 确认API订阅状态
- 检查是否超出API配额

### 用户添加失败
- 确认用户名拼写正确
- 检查API配置是否正确
- 查看服务器日志获取详细错误信息

## 📄 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，欢迎反馈。

---

**享受你的Twitter监控体验！** 🎉

