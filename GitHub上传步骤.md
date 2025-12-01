# 📤 上传到GitHub步骤

## 第一步：在GitHub创建仓库

1. 访问：https://github.com/new
2. 填写信息：
   - Repository name: `web-monitor`（或其他名字）
   - Description: `网页监控系统 - 反爬虫 + Telegram通知`
   - 选择：**Public**（公开）或 **Private**（私有）
   - ❌ 不要勾选 "Add a README file"
   - ❌ 不要勾选 "Add .gitignore"
   - ❌ 不要勾选 "Choose a license"
3. 点击 **Create repository**

## 第二步：推送代码

GitHub会显示推送命令，在你的Windows PowerShell中执行：

```powershell
cd D:\cursor\1

# 关联远程仓库（替换成你的GitHub用户名和仓库名）
git remote add origin https://github.com/你的用户名/web-monitor.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

**如果需要登录：**
- 用户名：你的GitHub用户名
- 密码：使用 **Personal Access Token**（不是账号密码）

**创建Token：**
1. 访问：https://github.com/settings/tokens
2. 点击 **Generate new token (classic)**
3. 勾选 **repo** 权限
4. 点击 **Generate token**
5. 复制token（只显示一次！）

## 第三步：验证上传

访问你的GitHub仓库页面，应该能看到所有代码文件。

---

# 🚀 Linux服务器一键安装

上传成功后，在你的**香港Linux服务器**上执行：

## 方法1：使用一键安装脚本

```bash
# 下载并运行一键安装脚本
curl -fsSL https://raw.githubusercontent.com/你的用户名/web-monitor/main/一键安装.sh | bash
```

## 方法2：手动安装

```bash
# 1. 克隆仓库
cd /opt
sudo git clone https://github.com/你的用户名/web-monitor.git
sudo chown -R $USER:$USER web-monitor
cd web-monitor

# 2. 运行安装
chmod +x install.sh
sudo ./install.sh

# 3. 启动服务
sudo systemctl start web-monitor
sudo systemctl enable web-monitor

# 4. 查看状态
sudo systemctl status web-monitor
```

## 访问Web界面

```
http://你的服务器IP:9527
```

## 常用管理命令

```bash
# 查看状态
sudo systemctl status web-monitor

# 查看日志
sudo journalctl -u web-monitor -f

# 重启服务
sudo systemctl restart web-monitor

# 停止服务
sudo systemctl stop web-monitor

# 更新代码
cd /opt/web-monitor
git pull
sudo systemctl restart web-monitor
```

---

完成！🎉

