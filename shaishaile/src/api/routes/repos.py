"""
仓库信息路由
"""
from flask import Blueprint, request, jsonify, current_app
from flask_caching import Cache
import requests
from typing import Dict, List

from src.api.utils.response_handler import success_response, error_response
from src.api.utils.validators import validate_repo_name
from src.api.utils.cache_manager import cache_key_generator
from src.api.config.api_config import get_config

repos_bp = Blueprint('repos', __name__)
config = get_config()
cache = Cache(current_app)

@repos_bp.route('/info/<path:repo_name>', methods=['GET'])
@cache.cached(timeout=3600, key_prefix=cache_key_generator)
def get_repository_info(repo_name: str):
    """
    获取仓库详细信息
    """
    try:
        if not validate_repo_name(repo_name):
            return error_response('Invalid repository name format', 400)
        
        # 分割owner和repo
        owner, repo = repo_name.split('/')
        
        # 获取GitHub仓库信息
        headers = {'Accept': 'application/vnd.github.v3+json'}
        token = config.get_github_token()
        if token:
            headers['Authorization'] = f'token {token}'
        
        # 获取基础信息
        repo_url = f"{config.GITHUB_API_BASE_URL}/repos/{owner}/{repo}"
        repo_response = requests.get(repo_url, headers=headers)
        
        if repo_response.status_code != 200:
            return error_response('Repository not found on GitHub', 404)
        
        repo_data = repo_response.json()
        
        # 获取贡献者信息
        contributors_url = f"{repo_url}/contributors"
        contributors_response = requests.get(contributors_url, headers=headers)
        contributors = contributors_response.json() if contributors_response.status_code == 200 else []
        
        # 获取语言信息
        languages_url = f"{repo_url}/languages"
        languages_response = requests.get(languages_url, headers=headers)
        languages = languages_response.json() if languages_response.status_code == 200 else {}
        
        # 获取README
        readme_url = f"{repo_url}/readme"
        readme_response = requests.get(readme_url, headers=headers)
        readme = readme_response.json() if readme_response.status_code == 200 else {}
        
        # 组织响应数据
        response_data = {
            'repository': repo_name,
            'basic_info': {
                'name': repo_data.get('name'),
                'full_name': repo_data.get('full_name'),
                'description': repo_data.get('description'),
                'url': repo_data.get('html_url'),
                'created_at': repo_data.get('created_at'),
                'updated_at': repo_data.get('updated_at'),
                'pushed_at': repo_data.get('pushed_at'),
                'language': repo_data.get('language'),
                'license': repo_data.get('license', {}).get('name') if repo_data.get('license') else None,
                'archived': repo_data.get('archived', False),
                'disabled': repo_data.get('disabled', False)
            },
            'stats': {
                'stars': repo_data.get('stargazers_count', 0),
                'forks': repo_data.get('forks_count', 0),
                'watchers': repo_data.get('watchers_count', 0),
                'open_issues': repo_data.get('open_issues_count', 0),
                'size': repo_data.get('size', 0),
                'has_wiki': repo_data.get('has_wiki', False),
                'has_projects': repo_data.get('has_projects', False),
                'has_downloads': repo_data.get('has_downloads', False)
            },
            'contributors': {
                'count': len(contributors),
                'top_contributors': [
                    {
                        'username': c.get('login'),
                        'contributions': c.get('contributions'),
                        'avatar_url': c.get('avatar_url'),
                        'url': c.get('html_url')
                    } for c in contributors[:10]  # 只取前10个
                ]
            },
            'languages': {
                'count': len(languages),
                'total_bytes': sum(languages.values()),
                'details': [
                    {
                        'language': lang,
                        'bytes': bytes_val,
                        'percentage': round(bytes_val / sum(languages.values()) * 100, 2)
                    } for lang, bytes_val in languages.items()
                ]
            },
            'readme': {
                'size': readme.get('size', 0),
                'download_url': readme.get('download_url'),
                'encoding': readme.get('encoding'),
                'type': readme.get('type')
            }
        }
        
        return success_response(data=response_data)
        
    except Exception as e:
        current_app.logger.error(f"Error fetching repository info for {repo_name}: {str(e)}")
        return error_response('Failed to fetch repository information', 500)

@repos_bp.route('/search', methods=['GET'])
@cache.cached(timeout=300, key_prefix=cache_key_generator)
def search_repositories():
    """
    搜索仓库
    """
    try:
        query = request.args.get('q', '')
        language = request.args.get('language', '')
        sort = request.args.get('sort', 'stars')
        order = request.args.get('order', 'desc')
        per_page = min(int(request.args.get('per_page', 10)), 100)
        page = int(request.args.get('page', 1))
        
        if not query and not language:
            return error_response('Search query or language required', 400)
        
        # 构建搜索参数
        search_params = []
        if query:
            search_params.append(query)
        if language:
            search_params.append(f'language:{language}')
        
        search_query = '+'.join(search_params)
        
        # GitHub搜索API
        search_url = f"{config.GITHUB_API_BASE_URL}/search/repositories"
        params = {
            'q': search_query,
            'sort': sort,
            'order': order,
            'per_page': per_page,
            'page': page
        }
        
        headers = {'Accept': 'application/vnd.github.v3+json'}
        token = config.get_github_token()
        if token:
            headers['Authorization'] = f'token {token}'
        
        response = requests.get(search_url, headers=headers, params=params)
        
        if response.status_code != 200:
            return error_response('Failed to search repositories', 500)
        
        search_results = response.json()
        
        # 格式化响应
        formatted_results = []
        for item in search_results.get('items', []):
            formatted_results.append({
                'full_name': item.get('full_name'),
                'name': item.get('name'),
                'owner': item.get('owner', {}).get('login'),
                'description': item.get('description'),
                'url': item.get('html_url'),
                'language': item.get('language'),
                'stars': item.get('stargazers_count'),
                'forks': item.get('forks_count'),
                'open_issues': item.get('open_issues_count'),
                'created_at': item.get('created_at'),
                'updated_at': item.get('updated_at'),
                'score': item.get('score')
            })
        
        response_data = {
            'query': search_query,
            'total_count': search_results.get('total_count', 0),
            'page': page,
            'per_page': per_page,
            'total_pages': (search_results.get('total_count', 0) + per_page - 1) // per_page,
            'results': formatted_results
        }
        
        return success_response(data=response_data)
        
    except Exception as e:
        current_app.logger.error(f"Error searching repositories: {str(e)}")
        return error_response('Failed to search repositories', 500)

@repos_bp.route('/recommend', methods=['GET'])
@cache.cached(timeout=86400, key_prefix=cache_key_generator)  # 24小时缓存
def get_recommended_repos():
    """
    获取推荐仓库
    """
    try:
        # 这里可以配置一些知名的开源仓库
        recommended_repos = [
            'X-lab2018/open-digger',
            'vuejs/vue',
            'facebook/react',
            'tensorflow/tensorflow',
            'kubernetes/kubernetes',
            'microsoft/vscode',
            'flutter/flutter',
            'golang/go',
            'rust-lang/rust',
            'pytorch/pytorch'
        ]
        
        # 获取每个仓库的基本信息
        repos_info = []
        for repo_name in recommended_repos:
            try:
                owner, repo = repo_name.split('/')
                
                # 从GitHub获取基本信息
                repo_url = f"{config.GITHUB_API_BASE_URL}/repos/{owner}/{repo}"
                headers = {'Accept': 'application/vnd.github.v3+json'}
                
                response = requests.get(repo_url, headers=headers)
                if response.status_code == 200:
                    repo_data = response.json()
                    
                    repos_info.append({
                        'full_name': repo_data.get('full_name'),
                        'description': repo_data.get('description'),
                        'url': repo_data.get('html_url'),
                        'stars': repo_data.get('stargazers_count'),
                        'forks': repo_data.get('forks_count'),
                        'language': repo_data.get('language'),
                        'topics': repo_data.get('topics', [])
                    })
                    
            except Exception as e:
                current_app.logger.warning(f"Failed to fetch info for {repo_name}: {str(e)}")
                continue
        
        return success_response(data={
            'repositories': repos_info,
            'count': len(repos_info),
            'description': 'Recommended popular open source repositories'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting recommended repos: {str(e)}")
        return error_response('Failed to get recommended repositories', 500)