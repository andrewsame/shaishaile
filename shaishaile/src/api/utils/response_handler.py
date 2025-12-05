"""
响应处理工具
"""
from flask import jsonify
from datetime import datetime
from typing import Any, Dict, List, Optional
import json

class APIResponse:
    """API响应封装类"""
    
    def __init__(self, 
                 success: bool = True, 
                 data: Any = None, 
                 message: str = '',
                 status_code: int = 200,
                 metadata: Optional[Dict] = None):
        self.success = success
        self.data = data
        self.message = message
        self.status_code = status_code
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        response = {
            'success': self.success,
            'data': self.data,
            'message': self.message,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }
        
        # 移除空值
        return {k: v for k, v in response.items() if v is not None}
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def to_flask_response(self):
        """转换为Flask响应"""
        return jsonify(self.to_dict()), self.status_code

def success_response(data: Any = None, 
                    message: str = 'Success', 
                    metadata: Optional[Dict] = None) -> tuple:
    """
    成功响应
    """
    response = APIResponse(
        success=True,
        data=data,
        message=message,
        status_code=200,
        metadata=metadata
    )
    return response.to_flask_response()

def error_response(message: str = 'Error', 
                   status_code: int = 400, 
                   errors: Optional[List] = None,
                   metadata: Optional[Dict] = None) -> tuple:
    """
    错误响应
    """
    response = APIResponse(
        success=False,
        data={'errors': errors} if errors else None,
        message=message,
        status_code=status_code,
        metadata=metadata
    )
    return response.to_flask_response()

def paginated_response(data: List, 
                       total: int, 
                       page: int, 
                       per_page: int,
                       message: str = 'Success') -> tuple:
    """
    分页响应
    """
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 1
    
    metadata = {
        'pagination': {
            'total': total,
            'count': len(data),
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }
    
    return success_response(data=data, message=message, metadata=metadata)

def created_response(data: Any = None, 
                     message: str = 'Resource created successfully') -> tuple:
    """创建成功响应"""
    response = APIResponse(
        success=True,
        data=data,
        message=message,
        status_code=201
    )
    return response.to_flask_response()

def not_found_response(message: str = 'Resource not found') -> tuple:
    """未找到资源响应"""
    return error_response(message=message, status_code=404)

def unauthorized_response(message: str = 'Unauthorized') -> tuple:
    """未授权响应"""
    return error_response(message=message, status_code=401)

def forbidden_response(message: str = 'Forbidden') -> tuple:
    """禁止访问响应"""
    return error_response(message=message, status_code=403)

def validation_error_response(errors: List, message: str = 'Validation failed') -> tuple:
    """验证错误响应"""
    return error_response(
        message=message,
        status_code=422,
        errors=errors
    )

def rate_limit_response(message: str = 'Too many requests', 
                        retry_after: int = 60) -> tuple:
    """速率限制响应"""
    metadata = {'retry_after': retry_after}
    return error_response(
        message=message,
        status_code=429,
        metadata=metadata
    )