"""
网页监控系统 - 主应用
包含反爬虫绕过功能，支持Telegram通知
"""
import os
import json
import asyncio
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
        telegram_notifier = TelegramNotifier(config['bot_token'], config['chat_id'])
    
    monitor = WebMonitor(db, telegram_notifier)


def run_monitor_task():
    """执行监控任务"""
    try:
        logger.info("开始执行监控任务...")
        if monitor:
            asyncio.run(monitor.check_all_urls())
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
        
        if not bot_token or not chat_id:
            return jsonify({'success': False, 'message': 'Bot Token和Chat ID不能为空'}), 400
        
        db.update_telegram_config(bot_token, chat_id)
        
        # 重新初始化Telegram通知器
        telegram_notifier = TelegramNotifier(bot_token, chat_id)
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
            scheduler.shutdown(wait=False)
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
        thread.start()
        
        return jsonify({'success': True, 'message': '监控任务已开始执行'})
    except Exception as e:
        logger.error(f"执行监控失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    # 创建必要的目录
    Path('templates').mkdir(exist_ok=True)
    Path('static').mkdir(exist_ok=True)
    
    # 初始化数据库
    db.init_db()
    
    # 启动Flask应用
    logger.info("启动Web服务器...")
    app.run(host='0.0.0.0', port=5000, debug=False)

