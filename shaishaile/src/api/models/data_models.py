"""
数据模型
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class Granularity(str, Enum):
    """数据粒度"""
    MONTHLY = 'monthly'
    YEARLY = 'yearly'

class MetricType(str, Enum):
    """指标类型"""
    ACTIVITY = 'activity'
    OPENRANK = 'openrank'
    ATTENTION = 'attention'
    STARS = 'stars'
    FORKS = 'technical_fork'
    PARTICIPANTS = 'participants'
    NEW_CONTRIBUTORS = 'new_contributors'
    BUS_FACTOR = 'bus_factor'

@dataclass
class Repository:
    """仓库模型"""
    id: str  # owner/name格式
    name: str
    owner: str
    description: Optional[str]
    url: str
    language: Optional[str]
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    archived: bool = False
    disabled: bool = False
    topics: List[str] = field(default_factory=list)
    
    @property
    def full_name(self) -> str:
        """完整名称"""
        return f"{self.owner}/{self.name}"
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'owner': self.owner,
            'full_name': self.full_name,
            'description': self.description,
            'url': self.url,
            'language': self.language,
            'stars': self.stars,
            'forks': self.forks,
            'open_issues': self.open_issues,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'archived': self.archived,
            'disabled': self.disabled,
            'topics': self.topics
        }

@dataclass
class Developer:
    """开发者模型"""
    login: str
    name: Optional[str]
    avatar_url: str
    bio: Optional[str]
    company: Optional[str]
    location: Optional[str]
    email: Optional[str]
    public_repos: int = 0
    public_gists: int = 0
    followers: int = 0
    following: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'login': self.login,
            'name': self.name,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'company': self.company,
            'location': self.location,
            'email': self.email,
            'public_repos': self.public_repos,
            'public_gists': self.public_gists,
            'followers': self.followers,
            'following': self.following,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

@dataclass
class MetricData:
    """指标数据模型"""
    repository_id: str
    metric_type: MetricType
    granularity: Granularity
    date: str  # YYYY-MM格式
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'repository': self.repository_id,
            'metric': self.metric_type.value,
            'granularity': self.granularity.value,
            'date': self.date,
            'value': self.value,
            'metadata': self.metadata
        }

@dataclass
class Contribution:
    """贡献模型"""
    developer_id: str
    repository_id: str
    event_type: str  # PushEvent, PullRequestEvent等
    count: int = 1
    last_contribution: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'developer': self.developer_id,
            'repository': self.repository_id,
            'event_type': self.event_type,
            'count': self.count,
            'last_contribution': self.last_contribution.isoformat() if self.last_contribution else None
        }

@dataclass
class TrendAnalysis:
    """趋势分析模型"""
    repository_id: str
    metric_type: MetricType
    period_months: int
    direction: str  # increasing, decreasing, stable
    percentage_change: float
    average_value: float
    volatility: float
    analysis_date: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'repository': self.repository_id,
            'metric': self.metric_type.value,
            'period_months': self.period_months,
            'direction': self.direction,
            'percentage_change': self.percentage_change,
            'average_value': self.average_value,
            'volatility': self.volatility,
            'analysis_date': self.analysis_date.isoformat() if self.analysis_date else None
        }

@dataclass
class Comparison:
    """比较分析模型"""
    repository_ids: List[str]
    metric_types: List[MetricType]
    comparison_date: datetime = field(default_factory=datetime.utcnow)
    results: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'repositories': self.repository_ids,
            'metrics': [m.value for m in self.metric_types],
            'comparison_date': self.comparison_date.isoformat() if self.comparison_date else None,
            'results': self.results
        }