#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微博监控程序安装和配置脚本
"""

import os
import sys
import yaml


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("❌ 需要 Python 3.7 或更高版本")
        sys.exit(1)
    print(f"✅ Python 版本: {sys.version.split()[0]}")


def install_dependencies():
    """安装依赖包"""
    print("\n📦 开始安装依赖包...")
    os.system(f"{sys.executable} -m pip install -r requirements.txt")
    print("✅ 依赖包安装完成")


def configure():
    """配置向导"""
    print("\n" + "="*50)
    print("📝 配置向导")
    print("="*50)
    
    # 读取配置文件
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print("\n1️⃣ 微博URL配置")
    print(f"当前配置: {config['weibo_url']}")
    new_url = input("是否修改？(直接回车跳过，或输入新URL): ").strip()
    if new_url:
        config['weibo_url'] = new_url
    
    print("\n2️⃣ 关键词配置")
    print(f"当前关键词: {', '.join(config['keywords'])}")
    print("请输入要监控的关键词（用逗号分隔，直接回车跳过）:")
    keywords_input = input("> ").strip()
    if keywords_input:
        config['keywords'] = [k.strip() for k in keywords_input.split(',') if k.strip()]
    
    print("\n3️⃣ Telegram Bot配置")
    print("⚠️ 如果还没有Bot，请先访问 @BotFather 创建")
    
    bot_token = input(f"Bot Token (当前: {config['telegram']['bot_token'][:20]}...): ").strip()
    if bot_token:
        config['telegram']['bot_token'] = bot_token
    
    chat_id = input(f"Chat ID (当前: {config['telegram']['chat_id']}): ").strip()
    if chat_id:
        config['telegram']['chat_id'] = chat_id
    
    print("\n4️⃣ 监控间隔配置")
    interval = input(f"检查间隔（分钟，当前: {config['monitor']['check_interval']}）: ").strip()
    if interval and interval.isdigit():
        config['monitor']['check_interval'] = int(interval)
    
    # 保存配置
    with open('config.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    
    print("\n✅ 配置已保存到 config.yaml")


def test_telegram():
    """测试Telegram连接"""
    print("\n🔍 测试Telegram连接...")
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        from telegram import Bot
        bot = Bot(token=config['telegram']['bot_token'])
        bot.send_message(
            chat_id=config['telegram']['chat_id'],
            text="✅ 微博监控程序配置成功！\n\n测试消息发送成功。"
        )
        print("✅ Telegram连接测试成功！")
        print("📱 请检查你的Telegram是否收到测试消息")
    except Exception as e:
        print(f"❌ Telegram连接测试失败: {e}")
        print("请检查Bot Token和Chat ID是否正确")


def main():
    """主函数"""
    print("="*50)
    print("🚀 微博监控程序安装向导")
    print("="*50)
    
    check_python_version()
    
    choice = input("\n请选择操作:\n1. 完整安装（安装依赖+配置）\n2. 仅安装依赖\n3. 仅配置\n4. 测试Telegram\n5. 退出\n请输入选项 (1-5): ").strip()
    
    if choice == '1':
        install_dependencies()
        configure()
        test_telegram()
    elif choice == '2':
        install_dependencies()
    elif choice == '3':
        configure()
    elif choice == '4':
        test_telegram()
    elif choice == '5':
        print("👋 再见！")
        return
    else:
        print("❌ 无效选项")
        return
    
    print("\n" + "="*50)
    print("🎉 安装完成！")
    print("="*50)
    print("\n▶️  运行命令: python weibo_monitor.py")
    print("📖 详细文档: 查看 README.md")
    print("\n祝使用愉快！")


if __name__ == '__main__':
    main()

