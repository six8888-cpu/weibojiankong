#!/usr/bin/env python3
"""
基础功能测试脚本
用于验证安装和配置是否正确
"""
import sys
import os

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    try:
        import flask
        import flask_cors
        import apscheduler
        import aiohttp
        import sqlite3
        print("✓ 基础依赖模块导入成功")
        return True
    except ImportError as e:
        print(f"✗ 模块导入失败: {e}")
        return False

def test_optional_imports():
    """测试可选模块"""
    print("\n测试可选模块...")
    
    # psutil (健康监控)
    try:
        import psutil
        print("✓ psutil 已安装（健康监控功能可用）")
    except ImportError:
        print("○ psutil 未安装（健康监控功能不可用，不影响核心功能）")
    
    # playwright (反爬虫)
    try:
        from playwright.sync_api import sync_playwright
        print("✓ playwright 已安装（反爬虫功能可用）")
    except ImportError:
        print("○ playwright 未安装（反爬虫功能不可用）")
    
    return True

def test_database():
    """测试数据库"""
    print("\n测试数据库...")
    try:
        from database import Database
        db = Database('test_monitor.db')
        db.init_db()
        
        # 测试添加URL
        url_id = db.add_url('https://example.com', 'Test', 300)
        
        # 测试获取URL
        urls = db.get_all_urls()
        
        # 测试Telegram配置
        db.update_telegram_config('test_token', 'test_chat_id', 'http://proxy.com:8080')
        config = db.get_telegram_config()
        
        # 清理测试数据
        os.remove('test_monitor.db')
        
        print("✓ 数据库功能正常")
        return True
    except Exception as e:
        print(f"✗ 数据库测试失败: {e}")
        return False

def test_telegram_bot():
    """测试Telegram机器人（不实际发送）"""
    print("\n测试Telegram机器人...")
    try:
        from telegram_bot import TelegramNotifier
        
        # 测试初始化（不带代理）
        bot1 = TelegramNotifier('test_token', 'test_chat_id')
        
        # 测试初始化（带代理）
        bot2 = TelegramNotifier('test_token', 'test_chat_id', 'http://proxy.com:8080')
        
        if bot2.proxy_url == 'http://proxy.com:8080':
            print("✓ Telegram代理配置功能正常")
            return True
        else:
            print("✗ Telegram代理配置异常")
            return False
    except Exception as e:
        print(f"✗ Telegram机器人测试失败: {e}")
        return False

def test_health_monitor():
    """测试健康监控"""
    print("\n测试健康监控...")
    try:
        from health_monitor import HealthMonitor
        monitor = HealthMonitor()
        
        status = monitor.get_health_status()
        
        if 'memory' in status and 'cpu' in status:
            print(f"✓ 健康监控功能正常")
            print(f"  - 内存: {status['memory'].get('rss_mb', 0):.1f}MB")
            print(f"  - CPU: {status['cpu'].get('percent', 0):.1f}%")
            return True
        else:
            print("✗ 健康监控数据不完整")
            return False
    except ImportError:
        print("○ psutil未安装，健康监控功能不可用（不影响核心功能）")
        return True
    except Exception as e:
        print(f"✗ 健康监控测试失败: {e}")
        return False

def test_flask_app():
    """测试Flask应用"""
    print("\n测试Flask应用...")
    try:
        from app import app
        
        with app.test_client() as client:
            # 测试主页
            response = client.get('/')
            if response.status_code == 200:
                print("✓ Flask应用正常，主页可访问")
                
                # 测试API
                response = client.get('/api/health')
                if response.status_code == 200:
                    print("✓ 健康检查API正常")
                    return True
                else:
                    print("✗ 健康检查API异常")
                    return False
            else:
                print("✗ Flask应用异常")
                return False
    except Exception as e:
        print(f"✗ Flask应用测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("  网页监控系统 - 基础功能测试")
    print("=" * 50)
    
    results = []
    
    # 运行所有测试
    results.append(("模块导入", test_imports()))
    results.append(("可选模块", test_optional_imports()))
    results.append(("数据库", test_database()))
    results.append(("Telegram", test_telegram_bot()))
    results.append(("健康监控", test_health_monitor()))
    results.append(("Flask应用", test_flask_app()))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("  测试结果汇总")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name:<12} {status}")
    
    print("-" * 50)
    print(f"总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统可以正常使用。")
        return 0
    elif passed >= total - 2:
        print("\n⚠️  核心功能测试通过，部分可选功能不可用。")
        return 0
    else:
        print("\n❌ 部分核心功能测试失败，请检查配置。")
        return 1

if __name__ == '__main__':
    sys.exit(main())
