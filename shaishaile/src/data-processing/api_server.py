from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from datetime import datetime

# 修复导入路径 - 使用绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))  # 项目根目录
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

print(f"📁 项目根目录: {project_root}")
print(f"📁 添加路径: {src_dir}")

try:
    from data_collection import CoreDataFetcher, ProjectScreener
    print("✅ 数据采集模块导入成功")
except ImportError as e:
    print(f"❌ 数据采集模块导入失败: {e}")
    # 显示Python路径用于调试
    print("Python路径:")
    for path in sys.path:
        print(f"  {path}")
    exit(1)

app = Flask(__name__)
CORS(app)

# 初始化处理器
core_fetcher = CoreDataFetcher()
project_screener = ProjectScreener()

@app.route('/')
def home():
    return jsonify({
        "message": "OpenDigger Data Platform API",
        "version": "1.0.0",
        "endpoints": {
            "/analyze": "POST - 分析单个仓库",
            "/batch_analyze": "POST - 批量分析仓库", 
            "/screening": "POST - 项目筛选",
            "/health": "GET - 健康检查"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "OpenDigger API",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/analyze', methods=['POST'])
def analyze_repo():
    """分析单个仓库"""
    data = request.json
    owner = data.get('owner')
    repo = data.get('repo')
    
    if not owner or not repo:
        return jsonify({"error": "Missing owner or repo"}), 400
    
    try:
        print(f"🔍 分析仓库: {owner}/{repo}")
        core_data = core_fetcher.get_repo_core_data(owner, repo)
        
        return jsonify({
            "success": True,
            "data": core_data,
            "repo": f"{owner}/{repo}"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/batch_analyze', methods=['POST'])
def batch_analyze():
    """批量分析多个仓库"""
    data = request.json
    repo_list = data.get('repos', [])
    
    if not repo_list:
        return jsonify({"error": "No repositories provided"}), 400
    
    try:
        print(f"🔍 批量分析 {len(repo_list)} 个仓库")
        results = {}
        
        for repo in repo_list:
            try:
                owner, name = repo.split('/')
                core_data = core_fetcher.get_repo_core_data(owner, name)
                results[repo] = {
                    "success": True,
                    "data": core_data
                }
                print(f"✅ 完成: {repo}")
            except Exception as e:
                results[repo] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"❌ 失败: {repo} - {e}")
        
        return jsonify({
            "success": True,
            "results": results,
            "total_repos": len(repo_list),
            "successful": sum(1 for r in results.values() if r['success'])
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/screening', methods=['POST'])
def screen_projects():
    """项目筛选"""
    data = request.json
    repo_list = data.get('repos', [])
    criteria = data.get('criteria', {})
    
    if not repo_list:
        return jsonify({"error": "No repositories provided"}), 400
    
    try:
        print(f"🔍 筛选 {len(repo_list)} 个项目")
        
        results = project_screener.screen_projects(
            repo_list,
            min_activity=criteria.get('min_activity', 30),
            min_openrank=criteria.get('min_openrank', 2),
            max_response_days=criteria.get('max_response_days', 7),
            min_contributors=criteria.get('min_contributors', 5)
        )
        
        return jsonify({
            "success": True,
            "results": results
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 启动 OpenDigger API 服务器...")
    print("📍 访问 http://localhost:5000 查看API文档")
    print("📍 访问 http://localhost:5000/health 进行健康检查")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)