#!/usr/bin/env python3
"""
紧急修复脚本 - 直接修复导入问题
"""

import os

# 修复 __init__.py 文件
init_file_path = 'src/data_collection/__init__.py'

print("🔧 修复 __init__.py 文件...")

# 写入正确的内容
correct_content = '''"""
OpenDigger 数据采集模块
"""

from .opendigger_core import OpenDiggerClient, CoreDataFetcher
from .project_analyzer import ProjectScreener

__all__ = ['OpenDiggerClient', 'CoreDataFetcher', 'ProjectScreener']
'''

try:
    with open(init_file_path, 'w', encoding='utf-8') as f:
        f.write(correct_content)
    print(f"✅ 已修复: {init_file_path}")
except Exception as e:
    print(f"❌ 修复失败: {e}")

# 测试修复结果
print("\n🧪 测试修复结果...")
import sys
sys.path.insert(0, 'src')

try:
    from data_collection import CoreDataFetcher, ProjectScreener
    print("✅ 导入成功！问题已解决")
    
    # 测试功能
    from data_collection.opendigger_core import OpenDiggerClient
    client = OpenDiggerClient()
    data = client.get_repo_metrics('X-lab2017', 'open-digger', ['stars'])
    print(f"✅ API调用成功: {len(data)} 个指标")
    
except Exception as e:
    print(f"❌ 仍然失败: {e}")