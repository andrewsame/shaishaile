#!/usr/bin/env python3
"""
DataEase配置导出工具
用于将API配置导出为DataEase可导入的格式
"""
import json
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.visualization.dataease_config import export_dataease_config
except ImportError:
    # 如果导入失败，使用简化的配置
    def export_dataease_config():
        config = {
            "version": "1.0.0",
            "name": "OpenDigger数据分析平台",
            "description": "基于OpenDigger的开源项目数据分析平台",
            "api_endpoints": {
                "analyze": "http://localhost:5000/analyze",
                "batch_analyze": "http://localhost:5000/batch_analyze",
                "screening": "http://localhost:5000/screening"
            }
        }
        return json.dumps(config, ensure_ascii=False, indent=2)

def create_dataease_import_file():
    """
    创建DataEase导入文件
    """
    # 确保输出目录存在
    output_dir = project_root / "data" / "exports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 导出配置文件
    config_json = export_dataease_config()
    
    # 保存为JSON文件
    config_file = output_dir / "dataease_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_json)
    
    print(f"✅ DataEase配置文件已生成: {config_file}")
    
    # 创建使用说明文档
    readme_content = f"""# DataEase 配置使用指南

## 配置文件位置
`{config_file.relative_to(project_root)}`

## 配置内容
该配置文件包含了以下数据源和图表配置：

### 1. API数据源
- **仓库分析API**: 单个仓库详细分析
- **批量仓库分析API**: 多仓库对比分析
- **趋势分析API**: 指标历史趋势分析

### 2. 图表类型
- 指标卡片 (核心指标展示)
- 雷达图 (多维度评分)
- 折线图 (趋势分析)
- 数据表格 (对比分析)

### 3. 仪表板布局
- 项目概览仪表板
- 项目对比仪表板

## DataEase导入步骤

### 方法一：直接导入JSON配置
1. 登录DataEase平台
2. 进入"数据源" -> "API数据源"
3. 点击"导入配置"
4. 选择 `{config_file.name}` 文件
5. 根据提示完成导入

### 方法二：手动配置
1. 根据配置文件中的API端点手动创建数据源
2. 使用预定义的图表模板创建可视化组件
3. 按照仪表板布局拖拽组件

## API服务器要求
确保以下API服务正在运行：
- OpenDigger API: http://localhost:5000

## 快速测试
1. 启动API服务器: `python src/api/app.py`
2. 访问API文档: http://localhost:5000/api/docs
3. 测试数据源连接

## 技术支持
如遇到问题，请检查：
1. API服务器是否正常运行
2. 网络连接是否正常
3. DataEase版本是否兼容
"""
    
    readme_file = output_dir / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ 使用指南已生成: {readme_file}")
    
    # 创建示例数据文件
    create_sample_data(output_dir)
    
    return config_file

def create_sample_data(output_dir):
    """
    创建示例数据文件
    """
    sample_data = {
        "example_repositories": [
            "X-lab2018/open-digger",
            "vuejs/vue", 
            "facebook/react",
            "tensorflow/tensorflow",
            "microsoft/vscode",
            "flutter/flutter"
        ],
        "api_test_examples": {
            "analyze_single_repo": {
                "method": "POST",
                "url": "http://localhost:5000/analyze",
                "body": {
                    "owner": "X-lab2018",
                    "repo": "open-digger"
                }
            },
            "batch_analyze": {
                "method": "POST", 
                "url": "http://localhost:5000/batch_analyze",
                "body": {
                    "repos": ["X-lab2018/open-digger", "vuejs/vue"]
                }
            }
        }
    }
    
    sample_file = output_dir / "sample_data.json"
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 示例数据已生成: {sample_file}")

def main():
    """
    主函数
    """
    print("=" * 60)
    print("DataEase 配置导出工具")
    print("=" * 60)
    
    try:
        config_file = create_dataease_import_file()
        
        print("\n" + "=" * 60)
        print("✅ 导出完成！")
        print("=" * 60)
        print("\n下一步操作：")
        print("1. 确保API服务器正在运行: python src/api/app.py")
        print("2. 打开预览页面查看效果: src/visualization/dataease_preview.html")
        print("3. 登录DataEase平台导入配置文件")
        print("4. 按照使用指南配置数据源和仪表板")
        
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()