"""
系统健康监控模块
用于长时间运行的程序优化和监控
"""
import psutil
import logging
import os
import time
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)


class HealthMonitor:
    """系统健康监控器"""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_time = time.time()
    
    def get_memory_usage(self) -> Dict:
        """获取内存使用情况"""
        try:
            mem_info = self.process.memory_info()
            mem_percent = self.process.memory_percent()
            
            return {
                'rss_mb': mem_info.rss / 1024 / 1024,  # 物理内存（MB）
                'vms_mb': mem_info.vms / 1024 / 1024,  # 虚拟内存（MB）
                'percent': mem_percent,
                'available_mb': psutil.virtual_memory().available / 1024 / 1024
            }
        except Exception as e:
            logger.error(f"获取内存信息失败: {e}")
            return {}
    
    def get_cpu_usage(self) -> Dict:
        """获取CPU使用情况"""
        try:
            cpu_percent = self.process.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            return {
                'percent': cpu_percent,
                'count': cpu_count,
                'system_percent': psutil.cpu_percent(interval=1)
            }
        except Exception as e:
            logger.error(f"获取CPU信息失败: {e}")
            return {}
    
    def get_disk_usage(self) -> Dict:
        """获取磁盘使用情况"""
        try:
            disk = psutil.disk_usage('/')
            
            return {
                'total_gb': disk.total / 1024 / 1024 / 1024,
                'used_gb': disk.used / 1024 / 1024 / 1024,
                'free_gb': disk.free / 1024 / 1024 / 1024,
                'percent': disk.percent
            }
        except Exception as e:
            logger.error(f"获取磁盘信息失败: {e}")
            return {}
    
    def get_uptime(self) -> Dict:
        """获取运行时间"""
        uptime_seconds = time.time() - self.start_time
        
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        return {
            'seconds': uptime_seconds,
            'formatted': f"{days}天 {hours}小时 {minutes}分钟"
        }
    
    def get_thread_count(self) -> int:
        """获取线程数"""
        try:
            return self.process.num_threads()
        except Exception as e:
            logger.error(f"获取线程数失败: {e}")
            return 0
    
    def get_open_files_count(self) -> int:
        """获取打开的文件数"""
        try:
            return len(self.process.open_files())
        except Exception as e:
            # 某些系统可能没有权限获取此信息
            return 0
    
    def get_health_status(self) -> Dict:
        """获取完整的健康状态"""
        memory = self.get_memory_usage()
        cpu = self.get_cpu_usage()
        disk = self.get_disk_usage()
        uptime = self.get_uptime()
        
        # 判断健康状态
        is_healthy = True
        warnings = []
        
        # 检查内存
        if memory.get('percent', 0) > 80:
            is_healthy = False
            warnings.append(f"内存使用率过高: {memory['percent']:.1f}%")
        
        # 检查CPU
        if cpu.get('percent', 0) > 90:
            warnings.append(f"CPU使用率过高: {cpu['percent']:.1f}%")
        
        # 检查磁盘
        if disk.get('percent', 0) > 90:
            is_healthy = False
            warnings.append(f"磁盘使用率过高: {disk['percent']:.1f}%")
        
        return {
            'healthy': is_healthy,
            'warnings': warnings,
            'memory': memory,
            'cpu': cpu,
            'disk': disk,
            'uptime': uptime,
            'threads': self.get_thread_count(),
            'open_files': self.get_open_files_count(),
            'timestamp': datetime.now().isoformat()
        }
    
    def log_health_status(self):
        """记录健康状态到日志"""
        status = self.get_health_status()
        
        log_msg = (
            f"系统健康检查 - "
            f"内存: {status['memory'].get('rss_mb', 0):.1f}MB ({status['memory'].get('percent', 0):.1f}%), "
            f"CPU: {status['cpu'].get('percent', 0):.1f}%, "
            f"运行时间: {status['uptime']['formatted']}, "
            f"线程数: {status['threads']}"
        )
        
        if status['healthy']:
            logger.info(log_msg)
        else:
            logger.warning(f"{log_msg} - 警告: {', '.join(status['warnings'])}")
    
    def should_restart(self) -> bool:
        """判断是否需要重启（内存泄漏检测）"""
        memory = self.get_memory_usage()
        
        # 如果内存使用超过500MB，建议重启
        if memory.get('rss_mb', 0) > 500:
            logger.warning(f"内存使用过高 ({memory['rss_mb']:.1f}MB)，建议重启服务")
            return True
        
        return False


# 全局健康监控实例
health_monitor = HealthMonitor()
