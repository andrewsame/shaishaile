#!/usr/bin/env python3
"""
OpenDigger 数据平台 - 系统测试脚本
"""

import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def print_header(title):
    """打印测试标题"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def test_module_imports():
    """测试模块导入"""
    print_header("模块导入测试")
    
    try:
        # 测试导入数据采集模块
        from data_collection import CoreDataFetcher
        print_success("成功导入 CoreDataFetcher")
        
        from data_collection import ProjectScreener
        print_success("成功导入 ProjectScreener")
        
        return True
    except ImportError as e:
        print_error(f"导入失败: {e}")
        print_info("检查 src/data-collection/ 目录是否存在")
        return False

def test_basic_functionality():
    """测试基础功能"""
    print_header("基础功能测试")
    
    try:
        from data_collection.opendigger_core import OpenDiggerClient
        
        client = OpenDiggerClient()
        print_success("OpenDiggerClient 初始化成功")
        
        # 测试简单API调用
        data = client.get_repo_metrics('X-lab2017', 'open-digger', ['stars'])
        if data:
            print_success("API调用成功")
            return True
        else:
            print_error("API调用返回空数据")
            return False
            
    except Exception as e:
        print_error(f"基础功能测试失败: {e}")
        return False

def main():
    print("🚀 OpenDigger 数据平台系统测试")
    print("=" * 50)
    
    # 首先检查目录结构
    print_header("检查项目结构")
    
    required_paths = [
        'src/data-collection/__init__.py',
        'src/data-collection/opendigger_core.py', 
        'src/data-collection/project_analyzer.py',
        'config/opendigger-config.json'
    ]
    
    all_paths_exist = True
    for path in required_paths:
        if os.path.exists(path):
            print_success(f"文件存在: {path}")
        else:
            print_error(f"文件不存在: {path}")
            all_paths_exist = False
    
    if not all_paths_exist:
        print_error("请先创建必要的文件结构")
        return
    
    # 运行测试
    test1 = test_module_imports()
    test2 = test_basic_functionality()
    
    print("\n" + "=" * 50)
    if test1 and test2:
        print("🎉 所有测试通过！系统运行正常。")
    else:
        print("⚠️  部分测试失败，请检查错误信息。")

if __name__ == "__main__":
    main()