"""
Flask API主应用文件
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_caching import Cache
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入蓝图
from .routes.metrics import metrics_bp
from .routes.repos import repos_bp
from .routes.developers import developers_bp
from .routes.analysis import analysis_bp

# 配置缓存
cache_config = {
    'CACHE_TYPE': 'redis' if os.getenv('REDIS_URL') else 'simple',
    'CACHE_REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    'CACHE_DEFAULT_TIMEOUT': 300  # 5分钟
}

def create_app():
    """
    创建Flask应用
    """
    app = Flask(__name__)
    
    # 应用配置
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'opendigger-secret-key-2024'),
        JSON_SORT_KEYS=False,
        JSON_AS_ASCII=False,
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB
    )
    
    # 启用CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 配置缓存
    cache = Cache(config=cache_config)
    cache.init_app(app)
    
    # 配置日志
    setup_logging(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册全局错误处理器
    register_error_handlers(app)
    
    # 添加请求钩子
    @app.before_request
    def before_request():
        """请求前处理"""
        if request.method in ['POST', 'PUT', 'PATCH']:
            if request.content_type and 'application/json' not in request.content_type:
                return jsonify({
                    'error': 'Content-Type must be application/json'
                }), 415
    
    @app.after_request
    def after_request(response):
        """响应后处理"""
        # 添加CORS头
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        
        # 添加API版本信息
        response.headers.add('X-API-Version', '1.0.0')
        response.headers.add('X-Server-Timestamp', datetime.utcnow().isoformat())
        
        # 记录访问日志
        app.logger.info(f'{request.method} {request.path} - {response.status_code}')
        
        return response
    
    # 健康检查端点
    @app.route('/api/health', methods=['GET'])
    @cache.cached(timeout=30)
    def health_check():
        """健康检查端点"""
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'OpenDigger Data Platform API',
            'version': '1.0.0',
            'uptime': get_uptime(),
            'environment': os.getenv('FLASK_ENV', 'development')
        }
        return jsonify(health_status)
    
    # API文档端点
    @app.route('/api/docs', methods=['GET'])
    def api_docs():
        """API文档端点"""
        docs = {
            'endpoints': {
                'health': {
                    'method': 'GET',
                    'url': '/api/health',
                    'description': '服务健康检查'
                },
                'metrics': {
                    'method': 'GET',
                    'url': '/api/metrics/repo/{owner}/{repo}',
                    'description': '获取仓库指标数据'
                },
                'repos': {
                    'method': 'GET',
                    'url': '/api/repos/search',
                    'description': '搜索仓库信息'
                },
                'developers': {
                    'method': 'GET',
                    'url': '/api/developers/{username}',
                    'description': '获取开发者指标'
                },
                'analysis': {
                    'method': 'POST',
                    'url': '/api/analysis/compare',
                    'description': '对比多个仓库的指标'
                }
            },
            'parameters': {
                'metrics': '要获取的指标，多个用逗号分隔',
                'start_date': '开始日期 (YYYY-MM)',
                'end_date': '结束日期 (YYYY-MM)',
                'granularity': '数据粒度 (monthly, yearly)'
            }
        }
        return jsonify(docs)
    
    return app

def setup_logging(app):
    """配置日志"""
    log_level = logging.DEBUG if app.debug else logging.INFO
    
    # 文件处理器
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    file_handler = logging.FileHandler('logs/api.log', encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # 配置根日志记录器
    app.logger.handlers.clear()
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)
    
    # 设置其他日志记录器
    logging.getLogger('werkzeug').setLevel(logging.WARNING)

def register_blueprints(app):
    """注册蓝图"""
    app.register_blueprint(metrics_bp, url_prefix='/api/metrics')
    app.register_blueprint(repos_bp, url_prefix='/api/repos')
    app.register_blueprint(developers_bp, url_prefix='/api/developers')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')

def register_error_handlers(app):
    """注册错误处理器"""
    from .utils.error_handler import (
        handle_400, handle_404, handle_405,
        handle_500, handle_exception
    )
    
    app.errorhandler(400)(handle_400)
    app.errorhandler(404)(handle_404)
    app.errorhandler(405)(handle_405)
    app.errorhandler(500)(handle_500)
    app.errorhandler(Exception)(handle_exception)

def get_uptime():
    """获取服务运行时间"""
    import psutil
    import time
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    
    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    
    return f"{days}d {hours}h {minutes}m {seconds}s"

# 应用工厂模式
app = create_app()

if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    app.run(host=host, port=port, debug=debug)