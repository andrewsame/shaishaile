# shaishaile



# Dataease 部分
使用步骤

## 1. 启动可视化平台
运行以下命令：

进入可视化目录

cd src/visualization

启动可视化平台

python start_visualization.py

## 2. 手动操作步骤
如果自动启动失败，可以手动操作：
第一步：启动API服务器

cd src/api

python app.py

第二步：在浏览器中打开预览页面

直接打开 src/visualization/dataease_preview.html

## 3. DataEase平台导入配置
登录DataEase平台
进入"数据源" -> "API数据源"
点击"导入配置"
选择 data/exports/dataease_config.json
按照使用指南配置

效果预览
打开 dataease_preview.html 可以看到一个完整的仪表板界面

在搜索框中输入仓库信息（如：X-lab2018/open-digger）

点击"开始分析"按钮

页面会显示：

核心指标卡片

雷达图（模拟）

趋势图（模拟）

对比表格

文件说明：

src/visualization/

├── dataease_config.py           # DataEase配置文件（主要）

├── dataease_preview.html        # 预览页面（HTML）

├── dataease_export.py          # 配置导出工具

├── start_visualization.py      # 启动脚本

└── __init__.py                 # 模块初始化
