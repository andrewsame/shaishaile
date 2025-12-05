"""
API配置文件
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """基础配置类"""
    # API配置
    API_TITLE = "OpenDigger Data Platform API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "OpenDigger数据平台API服务"
    
    # 数据源配置
    OPENDIGGER_BASE_URL = "https://oss.x-lab.info/open_digger/github/"
    GITHUB_API_BASE_URL = "https://api.github.com"
    
    # 缓存配置
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 300))
    
    # 请求限制
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'false').lower() == 'true'
    RATE_LIMIT_DEFAULT = os.getenv('RATE_LIMIT_DEFAULT', "100 per hour")
    
    # 数据验证
    MAX_REPOS_COMPARE = int(os.getenv('MAX_REPOS_COMPARE', 10))
    MAX_METRICS_PER_REQUEST = int(os.getenv('MAX_METRICS_PER_REQUEST', 10))
    
    # 支持的数据粒度
    SUPPORTED_GRANULARITIES = ['monthly', 'yearly']
    
    # 支持的指标
    SUPPORTED_METRICS = [
        'activity',
        'openrank', 
        'attention',
        'stars',
        'technical_fork',
        'participants',
        'new_contributors',
        'inactive_contributors',
        'bus_factor',
        'issues_new',
        'issues_closed',
        'issue_comments',
        'issue_response_time',
        'issue_resolution_duration',
        'issue_age',
        'code_change_lines_add',
        'code_change_lines_remove',
        'code_change_lines_sum',
        'change_requests',
        'change_requests_accepted',
        'change_requests_reviews',
        'change_request_response_time',
        'change_request_resolution_duration',
        'change_request_age'
    ]
    
    @staticmethod
    def get_github_token():
        """获取GitHub Token"""
        return os.getenv('GITHUB_TOKEN')
    
    @staticmethod
    def get_redis_url():
        """获取Redis URL"""
        return os.getenv('REDIS_URL')

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False
    ENV = 'development'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    ENV = 'production'
    CACHE_ENABLED = True
    RATE_LIMIT_ENABLED = True

class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    TESTING = True
    ENV = 'testing'
    CACHE_ENABLED = False

# 根据环境选择配置
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

def get_config():
    """获取当前环境配置"""
    env = os.getenv('FLASK_ENV', 'development')
    return config_map.get(env, DevelopmentConfig)