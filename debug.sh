#!/bin/bash

# Twitter监控系统 - 调试脚本

echo "=========================================="
echo "  Twitter监控系统 - 调试工具"
echo "=========================================="
echo ""

APP_DIR="/opt/twitter-monitor"
DATA_DIR="$APP_DIR/data"

# 检查服务状态
echo "1️⃣  检查服务状态..."
echo "----------------------------------------"
systemctl status twitter-monitor --no-pager
echo ""

# 检查配置文件
echo "2️⃣  检查配置文件..."
echo "----------------------------------------"
if [ -f "$DATA_DIR/config.json" ]; then
    echo "✅ 配置文件存在"
    
    # 检查API Key
    if grep -q '"rapidApiKey":""' "$DATA_DIR/config.json"; then
        echo "❌ RapidAPI Key 未配置！"
    else
        echo "✅ RapidAPI Key 已配置"
    fi
    
    # 检查Telegram
    if grep -q '"telegramBotToken":""' "$DATA_DIR/config.json"; then
        echo "❌ Telegram Bot Token 未配置！"
    else
        echo "✅ Telegram Bot Token 已配置"
    fi
    
    if grep -q '"telegramChatId":""' "$DATA_DIR/config.json"; then
        echo "❌ Telegram Chat ID 未配置！"
    else
        echo "✅ Telegram Chat ID 已配置"
    fi
    
    # 显示检查间隔
    INTERVAL=$(grep -o '"checkInterval":[0-9]*' "$DATA_DIR/config.json" | cut -d':' -f2)
    echo "⏰ 检查间隔: ${INTERVAL:-5} 分钟"
else
    echo "❌ 配置文件不存在！"
fi
echo ""

# 检查监控用户
echo "3️⃣  检查监控用户列表..."
echo "----------------------------------------"
if [ -f "$DATA_DIR/monitored_users.json" ]; then
    USER_COUNT=$(grep -o '"userId"' "$DATA_DIR/monitored_users.json" | wc -l)
    echo "📊 监控用户数量: $USER_COUNT"
    
    if [ $USER_COUNT -gt 0 ]; then
        echo ""
        echo "用户详情："
        cat "$DATA_DIR/monitored_users.json" | grep -E '"username"|"enabled"|"monitorTweets"' | head -20
    else
        echo "⚠️  没有添加任何监控用户！"
    fi
else
    echo "❌ 用户列表文件不存在！"
fi
echo ""

# 检查缓存
echo "4️⃣  检查缓存状态..."
echo "----------------------------------------"
if [ -f "$DATA_DIR/cache.json" ]; then
    CACHE_SIZE=$(wc -c < "$DATA_DIR/cache.json")
    echo "📦 缓存文件大小: $CACHE_SIZE 字节"
    
    if [ $CACHE_SIZE -lt 10 ]; then
        echo "⚠️  缓存为空，可能是首次运行"
        echo "💡 提示：首次添加用户会初始化缓存，不会发送通知"
    else
        echo "✅ 缓存已初始化"
    fi
else
    echo "❌ 缓存文件不存在！"
fi
echo ""

# 查看最近日志
echo "5️⃣  查看最近日志（最后20行）..."
echo "----------------------------------------"
journalctl -u twitter-monitor -n 20 --no-pager
echo ""

# 提供建议
echo "=========================================="
echo "  💡 调试建议"
echo "=========================================="
echo ""
echo "如果服务运行正常但没有收到通知："
echo ""
echo "1. 确认是首次运行后至少等待了一个检查周期"
echo "   - 查看上面的检查间隔设置"
echo "   - 首次运行会初始化缓存，不发送通知"
echo ""
echo "2. 测试Telegram配置"
echo "   - 在Web界面点击'测试Telegram'按钮"
echo "   - 确认收到测试消息"
echo ""
echo "3. 检查监控选项"
echo "   - 确保'启用监控'已勾选"
echo "   - 确保'新推文'选项已勾选"
echo ""
echo "4. 手动触发检查"
echo "   - 在Web界面点击'立即检查'按钮"
echo "   - 或运行: systemctl restart twitter-monitor"
echo ""
echo "5. 查看实时日志"
echo "   - 运行: journalctl -u twitter-monitor -f"
echo "   - 发一条新推文，观察日志输出"
echo ""
echo "=========================================="
echo "  🔧 快速修复命令"
echo "=========================================="
echo ""
echo "# 重启服务"
echo "systemctl restart twitter-monitor"
echo ""
echo "# 查看实时日志"
echo "journalctl -u twitter-monitor -f"
echo ""
echo "# 清空缓存重新初始化（谨慎使用）"
echo "echo '{}' > $DATA_DIR/cache.json"
echo "systemctl restart twitter-monitor"
echo ""

