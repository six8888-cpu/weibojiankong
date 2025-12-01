# 🌐 SOCKS5代理服务器 - 一键安装指南

## 📋 简介

这是一个用于香港/海外服务器的SOCKS5代理一键安装脚本，帮助中国服务器访问被墙的服务（如Telegram API）。

## 🚀 快速安装

### 香港服务器端（一键安装）

```bash
wget https://github.com/six8888-cpu/weibojiankong/raw/main/install_socks5_proxy.sh -O install_socks5_proxy.sh && chmod +x install_socks5_proxy.sh && ./install_socks5_proxy.sh
```

或使用curl：

```bash
curl -O https://github.com/six8888-cpu/weibojiankong/raw/main/install_socks5_proxy.sh && chmod +x install_socks5_proxy.sh && ./install_socks5_proxy.sh
```

## 📝 安装完成后

安装脚本会输出类似以下信息：

```
============================================
   SOCKS5代理服务安装成功！
============================================

服务器信息：
  IP地址: 你的香港服务器IP

代理配置：
  协议: SOCKS5
  地址: 你的香港服务器IP
  端口: 1080
  用户名: proxy
  密码: 随机生成的密码

完整代理地址（复制使用）：
socks5://proxy:密码@IP:1080
```

**⚠️ 请务必保存这些信息！**

配置信息也会保存在 `~/socks5_proxy_info.txt` 文件中。

## 🔧 在中国服务器使用代理

### 方法一：在监控系统网页端配置

1. 访问监控系统：`http://中国服务器IP:9527`
2. 进入"Telegram配置"页面
3. 在"代理地址"填写：
   ```
   socks5://proxy:密码@香港服务器IP:1080
   ```
4. 保存配置

### 方法二：测试代理连接

在中国服务器上测试代理是否可用：

```bash
curl -x socks5://proxy:密码@香港服务器IP:1080 https://api.telegram.org
```

如果返回JSON数据，说明代理可用。

### 方法三：设置系统代理（可选）

```bash
export http_proxy=socks5://proxy:密码@香港服务器IP:1080
export https_proxy=socks5://proxy:密码@香港服务器IP:1080

# 测试
curl https://api.telegram.org
```

## 📊 管理代理服务

### 查看服务状态
```bash
sudo systemctl status gost
```

### 启动服务
```bash
sudo systemctl start gost
```

### 停止服务
```bash
sudo systemctl stop gost
```

### 重启服务
```bash
sudo systemctl restart gost
```

### 查看日志
```bash
sudo journalctl -u gost -f
```

### 查看配置信息
```bash
cat ~/socks5_proxy_info.txt
```

## 🔒 安全建议

1. **修改默认端口**（可选）
   ```bash
   sudo nano /etc/gost/config.json
   # 修改端口后重启服务
   sudo systemctl restart gost
   ```

2. **定期更改密码**
   ```bash
   # 编辑配置文件
   sudo nano /etc/gost/config.json
   # 修改密码后重启
   sudo systemctl restart gost
   ```

3. **限制IP访问**（可选）
   ```bash
   # 只允许特定IP访问
   sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="中国服务器IP" port protocol="tcp" port="1080" accept'
   sudo firewall-cmd --reload
   ```

## 🌟 特性

- ✅ 一键安装，无需复杂配置
- ✅ 自动生成随机强密码
- ✅ 开机自启动
- ✅ 轻量级，内存占用小
- ✅ 支持多用户同时使用
- ✅ 稳定可靠，自动重启

## 🛠️ 故障排查

### 问题1：服务无法启动

```bash
# 查看详细日志
sudo journalctl -u gost -n 50

# 检查配置文件
cat /etc/gost/config.json

# 手动启动测试
/usr/local/bin/gost -C /etc/gost/config.json
```

### 问题2：中国服务器无法连接

```bash
# 1. 检查香港服务器防火墙
sudo firewall-cmd --list-ports

# 2. 检查服务是否运行
sudo systemctl status gost

# 3. 测试端口是否开放
# 在中国服务器上执行
telnet 香港服务器IP 1080
```

### 问题3：连接超时

可能原因：
- 香港服务器防火墙未开放端口
- 中国服务器到香港服务器网络不通
- 代理地址填写错误

解决方法：
```bash
# 在香港服务器检查端口
sudo netstat -tlnp | grep 1080

# 开放防火墙
sudo firewall-cmd --permanent --add-port=1080/tcp
sudo firewall-cmd --reload
```

## 🔄 卸载代理服务

```bash
# 停止并禁用服务
sudo systemctl stop gost
sudo systemctl disable gost

# 删除文件
sudo rm -f /usr/local/bin/gost
sudo rm -f /etc/systemd/system/gost.service
sudo rm -rf /etc/gost

# 重新加载systemd
sudo systemctl daemon-reload
```

## 📞 技术支持

如遇问题，请查看：
- 服务日志：`sudo journalctl -u gost -f`
- 配置文件：`/etc/gost/config.json`
- 配置信息：`~/socks5_proxy_info.txt`

## 💡 使用场景

1. **Telegram通知** - 监控系统发送Telegram消息
2. **访问GitHub** - 加速Git操作
3. **API访问** - 访问被墙的API服务
4. **开发测试** - 测试国际化功能

## ⚠️ 注意事项

1. 代理服务仅供合法用途使用
2. 请妥善保管用户名和密码
3. 定期检查服务运行状态
4. 建议配置防火墙限制访问IP

---

**安装完成后，记得在监控系统中配置代理！** 🎉
