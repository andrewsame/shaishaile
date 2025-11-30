"""
DataEase数据源和图表配置
"""

# API数据源配置
API_DATA_SOURCES = {
    "repo_analysis": {
        "name": "仓库分析API",
        "type": "api",
        "url": "http://localhost:5000/analyze",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json"
        },
        "fields": [
            {"field": "owner", "type": "string", "comment": "仓库所有者"},
            {"field": "repo", "type": "string", "comment": "仓库名称"}
        ]
    },
    "project_screening": {
        "name": "项目筛选API", 
        "type": "api",
        "url": "http://localhost:5000/screening",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json"
        },
        "fields": [
            {"field": "repos", "type": "array", "comment": "仓库列表"},
            {"field": "criteria", "type": "object", "comment": "筛选条件"}
        ]
    }
}

# 图表配置
CHART_CONFIGS = {
    "metric_cards": {
        "name": "核心指标卡片",
        "type": "statistic",
        "metrics": [
            {"field": "openrank", "name": "OpenRank指数", "format": "0.00"},
            {"field": "activity_score", "name": "活跃度分数", "format": "0.00"},
            {"field": "contributor_count", "name": "贡献者数量", "format": "0"},
            {"field": "avg_response_time", "name": "平均响应天数", "format": "0.0"}
        ]
    },
    "score_radar": {
        "name": "项目评分雷达图",
        "type": "radar",
        "dimensions": ["活跃度", "响应度", "OpenRank", "贡献者"],
        "metrics": ["activity_score", "response_score", "openrank_score", "contributor_score"]
    }
}

# 仪表板布局
DASHBOARD_LAYOUT = {
    "overview": {
        "name": "项目概览仪表板",
        "components": [
            {
                "type": "search",
                "title": "仓库搜索",
                "dataSource": "repo_analysis",
                "position": {"x": 0, "y": 0, "w": 12, "h": 2}
            },
            {
                "type": "metric_grid", 
                "title": "核心指标",
                "dataSource": "repo_analysis",
                "position": {"x": 0, "y": 2, "w": 12, "h": 3}
            },
            {
                "type": "radar_chart",
                "title": "项目评分",
                "dataSource": "repo_analysis", 
                "position": {"x": 0, "y": 5, "w": 6, "h": 6}
            }
        ]
    }
}