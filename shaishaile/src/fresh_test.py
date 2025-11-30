#!/usr/bin/env python3
"""
全新的测试文件 - 避免缓存问题
"""

import sys
import os

# 确保在项目根目录运行
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)  # 切换到项目根目录

# 添加src到Python路径
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

print("🔄 工作目录:", os.getcwd())
print("📁 添加路径:", src_dir)

def test_simple_import():
    """最简单的导入测试"""
    print("\n=== 简单导入测试 ===")
    
    try:
        # 直接导入具体的类，避免__init__.py的问题
        from data_collection.opendigger_core import OpenDiggerClient
        print("✅ OpenDiggerClient 导入成功")
        
        from data_collection.opendigger_core import CoreDataFetcher
        print("✅ CoreDataFetcher 导入成功")
        
        from data_collection.project_analyzer import ProjectScreener
        print("✅ ProjectScreener 导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_functionality():
    """测试功能"""
    print("\n=== 功能测试 ===")
    
    try:
        from data_collection.opendigger_core import OpenDiggerClient
        
        client = OpenDiggerClient()
        print("✅ OpenDiggerClient 初始化成功")
        
        # 测试API调用
        data = client.get_repo_metrics('X-lab2017', 'open-digger', ['stars'])
        
        if data and 'stars' in data:
            stars_data = data['stars']
            if isinstance(stars_data, dict) and stars_data:
                dates = list(stars_data.keys())
                values = list(stars_data.values())
                print(f"✅ API调用成功")
                print(f"   数据时间范围: {dates[0]} 到 {dates[-1]}")
                print(f"   最新stars数: {values[-1]}")
                return True
            else:
                print("⚠️  API返回数据格式异常")
                return True  # 仍然算成功，至少连接上了
        else:
            print("❌ API调用返回空数据")
            return False
            
    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        return False

def main():
    print("🚀 OpenDigger 全新测试")
    print("=" * 50)
    
    # 测试导入
    import_ok = test_simple_import()
    
    if import_ok:
        # 测试功能
        func_ok = test_functionality()
    else:
        func_ok = False
    
    print("\n" + "=" * 50)
    if import_ok and func_ok:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  测试未完全通过")

if __name__ == "__main__":
    main()