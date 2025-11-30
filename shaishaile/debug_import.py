import sys
import os

print("=== 调试信息 ===")
print("当前工作目录:", os.getcwd())

# 添加src目录到Python路径
src_path = os.path.join(os.getcwd(), 'src')
sys.path.insert(0, src_path)

print("添加后的Python路径:")
for path in sys.path[:3]:  # 只显示前3个
    print("  ", path)

print("\n=== 检查文件 ===")
files_to_check = [
    'src/data-collection/__init__.py',
    'src/data-collection/opendigger_core.py',
    'src/data-collection/project_analyzer.py'
]

for file_path in files_to_check:
    exists = os.path.exists(file_path)
    print(f"{file_path}: {'✅ 存在' if exists else '❌ 不存在'}")

print("\n=== 尝试导入 ===")
try:
    # 现在应该可以导入了
    import data_collection
    print("✅ 成功导入 data_collection")
    
    from data_collection import CoreDataFetcher
    print("✅ 成功导入 CoreDataFetcher")
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()