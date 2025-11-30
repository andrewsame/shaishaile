import requests
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class OpenDiggerClient:
    def __init__(self, config_path: str = "../../config/opendigger-config.json"):
        self.base_url = "https://oss.x-lab.info/open_digger/github/"
    
    def get_repo_metrics(self, owner: str, repo: str, metrics: List[str] = None) -> Dict[str, Any]:
        print(f"📡 获取 {owner}/{repo} 的数据")
        
        repo_data = {}
        for metric in metrics or ['stars']:
            url = f"{self.base_url}{owner}/{repo}/{metric}.json"
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    repo_data[metric] = response.json()
                else:
                    repo_data[metric] = {"error": f"Status {response.status_code}"}
            except Exception as e:
                repo_data[metric] = {"error": str(e)}
        
        return repo_data

class CoreDataFetcher:
    def __init__(self):
        self.client = OpenDiggerClient()
    
    def get_repo_core_data(self, owner: str, repo: str) -> Dict[str, Any]:
        print(f"🎯 获取核心数据: {owner}/{repo}")
        
        raw_data = self.client.get_repo_metrics(owner, repo, [
            'openrank', 'activity', 'participants', 'stars'
        ])
        
        core_data = self._process_core_fields(owner, repo, raw_data)
        return core_data
    
    def _process_core_fields(self, owner: str, repo: str, raw_data: Dict) -> Dict[str, Any]:
        core_data = {
            'repo_name': f"{owner}/{repo}",
            'primary_language': self._get_primary_language(owner, repo),
            'description': self._get_repo_description(owner, repo),
            'openrank': self._get_latest_value(raw_data.get('openrank', {})),
            'contributor_count': self._get_latest_value(raw_data.get('participants', {})),
            'activity_score': self._get_latest_value(raw_data.get('activity', {})),
            'commit_frequency': self._calculate_commit_frequency(raw_data),
            'avg_response_time': self._calculate_avg_response_time(raw_data),
            '_raw_metrics': raw_data
        }
        
        return core_data
    
    def _get_primary_language(self, owner: str, repo: str) -> str:
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}/languages"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                languages = response.json()
                if languages:
                    return max(languages.items(), key=lambda x: x[1])[0]
        except:
            pass
        return "Unknown"
    
    def _get_repo_description(self, owner: str, repo: str) -> str:
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                repo_info = response.json()
                return repo_info.get('description', 'No description')
        except:
            pass
        return "No description available"
    
    def _calculate_commit_frequency(self, raw_data: Dict) -> float:
        return 10.5  # 简化版本
    
    def _calculate_avg_response_time(self, raw_data: Dict) -> Optional[float]:
        return 5.0  # 简化版本
    
    def _get_latest_value(self, data: Dict) -> Optional[float]:
        if not data or not isinstance(data, dict):
            return None
        sorted_dates = sorted(data.keys())
        if not sorted_dates:
            return None
        latest_date = sorted_dates[-1]
        return data[latest_date]