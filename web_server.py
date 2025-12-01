#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微博监控Web管理界面 - 后端服务器
"""

import os
import json
import yaml
import logging
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from weibo_monitor import WeiboMonitor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('web_server.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# 全局变量
monitor_thread = None
monitor_instance = None
monitor_running = False
monitor_stats = {
    'status': 'stopped',
    'start_time': None,
    'check_count': 0,
    'last_check_time': None,
    'matched_count': 0,
    'last_matched_time': None
}


def load_config():
    """加载配置文件"""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return None


def save_config(config):
    """保存配置文件"""
    try:
        with open('config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        return True
    except Exception as e:
        logger.error(f"保存配置文件失败: {e}")
        return False


def read_logs(lines=50):
    """读取最近的日志"""
    try:
        log_files = ['weibo_monitor.log', 'web_server.log']
        all_logs = []
        
        for log_file in log_files:
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = f.readlines()
                    all_logs.extend([{'file': log_file, 'content': line.strip()} for line in logs[-lines:]])
        
        return all_logs[-lines:]
    except Exception as e:
        logger.error(f"读取日志失败: {e}")
        return []


def read_notified_weibs():
    """读取已通知的微博记录"""
    try:
        config = load_config()
        notified_file = config['monitor']['notified_file']
        
        if os.path.exists(notified_file):
            with open(notified_file, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        return []
    except Exception as e:
        logger.error(f"读取通知记录失败: {e}")
        return []


# ===== Web路由 =====

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/config', methods=['GET'])
def get_config():
    """获取当前配置"""
    config = load_config()
    if config:
        return jsonify({
            'success': True,
            'config': config
        })
    return jsonify({
        'success': False,
        'message': '加载配置失败'
    }), 500


@app.route('/api/config', methods=['POST'])
def update_config():
    """更新配置"""
    try:
        data = request.json
        config = load_config()
        
        if not config:
            return jsonify({
                'success': False,
                'message': '加载配置失败'
            }), 500
        
        # 更新配置
        if 'weibo_url' in data:
            config['weibo_url'] = data['weibo_url']
        
        if 'keywords' in data:
            config['keywords'] = data['keywords']
        
        if 'telegram' in data:
            if 'bot_token' in data['telegram']:
                config['telegram']['bot_token'] = data['telegram']['bot_token']
            if 'chat_id' in data['telegram']:
                config['telegram']['chat_id'] = data['telegram']['chat_id']
        
        if 'monitor' in data:
            if 'check_interval' in data['monitor']:
                config['monitor']['check_interval'] = int(data['monitor']['check_interval'])
            if 'headless' in data['monitor']:
                config['monitor']['headless'] = data['monitor']['headless']
        
        # 保存配置
        if save_config(config):
            # 如果监控正在运行，需要重启以应用新配置
            global monitor_instance
            if monitor_running and monitor_instance:
                logger.info("配置已更新，将在下次检查时应用新配置")
            
            return jsonify({
                'success': True,
                'message': '配置保存成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '配置保存失败'
            }), 500
    
    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        return jsonify({
            'success': False,
            'message': f'更新配置失败: {str(e)}'
        }), 500


@app.route('/api/monitor/start', methods=['POST'])
def start_monitor():
    """启动监控"""
    global monitor_thread, monitor_instance, monitor_running, monitor_stats
    
    if monitor_running:
        return jsonify({
            'success': False,
            'message': '监控已在运行中'
        })
    
    try:
        monitor_instance = WeiboMonitor()
        monitor_running = True
        monitor_stats['status'] = 'running'
        monitor_stats['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 在新线程中启动监控
        monitor_thread = threading.Thread(target=run_monitor, daemon=True)
        monitor_thread.start()
        
        logger.info("监控已启动")
        return jsonify({
            'success': True,
            'message': '监控启动成功'
        })
    
    except Exception as e:
        monitor_running = False
        monitor_stats['status'] = 'error'
        logger.error(f"启动监控失败: {e}")
        return jsonify({
            'success': False,
            'message': f'启动监控失败: {str(e)}'
        }), 500


@app.route('/api/monitor/stop', methods=['POST'])
def stop_monitor():
    """停止监控"""
    global monitor_running, monitor_stats, monitor_instance
    
    if not monitor_running:
        return jsonify({
            'success': False,
            'message': '监控未运行'
        })
    
    try:
        monitor_running = False
        monitor_stats['status'] = 'stopped'
        
        # 关闭浏览器驱动
        if monitor_instance:
            monitor_instance._close_driver()
        
        logger.info("监控已停止")
        return jsonify({
            'success': True,
            'message': '监控停止成功'
        })
    
    except Exception as e:
        logger.error(f"停止监控失败: {e}")
        return jsonify({
            'success': False,
            'message': f'停止监控失败: {str(e)}'
        }), 500


@app.route('/api/monitor/status', methods=['GET'])
def get_status():
    """获取监控状态"""
    return jsonify({
        'success': True,
        'status': monitor_stats
    })


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """获取日志"""
    lines = request.args.get('lines', 50, type=int)
    logs = read_logs(lines)
    return jsonify({
        'success': True,
        'logs': logs
    })


@app.route('/api/notified', methods=['GET'])
def get_notified():
    """获取已通知的微博列表"""
    notified = read_notified_weibs()
    return jsonify({
        'success': True,
        'count': len(notified),
        'notified': notified[-20:]  # 只返回最近20条
    })


@app.route('/api/keywords', methods=['GET'])
def get_keywords():
    """获取关键词列表"""
    config = load_config()
    if config:
        return jsonify({
            'success': True,
            'keywords': config.get('keywords', [])
        })
    return jsonify({
        'success': False,
        'message': '加载配置失败'
    }), 500


@app.route('/api/keywords', methods=['POST'])
def add_keyword():
    """添加关键词"""
    try:
        data = request.json
        keyword = data.get('keyword', '').strip()
        
        if not keyword:
            return jsonify({
                'success': False,
                'message': '关键词不能为空'
            }), 400
        
        config = load_config()
        if not config:
            return jsonify({
                'success': False,
                'message': '加载配置失败'
            }), 500
        
        if 'keywords' not in config:
            config['keywords'] = []
        
        if keyword in config['keywords']:
            return jsonify({
                'success': False,
                'message': '关键词已存在'
            }), 400
        
        config['keywords'].append(keyword)
        
        if save_config(config):
            logger.info(f"添加关键词: {keyword}")
            return jsonify({
                'success': True,
                'message': '关键词添加成功',
                'keywords': config['keywords']
            })
        else:
            return jsonify({
                'success': False,
                'message': '保存配置失败'
            }), 500
    
    except Exception as e:
        logger.error(f"添加关键词失败: {e}")
        return jsonify({
            'success': False,
            'message': f'添加关键词失败: {str(e)}'
        }), 500


@app.route('/api/keywords/<int:index>', methods=['PUT'])
def update_keyword(index):
    """更新关键词"""
    try:
        data = request.json
        new_keyword = data.get('keyword', '').strip()
        
        if not new_keyword:
            return jsonify({
                'success': False,
                'message': '关键词不能为空'
            }), 400
        
        config = load_config()
        if not config:
            return jsonify({
                'success': False,
                'message': '加载配置失败'
            }), 500
        
        if index < 0 or index >= len(config['keywords']):
            return jsonify({
                'success': False,
                'message': '关键词索引无效'
            }), 400
        
        old_keyword = config['keywords'][index]
        config['keywords'][index] = new_keyword
        
        if save_config(config):
            logger.info(f"更新关键词: {old_keyword} -> {new_keyword}")
            return jsonify({
                'success': True,
                'message': '关键词更新成功',
                'keywords': config['keywords']
            })
        else:
            return jsonify({
                'success': False,
                'message': '保存配置失败'
            }), 500
    
    except Exception as e:
        logger.error(f"更新关键词失败: {e}")
        return jsonify({
            'success': False,
            'message': f'更新关键词失败: {str(e)}'
        }), 500


@app.route('/api/keywords/<int:index>', methods=['DELETE'])
def delete_keyword(index):
    """删除关键词"""
    try:
        config = load_config()
        if not config:
            return jsonify({
                'success': False,
                'message': '加载配置失败'
            }), 500
        
        if index < 0 or index >= len(config['keywords']):
            return jsonify({
                'success': False,
                'message': '关键词索引无效'
            }), 400
        
        deleted_keyword = config['keywords'].pop(index)
        
        if save_config(config):
            logger.info(f"删除关键词: {deleted_keyword}")
            return jsonify({
                'success': True,
                'message': '关键词删除成功',
                'keywords': config['keywords']
            })
        else:
            return jsonify({
                'success': False,
                'message': '保存配置失败'
            }), 500
    
    except Exception as e:
        logger.error(f"删除关键词失败: {e}")
        return jsonify({
            'success': False,
            'message': f'删除关键词失败: {str(e)}'
        }), 500


@app.route('/api/test/telegram', methods=['POST'])
def test_telegram():
    """测试Telegram连接"""
    try:
        from telegram import Bot
        config = load_config()
        
        # 检查是否配置了代理
        proxy_url = config['telegram'].get('proxy_url', '')
        if proxy_url:
            from telegram.request import HTTPXRequest
            request = HTTPXRequest(proxy=proxy_url)
            bot = Bot(token=config['telegram']['bot_token'], request=request)
        else:
            bot = Bot(token=config['telegram']['bot_token'])
        
        bot.send_message(
            chat_id=config['telegram']['chat_id'],
            text=f"✅ Telegram连接测试成功！\n\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        return jsonify({
            'success': True,
            'message': 'Telegram连接测试成功，请检查消息'
        })
    
    except Exception as e:
        logger.error(f"Telegram测试失败: {e}")
        return jsonify({
            'success': False,
            'message': f'Telegram连接失败: {str(e)}'
        }), 500


def run_monitor():
    """运行监控（在后台线程中）"""
    global monitor_instance, monitor_running, monitor_stats
    
    try:
        import schedule
        import time
        
        # 设置定时任务
        config = load_config()
        interval = config['monitor']['check_interval']
        
        def check_wrapper():
            global monitor_stats
            try:
                monitor_stats['check_count'] += 1
                monitor_stats['last_check_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                monitor_instance.monitor_once()
            except Exception as e:
                logger.error(f"监控检查出错: {e}")
        
        # 立即执行一次
        check_wrapper()
        
        # 设置定时任务
        schedule.every(interval).minutes.do(check_wrapper)
        
        logger.info(f"监控循环已启动，每 {interval} 分钟检查一次")
        
        while monitor_running:
            schedule.run_pending()
            time.sleep(1)
        
        logger.info("监控循环已退出")
    
    except Exception as e:
        logger.error(f"监控运行出错: {e}")
        monitor_stats['status'] = 'error'


def main():
    """主函数"""
    config = load_config()
    if not config:
        logger.error("无法加载配置文件，请检查 config.yaml")
        return
    
    host = config.get('web', {}).get('host', '127.0.0.1')
    port = config.get('web', {}).get('port', 5000)
    
    logger.info("="*50)
    logger.info("微博监控Web管理界面")
    logger.info("="*50)
    logger.info(f"服务器地址: http://{host}:{port}")
    logger.info("按 Ctrl+C 停止服务器")
    logger.info("="*50)
    
    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == '__main__':
    main()

