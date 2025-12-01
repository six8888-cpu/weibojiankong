"""
简化版监控模块 - 不需要Playwright
使用requests库进行监控，适合简单网页
"""
import logging
import asyncio
import aiohttp
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class WebMonitor:
    """简化版网页监控器（使用HTTP请求，不需要浏览器）"""
    
    def __init__(self, database, telegram_notifier=None):
        self.db = database
        self.telegram_notifier = telegram_notifier
        logger.info("初始化简化版监控器（HTTP模式）")
    
    async def check_url(self, url_data: dict):
        """检查单个URL"""
        url_id = url_data['id']
        url = url_data['url']
        name = url_data['name']
        
        try:
            logger.info(f"开始检查URL: {name} ({url})")
            
            # 获取该URL的所有关键词
            keywords = self.db.get_keywords_by_url(url_id)
            
            if not keywords:
                logger.warning(f"URL {name} 没有配置关键词")
                return
            
            # 使用aiohttp获取页面内容
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                try:
                    async with session.get(url, headers=headers, timeout=30) as response:
                        if response.status != 200:
                            logger.error(f"访问失败: {url}, 状态码: {response.status}")
                            self.db.add_log(url_id, None, False, f"访问失败，状态码: {response.status}")
                            return
                        
                        # 获取页面内容
                        content = await response.text()
                        logger.info(f"成功获取页面内容，长度: {len(content)}")
                        
                except asyncio.TimeoutError:
                    logger.error(f"访问超时: {url}")
                    self.db.add_log(url_id, None, False, "访问超时")
                    return
                except Exception as e:
                    logger.error(f"访问出错: {url}, 错误: {e}")
                    self.db.add_log(url_id, None, False, f"访问出错: {str(e)}")
                    return
            
            # 检查关键词
            found_keywords = []
            for keyword_data in keywords:
                keyword = keyword_data['keyword']
                fuzzy_match = keyword_data['fuzzy_match']
                
                if fuzzy_match:
                    # 模糊匹配
                    if keyword.lower() in content.lower():
                        found_keywords.append(keyword)
                        logger.info(f"✓ 找到关键词: {keyword}")
                else:
                    # 精确匹配
                    if keyword in content:
                        found_keywords.append(keyword)
                        logger.info(f"✓ 找到关键词: {keyword}")
            
            # 记录结果
            if found_keywords:
                message = f"发现 {len(found_keywords)} 个关键词"
                logger.info(f"URL {name}: {message}")
                
                # 记录日志
                for kw in found_keywords:
                    self.db.add_log(url_id, kw, True, "关键词匹配成功")
                
                # 发送Telegram通知
                if self.telegram_notifier:
                    notify_msg = (
                        f"🔔 <b>监控提醒</b>\n\n"
                        f"📋 网址：{name}\n"
                        f"🔗 链接：{url}\n"
                        f"🔑 关键词：{', '.join(found_keywords)}\n"
                        f"⏰ 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    await self.telegram_notifier.send_message(notify_msg)
            else:
                logger.info(f"URL {name}: 未发现关键词")
                self.db.add_log(url_id, None, False, "未发现关键词")
                
        except Exception as e:
            logger.error(f"检查URL失败: {name}, 错误: {e}", exc_info=True)
            self.db.add_log(url_id, None, False, f"检查失败: {str(e)}")
    
    async def check_all_urls(self):
        """检查所有启用的URL"""
        try:
            urls = self.db.get_enabled_urls()
            
            if not urls:
                logger.info("没有启用的监控URL")
                return
            
            logger.info(f"开始检查 {len(urls)} 个URL...")
            
            # 并发检查所有URL
            tasks = [self.check_url(url) for url in urls]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            logger.info("所有URL检查完成")
            
        except Exception as e:
            logger.error(f"检查所有URL失败: {e}", exc_info=True)
