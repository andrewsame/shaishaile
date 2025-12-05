"""
缓存管理工具
"""
from functools import wraps
from flask import request
import hashlib
import json
from typing import Any, Callable
import time

def cache_key_generator() -> str:
    """
    生成缓存键
    基于请求路径、参数和用户身份
    """
    # 基础键：请求路径
    key_parts = [request.path]
    
    # 添加查询参数
    if request.args:
        sorted_args = sorted(request.args.items())
        key_parts.append(str(hashlib.md5(json.dumps(sorted_args).encode()).hexdigest()))
    
    # 对于POST请求，添加请求体
    if request.method == 'POST' and request.get_data():
        try:
            body_hash = hashlib.md5(request.get_data()).hexdigest()
            key_parts.append(body_hash)
        except:
            pass
    
    # 添加用户身份（如果存在）
    auth_header = request.headers.get('Authorization')
    if auth_header:
        key_parts.append(hashlib.md5(auth_header.encode()).hexdigest()[:8])
    
    # 组合所有部分
    cache_key = ':'.join(key_parts)
    return cache_key

def cache_response(timeout: int = 300) -> Callable:
    """
    缓存响应装饰器
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask_caching import Cache
            from flask import current_app
            
            cache = Cache(current_app)
            key = cache_key_generator()
            
            # 尝试从缓存获取
            cached_data = cache.get(key)
            if cached_data is not None:
                return cached_data
            
            # 执行函数
            result = f(*args, **kwargs)
            
            # 缓存结果
            cache.set(key, result, timeout=timeout)
            
            return result
        return decorated_function
    return decorator

def clear_cache_pattern(pattern: str) -> int:
    """
    清除匹配模式的缓存
    """
    from flask_caching import Cache
    from flask import current_app
    
    cache = Cache(current_app)
    if hasattr(cache.cache, 'delete_pattern'):  # Redis支持
        return cache.cache.delete_pattern(pattern)
    
    return 0

def get_cache_stats() -> dict:
    """
    获取缓存统计信息
    """
    from flask_caching import Cache
    from flask import current_app
    
    cache = Cache(current_app)
    stats = {
        'type': str(type(cache.cache)),
        'enabled': current_app.config.get('CACHE_ENABLED', True)
    }
    
    # 尝试获取Redis统计信息
    if hasattr(cache.cache, 'info'):
        try:
            redis_info = cache.cache.info()
            stats.update({
                'redis_version': redis_info.get('redis_version'),
                'used_memory': redis_info.get('used_memory_human'),
                'connected_clients': redis_info.get('connected_clients'),
                'total_commands_processed': redis_info.get('total_commands_processed')
            })
        except:
            pass
    
    return stats

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, app=None):
        self.app = app
        self.cache = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化应用"""
        from flask_caching import Cache
        
        self.app = app
        self.cache = Cache(app)
    
    def get(self, key: str) -> Any:
        """获取缓存值"""
        return self.cache.get(key)
    
    def set(self, key: str, value: Any, timeout: int = None) -> bool:
        """设置缓存值"""
        return self.cache.set(key, value, timeout=timeout)
    
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        return self.cache.delete(key)
    
    def clear(self) -> bool:
        """清除所有缓存"""
        return self.cache.clear()
    
    def memoize(self, timeout: int = 300):
        """记忆化装饰器"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # 生成基于函数参数和名称的键
                key_parts = [
                    f.__name__,
                    str(args),
                    str(sorted(kwargs.items()))
                ]
                key = hashlib.md5(json.dumps(key_parts).encode()).hexdigest()
                
                # 尝试从缓存获取
                cached = self.get(key)
                if cached is not None:
                    return cached
                
                # 执行函数
                result = f(*args, **kwargs)
                
                # 缓存结果
                self.set(key, result, timeout=timeout)
                
                return result
            return decorated_function
        return decorator