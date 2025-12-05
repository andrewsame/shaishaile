"""
错误处理工具
"""
import logging
import traceback
from flask import jsonify, request, current_app
from typing import Dict, Any

logger = logging.getLogger(__name__)

def handle_400(error):
    """处理400错误"""
    return jsonify({
        'error': 'Bad Request',
        'message': str(error),
        'path': request.path,
        'timestamp': get_timestamp()
    }), 400

def handle_404(error):
    """处理404错误"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found',
        'path': request.path,
        'timestamp': get_timestamp()
    }), 404

def handle_405(error):
    """处理405错误"""
    return jsonify({
        'error': 'Method Not Allowed',
        'message': 'The method is not allowed for the requested URL',
        'path': request.path,
        'timestamp': get_timestamp()
    }), 405

def handle_500(error):
    """处理500错误"""
    logger.error(f'Internal Server Error: {str(error)}')
    
    # 在生产环境中隐藏详细错误信息
    if current_app.config.get('ENV') == 'production':
        error_message = 'An internal server error occurred'
    else:
        error_message = str(error)
    
    return jsonify({
        'error': 'Internal Server Error',
        'message': error_message,
        'path': request.path,
        'timestamp': get_timestamp()
    }), 500

def handle_exception(error):
    """处理未捕获的异常"""
    logger.error(f'Unhandled Exception: {str(error)}')
    logger.error(traceback.format_exc())
    
    # 记录异常详细信息
    error_info = {
        'type': type(error).__name__,
        'message': str(error),
        'traceback': traceback.format_exc()
    }
    
    # 在生产环境中隐藏详细错误信息
    if current_app.config.get('ENV') == 'production':
        error_message = 'An unexpected error occurred'
    else:
        error_message = str(error)
    
    response = {
        'error': 'Unhandled Exception',
        'message': error_message,
        'path': request.path,
        'timestamp': get_timestamp()
    }
    
    # 开发环境添加调试信息
    if current_app.debug:
        response['debug_info'] = error_info
    
    return jsonify(response), 500

def get_timestamp() -> str:
    """获取当前时间戳"""
    from datetime import datetime
    return datetime.utcnow().isoformat()

class APIError(Exception):
    """自定义API异常基类"""
    
    def __init__(self, message: str, status_code: int = 400, 
                 error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        error_dict = {
            'error': self.__class__.__name__,
            'message': self.message,
            'status_code': self.status_code,
            'timestamp': get_timestamp()
        }
        
        if self.error_code:
            error_dict['error_code'] = self.error_code
        
        if self.details:
            error_dict['details'] = self.details
        
        return error_dict
    
    def to_response(self):
        """转换为Flask响应"""
        return jsonify(self.to_dict()), self.status_code

class ValidationError(APIError):
    """验证错误"""
    def __init__(self, message: str = 'Validation failed', 
                 details: Dict[str, Any] = None):
        super().__init__(message, 422, 'VALIDATION_ERROR', details)

class NotFoundError(APIError):
    """资源未找到错误"""
    def __init__(self, message: str = 'Resource not found',
                 details: Dict[str, Any] = None):
        super().__init__(message, 404, 'NOT_FOUND', details)

class UnauthorizedError(APIError):
    """未授权错误"""
    def __init__(self, message: str = 'Unauthorized',
                 details: Dict[str, Any] = None):
        super().__init__(message, 401, 'UNAUTHORIZED', details)

class ForbiddenError(APIError):
    """禁止访问错误"""
    def __init__(self, message: str = 'Forbidden',
                 details: Dict[str, Any] = None):
        super().__init__(message, 403, 'FORBIDDEN', details)

class RateLimitError(APIError):
    """速率限制错误"""
    def __init__(self, message: str = 'Too many requests',
                 retry_after: int = 60,
                 details: Dict[str, Any] = None):
        if not details:
            details = {'retry_after': retry_after}
        super().__init__(message, 429, 'RATE_LIMITED', details)

class ServiceUnavailableError(APIError):
    """服务不可用错误"""
    def __init__(self, message: str = 'Service temporarily unavailable',
                 details: Dict[str, Any] = None):
        super().__init__(message, 503, 'SERVICE_UNAVAILABLE', details)