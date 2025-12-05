"""
开发者数据路由
"""
from flask import Blueprint, request, jsonify, current_app
from flask_caching import Cache
import requests
from typing import Dict, List

from src.data_collection.opendigger_client import OpenDiggerClient
from src.api.utils.response_handler import success_response, error_response
from src.api.utils.validators import validate_username
from src.api.utils.cache_manager import cache_key_generator
from src.api.config.api_config import get_config

developers_bp = Blueprint('developers', __name__)
client = OpenDiggerClient()
config = get_config()
cache = Cache(current_app)

@developers_bp.route('/<username>', methods=['GET'])
@cache.cached(timeout=1800, key_prefix=cache_key_generator)
def get_developer_metrics(username: str):
    """
    获取开发者指标
    """
    try:
        if not validate_username(username):
            return error_response('Invalid username format', 400)
        
        metrics_param = request.args.get('metrics', 'activity,openrank')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        metrics_list = [m.strip() for m in metrics_param.split(',')]
        
        # 获取OpenDigger数据
        metrics_data = client.get_developer_metrics(
            username=username,
            metrics=metrics_list
        )
        
        # 获取GitHub用户信息
        headers = {'Accept': 'application/vnd.github.v3+json'}
        token = config.get_github_token()
        if token:
            headers['Authorization'] = f'token {token}'
        
        user_url = f"{config.GITHUB_API_BASE_URL}/users/{username}"
        user_response = requests.get(user_url, headers=headers)
        
        user_info = {}
        if user_response.status_code == 200:
            user_data = user_response.json()
            user_info = {
                'login': user_data.get('login'),
                'name': user_data.get('name'),
                'avatar_url': user_data.get('avatar_url'),
                'bio': user_data.get('bio'),
                'blog': user_data.get('blog'),
                'company': user_data.get('company'),
                'location': user_data.get('location'),
                'email': user_data.get('email'),
                'twitter_username': user_data.get('twitter_username'),
                'public_repos': user_data.get('public_repos'),
                'public_gists': user_data.get('public_gists'),
                'followers': user_data.get('followers'),
                'following': user_data.get('following'),
                'created_at': user_data.get('created_at'),
                'updated_at': user_data.get('updated_at')
            }
        
        # 获取用户参与的项目
        repos_url = f"{config.GITHUB_API_BASE_URL}/users/{username}/repos"
        repos_response = requests.get(repos_url, headers=headers, params={'sort': 'updated', 'per_page': 10})
        
        recent_repos = []
        if repos_response.status_code == 200:
            repos_data = repos_response.json()
            for repo in repos_data[:5]:  # 只取最近5个
                recent_repos.append({
                    'name': repo.get('full_name'),
                    'description': repo.get('description'),
                    'language': repo.get('language'),
                    'stars': repo.get('stargazers_count'),
                    'forks': repo.get('forks_count'),
                    'url': repo.get('html_url'),
                    'updated_at': repo.get('updated_at')
                })
        
        response_data = {
            'developer': username,
            'user_info': user_info,
            'metrics': metrics_data,
            'recent_repositories': recent_repos,
            'date_range': {
                'start': start_date,
                'end': end_date
            }
        }
        
        return success_response(data=response_data)
        
    except Exception as e:
        current_app.logger.error(f"Error fetching developer data for {username}: {str(e)}")
        return error_response('Failed to fetch developer data', 500)

@developers_bp.route('/<username>/contributions', methods=['GET'])
@cache.cached(timeout=3600, key_prefix=cache_key_generator)
def get_developer_contributions(username: str):
    """
    获取开发者贡献统计
    """
    try:
        if not validate_username(username):
            return error_response('Invalid username format', 400)
        
        # 获取用户的公共活动
        headers = {'Accept': 'application/vnd.github.v3+json'}
        token = config.get_github_token()
        if token:
            headers['Authorization'] = f'token {token}'
        
        events_url = f"{config.GITHUB_API_BASE_URL}/users/{username}/events/public"
        events_response = requests.get(events_url, headers=headers, params={'per_page': 100})
        
        if events_response.status_code != 200:
            return error_response('Failed to fetch user events', 500)
        
        events = events_response.json()
        
        # 统计不同类型的贡献
        contribution_stats = {
            'PushEvent': 0,
            'PullRequestEvent': 0,
            'IssuesEvent': 0,
            'CreateEvent': 0,
            'WatchEvent': 0,
            'ForkEvent': 0,
            'PublicEvent': 0,
            'total': len(events)
        }
        
        # 统计每个仓库的贡献
        repo_contributions = {}
        
        for event in events:
            event_type = event.get('type')
            if event_type in contribution_stats:
                contribution_stats[event_type] += 1
            
            # 记录仓库贡献
            repo = event.get('repo', {})
            repo_name = repo.get('name') if repo else 'unknown'
            
            if repo_name not in repo_contributions:
                repo_contributions[repo_name] = {
                    'PushEvent': 0,
                    'PullRequestEvent': 0,
                    'IssuesEvent': 0,
                    'CreateEvent': 0,
                    'total': 0
                }
            
            if event_type in repo_contributions[repo_name]:
                repo_contributions[repo_name][event_type] += 1
                repo_contributions[repo_name]['total'] += 1
        
        # 排序仓库贡献
        sorted_repos = sorted(
            repo_contributions.items(),
            key=lambda x: x[1]['total'],
            reverse=True
        )[:10]  # 取前10个
        
        response_data = {
            'developer': username,
            'total_events': contribution_stats.pop('total'),
            'event_types': contribution_stats,
            'top_repositories': [
                {
                    'repository': repo_name,
                    'contributions': stats
                } for repo_name, stats in sorted_repos
            ],
            'analysis': {
                'is_active': contribution_stats['PushEvent'] > 0 or contribution_stats['PullRequestEvent'] > 0,
                'primary_activity': max(contribution_stats, key=contribution_stats.get),
                'contribution_score': calculate_contribution_score(contribution_stats)
            }
        }
        
        return success_response(data=response_data)
        
    except Exception as e:
        current_app.logger.error(f"Error fetching contributions for {username}: {str(e)}")
        return error_response('Failed to fetch contribution data', 500)

@developers_bp.route('/compare', methods=['POST'])
def compare_developers():
    """
    比较多个开发者的指标
    """
    try:
        request_data = request.get_json()
        
        if not request_data or 'developers' not in request_data:
            return error_response('Missing developers in request body', 400)
        
        developers = request_data['developers']
        metrics = request_data.get('metrics', ['activity', 'openrank'])
        
        if len(developers) > 5:
            return error_response('Maximum 5 developers allowed per comparison', 400)
        
        results = {}
        all_valid = True
        
        for dev in developers:
            if not validate_username(dev):
                results[dev] = {'error': 'Invalid username format'}
                all_valid = False
            else:
                try:
                    data = client.get_developer_metrics(
                        username=dev,
                        metrics=metrics
                    )
                    results[dev] = data
                except Exception as e:
                    results[dev] = {'error': str(e)}
                    all_valid = False
        
        response_data = {
            'comparison': results,
            'metrics': metrics,
            'all_valid': all_valid,
            'developer_count': len(developers)
        }
        
        return success_response(data=response_data)
        
    except Exception as e:
        current_app.logger.error(f"Error comparing developers: {str(e)}")
        return error_response('Failed to compare developers', 500)

def calculate_contribution_score(stats: Dict) -> float:
    """
    计算贡献分数
    """
    # 不同的活动类型有不同的权重
    weights = {
        'PushEvent': 2.0,          # 代码提交
        'PullRequestEvent': 1.5,   # PR创建/合并
        'IssuesEvent': 1.0,        # Issue相关
        'CreateEvent': 0.8,        # 创建仓库/分支
        'WatchEvent': 0.3,         # 关注仓库
        'ForkEvent': 0.5,          # Fork仓库
        'PublicEvent': 0.7         # 开源仓库
    }
    
    score = 0
    total_weight = 0
    
    for event_type, count in stats.items():
        if event_type in weights:
            score += count * weights[event_type]
            total_weight += weights[event_type]
    
    # 归一化到0-100分
    if total_weight > 0:
        normalized_score = (score / max(total_weight * 10, 1)) * 100
        return round(min(normalized_score, 100), 2)
    
    return 0.0