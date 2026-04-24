# 📘 GitHub AI Coding 趋势与归档 —— 极简实战教程

## 1. 项目定位
一个**完全静态**、**零服务器成本**的小型看板，每天自动抓取一批精选 AI Coding 仓库的 Star 数，生成排行榜与历史趋势图，并以归档形式保存。全程只需 Python 脚本 + GitHub Actions + GitHub Pages，非常适合“短期快速”交付。

## 2. 系统边界（非常重要）
> 不画大饼，功能必须能在一个下午开发完毕。

### v1.0
**✅ 在边界内**
- 追踪**预先选定**的 10~15 个知名 AI Coding 开源仓库（如 `continuedev/continue`、`gpt-engineer-org/gpt-engineer` 等）
- 使用 GitHub REST API（无需鉴权即可访问公开数据）
- 每天通过 GitHub Actions 自动运行一次抓取脚本
- 抓取的数据保存为 `data/archive.json`（归档）+ 计算出当日趋势值
- 纯静态前端展示：
  - 当前 Star 数排行榜（按今日新增排序）
  - 每个仓库最近 7 天的 Star 变化曲线
- 网页部署在 GitHub Pages

**❌ 绝不做的事情**
- 不做用户登录、个性化收藏、评论
- 不做实时动态发现新的 AI Coding 仓库（手动维护仓库列表）
- 不做后端数据库（全部是 JSON 文件）
- 不处理 GitHub API 限流外的复杂异常
- 不支持移动端复杂适配（桌面优先）
- 不展示代码贡献者、commit 趋势等额外维度

### v2.0
**✅ 在边界内**
- 实时动态发现新的 AI Coding 仓库
- 使用 GitHub Actions token实现鉴权
- 纯静态前端展示：
  - 近一个月/近一周/昨天/今天 Star 数排行榜
  - 每个仓库近一个月/近一周的 Star 变化曲线
- 处理 GitHub API 限流外的复杂异常
- 不支持移动端复杂适配（桌面优先）
- 展示代码贡献者、commit 趋势等额外维度


## 3. 产品细节规格
### 3.1 数据存储格式
`data/repos.json` – 追踪仓库列表（手动维护）：
```json
[
  {"full_name": "continuedev/continue", "description": "⏩ Continue is the leading open-source AI code assistant."},
  {"full_name": "gpt-engineer-org/gpt-engineer", "description": "Specify what you want it to build, the AI asks for clarification, and then builds it."},
  ...
]
```

`data/archive.json` – 归档数据，自动生成：
```json
[
  {"date": "2026-04-23", "repos": {
    "continuedev/continue": 18500,
    "gpt-engineer-org/gpt-engineer": 54200
  }},
  ...
]
```
每天追加一条记录，文件会逐渐增大，但 10 个仓库的文本量极小，完全可控。

### 3.2 前端页面设计
**单页面应用**：
- **标题区**：GitHub AI Coding 趋势（今日日期）
- **排行榜表格**：
  - 列：排名、仓库名、描述、当前 Star 数、今日新增 Star
  - 默认按今日新增降序排列
- **趋势图弹窗/内嵌区**：
  - 点击某个仓库名，下方用折线图展示该仓库最近 7 天的 Star 增长曲线
- **颜色风格**：类 GitHub 的个性化风格

### 3.3 用户交互
- 页面加载即显示今天数据（读取预生成的 `data/today.json` 以及归档文件）
- 点击仓库行 → 使用同一归档数据动态渲染图表
- 没有其他交互，零路由。

## 4. 技术栈与工具
- **抓取脚本**：Python 3 + `requests` 库
- **定时运行**：GitHub Actions (schedule, 每日 UTC 0 点)
- **数据存储**：仓库中的 JSON 文件
- **前端展示**：纯 HTML/CSS/JS + Chart.js (CDN)
- **部署**：GitHub Pages (从 `main` 分支的 `/docs` 目录或 gh-pages 分支)

> 完全不需要购买服务器或域名，白嫖 GitHub 生态。

## 5. 开发实战步骤 (约 3～4 小时)

### 步骤 1：创建 GitHub 仓库并初始化
1. 新建公开仓库：`ai-coding-trends`
2. 克隆到本地，建立基本文件结构：
```
ai-coding-trends/
├── .github/workflows/update.yml   # GitHub Actions 配置
├── scripts/
│   └── fetch.py                   # 抓取脚本
├── data/
│   ├── repos.json                 # 手工维护的仓库列表
│   └── archive.json               # 空数组 [] 初始
├── docs/                          # 用于 Pages 的静态网站根目录
│   ├── index.html
│   └── style.css
├── README.md
```

### 步骤 2：编写抓取脚本 `scripts/fetch.py`
核心逻辑：
- 读取 `data/repos.json`
- 通过 GitHub API `GET /repos/{owner}/{repo}` 获取每一个仓库的 `stargazers_count`
- 读取 `archive.json`，追加今日日期与各仓库 Star 数
- 计算今日新增（今日 Star - 昨日 Star）
- 将今日排行榜（含新增）另存为 `data/today.json`，前端直接使用
- 写出新的 `archive.json`

### 步骤 3：配置 GitHub Actions 定时运行
创建 `.github/workflows/update.yml`：

**注意**：因为需要 Push，Actions 需要有写权限，仓库设置 -> Actions -> General -> Workflow permissions 选择 "Read and write permissions"。

### 步骤 4：编写前端页面 `docs/index.html`
略

### 步骤 5：启用 GitHub Pages
- 仓库设置 -> Pages -> Source 选择 `main` 分支，目录选 `/docs`
- 保存后几分钟即可通过 `https://你的用户名.github.io/ai-coding-trends` 访问

### 步骤 6：手动添加仓库列表
编辑 `data/repos.json`，写入 10~15 个当前热门的 AI Coding 仓库（可通过 GitHub 搜索 “ai coding assistant” 等关键词挑选）。例如：
```json
[
  {"full_name": "continuedev/continue", "description": "AI code assistant"},
  {"full_name": "gpt-engineer-org/gpt-engineer", "description": "AI that builds apps"},
  {"full_name": "tabbyml/tabby", "description": "Self-hosted AI coding assistant"},
  {"full_name": "open-interpreter/open-interpreter", "description": "Natural language interface for code"},
  {"full_name": "Pythagora-io/gpt-pilot", "description": "Dev tool that writes full apps"},
  {"full_name": "sweepai/sweep", "description": "AI junior developer"},
  {"full_name": "microsoft/autogen", "description": "Multi-agent conversation framework"},
  {"full_name": "microsoft/JARVIS", "description": "LLM-driven system (HuggingGPT)"},
  {"full_name": "Codium-ai/pr-agent", "description": "AI PR reviewer"}
]
```
提交并推送，手动在 Actions 页面触发一次 `Daily Fetch`，即可获得首次数据。

## 6. 项目交付与展示建议
- 将 README 写清楚：系统边界、数据来源、使用方法。
- 可发布到社交平台体现“极客价值”：一个完全自动化的 AI 开源趋势追踪器。
- 课程设计/竞赛答辩时重点讲：如何用无服务器架构实现日级数据归档 + 可视化，工程化边界意识。
