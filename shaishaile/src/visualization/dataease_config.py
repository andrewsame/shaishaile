"""
DataEase数据源和图表配置
"""
from typing import Dict, List, Any
import json

# API数据源配置 - 更新为实际可用的API端点
API_DATA_SOURCES = {
    "repo_analysis": {
        "name": "仓库分析API",
        "type": "api",
        "url": "http://localhost:5000/analyze",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json"
        },
        "auth": {
            "type": "none"
        },
        "fields": [
            {"field": "owner", "type": "string", "comment": "仓库所有者", "required": True},
            {"field": "repo", "type": "string", "comment": "仓库名称", "required": True}
        ],
        "response_parser": """
            function parseResponse(response) {
                if (response.success) {
                    return {
                        data: [response.data],
                        fields: [
                            {name: 'repo_name', type: 'string'},
                            {name: 'primary_language', type: 'string'},
                            {name: 'description', type: 'string'},
                            {name: 'openrank', type: 'number'},
                            {name: 'contributor_count', type: 'number'},
                            {name: 'activity_score', type: 'number'},
                            {name: 'commit_frequency', type: 'number'},
                            {name: 'avg_response_time', type: 'number'}
                        ]
                    };
                }
                return {data: [], fields: []};
            }
        """
    },
    "batch_analysis": {
        "name": "批量仓库分析API",
        "type": "api",
        "url": "http://localhost:5000/batch_analyze",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json"
        },
        "fields": [
            {"field": "repos", "type": "array", "comment": "仓库列表，格式: ['owner/repo1', 'owner/repo2']"}
        ],
        "response_parser": """
            function parseResponse(response) {
                if (response.success) {
                    const data = [];
                    for (const [repo, result] of Object.entries(response.results)) {
                        if (result.success && result.data) {
                            data.push({
                                repo_name: repo,
                                primary_language: result.data.primary_language,
                                openrank: result.data.openrank,
                                activity_score: result.data.activity_score,
                                contributor_count: result.data.contributor_count,
                                commit_frequency: result.data.commit_frequency,
                                avg_response_time: result.data.avg_response_time
                            });
                        }
                    }
                    return {
                        data: data,
                        fields: [
                            {name: 'repo_name', type: 'string'},
                            {name: 'primary_language', type: 'string'},
                            {name: 'openrank', type: 'number'},
                            {name: 'activity_score', type: 'number'},
                            {name: 'contributor_count', type: 'number'},
                            {name: 'commit_frequency', type: 'number'},
                            {name: 'avg_response_time', type: 'number'}
                        ]
                    };
                }
                return {data: [], fields: []};
            }
        """
    },
    "trend_analysis": {
        "name": "趋势分析API",
        "type": "api",
        "url": "http://localhost:5000/api/metrics/trend/{repo_name}",
        "method": "GET",
        "headers": {
            "Content-Type": "application/json"
        },
        "path_params": [
            {"field": "repo_name", "comment": "仓库名称"}
        ],
        "query_params": [
            {"field": "metric", "comment": "指标名称", "default": "activity"},
            {"field": "period", "comment": "分析周期(月)", "default": "12"}
        ]
    }
}

# 图表配置
CHART_CONFIGS = {
    "metric_cards": {
        "name": "核心指标卡片",
        "type": "statistic",
        "description": "显示仓库的核心指标数据",
        "data_source": "repo_analysis",
        "layout": {
            "columns": 4,
            "spacing": 16
        },
        "metrics": [
            {
                "field": "openrank", 
                "name": "OpenRank指数", 
                "format": "0.00",
                "color": "#4CAF50",
                "icon": "📊"
            },
            {
                "field": "activity_score", 
                "name": "活跃度分数", 
                "format": "0.00",
                "color": "#2196F3",
                "icon": "⚡"
            },
            {
                "field": "contributor_count", 
                "name": "贡献者数量", 
                "format": "0",
                "color": "#FF9800",
                "icon": "👥"
            },
            {
                "field": "avg_response_time", 
                "name": "平均响应天数", 
                "format": "0.0",
                "color": "#9C27B0",
                "icon": "⏱️"
            }
        ]
    },
    "score_radar": {
        "name": "项目评分雷达图",
        "type": "radar",
        "description": "多维度展示项目评分",
        "data_source": "repo_analysis",
        "dimensions": ["活跃度", "响应度", "OpenRank", "贡献者", "提交频率"],
        "metrics": [
            {
                "field": "activity_score",
                "name": "活跃度分数",
                "max": 100
            },
            {
                "field": "response_score",
                "name": "响应度分数",
                "max": 100
            },
            {
                "field": "openrank_score",
                "name": "OpenRank分数",
                "max": 100
            },
            {
                "field": "contributor_score",
                "name": "贡献者分数",
                "max": 100
            },
            {
                "field": "commit_frequency_score",
                "name": "提交频率分数",
                "max": 100
            }
        ],
        "theme": {
            "area_opacity": 0.3,
            "line_width": 2,
            "colors": ["#4CAF50", "#2196F3"]
        }
    },
    "repo_comparison_table": {
        "name": "仓库对比表格",
        "type": "table",
        "description": "多个仓库指标对比",
        "data_source": "batch_analysis",
        "columns": [
            {"field": "repo_name", "name": "仓库名称", "width": 200, "sortable": True},
            {"field": "primary_language", "name": "主要语言", "width": 120},
            {"field": "openrank", "name": "OpenRank", "width": 100, "format": "0.00"},
            {"field": "activity_score", "name": "活跃度", "width": 100, "format": "0.00"},
            {"field": "contributor_count", "name": "贡献者数", "width": 100, "format": "0"},
            {"field": "commit_frequency", "name": "提交频率", "width": 100, "format": "0.0"},
            {"field": "avg_response_time", "name": "响应时间", "width": 120, "format": "0.0"}
        ],
        "features": {
            "pagination": True,
            "search": True,
            "sorting": True
        }
    },
    "trend_line_chart": {
        "name": "指标趋势图",
        "type": "line",
        "description": "指标随时间变化趋势",
        "data_source": "trend_analysis",
        "x_axis": {
            "field": "date",
            "name": "日期",
            "type": "time"
        },
        "y_axis": {
            "field": "value",
            "name": "指标值"
        },
        "series": [
            {
                "field": "value",
                "name": "指标值",
                "color": "#2196F3",
                "line_type": "solid"
            }
        ],
        "theme": {
            "grid": True,
            "tooltip": True,
            "legend": True
        }
    }
}

# 仪表板布局配置
DASHBOARD_LAYOUT = {
    "overview": {
        "name": "项目概览仪表板",
        "description": "开源项目核心指标概览",
        "theme": {
            "primary_color": "#1890ff",
            "background_color": "#f0f2f5",
            "font_family": "'Microsoft YaHei', 'Segoe UI'"
        },
        "components": [
            {
                "id": "search_panel",
                "type": "search",
                "title": "仓库搜索分析",
                "data_source": "repo_analysis",
                "position": {"x": 0, "y": 0, "w": 12, "h": 2},
                "config": {
                    "placeholder": "输入仓库地址，格式：owner/repo",
                    "button_text": "分析",
                    "fields": [
                        {"name": "owner", "label": "所有者", "type": "text", "required": True},
                        {"name": "repo", "label": "仓库名", "type": "text", "required": True}
                    ]
                }
            },
            {
                "id": "metric_grid",
                "type": "metric_grid", 
                "title": "核心指标",
                "data_source": "repo_analysis",
                "position": {"x": 0, "y": 2, "w": 12, "h": 3},
                "config": CHART_CONFIGS["metric_cards"]
            },
            {
                "id": "radar_chart",
                "type": "radar_chart",
                "title": "项目综合评分",
                "data_source": "repo_analysis", 
                "position": {"x": 0, "y": 5, "w": 6, "h": 6},
                "config": CHART_CONFIGS["score_radar"]
            },
            {
                "id": "trend_chart",
                "type": "line_chart",
                "title": "活跃度趋势",
                "data_source": "trend_analysis",
                "position": {"x": 6, "y": 5, "w": 6, "h": 6},
                "config": {
                    **CHART_CONFIGS["trend_line_chart"],
                    "title": "活跃度变化趋势"
                }
            },
            {
                "id": "comparison_table",
                "type": "data_table",
                "title": "热门仓库对比",
                "data_source": "batch_analysis",
                "position": {"x": 0, "y": 11, "w": 12, "h": 8},
                "config": {
                    **CHART_CONFIGS["repo_comparison_table"],
                    "predefined_repos": [
                        "X-lab2018/open-digger",
                        "vuejs/vue",
                        "facebook/react",
                        "tensorflow/tensorflow"
                    ]
                }
            }
        ]
    },
    "comparison": {
        "name": "项目对比仪表板",
        "description": "多项目详细对比分析",
        "components": [
            {
                "type": "multi_search",
                "title": "选择对比项目",
                "data_source": "batch_analysis",
                "position": {"x": 0, "y": 0, "w": 12, "h": 2}
            },
            {
                "type": "comparison_table",
                "title": "详细对比",
                "data_source": "batch_analysis",
                "position": {"x": 0, "y": 2, "w": 12, "h": 10}
            }
        ]
    }
}

# 数据预处理函数
def preprocess_repo_data(data: Dict) -> Dict:
    """
    预处理仓库数据，计算衍生指标
    """
    if not data:
        return {}
    
    # 计算各项分数（0-100分）
    processed = data.copy()
    
    # OpenRank分数（假设OpenRank最大值为50）
    openrank = data.get('openrank', 0)
    processed['openrank_score'] = min(openrank * 2, 100) if openrank else 0
    
    # 活跃度分数
    activity = data.get('activity_score', 0)
    processed['activity_score_normalized'] = min(activity * 10, 100) if activity else 0
    
    # 响应度分数（响应时间越短分数越高）
    response_time = data.get('avg_response_time', 30)
    processed['response_score'] = max(0, 100 - response_time * 5) if response_time else 100
    
    # 贡献者分数（假设100个贡献者为满分）
    contributors = data.get('contributor_count', 0)
    processed['contributor_score'] = min(contributors, 100)
    
    # 提交频率分数
    commit_freq = data.get('commit_frequency', 0)
    processed['commit_frequency_score'] = min(commit_freq * 5, 100) if commit_freq else 0
    
    # 计算综合评分
    scores = [
        processed.get('activity_score_normalized', 0),
        processed.get('response_score', 0),
        processed.get('openrank_score', 0),
        processed.get('contributor_score', 0),
        processed.get('commit_frequency_score', 0)
    ]
    processed['overall_score'] = sum(scores) / len(scores) if scores else 0
    
    return processed

# DataEase连接配置导出
def export_dataease_config():
    """
    导出DataEase配置
    """
    config = {
        "version": "1.0.0",
        "name": "OpenDigger数据分析平台",
        "description": "基于OpenDigger的开源项目数据分析平台",
        "api_version": "1.0.0",
        "data_sources": API_DATA_SOURCES,
        "charts": CHART_CONFIGS,
        "dashboards": DASHBOARD_LAYOUT,
        "preprocessors": {
            "repo_analysis": preprocess_repo_data
        }
    }
    
    return json.dumps(config, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    print("DataEase配置已更新")
    print("=" * 50)
    print("使用方法:")
    print("1. 启动API服务器: python src/api/app.py")
    print("2. 访问DataEase平台，导入此配置")
    print("3. 使用仓库搜索功能进行分析")