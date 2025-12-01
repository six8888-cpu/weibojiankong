#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微博关键词监控脚本
监控指定微博用户的最新内容，发现关键词时通过Telegram发送通知
"""

import os
import time
import yaml
import json
import logging
from datetime import datetime
from typing import List, Set, Dict
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import schedule
from telegram import Bot
from telegram.error import TelegramError

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weibo_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WeiboMonitor:
    """微博监控类"""
    
    def __init__(self, config_file: str = 'config.yaml'):
        """初始化监控器"""
        self.config = self._load_config(config_file)
        self.notified_ids: Set[str] = self._load_notified_ids()
        self.driver = None
        self.telegram_bot = None
        
        # 初始化Telegram Bot
        if self.config['telegram']['bot_token'] != 'YOUR_BOT_TOKEN_HERE':
            try:
                # 检查是否配置了代理
                proxy_url = self.config['telegram'].get('proxy_url', '')
                if proxy_url:
                    from telegram.request import HTTPXRequest
                    request = HTTPXRequest(proxy=proxy_url)
                    self.telegram_bot = Bot(token=self.config['telegram']['bot_token'], request=request)
                    logger.info(f"Telegram Bot 初始化成功（使用代理: {proxy_url}）")
                else:
                    self.telegram_bot = Bot(token=self.config['telegram']['bot_token'])
                    logger.info("Telegram Bot 初始化成功")
            except Exception as e:
                logger.error(f"Telegram Bot 初始化失败: {e}")
        else:
            logger.warning("请在 config.yaml 中配置 Telegram Bot Token")
    
    def _load_config(self, config_file: str) -> dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"配置文件加载成功: {config_file}")
            return config
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            raise
    
    def _load_notified_ids(self) -> Set[str]:
        """加载已通知的微博ID"""
        notified_file = self.config['monitor']['notified_file']
        if os.path.exists(notified_file):
            try:
                with open(notified_file, 'r', encoding='utf-8') as f:
                    ids = set(line.strip() for line in f if line.strip())
                logger.info(f"已加载 {len(ids)} 个已通知的微博ID")
                return ids
            except Exception as e:
                logger.error(f"加载已通知ID文件失败: {e}")
                return set()
        return set()
    
    def _save_notified_id(self, weibo_id: str):
        """保存已通知的微博ID"""
        self.notified_ids.add(weibo_id)
        try:
            with open(self.config['monitor']['notified_file'], 'a', encoding='utf-8') as f:
                f.write(f"{weibo_id}\n")
            logger.info(f"已保存通知记录: {weibo_id}")
        except Exception as e:
            logger.error(f"保存通知记录失败: {e}")
    
    def _init_driver(self):
        """初始化浏览器驱动"""
        try:
            options = uc.ChromeOptions()
            
            if self.config['monitor']['headless']:
                options.add_argument('--headless=new')  # 使用新版无头模式
            
            # 添加反爬策略 - 增强版
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # 隐藏webdriver特征
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = uc.Chrome(options=options)
            
            # 额外的反检测措施
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.driver.set_page_load_timeout(self.config['monitor']['page_load_timeout'])
            logger.info("浏览器驱动初始化成功（已启用反检测）")
        except Exception as e:
            logger.error(f"浏览器驱动初始化失败: {e}")
            raise
    
    def _close_driver(self):
        """关闭浏览器驱动"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("浏览器驱动已关闭")
            except Exception as e:
                logger.error(f"关闭浏览器驱动失败: {e}")
    
    def fetch_weibo_content(self) -> List[Dict[str, str]]:
        """获取微博内容"""
        weibo_list = []
        
        try:
            logger.info(f"开始访问微博页面: {self.config['weibo_url']}")
            self.driver.get(self.config['weibo_url'])
            
            # 等待页面加载 - 让微博的访客系统完成验证
            logger.info("等待页面加载和访客验证...")
            time.sleep(8)  # 增加等待时间以通过访客验证
            
            # 检查是否被重定向到登录页面
            current_url = self.driver.current_url
            if 'passport.weibo.com' in current_url or 'login' in current_url:
                logger.warning("页面被重定向到登录/验证页面，等待自动跳转...")
                time.sleep(5)
                # 刷新一次
                self.driver.refresh()
                time.sleep(5)
            
            # 尝试滚动页面以加载更多内容
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(3)
            
            # 获取页面源代码
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            
            # 尝试多种选择器来提取微博内容
            # 微博的HTML结构可能会变化，这里提供几种常见的选择方式
            
            # 方法1：查找包含微博文字的元素
            weibo_items = soup.find_all('article') or soup.find_all('div', class_=['card-wrap', 'weibo-card'])
            
            logger.info(f"找到 {len(weibo_items)} 个可能的微博元素")
            
            for item in weibo_items[:10]:  # 只检查最新的10条
                try:
                    # 提取微博ID（用于去重）
                    weibo_id = None
                    mid_elem = item.get('mid') or item.get('data-mid')
                    if mid_elem:
                        weibo_id = str(mid_elem)
                    
                    # 提取文字内容
                    text_content = ""
                    
                    # 尝试多种方式提取文字
                    text_elem = (
                        item.find('div', class_='txt') or 
                        item.find('div', class_='content') or
                        item.find('div', class_='Feed_body')
                    )
                    
                    if text_elem:
                        text_content = text_elem.get_text(strip=True, separator=' ')
                    else:
                        # 如果找不到特定class，就取整个item的文字
                        text_content = item.get_text(strip=True, separator=' ')
                    
                    # 如果没有ID，使用文字内容的hash作为ID
                    if not weibo_id and text_content:
                        weibo_id = str(hash(text_content[:100]))
                    
                    if text_content and weibo_id:
                        weibo_list.append({
                            'id': weibo_id,
                            'text': text_content,
                            'url': self.config['weibo_url']
                        })
                        logger.debug(f"提取到微博 {weibo_id}: {text_content[:50]}...")
                
                except Exception as e:
                    logger.error(f"解析单条微博失败: {e}")
                    continue
            
            logger.info(f"成功提取 {len(weibo_list)} 条微博")
            
        except Exception as e:
            logger.error(f"获取微博内容失败: {e}")
        
        return weibo_list
    
    def check_keywords(self, text: str) -> List[str]:
        """检查文本中是否包含关键词"""
        found_keywords = []
        for keyword in self.config['keywords']:
            if keyword in text:
                found_keywords.append(keyword)
        return found_keywords
    
    def send_telegram_notification(self, weibo: Dict[str, str], keywords: List[str]):
        """发送Telegram通知"""
        if not self.telegram_bot:
            logger.warning("Telegram Bot 未配置，跳过发送通知")
            return
        
        try:
            message = (
                f"🔔 微博关键词提醒\n\n"
                f"🎯 匹配关键词: {', '.join(keywords)}\n\n"
                f"📝 微博内容:\n{weibo['text'][:500]}\n\n"
                f"🔗 链接: {weibo['url']}\n\n"
                f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            self.telegram_bot.send_message(
                chat_id=self.config['telegram']['chat_id'],
                text=message
            )
            logger.info(f"Telegram通知发送成功: 微博 {weibo['id']}")
        except TelegramError as e:
            logger.error(f"Telegram通知发送失败: {e}")
        except Exception as e:
            logger.error(f"发送通知时发生错误: {e}")
    
    def monitor_once(self):
        """执行一次监控"""
        logger.info("=" * 50)
        logger.info(f"开始监控检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 初始化浏览器（如果还没有）
            if not self.driver:
                self._init_driver()
            
            # 获取微博内容
            weibo_list = self.fetch_weibo_content()
            
            if not weibo_list:
                logger.warning("未获取到任何微博内容")
                return
            
            # 检查每条微博
            for weibo in weibo_list:
                # 跳过已通知的微博
                if weibo['id'] in self.notified_ids:
                    continue
                
                # 检查关键词
                found_keywords = self.check_keywords(weibo['text'])
                
                if found_keywords:
                    logger.info(f"发现匹配关键词: {found_keywords}")
                    logger.info(f"微博内容: {weibo['text'][:100]}...")
                    
                    # 发送通知
                    self.send_telegram_notification(weibo, found_keywords)
                    
                    # 保存已通知ID
                    self._save_notified_id(weibo['id'])
            
            logger.info(f"监控检查完成")
            
        except Exception as e:
            logger.error(f"监控过程中发生错误: {e}")
            # 如果出错，尝试重启浏览器
            self._close_driver()
            self.driver = None
    
    def start_monitoring(self):
        """开始监控"""
        logger.info("微博监控程序启动")
        logger.info(f"监控URL: {self.config['weibo_url']}")
        logger.info(f"关键词: {', '.join(self.config['keywords'])}")
        logger.info(f"检查间隔: {self.config['monitor']['check_interval']} 分钟")
        
        # 立即执行一次监控
        self.monitor_once()
        
        # 设置定时任务
        schedule.every(self.config['monitor']['check_interval']).minutes.do(self.monitor_once)
        
        logger.info("进入监控循环...")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("接收到停止信号，正在关闭...")
        finally:
            self._close_driver()
            logger.info("监控程序已停止")


def main():
    """主函数"""
    try:
        monitor = WeiboMonitor()
        monitor.start_monitoring()
    except Exception as e:
        logger.error(f"程序启动失败: {e}")
        raise


if __name__ == '__main__':
    main()

