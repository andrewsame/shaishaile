"""
数据验证工具
"""
import re
from datetime import datetime
from typing import List, Optional
from src.api.config.api_config import get_config

config = get_config()

def validate_repo_name(repo_name: str) -> bool:
    """
    验证仓库名称格式
    """
    if not repo_name or not isinstance(repo_name, str):
        return False
    
    # 格式：owner/repo
    pattern = r'^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$'
    return bool(re.match(pattern, repo_name))

def validate_username(username: str) -> bool:
    """
    验证用户名格式
    """
    if not username or not isinstance(username, str):
        return False
    
    # GitHub用户名规则
    pattern = r'^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$'
    return bool(re.match(pattern, username))

def validate_date_format(date_str: str, format_str: str = '%Y-%m') -> bool:
    """
    验证日期格式
    """
    if not date_str:
        return False
    
    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False

def validate_metrics_list(metrics: List[str]) -> bool:
    """
    验证指标列表
    """
    if not metrics:
        return False
    
    # 检查是否所有指标都受支持
    for metric in metrics:
        if metric not in config.SUPPORTED_METRICS:
            return False
    
    return True

def validate_granularity(granularity: str) -> bool:
    """
    验证数据粒度
    """
    return granularity in config.SUPPORTED_GRANULARITIES

def validate_time_range(start_date: Optional[str], end_date: Optional[str]) -> tuple[bool, str]:
    """
    验证时间范围
    """
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m')
            end = datetime.strptime(end_date, '%Y-%m')
            
            if start > end:
                return False, 'Start date must be before end date'
            
            # 检查时间范围是否过大
            months_diff = (end.year - start.year) * 12 + (end.month - start.month)
            if months_diff > 60:  # 限制为5年
                return False, 'Time range cannot exceed 5 years'
            
            return True, ''
        except ValueError:
            return False, 'Invalid date format'
    
    return True, ''

def validate_positive_integer(value: str, field_name: str) -> tuple[bool, str]:
    """
    验证正整数
    """
    try:
        num = int(value)
        if num <= 0:
            return False, f'{field_name} must be positive'
        if num > 1000:
            return False, f'{field_name} cannot exceed 1000'
        return True, ''
    except (ValueError, TypeError):
        return False, f'{field_name} must be a valid integer'

def validate_email(email: str) -> bool:
    """
    验证邮箱格式
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_url(url: str) -> bool:
    """
    验证URL格式
    """
    if not url:
        return False
    
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))

def validate_json_schema(data: dict, schema: dict) -> tuple[bool, List[str]]:
    """
    验证JSON数据是否符合模式
    """
    errors = []
    
    def check_required(schema_fields: dict, data_fields: dict, path: str = ''):
        for field, rules in schema_fields.items():
            field_path = f'{path}.{field}' if path else field
            
            # 检查必需字段
            if rules.get('required', False) and field not in data_fields:
                errors.append(f'Missing required field: {field_path}')
                continue
            
            if field in data_fields:
                value = data_fields[field]
                field_type = rules.get('type')
                
                # 检查类型
                if field_type == 'string' and not isinstance(value, str):
                    errors.append(f'{field_path} must be a string')
                elif field_type == 'integer' and not isinstance(value, int):
                    errors.append(f'{field_path} must be an integer')
                elif field_type == 'number' and not isinstance(value, (int, float)):
                    errors.append(f'{field_path} must be a number')
                elif field_type == 'boolean' and not isinstance(value, bool):
                    errors.append(f'{field_path} must be a boolean')
                elif field_type == 'array' and not isinstance(value, list):
                    errors.append(f'{field_path} must be an array')
                elif field_type == 'object' and not isinstance(value, dict):
                    errors.append(f'{field_path} must be an object')
                
                # 检查枚举值
                enum_values = rules.get('enum')
                if enum_values and value not in enum_values:
                    errors.append(f'{field_path} must be one of {enum_values}')
                
                # 检查最小值/最大值
                if 'min' in rules and isinstance(value, (int, float)) and value < rules['min']:
                    errors.append(f'{field_path} must be at least {rules["min"]}')
                if 'max' in rules and isinstance(value, (int, float)) and value > rules['max']:
                    errors.append(f'{field_path} must be at most {rules["max"]}')
                
                # 检查最小长度/最大长度
                if 'min_length' in rules and isinstance(value, (str, list)) and len(value) < rules['min_length']:
                    errors.append(f'{field_path} must have at least {rules["min_length"]} items')
                if 'max_length' in rules and isinstance(value, (str, list)) and len(value) > rules['max_length']:
                    errors.append(f'{field_path} must have at most {rules["max_length"]} items')
                
                # 递归检查嵌套对象
                if field_type == 'object' and 'properties' in rules:
                    check_required(rules['properties'], value, field_path)
                
                # 递归检查数组项
                if field_type == 'array' and 'items' in rules:
                    for i, item in enumerate(value):
                        if isinstance(item, dict) and 'properties' in rules['items']:
                            check_required(rules['items']['properties'], item, f'{field_path}[{i}]')
    
    check_required(schema, data)
    return len(errors) == 0, errors