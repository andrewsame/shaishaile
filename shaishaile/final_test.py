#!/usr/bin/env python3
"""
OpenDigger 数据平台 - 修复版完整测试
"""

import sys
import os

# 添加src到Python路径
sys.path.insert(0, 'src')

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def test_all_modules():
    """测试所有模块"""
    print_header("模块导入测试")
    
    try:
        # 直接导入测试
        from data_collection import CoreDataFetcher
        print_success("CoreDataFetcher 导入成功")
        
        from data_collection import ProjectScreener
        print_success("ProjectScreener 导入成功")
        
        from data_collection.opendigger_core import OpenDiggerClient
        print_success("OpenDiggerClient 导入成功")
        
        # 返回导入的类
        return True, {
            'CoreDataFetcher': CoreDataFetcher,
            'ProjectScreener': ProjectScreener,
            'OpenDiggerClient': OpenDiggerClient
        }
        
    except Exception as e:
        print_error(f"模块导入失败: {e}")
        return False, {}

def test_api_functionality(imported_modules):
    """测试API功能"""
    print_header("API功能测试")
    
    try:
        OpenDiggerClient = imported_modules['OpenDiggerClient']
        client = OpenDiggerClient()
        
        # 测试多个指标
        test_repos = [
            ('X-lab2017', 'open-digger', ['stars', 'openrank']),
            ('facebook', 'react', ['stars'])
        ]
        
        all_success = True
        
        for owner, repo, metrics in test_repos:
            print(f"\n📊 测试 {owner}/{repo}: {metrics}")
            data = client.get_repo_metrics(owner, repo, metrics)
            
            if data:
                valid_metrics = 0
                for metric, metric_data in data.items():
                    if metric_data and not (isinstance(metric_data, dict) and 'error' in metric_data):
                        valid_metrics += 1
                        if isinstance(metric_data, dict) and metric_data:
                            dates = list(metric_data.keys())
                            values = list(metric_data.values())
                            print(f"   {metric}: {len(dates)}个月数据，最新值: {values[-1] if values else 'N/A'}")
                        else:
                            print(f"   {metric}: 数据有效")
                    else:
                        print(f"   {metric}: 获取失败")
                
                if valid_metrics > 0:
                    print_success(f"  {owner}/{repo}: {valid_metrics}/{len(metrics)} 个指标成功")
                else:
                    print_error(f"  {owner}/{repo}: 所有指标获取失败")
                    all_success = False
            else:
                print_error(f"  {owner}/{repo}: 无数据返回")
                all_success = False
        
        return all_success
        
    except Exception as e:
        print_error(f"API功能测试失败: {e}")
        return False

def test_core_data_fetcher(imported_modules):
    """测试核心数据获取器"""
    print_header("核心数据获取测试")
    
    try:
        CoreDataFetcher = imported_modules['CoreDataFetcher']
        fetcher = CoreDataFetcher()
        core_data = fetcher.get_repo_core_data('X-lab2017', 'open-digger')
        
        print("📋 获取的核心数据:")
        required_fields = [
            'repo_name', 'primary_language', 'description',
            'openrank', 'contributor_count', 'activity_score'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field in core_data:
                value = core_data[field]
                print_success(f"  {field}: {value}")
            else:
                missing_fields.append(field)
                print_error(f"  {field}: 缺失")
        
        if not missing_fields:
            print_success("所有核心字段获取成功")
            return True
        else:
            print_error(f"缺失字段: {missing_fields}")
            return False
            
    except Exception as e:
        print_error(f"核心数据获取测试失败: {e}")
        return False

def test_project_screening(imported_modules):
    """测试项目筛选"""
    print_header("项目筛选测试")
    
    try:
        ProjectScreener = imported_modules['ProjectScreener']
        screener = ProjectScreener()
        
        test_repos = [
            'X-lab2017/open-digger',
            'facebook/react'
        ]
        
        results = screener.screen_projects(test_repos)
        
        print(f"📈 筛选结果:")
        print(f"   总项目数: {len(test_repos)}")
        print(f"   通过: {len(results['passed'])}")
        print(f"   未通过: {len(results['failed'])}")
        
        # 显示详细信息
        for repo in results['passed']:
            print_success(f"   ✅ {repo} 通过筛选")
        
        for repo in results['failed']:
            detail = results['details'][repo]
            if 'error' in detail:
                print_error(f"   ❌ {repo} 失败: {detail['error']}")
            else:
                print_error(f"   ❌ {repo} 未通过筛选")
        
        if results['passed']:
            print_success("项目筛选功能正常")
            return True
        else:
            print_error("没有项目通过筛选")
            return False
            
    except Exception as e:
        print_error(f"项目筛选测试失败: {e}")
        return False

def main():
    print("🚀 OpenDigger 数据平台 - 完整系统测试")
    print("=" * 60)
    
    # 测试模块导入
    import_success, imported_modules = test_all_modules()
    
    if not import_success:
        print_error("模块导入失败，无法继续测试")
        return
    
    # 运行各项功能测试
    tests = [
        ('API功能', lambda: test_api_functionality(imported_modules)),
        ('核心数据获取', lambda: test_core_data_fetcher(imported_modules)),
        ('项目筛选', lambda: test_project_screening(imported_modules))
    ]
    
    test_results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print_error(f"{test_name} 测试异常: {e}")
            test_results.append((test_name, False))
    
    # 汇总结果
    print_header("测试结果汇总")
    
    passed_tests = sum(1 for name, result in test_results if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总成绩: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("\n🎉 恭喜！所有测试通过！OpenDigger数据平台可以正常工作了！")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} 个测试失败，请检查相关功能")

if __name__ == "__main__":
    main()