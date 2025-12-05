"""
数据分析路由
"""
from flask import Blueprint, request, jsonify, current_app
from flask_caching import Cache
from typing import Dict, List, Tuple
import statistics
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from src.data_collection.opendigger_client import OpenDiggerClient
from src.api.utils.response_handler import success_response, error_response
from src.api.utils.validators import validate_repo_name, validate_metrics_list
from src.api.utils.cache_manager import cache_key_generator

analysis_bp = Blueprint('analysis', __name__)
client = OpenDiggerClient()
cache = Cache(current_app)

@analysis_bp.route('/compare', methods=['POST'])
def compare_repositories():
    """
    比较多个仓库的指标
    """
    try:
        request_data = request.get_json()
        
        if not request_data or 'repositories' not in request_data:
            return error_response('Missing repositories in request body', 400)
        
        repositories = request_data['repositories']
        metrics = request_data.get('metrics', ['activity', 'openrank'])
        start_date = request_data.get('start_date')
        end_date = request_data.get('end_date')
        
        # 参数验证
        if len(repositories) > 10:
            return error_response('Maximum 10 repositories allowed per comparison', 400)
        
        if not validate_metrics_list(metrics):
            return error_response('One or more metrics are not supported', 400)
        
        # 检查仓库名称格式
        invalid_repos = []
        for repo in repositories:
            if not validate_repo_name(repo):
                invalid_repos.append(repo)
        
        if invalid_repos:
            return error_response(
                f'Invalid repository format: {", ".join(invalid_repos)}',
                400
            )
        
        # 获取数据
        comparison_data = {}
        for repo in repositories:
            try:
                data = client.get_repo_metrics(
                    repo_name=repo,
                    metrics=metrics,
                    start_date=start_date,
                    end_date=end_date
                )
                comparison_data[repo] = data
            except Exception as e:
                comparison_data[repo] = {'error': str(e)}
        
        # 分析比较结果
        analysis_results = analyze_comparison(comparison_data, metrics)
        
        response_data = {
            'comparison': comparison_data,
            'analysis': analysis_results,
            'summary': {
                'total_repositories': len(repositories),
                'successful': len([d for d in comparison_data.values() if not d.get('error')]),
                'failed': len([d for d in comparison_data.values() if d.get('error')]),
                'metrics_analyzed': metrics,
                'date_range': {
                    'start': start_date,
                    'end': end_date
                }
            }
        }
        
        return success_response(data=response_data)
        
    except Exception as e:
        current_app.logger.error(f"Error comparing repositories: {str(e)}")
        return error_response('Failed to compare repositories', 500)

@analysis_bp.route('/trend', methods=['POST'])
def analyze_trend():
    """
    分析指标趋势
    """
    try:
        request_data = request.get_json()
        
        if not request_data or 'repository' not in request_data:
            return error_response('Missing repository in request body', 400)
        
        repo_name = request_data['repository']
        metric = request_data.get('metric', 'activity')
        period = request_data.get('period', 12)  # 月数
        
        if not validate_repo_name(repo_name):
            return error_response('Invalid repository name format', 400)
        
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=period)
        
        # 获取数据
        data = client.get_repo_metrics(
            repo_name=repo_name,
            metrics=[metric],
            start_date=start_date.strftime('%Y-%m'),
            end_date=end_date.strftime('%Y-%m')
        )
        
        if not data or metric not in data or not data[metric]:
            return error_response('No data available for trend analysis', 404)
        
        trend_data = data[metric]
        
        # 分析趋势
        analysis = analyze_trend_data(trend_data, metric)
        
        response_data = {
            'repository': repo_name,
            'metric': metric,
            'period': period,
            'data': trend_data,
            'analysis': analysis
        }
        
        return success_response(data=response_data)
        
    except Exception as e:
        current_app.logger.error(f"Error analyzing trend: {str(e)}")
        return error_response('Failed to analyze trend', 500)

@analysis_bp.route('/correlation', methods=['POST'])
def analyze_correlation():
    """
    分析指标相关性
    """
    try:
        request_data = request.get_json()
        
        if not request_data or 'repository' not in request_data:
            return error_response('Missing repository in request body', 400)
        
        repo_name = request_data['repository']
        metric1 = request_data.get('metric1', 'activity')
        metric2 = request_data.get('metric2', 'openrank')
        start_date = request_data.get('start_date')
        end_date = request_data.get('end_date')
        
        if not validate_repo_name(repo_name):
            return error_response('Invalid repository name format', 400)
        
        # 获取两个指标的数据
        data = client.get_repo_metrics(
            repo_name=repo_name,
            metrics=[metric1, metric2],
            start_date=start_date,
            end_date=end_date
        )
        
        if not data or metric1 not in data or metric2 not in data:
            return error_response('Data not available for correlation analysis', 404)
        
        metric1_data = data[metric1] or {}
        metric2_data = data[metric2] or {}
        
        # 找到两个指标都有数据的日期
        common_dates = set(metric1_data.keys()) & set(metric2_data.keys())
        
        if len(common_dates) < 3:
            return error_response('Insufficient data for correlation analysis', 400)
        
        # 提取数据值
        values1 = [metric1_data[date] for date in sorted(common_dates)]
        values2 = [metric2_data[date] for date in sorted(common_dates)]
        
        # 计算相关性
        correlation = calculate_correlation(values1, values2)
        
        response_data = {
            'repository': repo_name,
            'metrics': {
                'metric1': metric1,
                'metric2': metric2
            },
            'data_points': len(common_dates),
            'correlation': correlation,
            'interpretation': interpret_correlation(correlation)
        }
        
        return success_response(data=response_data)
        
    except Exception as e:
        current_app.logger.error(f"Error analyzing correlation: {str(e)}")
        return error_response('Failed to analyze correlation', 500)

@analysis_bp.route('/predict', methods=['POST'])
def predict_metric():
    """
    预测指标未来值（简单线性回归）
    """
    try:
        request_data = request.get_json()
        
        if not request_data or 'repository' not in request_data:
            return error_response('Missing repository in request body', 400)
        
        repo_name = request_data['repository']
        metric = request_data.get('metric', 'activity')
        periods = min(request_data.get('periods', 3), 12)  # 最多预测12期
        
        if not validate_repo_name(repo_name):
            return error_response('Invalid repository name format', 400)
        
        # 获取历史数据
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=24)  # 使用2年数据
        
        data = client.get_repo_metrics(
            repo_name=repo_name,
            metrics=[metric],
            start_date=start_date.strftime('%Y-%m'),
            end_date=end_date.strftime('%Y-%m')
        )
        
        if not data or metric not in data or not data[metric]:
            return error_response('Insufficient historical data for prediction', 404)
        
        historical_data = data[metric]
        
        if len(historical_data) < 6:
            return error_response('At least 6 months of data required for prediction', 400)
        
        # 简单线性回归预测
        prediction = predict_linear_trend(list(historical_data.values()), periods)
        
        # 生成未来日期
        last_date = datetime.strptime(max(historical_data.keys()), '%Y-%m')
        future_dates = []
        
        for i in range(1, periods + 1):
            future_date = last_date + relativedelta(months=i)
            future_dates.append(future_date.strftime('%Y-%m'))
        
        response_data = {
            'repository': repo_name,
            'metric': metric,
            'historical_data': historical_data,
            'prediction': {
                'periods': periods,
                'dates': future_dates,
                'values': prediction,
                'confidence': 0.7,  # 简单置信度
                'method': 'linear_regression'
            },
            'disclaimer': 'This is a simple prediction based on historical trends and should not be used for critical decisions.'
        }
        
        return success_response(data=response_data)
        
    except Exception as e:
        current_app.logger.error(f"Error predicting metric: {str(e)}")
        return error_response('Failed to generate prediction', 500)

def analyze_comparison(data: Dict, metrics: List[str]) -> Dict:
    """分析比较结果"""
    analysis = {}
    
    for metric in metrics:
        metric_values = {}
        
        for repo, repo_data in data.items():
            if not repo_data.get('error') and metric in repo_data:
                metric_data = repo_data[metric]
                if metric_data:
                    values = list(metric_data.values())
                    if values:
                        metric_values[repo] = {
                            'current': values[-1] if values else 0,
                            'average': statistics.mean(values) if len(values) > 1 else values[0],
                            'max': max(values) if values else 0,
                            'min': min(values) if values else 0,
                            'trend': 'increasing' if len(values) > 1 and values[-1] > values[0] else 'decreasing'
                        }
        
        if metric_values:
            # 找出排名
            sorted_repos = sorted(
                metric_values.items(),
                key=lambda x: x[1]['current'],
                reverse=True
            )
            
            analysis[metric] = {
                'ranking': [
                    {
                        'repository': repo,
                        'rank': i + 1,
                        **values
                    } for i, (repo, values) in enumerate(sorted_repos)
                ],
                'summary': {
                    'top_repository': sorted_repos[0][0] if sorted_repos else None,
                    'average_all': statistics.mean([v['current'] for v in metric_values.values()]) if metric_values else 0,
                    'total_repositories': len(metric_values)
                }
            }
    
    return analysis

def analyze_trend_data(trend_data: Dict, metric: str) -> Dict:
    """分析趋势数据"""
    if not trend_data:
        return {}
    
    dates = sorted(trend_data.keys())
    values = [trend_data[date] for date in dates]
    
    if len(values) < 2:
        return {
            'status': 'insufficient_data',
            'message': 'Need at least 2 data points for trend analysis'
        }
    
    # 计算基本统计
    avg_value = statistics.mean(values)
    max_value = max(values)
    min_value = min(values)
    
    # 计算趋势
    first_value = values[0]
    last_value = values[-1]
    
    if first_value != 0:
        change_pct = ((last_value - first_value) / abs(first_value)) * 100
    else:
        change_pct = 0
    
    # 判断趋势方向
    if change_pct > 5:
        trend_direction = 'strong_increase'
    elif change_pct > 0:
        trend_direction = 'slight_increase'
    elif change_pct < -5:
        trend_direction = 'strong_decrease'
    elif change_pct < 0:
        trend_direction = 'slight_decrease'
    else:
        trend_direction = 'stable'
    
    # 计算移动平均
    window_size = min(3, len(values))
    if window_size > 1:
        moving_avg = []
        for i in range(len(values) - window_size + 1):
            window = values[i:i + window_size]
            moving_avg.append(statistics.mean(window))
        
        # 判断移动平均趋势
        if len(moving_avg) >= 2:
            ma_trend = 'increasing' if moving_avg[-1] > moving_avg[0] else 'decreasing'
        else:
            ma_trend = 'unknown'
    else:
        moving_avg = []
        ma_trend = 'unknown'
    
    return {
        'statistics': {
            'average': round(avg_value, 2),
            'maximum': max_value,
            'minimum': min_value,
            'range': max_value - min_value,
            'std_deviation': round(statistics.stdev(values) if len(values) > 1 else 0, 2)
        },
        'trend': {
            'direction': trend_direction,
            'percentage_change': round(change_pct, 2),
            'absolute_change': last_value - first_value,
            'moving_average_trend': ma_trend,
            'volatility': calculate_volatility(values)
        },
        'periods': {
            'total': len(values),
            'start_date': dates[0],
            'end_date': dates[-1],
            'duration_months': len(dates)
        }
    }

def calculate_correlation(values1: List[float], values2: List[float]) -> float:
    """计算皮尔逊相关系数"""
    if len(values1) != len(values2) or len(values1) < 2:
        return 0.0
    
    try:
        # 手动计算相关系数
        n = len(values1)
        
        # 计算均值
        mean1 = statistics.mean(values1)
        mean2 = statistics.mean(values2)
        
        # 计算协方差和标准差
        covariance = sum((values1[i] - mean1) * (values2[i] - mean2) for i in range(n))
        std1 = statistics.stdev(values1) * (n - 1) / n if n > 1 else 0
        std2 = statistics.stdev(values2) * (n - 1) / n if n > 1 else 0
        
        # 计算相关系数
        if std1 * std2 == 0:
            return 0.0
        
        correlation = covariance / (std1 * std2 * n)
        return round(correlation, 4)
    except:
        return 0.0

def interpret_correlation(correlation: float) -> str:
    """解释相关系数"""
    if correlation > 0.7:
        return "Strong positive correlation"
    elif correlation > 0.3:
        return "Moderate positive correlation"
    elif correlation > 0.1:
        return "Weak positive correlation"
    elif correlation > -0.1:
        return "No significant correlation"
    elif correlation > -0.3:
        return "Weak negative correlation"
    elif correlation > -0.7:
        return "Moderate negative correlation"
    else:
        return "Strong negative correlation"

def calculate_volatility(values: List[float]) -> float:
    """计算波动率"""
    if len(values) < 2:
        return 0.0
    
    # 计算收益率
    returns = []
    for i in range(1, len(values)):
        if values[i-1] != 0:
            returns.append((values[i] - values[i-1]) / values[i-1])
    
    if returns:
        volatility = statistics.stdev(returns) if len(returns) > 1 else 0
        return round(volatility, 4)
    
    return 0.0

def predict_linear_trend(values: List[float], periods: int) -> List[float]:
    """使用简单线性回归预测"""
    n = len(values)
    
    if n < 2:
        return [values[-1]] * periods if values else [0] * periods
    
    # 计算线性回归参数
    x = list(range(n))
    y = values
    
    # 计算均值
    x_mean = statistics.mean(x)
    y_mean = statistics.mean(y)
    
    # 计算斜率和截距
    numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return [y_mean] * periods
    
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    
    # 预测未来值
    predictions = []
    for i in range(n, n + periods):
        prediction = slope * i + intercept
        # 确保预测值不为负
        predictions.append(max(prediction, 0))
    
    return [round(p, 2) for p in predictions]