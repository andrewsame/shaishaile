from typing import Dict, List, Any
from .opendigger_core import CoreDataFetcher

class ProjectScreener:
    def __init__(self):
        self.fetcher = CoreDataFetcher()
    
    def screen_projects(self, repo_list: List[str], 
                       min_activity: float = 50,
                       min_openrank: float = 5,
                       max_response_days: float = 14,
                       min_contributors: int = 10) -> Dict[str, Any]:
        
        results = {'passed': [], 'failed': [], 'details': {}}
        
        for repo in repo_list:
            try:
                owner, name = repo.split('/')
                core_data = self.fetcher.get_repo_core_data(owner, name)
                
                # 简化评估逻辑
                results['passed'].append(repo)
                results['details'][repo] = {'core_data': core_data}
                
            except Exception as e:
                results['failed'].append(repo)
                results['details'][repo] = {'error': str(e)}
        
        return results