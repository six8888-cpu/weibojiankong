# 更新日志

## [2.0.0] - 2024-12-01 - 中国服务器优化版

### 🎉 重大更新

#### 新增功能
- ✅ **Telegram代理配置** - 支持在网页端直接配置HTTP/SOCKS5代理
- ✅ **日志自动清理** - 监控日志超过5条自动清空，防止数据库膨胀
- ✅ **系统健康监控** - 实时监控内存、CPU、磁盘使用情况
- ✅ **一键安装脚本** - `install_china.sh` 自动化安装所有依赖
- ✅ **生产环境部署** - 支持Gunicorn、systemd等生产级部署方案
- ✅ **健康检查API** - `/api/health` 端点提供系统状态信息

#### 性能优化
- ⚡ **内存管理** - 自动垃圾回收，防止内存泄漏
- ⚡ **守护线程** - 后台任务使用daemon线程，优雅关闭
- ⚡ **数据库清理** - 定期清理旧日志，保持数据库小巧
- ⚡ **Gunicorn配置** - worker自动重启，防止内存累积
- ⚡ **资源监控** - 实时监控系统资源，及时告警

#### 中国服务器优化
- 🇨🇳 **国内镜像** - requirements_china.txt 支持阿里云镜像
- 🇨🇳 **代理支持** - Telegram完整的代理配置支持
- 🇨🇳 **部署文档** - 详细的中国服务器部署指南
- 🇨🇳 **故障排查** - 针对中国网络环境的问题解决方案

#### 数据库变更
- 📊 **telegram_config表** - 新增 `proxy_url` 字段
- 📊 **日志清理方法** - 新增 `cleanup_old_logs()` 方法

#### 文件变更
- 📝 **database.py** - 添加代理字段和日志清理功能
- 📝 **telegram_bot.py** - 添加代理支持（HTTP/SOCKS5）
- 📝 **app.py** - 添加健康检查、日志清理API、内存优化
- 📝 **templates/index.html** - 添加代理配置界面和日志清理按钮
- 📝 **health_monitor.py** - 新增系统健康监控模块
- 📝 **requirements_china.txt** - 中国优化版依赖文件
- 📝 **install_china.sh** - 一键安装脚本
- 📝 **start_production.sh** - 生产环境启动脚本
- 📝 **deploy_china.md** - 完整部署文档
- 📝 **README_CHINA.md** - 中国服务器专用README

### 🔄 改进
- 改进了日志输出格式
- 优化了错误处理机制
- 增强了系统稳定性
- 改进了用户界面提示

### 🐛 修复
- 修复了长时间运行可能导致的内存泄漏
- 修复了日志文件无限增长的问题
- 修复了Telegram在中国服务器无法使用的问题

### 📝 文档
- 新增完整的中国服务器部署指南
- 新增故障排查文档
- 新增代理配置说明
- 更新了README文档

### ⚠️ 破坏性变更
- 数据库结构有更新，旧版本需要手动迁移
  ```sql
  ALTER TABLE telegram_config ADD COLUMN proxy_url TEXT;
  ```

### 🔧 升级指南

#### 从v1.0升级到v2.0

1. **备份数据**
   ```bash
   cp monitor.db monitor.db.backup
   ```

2. **更新代码**
   ```bash
   git pull origin main
   ```

3. **安装新依赖**
   ```bash
   pip3 install -r requirements_china.txt -i https://mirrors.aliyun.com/pypi/simple/
   ```

4. **更新数据库**
   ```bash
   python3 -c "from database import Database; db = Database(); db.init_db()"
   ```

5. **重启服务**
   ```bash
   sudo systemctl restart webmonitor
   # 或
   ./start_production.sh
   ```

### 📋 依赖变更

#### 新增依赖
- `psutil==5.9.6` - 系统资源监控
- `gunicorn==21.2.0` - 生产环境服务器
- `aiohttp-socks==0.8.4` - SOCKS代理支持

#### 依赖版本更新
- 所有依赖版本已锁定，确保稳定性

---

## [1.0.0] - 2024-11-15 - 初始版本

### 功能
- ✅ 基础网页监控功能
- ✅ 关键词检测（精确/模糊）
- ✅ Telegram通知
- ✅ 反爬虫绕过（Playwright）
- ✅ Web管理界面
- ✅ SQLite数据存储
- ✅ 定时任务调度

---

## 开发路线图

### v2.1 (计划中)
- [ ] Docker镜像支持
- [ ] 邮件通知支持
- [ ] Webhook通知支持
- [ ] 多用户支持
- [ ] 数据导出功能

### v3.0 (未来)
- [ ] 分布式部署
- [ ] 图表可视化
- [ ] 移动端适配
- [ ] 更多通知渠道

---

## 贡献者

感谢所有为这个项目做出贡献的开发者！

---

## 许可证

本项目采用 MIT 协议开源。
