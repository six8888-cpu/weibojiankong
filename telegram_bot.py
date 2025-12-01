"""
Telegram通知模块
用于发送监控提醒
"""
import logging
import aiohttp
from typing import Optional

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
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
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, timeout=10) as response:
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
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
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

