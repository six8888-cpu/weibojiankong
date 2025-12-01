"""
Telegram通知模块
用于发送监控提醒
"""
import logging
import aiohttp
from typing import Optional

# 尝试导入SOCKS5支持
try:
    from aiohttp_socks import ProxyConnector
    SOCKS_AVAILABLE = True
except ImportError:
    SOCKS_AVAILABLE = False
    logging.warning("aiohttp-socks未安装，SOCKS5代理功能不可用")

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str, proxy_url: str = None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.proxy_url = proxy_url
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    async def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """
        发送Telegram消息
        
        Args:
            message: 消息内容
            parse_mode: 解析模式（HTML或Markdown）
        
        Returns:
            是否发送成功
        """
        try:
            url = f"{self.api_url}/sendMessage"
            
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            # 配置连接器和代理
            connector = None
            
            if self.proxy_url:
                if self.proxy_url.startswith('socks5://') or self.proxy_url.startswith('socks4://'):
                    # SOCKS代理需要aiohttp-socks
                    if SOCKS_AVAILABLE:
                        connector = ProxyConnector.from_url(self.proxy_url)
                        logger.info(f"使用SOCKS代理: {self.proxy_url.split('@')[-1]}")
                    else:
                        logger.error("SOCKS5代理需要安装 aiohttp-socks: pip install aiohttp-socks")
                        return False
                else:
                    # HTTP/HTTPS代理使用普通connector
                    connector = aiohttp.TCPConnector()
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            # 根据代理类型决定如何传递
            if self.proxy_url and not self.proxy_url.startswith('socks'):
                # HTTP/HTTPS代理
                async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                    async with session.post(url, json=data, proxy=self.proxy_url) as response:
                        if response.status == 200:
                            logger.info("Telegram消息发送成功")
                            return True
                        else:
                            error_text = await response.text()
                            logger.error(f"Telegram消息发送失败: {response.status}, {error_text}")
                            return False
            else:
                # SOCKS代理或无代理
                async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                    async with session.post(url, json=data) as response:
                        if response.status == 200:
                            logger.info("Telegram消息发送成功")
                            return True
                        else:
                            error_text = await response.text()
                            logger.error(f"Telegram消息发送失败: {response.status}, {error_text}")
                            return False
        
        except Exception as e:
            logger.error(f"发送Telegram消息异常: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """
        测试Telegram连接
        
        Returns:
            连接是否正常
        """
        try:
            url = f"{self.api_url}/getMe"
            
            # 配置连接器和代理
            connector = None
            
            if self.proxy_url:
                if self.proxy_url.startswith('socks5://') or self.proxy_url.startswith('socks4://'):
                    # SOCKS代理需要aiohttp-socks
                    if SOCKS_AVAILABLE:
                        connector = ProxyConnector.from_url(self.proxy_url)
                    else:
                        logger.error("SOCKS5代理需要安装 aiohttp-socks: pip install aiohttp-socks")
                        return False
                else:
                    # HTTP/HTTPS代理
                    connector = aiohttp.TCPConnector()
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            # 根据代理类型决定如何传递
            if self.proxy_url and not self.proxy_url.startswith('socks'):
                # HTTP/HTTPS代理
                async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                    async with session.get(url, proxy=self.proxy_url) as response:
                        if response.status == 200:
                            result = await response.json()
                            if result.get('ok'):
                                logger.info(f"Telegram连接测试成功: {result.get('result', {}).get('username')}")
                                return True
                        
                        logger.error(f"Telegram连接测试失败: {response.status}")
                        return False
            else:
                # SOCKS代理或无代理
                async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            result = await response.json()
                            if result.get('ok'):
                                logger.info(f"Telegram连接测试成功: {result.get('result', {}).get('username')}")
                                return True
                        
                        logger.error(f"Telegram连接测试失败: {response.status}")
                        return False
        
        except Exception as e:
            logger.error(f"Telegram连接测试异常: {e}")
            return False

