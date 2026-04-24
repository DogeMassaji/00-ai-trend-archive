# GitHub AI Coding 趋势归档 — Copilot 指令

## 项目简介
纯静态、零服务器的 AI Coding 仓库趋势看板。用 Python 每天抓取 Star 数，保存到 JSON，用 GitHub Pages 展示排行榜与趋势图。

## 技术栈
- **抓取**：Python 3 + `requests`
- **调度**：GitHub Actions（每日 UTC 0:00 自动运行）
- **存储**：JSON 文件（无数据库）
- **前端**：纯 HTML/CSS/JS + Chart.js（CDN）
- **部署**：GitHub Pages（`/docs` 目录）

## 文件结构
```
.github/workflows/update.yml   # 定时抓取任务
scripts/fetch.py               # 数据抓取脚本
data/repos.json                # 手动维护的仓库列表
data/archive.json              # 每日累积归档数据
data/today.json                # 当日排行榜（前端直接读取）
docs/index.html                # 静态展示页面
docs/style.css
```

## 数据格式
**`data/repos.json`**（手动维护）：
```json
[{"full_name": "owner/repo", "description": "描述"}]
```

**`data/archive.json`**（自动追加）：
```json
[{"date": "2026-04-24", "repos": {"owner/repo": 18500}}]
```

**`data/today.json`**（每日覆盖）：当日排行榜，含今日新增 Star 数。

## 核心逻辑（fetch.py）
1. 读取 `repos.json` 中的仓库列表
2. 调用 GitHub API `GET /repos/{owner}/{repo}` 获取 `stargazers_count`
3. 追加到 `archive.json`
4. 计算今日新增 = 今日 Star - 昨日 Star
5. 输出 `today.json` 供前端使用

## 前端行为
- 页面加载读取 `today.json`（排行榜）和 `archive.json`（趋势图数据）
- 点击仓库行 → 渲染该仓库近 7 天 Star 折线图
- 风格参考 GitHub，单页无路由

## 边界约定（严格遵守）
**做**：
- 追踪预设的 10~15 个仓库
- 每日自动抓取并归档
- 展示排行榜 + 7 天趋势图

**不做**：
- 不做用户登录、收藏、评论
- 不自动发现新仓库（手动维护列表）
- 不使用后端数据库
- 不做移动端适配
- 不展示 commit / 贡献者等额外维度

## GitHub Actions 注意
Actions 需要写权限：仓库设置 → Actions → General → Workflow permissions → 选择 **Read and write permissions**。
