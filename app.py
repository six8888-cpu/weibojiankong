"""
网页监控系统 - 主应用
包含反爬虫绕过功能，支持Telegram通知
"""
import os
import json
import asyncio
import gc
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import sqlite3
import logging
from pathlib import Path

# 导入监控模块
from monitor import WebMonitor
from database import Database
from telegram_bot import TelegramNotifier

# 尝试导入健康监控（可选）
try:
    from health_monitor import health_monitor
    HEALTH_MONITOR_AVAILABLE = True
except ImportError:
    health_monitor = None
    HEALTH_MONITOR_AVAILABLE = False
    logging.warning("健康监控模块未安装（需要psutil），部分功能不可用")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 初始化Flask应用
app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

# 初始化数据库
db = Database()

# 全局变量
monitor = None
scheduler = BackgroundScheduler()
telegram_notifier = None


def init_monitor():
    """初始化监控器"""
    global monitor, telegram_notifier
    
    # 获取Telegram配置
    config = db.get_telegram_config()
    if config:
        telegram_notifier = TelegramNotifier(
            config['bot_token'], 
            config['chat_id'],
            config.get('proxy_url')
        )
    
    monitor = WebMonitor(db, telegram_notifier)


def run_monitor_task():
    """执行监控任务"""
    try:
        logger.info("开始执行监控任务...")
        
        # 执行监控
        if monitor:
            asyncio.run(monitor.check_all_urls())
        
        # 自动清理旧日志（保留最新5条）
        db.cleanup_old_logs(keep_count=5)
        
        # 健康检查（每次监控后）
        if HEALTH_MONITOR_AVAILABLE:
            health_monitor.log_health_status()
            
            # 检查是否需要手动GC
            if health_monitor.should_restart():
                logger.info("执行垃圾回收以释放内存...")
                gc.collect()
        
        logger.info("监控任务执行完成")
    except Exception as e:
        logger.error(f"监控任务执行出错: {e}", exc_info=True)


# ==================== API路由 ====================

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/urls', methods=['GET'])
def get_urls():
    """获取所有监控URL"""
    try:
        urls = db.get_all_urls()
        return jsonify({'success': True, 'data': urls})
    except Exception as e:
        logger.error(f"获取URL列表失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/urls', methods=['POST'])
def add_url():
    """添加监控URL"""
    try:
        data = request.json
        url = data.get('url', '').strip()
        name = data.get('name', '').strip()
        check_interval = data.get('check_interval', 300)
        
        if not url:
            return jsonify({'success': False, 'message': 'URL不能为空'}), 400
        
        url_id = db.add_url(url, name, check_interval)
        return jsonify({'success': True, 'data': {'id': url_id}})
    except Exception as e:
        logger.error(f"添加URL失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/urls/<int:url_id>', methods=['PUT'])
def update_url(url_id):
    """更新监控URL"""
    try:
        data = request.json
        db.update_url(
            url_id,
            data.get('url'),
            data.get('name'),
            data.get('check_interval'),
            data.get('enabled')
        )
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"更新URL失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/urls/<int:url_id>', methods=['DELETE'])
def delete_url(url_id):
    """删除监控URL"""
    try:
        db.delete_url(url_id)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"删除URL失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/keywords', methods=['GET'])
def get_keywords():
    """获取所有关键词"""
    try:
        url_id = request.args.get('url_id', type=int)
        keywords = db.get_keywords(url_id)
        return jsonify({'success': True, 'data': keywords})
    except Exception as e:
        logger.error(f"获取关键词失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/keywords', methods=['POST'])
def add_keyword():
    """添加关键词"""
    try:
        data = request.json
        url_id = data.get('url_id')
        keyword = data.get('keyword', '').strip()
        fuzzy_match = data.get('fuzzy_match', True)
        
        if not keyword:
            return jsonify({'success': False, 'message': '关键词不能为空'}), 400
        
        keyword_id = db.add_keyword(url_id, keyword, fuzzy_match)
        return jsonify({'success': True, 'data': {'id': keyword_id}})
    except Exception as e:
        logger.error(f"添加关键词失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/keywords/<int:keyword_id>', methods=['DELETE'])
def delete_keyword(keyword_id):
    """删除关键词"""
    try:
        db.delete_keyword(keyword_id)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"删除关键词失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """获取监控日志"""
    try:
        limit = request.args.get('limit', 100, type=int)
        url_id = request.args.get('url_id', type=int)
        logs = db.get_logs(limit, url_id)
        return jsonify({'success': True, 'data': logs})
    except Exception as e:
        logger.error(f"获取日志失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/telegram/config', methods=['GET'])
def get_telegram_config():
    """获取Telegram配置"""
    try:
        config = db.get_telegram_config()
        if config:
            # 隐藏部分token信息
            config['bot_token'] = config['bot_token'][:10] + '...' if config['bot_token'] else ''
            # 代理URL不需要隐藏
        return jsonify({'success': True, 'data': config})
    except Exception as e:
        logger.error(f"获取Telegram配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/telegram/config', methods=['POST'])
def update_telegram_config():
    """更新Telegram配置"""
    try:
        global telegram_notifier
        
        data = request.json
        bot_token = data.get('bot_token', '').strip()
        chat_id = data.get('chat_id', '').strip()
        proxy_url = data.get('proxy_url', '').strip() or None
        
        if not bot_token or not chat_id:
            return jsonify({'success': False, 'message': 'Bot Token和Chat ID不能为空'}), 400
        
        # 验证代理URL格式（如果提供）
        if proxy_url:
            # 支持的格式：
            # http://host:port
            # https://host:port
            # socks5://host:port
            # socks5://user:pass@host:port
            if not (proxy_url.startswith('http://') or 
                    proxy_url.startswith('https://') or 
                    proxy_url.startswith('socks5://')):
                return jsonify({'success': False, 'message': '代理地址格式不正确，应为 http://、https:// 或 socks5:// 开头'}), 400
        
        db.update_telegram_config(bot_token, chat_id, proxy_url)
        
        # 重新初始化Telegram通知器
        telegram_notifier = TelegramNotifier(bot_token, chat_id, proxy_url)
        if monitor:
            monitor.telegram_notifier = telegram_notifier
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"更新Telegram配置失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/telegram/test', methods=['POST'])
def test_telegram():
    """测试Telegram通知"""
    try:
        if not telegram_notifier:
            return jsonify({'success': False, 'message': '请先配置Telegram'}), 400
        
        success = asyncio.run(telegram_notifier.send_message("✅ Telegram通知测试成功！"))
        
        if success:
            return jsonify({'success': True, 'message': '测试消息已发送'})
        else:
            return jsonify({'success': False, 'message': '发送失败，请检查配置'}), 500
    except Exception as e:
        logger.error(f"测试Telegram失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/monitor/start', methods=['POST'])
def start_monitor():
    """启动监控"""
    try:
        if not scheduler.running:
            init_monitor()
            
            # 添加定时任务（每1分钟执行一次）
            scheduler.add_job(
                func=run_monitor_task,
                trigger=IntervalTrigger(seconds=60),
                id='monitor_task',
                name='网页监控任务',
                replace_existing=True
            )
            
            scheduler.start()
            logger.info("监控调度器已启动")
            
        return jsonify({'success': True, 'message': '监控已启动'})
    except Exception as e:
        logger.error(f"启动监控失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/monitor/stop', methods=['POST'])
def stop_monitor():
    """停止监控"""
    try:
        if scheduler.running:
            # 优雅关闭：先暂停，再关闭
            scheduler.pause()
            scheduler.shutdown(wait=True)
            logger.info("监控调度器已停止")
            
        return jsonify({'success': True, 'message': '监控已停止'})
    except Exception as e:
        logger.error(f"停止监控失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/monitor/status', methods=['GET'])
def get_monitor_status():
    """获取监控状态"""
    try:
        status = {
            'running': scheduler.running,
            'next_run_time': None
        }
        
        if scheduler.running:
            job = scheduler.get_job('monitor_task')
            if job and job.next_run_time:
                status['next_run_time'] = job.next_run_time.isoformat()
        
        return jsonify({'success': True, 'data': status})
    except Exception as e:
        logger.error(f"获取监控状态失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/monitor/run', methods=['POST'])
def run_monitor_now():
    """立即执行一次监控"""
    try:
        if not monitor:
            init_monitor()
        
        # 在后台执行监控任务
        import threading
        thread = threading.Thread(target=run_monitor_task)
        thread.daemon = True  # 设置为守护线程，程序退出时自动结束
        thread.start()
        
        return jsonify({'success': True, 'message': '监控任务已开始执行'})
    except Exception as e:
        logger.error(f"执行监控失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/logs/cleanup', methods=['POST'])
def cleanup_logs():
    """手动清理日志"""
    try:
        keep_count = request.json.get('keep_count', 5) if request.json else 5
        cleaned = db.cleanup_old_logs(keep_count)
        
        if cleaned:
            return jsonify({'success': True, 'message': f'日志已清理，保留最新{keep_count}条'})
        else:
            return jsonify({'success': True, 'message': '日志数量未超过限制，无需清理'})
    except Exception as e:
        logger.error(f"清理日志失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接
        urls = db.get_all_urls()
        
        status = {
            'status': 'healthy',
            'monitor_running': scheduler.running,
            'urls_count': len(urls),
            'telegram_configured': db.get_telegram_config() is not None
        }
        
        # 添加系统资源信息
        if HEALTH_MONITOR_AVAILABLE:
            system_status = health_monitor.get_health_status()
            status.update({
                'system': system_status,
                'health_monitor_enabled': True
            })
        else:
            status['health_monitor_enabled'] = False
        
        return jsonify({'success': True, 'data': status})
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({'success': False, 'message': str(e), 'status': 'unhealthy'}), 500


if __name__ == '__main__':
    import signal
    import sys
    
    # 优雅关闭处理
    def signal_handler(sig, frame):
        logger.info("收到关闭信号，正在优雅关闭...")
        if scheduler.running:
            scheduler.shutdown(wait=False)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 创建必要的目录
    Path('templates').mkdir(exist_ok=True)
    Path('static').mkdir(exist_ok=True)
    
    # 初始化数据库
    db.init_db()
    
    # 启动Flask应用
    logger.info("启动Web服务器...")
    try:
        app.run(host='0.0.0.0', port=9527, debug=False)
    finally:
        if scheduler.running:
            scheduler.shutdown(wait=False)

