from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# 添加数据采集模块路径
sys.path.append('../data_collection')
from data_collection import CoreDataFetcher, ProjectScreener

app = Flask(__name__)
CORS(app)

core_fetcher = CoreDataFetcher()
project_screener = ProjectScreener()

@app.route('/analyze', methods=['POST'])
def analyze_repo():
    data = request.json
    owner = data.get('owner')
    repo = data.get('repo')
    
    try:
        core_data = core_fetcher.get_repo_core_data(owner, repo)
        return jsonify({"success": True, "data": core_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)