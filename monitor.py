"""
网页监控模块
使用Playwright进行反爬虫绕过
参考: https://github.com/bright-cn/bypass-cloudflare
"""
import asyncio
import logging
import re
from typing import List, Dict, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)


class WebMonitor:
    def __init__(self, database, telegram_notifier=None):
        self.db = database
        self.telegram_notifier = telegram_notifier
        self.browser = None
    
    async def init_browser(self):
        """初始化浏览器（反检测配置）"""
        if self.browser:
            return
        
        try:
            playwright = await async_playwright().start()
            
            # 启动浏览器，配置反检测参数
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',  # 禁用自动化控制特征
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--no-proxy-server',  # 禁用代理服务器
                ]
            )
            
            logger.info("浏览器初始化成功")
        except Exception as e:
            logger.error(f"浏览器初始化失败: {e}")
            raise
    
    async def create_stealth_page(self) -> Page:
        """创建反检测页面"""
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
        )
        
        page = await context.new_page()
        
        # 注入反检测脚本
        await page.add_init_script("""
            // 覆盖 navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // 覆盖 navigator.plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // 覆盖 navigator.languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en-US', 'en']
            });
            
            // 覆盖 chrome 对象
            window.chrome = {
                runtime: {}
            };
            
            // 覆盖权限查询
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        return page
    
    async def fetch_page_content(self, url: str) -> Optional[str]:
        """
        获取网页内容（反爬虫绕过）
        使用Playwright模拟真实浏览器行为
        """
        page = None
        try:
            if not self.browser:
                await self.init_browser()
            
            page = await self.create_stealth_page()
            
            # 设置超时时间
            page.set_default_timeout(30000)
            
            # 访问页面
            logger.info(f"正在访问: {url}")
            response = await page.goto(url, wait_until='networkidle')
            
            if not response:
                logger.error(f"无法访问: {url}")
                return None
            
            # 等待页面加载完成
            await asyncio.sleep(2)
            
            # 随机滚动页面（模拟真实用户行为）
            await page.evaluate("""
                window.scrollTo(0, document.body.scrollHeight / 2);
            """)
            await asyncio.sleep(1)
            
            # 获取页面内容
            content = await page.content()
            
            logger.info(f"成功获取页面内容: {url} (长度: {len(content)})")
            return content
            
        except PlaywrightTimeoutError:
            logger.error(f"访问超时: {url}")
            return None
        except Exception as e:
            logger.error(f"获取页面内容失败: {url}, 错误: {e}")
            return None
        finally:
            if page:
                await page.close()
    
    def check_keyword(self, content: str, keyword: str, fuzzy_match: bool = True) -> bool:
        """
        检查内容中是否包含关键词
        
        Args:
            content: 网页内容
            keyword: 关键词
            fuzzy_match: 是否模糊匹配
        
        Returns:
            是否找到关键词
        """
        if not content or not keyword:
            return False
        
        # 转换为小写进行比较
        content_lower = content.lower()
        keyword_lower = keyword.lower()
        
        if fuzzy_match:
            # 模糊匹配：只要包含关键词即可
            return keyword_lower in content_lower
        else:
            # 精确匹配：使用正则表达式匹配完整单词
            pattern = r'\b' + re.escape(keyword_lower) + r'\b'
            return bool(re.search(pattern, content_lower))
    
    async def check_url(self, url_data: Dict):
        """
        检查单个URL
        
        Args:
            url_data: URL数据，包含id, url, name等字段
        """
        url_id = url_data['id']
        url = url_data['url']
        url_name = url_data.get('name', url)
        
        logger.info(f"开始检查: {url_name} ({url})")
        
        # 获取该URL的所有关键词
        keywords = self.db.get_keywords_by_url(url_id)
        
        if not keywords:
            logger.warning(f"URL {url_name} 没有配置关键词，跳过检查")
            self.db.add_log(url_id, None, False, "没有配置关键词")
            return
        
        # 获取网页内容
        content = await self.fetch_page_content(url)
        
        if not content:
            logger.error(f"无法获取页面内容: {url_name}")
            self.db.add_log(url_id, None, False, "无法获取页面内容")
            return
        
        # 检查每个关键词
        found_keywords = []
        
        for kw_data in keywords:
            keyword = kw_data['keyword']
            fuzzy_match = bool(kw_data['fuzzy_match'])
            
            if self.check_keyword(content, keyword, fuzzy_match):
                found_keywords.append(keyword)
                logger.info(f"✓ 找到关键词: {keyword} (URL: {url_name})")
                
                # 记录日志
                self.db.add_log(url_id, keyword, True, f"检测到关键词: {keyword}")
                
                # 发送Telegram通知
                if self.telegram_notifier:
                    message = f"""
🔔 <b>监控提醒</b>

📌 <b>网址:</b> {url_name}
🔗 <b>链接:</b> {url}
🔑 <b>关键词:</b> {keyword}
⏰ <b>时间:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ 检测到指定关键词！

⚠️ 该关键词已自动删除，不会再次通知。
                    """.strip()
                    
                    await self.telegram_notifier.send_message(message)
                
                # 自动删除已检测到的关键词，避免重复通知
                self.db.delete_keyword(kw_data['id'])
                logger.info(f"🗑️ 自动删除关键词: {keyword} (已通知)")
        
        if not found_keywords:
            logger.info(f"✗ 未找到关键词 (URL: {url_name})")
            self.db.add_log(url_id, None, False, "未检测到关键词")
    
    async def check_all_urls(self):
        """检查所有启用的URL"""
        try:
            # 获取所有启用的URL
            urls = self.db.get_enabled_urls()
            
            if not urls:
                logger.info("没有启用的监控URL")
                return
            
            logger.info(f"开始检查 {len(urls)} 个URL...")
            
            # 初始化浏览器
            await self.init_browser()
            
            # 检查每个URL
            for url_data in urls:
                try:
                    await self.check_url(url_data)
                except Exception as e:
                    logger.error(f"检查URL失败: {url_data.get('name', url_data['url'])}, 错误: {e}")
                
                # 添加延迟，避免请求过快
                await asyncio.sleep(2)
            
            logger.info("所有URL检查完成")
            
        except Exception as e:
            logger.error(f"检查所有URL失败: {e}", exc_info=True)
        finally:
            # 关闭浏览器
            if self.browser:
                await self.browser.close()
                self.browser = None

