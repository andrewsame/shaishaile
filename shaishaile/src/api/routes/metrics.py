"""
指标数据路由
"""
from flask import Blueprint, request, jsonify, current_app
from flask_caching import Cache
from typing import Dict, List, Optional
import json

from src.data_collection.opendigger_client import OpenDiggerClient
from src.api.utils.validators import (
    validate_repo_name, 
    validate_date_format,
    validate_metrics_list,
    validate_granularity
)
from src.api.utils.response_handler import (
    success_response,
    error_response,
    paginated_response
)
from src.api.utils.cache_manager import cache_key_generator
from src.api.models.response_models import MetricResponse

metrics_bp = Blueprint('metrics', __name__)
client = OpenDiggerClient()
cache = Cache(current_app)

@metrics_bp.route('/repo/<path:repo_name>', methods=['GET'])
@cache.cached(timeout=300, key_prefix=cache_key_generator)
def get_repo_metrics(repo_name: str):
    """
    获取仓库指标数据
    ---
    tags:
      - Metrics
    parameters:
      - name: repo_name
        in: path
        type: string
        required: true
        description: 仓库名称，格式：owner/repo
      - name: metrics
        in: query
        type: string
        required: false
        description: 指标列表，用逗号分隔
      - name: start_date
        in: query
        type: string
        required: false
        description: 开始日期，格式：YYYY-MM
      - name: end_date
        in: query
        type: string
        required: false
        description: 结束日期，格式：YYYY-MM
      - name: granularity
        in: query
        type: string
        required: false
        description: 数据粒度，monthly或yearly
      - name: format
        in: query
        type: string
        required: false
        description: 返回格式，json或csv
    responses:
      200:
        description: 成功返回指标数据
      400:
        description: 参数错误
      500:
        description: 服务器内部错误
    """
    try:
        # 参数验证
        if not validate_repo_name(repo_name):
            return error_response(
                message='Invalid repository name format. Expected: owner/repo',
                status_code=400
            )
        
        # 获取查询参数
        metrics_param = request.args.get('metrics', 'activity,openrank')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        granularity = request.args.get('granularity', 'monthly')
        format_type = request.args.get('format', 'json')
        
        # 验证参数
        if start_date and not validate_date_format(start_date, '%Y-%m'):
            return error_response(
                message='Invalid start_date format. Expected: YYYY-MM',
                status_code=400
            )
        
        if end_date and not validate_date_format(end_date, '%Y-%m'):
            return error_response(
                message='Invalid end_date format. Expected: YYYY-MM',
                status_code=400
            )
        
        if not validate_granularity(granularity):
            return error_response(
                message='Invalid granularity. Supported: monthly, yearly',
                status_code=400
            )
        
        # 解析指标列表
        metrics_list = [m.strip() for m in metrics_param.split(',')]
        if not validate_metrics_list(metrics_list):
            return error_response(
                message='One or more metrics are not supported',
                status_code=400
            )
        
        # 获取数据
        data = client.get_repo_metrics(
            repo_name=repo_name,
            metrics=metrics_list,
            start_date=start_date,
            end_date=end_date,
            granularity=granularity
        )
        
        # 处理空数据
        if not data or all(v is None for v in data.values()):
            return error_response(
                message=f'No data found for repository {repo_name}',
                status_code=404
            )
        
        # 构建响应
        response_data = MetricResponse(
            repository=repo_name,
            metrics=metrics_list,
            date_range={
                'start': start_date,
                'end': end_date,
                'granularity': granularity
            },
            data=data,
            total_metrics=len([v for v in data.values() if v is not None])
        ).to_dict()
        
        # 格式转换
        if format_type.lower() == 'csv':
            return convert_to_csv(response_data)
        
        return success_response(data=response_data)
        
    except Exception as e:
        current_app.logger.error(f"Error fetching metrics for {repo_name}: {str(e)}")
        return error_response(
            message=f'Failed to fetch metrics: {str(e)}',
            status_code=500
        )

@metrics_bp.route('/trend/<path:repo_name>', methods=['GET'])
@cache.cached(timeout=600, key_prefix=cache_key_generator)
def get_metrics_trend(repo_name: str):
    """
    获取指标趋势数据
    """
    try:
        # 参数验证
        if not validate_repo_name(repo_name):
            return error_response('Invalid repository name', 400)
        
        metric = request.args.get('metric', 'activity')
        period = request.args.get('period', '12')  # 最近N个月
        
        if not validate_metrics_list([metric]):
            return error_response('Unsupported metric', 400)
        
        # 计算日期范围
        from datetime import datetime, timedelta
        from dateutil.relativedelta import relativedelta
        
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=int(period))
        
        # 获取数据
        data = client.get_repo_metrics(
            repo_name=repo_name,
            metrics=[metric],
            start_date=start_date.strftime('%Y-%m'),
            end_date=end_date.strftime('%Y-%m')
        )
        
        if not data or metric not in data:
            return error_response('No trend data found', 404)
        
        # 分析趋势
        trend_data = data[metric]
        if trend_data:
            dates = sorted(trend_data.keys())
            values = [trend_data[d] for d in dates]
            
            # 计算趋势指标
            if len(values) >= 2:
                first_value = values[0]
                last_value = values[-1]
                avg_value = sum(values) / len(values)
                
                # 判断趋势方向
                if last_value > avg_value:
                    trend_direction = 'up'
                elif last_value < avg_value:
                    trend_direction = 'down'
                else:
                    trend_direction = 'stable'
                
                # 计算变化百分比
                if first_value != 0:
                    change_pct = ((last_value - first_value) / abs(first_value)) * 100
                else:
                    change_pct = 0
            else:
                trend_direction = 'insufficient_data'
                change_pct = 0
            
            response_data = {
                'repository': repo_name,
                'metric': metric,
                'period': period,
                'trend': {
                    'direction': trend_direction,
                    'change_percentage': round(change_pct, 2),
                    'data_points': len(values)
                },
                'data': trend_data
            }
            
            return success_response(data=response_data)
        
        return error_response('No data available for trend analysis', 404)
        
    except Exception as e:
        current_app.logger.error(f"Error analyzing trend: {str(e)}")
        return error_response('Failed to analyze trend', 500)

@metrics_bp.route('/bulk', methods=['POST'])
def get_bulk_metrics():
    """
    批量获取多个仓库的指标
    """
    try:
        request_data = request.get_json()
        
        if not request_data or 'repositories' not in request_data:
            return error_response('Missing repositories in request body', 400)
        
        repositories = request_data['repositories']
        metrics = request_data.get('metrics', ['activity', 'openrank'])
        start_date = request_data.get('start_date')
        end_date = request_data.get('end_date')
        
        # 限制批量请求数量
        if len(repositories) > 10:
            return error_response('Maximum 10 repositories allowed per request', 400)
        
        results = {}
        errors = []
        
        for repo in repositories:
            try:
                if not validate_repo_name(repo):
                    errors.append(f'Invalid repository format: {repo}')
                    continue
                
                data = client.get_repo_metrics(
                    repo_name=repo,
                    metrics=metrics,
                    start_date=start_date,
                    end_date=end_date
                )
                
                results[repo] = data
                
            except Exception as e:
                errors.append(f'Error fetching {repo}: {str(e)}')
                results[repo] = None
        
        response_data = {
            'results': results,
            'errors': errors,
            'total_requests': len(repositories),
            'successful': len([r for r in results.values() if r is not None])
        }
        
        return success_response(data=response_data)
        
    except Exception as e:
        current_app.logger.error(f"Error in bulk metrics: {str(e)}")
        return error_response('Failed to process bulk request', 500)

def convert_to_csv(data: Dict) -> str:
    """将数据转换为CSV格式"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow(['Repository', 'Metric', 'Date', 'Value'])
    
    # 写入数据
    repo = data['repository']
    
    for metric, metric_data in data['data'].items():
        if metric_data:
            for date, value in metric_data.items():
                writer.writerow([repo, metric, date, value])
    
    output.seek(0)
    
    from flask import Response
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={repo}_metrics.csv'}
    )