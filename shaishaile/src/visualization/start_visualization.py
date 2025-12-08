#!/usr/bin/env python3
"""
可视化平台启动脚本
启动API服务器并打开预览页面
"""
import os
import sys
import webbrowser
import subprocess
import time
from pathlib import Path

def check_api_server():
    """检查API服务器状态"""
    try:
        import requests
        response = requests.get("http://localhost:5000/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def start_api_server():
    """启动API服务器"""
    print("🚀 启动API服务器...")
    
    # 获取项目根目录
    current_dir = Path(__file__).parent
    api_app_path = current_dir.parent / "api" / "app.py"
    
    if not api_app_path.exists():
        print(f"❌ 找不到API应用文件: {api_app_path}")
        return None
    
    # 使用subprocess启动API服务器
    env = os.environ.copy()
    env["PYTHONPATH"] = str(current_dir.parent) + os.pathsep + env.get("PYTHONPATH", "")
    
    process = subprocess.Popen(
        [sys.executable, str(api_app_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    # 等待服务器启动
    print("⏳ 等待API服务器启动...")
    for i in range(30):  # 最多等待30秒
        if check_api_server():
            print("✅ API服务器启动成功！")
            return process
        time.sleep(1)
    
    print("❌ API服务器启动超时")
    return None

def open_preview_page():
    """打开预览页面"""
    current_dir = Path(__file__).parent
    preview_path = current_dir / "dataease_preview.html"
    
    if preview_path.exists():
        # 转换为文件URL
        preview_url = preview_path.as_uri()
        print(f"🌐 打开预览页面: {preview_url}")
        webbrowser.open(preview_url)
        return True
    else:
        print(f"❌ 找不到预览页面: {preview_path}")
        return False

def export_config():
    """导出DataEase配置"""
    try:
        from dataease_export import main as export_main
        print("\n📊 导出DataEase配置...")
        export_main()
        return True
    except Exception as e:
        print(f"⚠️  配置导出失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("📊 OpenDigger可视化平台启动器")
    print("=" * 60)
    
    # 检查必要文件
    required_files = [
        "dataease_config.py",
        "dataease_preview.html", 
        "dataease_export.py"
    ]
    
    current_dir = Path(__file__).parent
    for file in required_files:
        if not (current_dir / file).exists():
            print(f"❌ 找不到必要文件: {file}")
            return
    
    print("✅ 所有必要文件存在")
    
    # 导出配置
    export_config()
    
    # 检查API服务器
    print("\n🔍 检查API服务器状态...")
    if check_api_server():
        print("✅ API服务器已在运行")
        api_process = None
    else:
        api_process = start_api_server()
        if not api_process:
            print("❌ API服务器启动失败")
            return
    
    # 打开预览页面
    print("\n🖥️  打开可视化预览...")
    if not open_preview_page():
        print("❌ 无法打开预览页面")
        if api_process:
            api_process.terminate()
        return
    
    print("\n" + "=" * 60)
    print("🎉 可视化平台启动成功！")
    print("=" * 60)
    print("\n访问以下地址：")
    print("1. 预览页面: file://" + str(current_dir / "dataease_preview.html"))
    print("2. API服务器: http://localhost:5000")
    print("3. API文档: http://localhost:5000/api/docs")
    print("\n按 Ctrl+C 停止所有服务")
    print("=" * 60)
    
    try:
        # 保持程序运行
        if api_process:
            api_process.wait()
        else:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 正在停止服务...")
        if api_process:
            api_process.terminate()
        print("✅ 服务已停止")

if __name__ == "__main__":
    main()