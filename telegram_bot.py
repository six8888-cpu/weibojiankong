"""
Telegram通知模块
用于发送监控提醒
"""
import logging
import aiohttp
from typing import Optional

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
            
            # 配置连接器（支持代理）
            connector = None
            if self.proxy_url:
                connector = aiohttp.TCPConnector()
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                kwargs = {'json': data}
                if self.proxy_url:
                    kwargs['proxy'] = self.proxy_url
                
                async with session.post(url, **kwargs) as response:
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
            
            # 配置连接器（支持代理）
            connector = None
            if self.proxy_url:
                connector = aiohttp.TCPConnector()
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                kwargs = {}
                if self.proxy_url:
                    kwargs['proxy'] = self.proxy_url
                
                async with session.get(url, **kwargs) as response:
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

