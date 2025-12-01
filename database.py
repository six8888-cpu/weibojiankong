"""
数据库管理模块
使用SQLite存储监控配置和日志
"""
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path='monitor.db'):
        self.db_path = db_path
    
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """初始化数据库"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 创建监控URL表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitor_urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                name TEXT,
                check_interval INTEGER DEFAULT 300,
                enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建关键词表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_id INTEGER NOT NULL,
                keyword TEXT NOT NULL,
                fuzzy_match BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (url_id) REFERENCES monitor_urls (id) ON DELETE CASCADE
            )
        ''')
        
        # 创建监控日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitor_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_id INTEGER NOT NULL,
                keyword TEXT,
                found BOOLEAN DEFAULT 0,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (url_id) REFERENCES monitor_urls (id) ON DELETE CASCADE
            )
        ''')
        
        # 创建Telegram配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS telegram_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_token TEXT NOT NULL,
                chat_id TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("数据库初始化完成")
    
    # ==================== URL管理 ====================
    
    def add_url(self, url: str, name: str = None, check_interval: int = 300) -> int:
        """添加监控URL"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO monitor_urls (url, name, check_interval)
            VALUES (?, ?, ?)
        ''', (url, name or url, check_interval))
        
        url_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"添加监控URL: {url} (ID: {url_id})")
        return url_id
    
    def get_all_urls(self) -> List[Dict]:
        """获取所有监控URL"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, url, name, check_interval, enabled, created_at, updated_at
            FROM monitor_urls
            ORDER BY created_at DESC
        ''')
        
        urls = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return urls
    
    def get_enabled_urls(self) -> List[Dict]:
        """获取启用的监控URL"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, url, name, check_interval
            FROM monitor_urls
            WHERE enabled = 1
            ORDER BY created_at DESC
        ''')
        
        urls = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return urls
    
    def update_url(self, url_id: int, url: str = None, name: str = None, 
                   check_interval: int = None, enabled: bool = None):
        """更新监控URL"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if url is not None:
            updates.append('url = ?')
            params.append(url)
        if name is not None:
            updates.append('name = ?')
            params.append(name)
        if check_interval is not None:
            updates.append('check_interval = ?')
            params.append(check_interval)
        if enabled is not None:
            updates.append('enabled = ?')
            params.append(1 if enabled else 0)
        
        if updates:
            updates.append('updated_at = CURRENT_TIMESTAMP')
            params.append(url_id)
            
            sql = f'''
                UPDATE monitor_urls
                SET {', '.join(updates)}
                WHERE id = ?
            '''
            
            cursor.execute(sql, params)
            conn.commit()
        
        conn.close()
        logger.info(f"更新监控URL: {url_id}")
    
    def delete_url(self, url_id: int):
        """删除监控URL"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM monitor_urls WHERE id = ?', (url_id,))
        conn.commit()
        conn.close()
        
        logger.info(f"删除监控URL: {url_id}")
    
    # ==================== 关键词管理 ====================
    
    def add_keyword(self, url_id: int, keyword: str, fuzzy_match: bool = True) -> int:
        """添加关键词"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO keywords (url_id, keyword, fuzzy_match)
            VALUES (?, ?, ?)
        ''', (url_id, keyword, 1 if fuzzy_match else 0))
        
        keyword_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"添加关键词: {keyword} (URL ID: {url_id})")
        return keyword_id
    
    def get_keywords(self, url_id: int = None) -> List[Dict]:
        """获取关键词"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if url_id:
            cursor.execute('''
                SELECT k.id, k.url_id, k.keyword, k.fuzzy_match, k.created_at,
                       u.name as url_name, u.url
                FROM keywords k
                JOIN monitor_urls u ON k.url_id = u.id
                WHERE k.url_id = ?
                ORDER BY k.created_at DESC
            ''', (url_id,))
        else:
            cursor.execute('''
                SELECT k.id, k.url_id, k.keyword, k.fuzzy_match, k.created_at,
                       u.name as url_name, u.url
                FROM keywords k
                JOIN monitor_urls u ON k.url_id = u.id
                ORDER BY k.created_at DESC
            ''')
        
        keywords = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return keywords
    
    def get_keywords_by_url(self, url_id: int) -> List[Dict]:
        """获取指定URL的关键词"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, keyword, fuzzy_match
            FROM keywords
            WHERE url_id = ?
        ''', (url_id,))
        
        keywords = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return keywords
    
    def delete_keyword(self, keyword_id: int):
        """删除关键词"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM keywords WHERE id = ?', (keyword_id,))
        conn.commit()
        conn.close()
        
        logger.info(f"删除关键词: {keyword_id}")
    
    # ==================== 日志管理 ====================
    
    def add_log(self, url_id: int, keyword: str = None, found: bool = False, message: str = None):
        """添加监控日志"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO monitor_logs (url_id, keyword, found, message)
            VALUES (?, ?, ?, ?)
        ''', (url_id, keyword, 1 if found else 0, message))
        
        conn.commit()
        conn.close()
    
    def get_logs(self, limit: int = 100, url_id: int = None) -> List[Dict]:
        """获取监控日志"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if url_id:
            cursor.execute('''
                SELECT l.id, l.url_id, l.keyword, l.found, l.message, l.created_at,
                       u.name as url_name, u.url
                FROM monitor_logs l
                JOIN monitor_urls u ON l.url_id = u.id
                WHERE l.url_id = ?
                ORDER BY l.created_at DESC
                LIMIT ?
            ''', (url_id, limit))
        else:
            cursor.execute('''
                SELECT l.id, l.url_id, l.keyword, l.found, l.message, l.created_at,
                       u.name as url_name, u.url
                FROM monitor_logs l
                JOIN monitor_urls u ON l.url_id = u.id
                ORDER BY l.created_at DESC
                LIMIT ?
            ''', (limit,))
        
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return logs
    
    # ==================== Telegram配置 ====================
    
    def update_telegram_config(self, bot_token: str, chat_id: str):
        """更新Telegram配置"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 删除旧配置
        cursor.execute('DELETE FROM telegram_config')
        
        # 插入新配置
        cursor.execute('''
            INSERT INTO telegram_config (bot_token, chat_id)
            VALUES (?, ?)
        ''', (bot_token, chat_id))
        
        conn.commit()
        conn.close()
        
        logger.info("更新Telegram配置")
    
    def get_telegram_config(self) -> Optional[Dict]:
        """获取Telegram配置"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT bot_token, chat_id, updated_at
            FROM telegram_config
            ORDER BY id DESC
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None

