# DataEase下拉菜单数据对接说明

## 下拉菜单数据结构

下拉菜单使用以下JSON结构，可以将其替换为DataDigger的实际数据：

```javascript
const repositoryData = {
    // 所有者列表（数组）
    owners: ["owner1", "owner2", ...],
    
    // 按所有者分组的仓库（对象）
    reposByOwner: {
        "owner1": ["repo1", "repo2", ...],
        "owner2": ["repo3", "repo4", ...]
    },
    
    // 热门仓库（用于快速选择）
    popularRepos: [
        {owner: "owner1", repo: "repo1", language: "JavaScript", category: "web"},
        {owner: "owner2", repo: "repo2", language: "Python", category: "ai"}
    ],
    
    // 按语言分类
    languages: {
        "JavaScript": ["owner1/repo1", "owner2/repo2"],
        "Python": ["owner3/repo3", "owner4/repo4"]
    },
    
    // 按项目分类
    categories: {
        "web": ["owner1/repo1", "owner2/repo2"],
        "ai": ["owner3/repo3", "owner4/repo4"]
    }
};
```

## 如何对接您的DataDigger数据

### 方案1：直接替换数据（推荐）

在你的DataDigger数据处理完成后，将数据导出为JSON格式，然后：

1. 将 `repositoryData` 变量替换为您的实际数据
2. 确保数据结构与上述格式一致

### 方案2：通过API动态加载

修改HTML中的JavaScript部分，添加API调用：

```javascript
// 动态加载仓库数据
async function loadRepositoryData() {
    try {
        // 调用您的DataDigger API
        const response = await fetch('http://your-datadigger-api/repositories');
        const data = await response.json();
        
        // 转换为页面所需格式
        repositoryData = {
            owners: data.owners,
            reposByOwner: data.repos_by_owner,
            popularRepos: data.popular_repos,
            languages: data.languages,
            categories: data.categories
        };
        
        // 重新初始化下拉菜单
        initOwnerDropdown();
    } catch (error) {
        console.error('加载仓库数据失败:', error);
    }
}
```

### 方案3：从文件加载

将DataDigger数据保存为JSON文件，然后通过fetch加载：

```javascript
async function loadDataFromFile() {
    const response = await fetch('data/repositories.json');
    repositoryData = await response.json();
    initOwnerDropdown();
}
```

## 下拉菜单功能说明

### 1. 所有者选择器
- 显示所有仓库所有者
- 按组织类型分组显示
- 选择后自动更新仓库列表

### 2. 仓库选择器
- 根据选择的所有者显示对应仓库
- 支持语言筛选
- 支持分类筛选

### 3. 快速选择按钮
- 显示热门项目
- 一键选择和分析

### 4. 筛选功能
- 按语言筛选：JavaScript、Python、Java等
- 按分类筛选：Web框架、AI、数据库等

## 与DataEase的集成点

1. **搜索表单**：下拉菜单的选择值会自动填充到搜索表单
2. **API调用**：选择完成后点击"开始分析"，会调用OpenDigger API
3. **数据显示**：API返回的数据会更新仪表板
4. **对比功能**：自动加载同类型项目进行对比

## 测试方法

1. 打开 `dataease_preview.html`
2. 在下拉菜单中选择所有者和仓库
3. 使用筛选功能按语言或分类查找
4. 点击"开始分析"查看效果
5. 使用快速选择按钮测试热门项目

## 数据格式转换示例

如果您的DataDigger数据格式不同，可以使用以下转换函数：

```javascript
function convertDataDiggerFormat(datadiggerData) {
    return {
        owners: datadiggerData.orgs.map(org => org.name),
        reposByOwner: datadiggerData.repos.reduce((acc, repo) => {
            if (!acc[repo.owner]) acc[repo.owner] = [];
            acc[repo.owner].push(repo.name);
            return acc;
        }, {}),
        popularRepos: datadiggerData.top_repos.map(repo => ({
            owner: repo.owner,
            repo: repo.name,
            language: repo.language,
            category: repo.category
        })),
        languages: datadiggerData.by_language,
        categories: datadiggerData.by_category
    };
}
```

## 注意事项

1. **数据一致性**：确保下拉菜单数据与OpenDigger API支持的项目一致
2. **性能考虑**：如果数据量很大，考虑分页或搜索功能
3. **错误处理**：做好API调用失败的处理
4. **缓存策略**：考虑本地缓存已加载的数据
```

## 3. 如何使用

### 步骤1：打开预览页面

直接双击打开 `src/visualization/dataease_preview.html`

### 步骤2：使用下拉菜单

1. **选择所有者**：从第一个下拉菜单中选择仓库所有者（如 "X-lab2018"）
2. **选择仓库**：从第二个下拉菜单中选择仓库（如 "open-digger"）
3. **筛选功能**：
   - 使用"主要语言"下拉菜单按语言筛选
   - 使用"项目分类"下拉菜单按分类筛选
4. **快速选择**：点击下方的快速选择按钮

### 步骤3：分析数据

点击"开始分析"按钮，页面会：
1. 显示加载状态
2. 更新核心指标卡片
3. 显示对比表格
4. 更新图表区域（模拟）

### 步骤4：对接您的DataDigger数据

当您的DataDigger数据处理完成后，只需要：

1. 将您的数据转换为 `repositoryData` 格式
2. 替换HTML中第200-300行的数据定义部分
3. 或者改为从API动态加载数据

## 特点

✅ **完整的下拉菜单系统**：所有者、仓库、语言、分类四级筛选
✅ **快速选择**：热门项目一键选择
✅ **分类筛选**：按语言和项目类型筛选
✅ **模拟数据**：在没有API时也能演示效果
✅ **响应式设计**：适配不同屏幕尺寸
✅ **与DataEase兼容**：可以直接在DataEase中使用

这个下拉菜单系统完全独立，不依赖后端API，您只需要提供数据源即可。当您的DataDigger数据准备好后，只需要简单替换数据变量即可完成对接。