"""
响应数据模型
"""
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime
import json

@dataclass
class MetricDataPoint:
    """指标数据点"""
    date: str
    value: float
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)

@dataclass
class MetricSeries:
    """指标序列"""
    metric_name: str
    data_points: List[MetricDataPoint]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'metric': self.metric_name,
            'data': [dp.to_dict() for dp in self.data_points]
        }

@dataclass
class MetricResponse:
    """指标响应"""
    repository: str
    metrics: List[str]
    date_range: Dict[str, Optional[str]]
    data: Dict[str, Optional[Dict[str, float]]]
    total_metrics: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'repository': self.repository,
            'metrics': self.metrics,
            'date_range': self.date_range,
            'data': self.data,
            'total_metrics': self.total_metrics,
            'timestamp': self.timestamp
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

@dataclass
class RepositoryInfo:
    """仓库信息"""
    full_name: str
    name: str
    owner: str
    description: Optional[str]
    url: str
    language: Optional[str]
    stars: int
    forks: int
    open_issues: int
    created_at: str
    updated_at: str
    license: Optional[str] = None
    topics: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)

@dataclass
class DeveloperInfo:
    """开发者信息"""
    login: str
    name: Optional[str]
    avatar_url: str
    bio: Optional[str]
    blog: Optional[str]
    company: Optional[str]
    location: Optional[str]
    email: Optional[str]
    public_repos: int
    followers: int
    following: int
    created_at: str
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)

@dataclass
class ComparisonResult:
    """比较结果"""
    repositories: List[str]
    metrics: List[str]
    data: Dict[str, Dict[str, Any]]
    analysis: Dict[str, Any]
    summary: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)

@dataclass
class PaginatedResponse:
    """分页响应"""
    data: List[Any]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'data': self.data,
            'pagination': {
                'total': self.total,
                'page': self.page,
                'per_page': self.per_page,
                'total_pages': self.total_pages,
                'has_next': self.has_next,
                'has_prev': self.has_prev
            }
        }

@dataclass
class ErrorResponse:
    """错误响应"""
    error: str
    message: str
    status_code: int
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    details: Optional[Dict] = None
    error_code: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        response = {
            'error': self.error,
            'message': self.message,
            'status_code': self.status_code,
            'timestamp': self.timestamp
        }
        
        if self.error_code:
            response['error_code'] = self.error_code
        
        if self.details:
            response['details'] = self.details
        
        return response
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)