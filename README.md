# GitHub AI Coding 趋势归档

> 纯静态、零服务器的 AI Coding 仓库 Star 趋势看板。
> Python 每日抓取数据 → 归档为 JSON → GitHub Pages 展示排行榜与 7 天趋势图。

---

## 目录

- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [维护仓库列表](#维护仓库列表)
- [本地调试](#本地调试)
- [GitHub Actions 配置](#github-actions-配置)
- [GitHub Pages 配置](#github-pages-配置)
- [数据格式说明](#数据格式说明)
- [常见问题](#常见问题)

---

## 项目结构

```
.
├── .github/
│   └── workflows/
│       └── update.yml        # 每日定时抓取任务
├── data/
│   └── repos.json            # 手动维护的仓库列表
├── docs/                     # GitHub Pages 根目录
│   ├── data/
│   │   ├── archive.json      # 每日累积归档（自动生成）
│   │   └── today.json        # 当日排行榜（自动生成）
│   ├── index.html            # 静态前端页面
│   └── style.css             # 样式
├── scripts/
│   └── fetch.py              # 数据抓取脚本
└── README.md
```

---

## 快速开始

### 1. Fork / Clone 仓库

```bash
git clone https://github.com/<你的用户名>/ai-coding-trends.git
cd ai-coding-trends
```

### 2. 开启 Actions 写权限

> **必须先做这一步，否则 Actions 无法提交数据文件。**

1. 进入仓库页面 → **Settings** → **Actions** → **General**
2. 在 **Workflow permissions** 部分选择 **Read and write permissions**
3. 点击 **Save**

### 3. 启用 GitHub Pages

1. 进入仓库页面 → **Settings** → **Pages**
2. **Source** 选择 `Deploy from a branch`
3. **Branch** 选 `main`，目录选 `/docs`
4. 点击 **Save**
5. 等待约 1 分钟，访问 `https://<你的用户名>.github.io/<仓库名>/` 即可看到页面

### 4. 手动触发首次抓取

1. 进入仓库页面 → **Actions** → 左侧选 **Daily Fetch**
2. 点击右侧 **Run workflow** → **Run workflow**
3. 等待约 30 秒执行完毕，`data/today.json` 和 `data/archive.json` 会自动提交到仓库
4. 刷新 GitHub Pages 页面，即可看到数据

---

## 维护仓库列表

编辑 `data/repos.json`，格式如下：

```json
[
  {
    "full_name": "owner/repo",
    "description": "仓库描述"
  }
]
```

**注意事项：**
- 仓库必须是 **公开** 仓库，私有仓库无法通过 API 获取 Star 数
- 建议维护 10～15 个仓库，过多会增加 API 调用次数
- 修改后提交推送，下一次定时任务会自动使用新列表

---

## 本地调试

### 环境要求

- Python 3.9+
- `requests` 库

### 安装依赖

```bash
pip install requests
```

### 运行抓取脚本

```bash
# 在项目根目录下执行
python scripts/fetch.py
```

脚本执行完毕后会在 `data/` 目录下生成/更新 `archive.json` 和 `today.json`。

### 本地预览前端

直接用浏览器打开 `docs/index.html` **无法**加载数据（浏览器跨域限制），需启动一个本地 HTTP 服务器：

```bash
# Python 内置服务器，在项目根目录执行
python -m http.server 8080
```

然后访问 `http://localhost:8080/docs/`。

### 使用 GitHub Token（可选，推荐）

未鉴权时 GitHub API 限速为 **60 次/小时**，14 个仓库一次消耗 14 次，正常情况足够。  
若想提升限速至 5000 次/小时，可设置环境变量：

```bash
# Linux / macOS
export GITHUB_TOKEN=ghp_xxxx
python scripts/fetch.py

# Windows PowerShell
$env:GITHUB_TOKEN = "ghp_xxxx"
python scripts/fetch.py
```

---

## GitHub Actions 配置

`.github/workflows/update.yml` 已预配置好以下内容：

| 配置项 | 值 |
|---|---|
| 触发时间 | 每天 UTC 00:00（北京时间 08:00） |
| 手动触发 | 支持（`workflow_dispatch`） |
| Python 版本 | 3.12 |
| 权限 | `contents: write`（提交数据文件） |

Actions 使用仓库内置的 `GITHUB_TOKEN`，**无需额外配置 Secrets**。

---

## GitHub Pages 配置

| 配置项 | 值 |
|---|---|
| Source | `main` 分支 |
| 目录 | `/docs` |
| 访问地址 | `https://<用户名>.github.io/<仓库名>/` |

前端页面通过相对路径 `../data/today.json` 和 `../data/archive.json` 读取数据，无需任何构建步骤。

---

## 数据格式说明

### `data/repos.json`（手动维护）

追踪的仓库列表：

```json
[
  {"full_name": "continuedev/continue", "description": "AI code assistant"}
]
```

### `data/archive.json`（自动生成）

每日累积归档，按日期升序排列：

```json
[
  {
    "date": "2026-04-24",
    "repos": {
      "continuedev/continue": 18500,
      "tabbyml/tabby": 29000
    }
  }
]
```

### `data/today.json`（自动生成）

当日排行榜，含今日新增 Star 数，按新增降序排列：

```json
{
  "date": "2026-04-24",
  "repos": [
    {
      "full_name": "continuedev/continue",
      "description": "AI code assistant",
      "stars": 18500,
      "delta": 120
    }
  ]
}
```

`delta` 为 `null` 表示没有昨日数据（如首次运行），`-1` 表示仓库不存在或已私有。

---

## 常见问题

**Q: Actions 运行成功但数据没有推送到仓库？**  
A: 检查 Settings → Actions → General → Workflow permissions 是否已选择 **Read and write permissions**。

**Q: 页面显示"数据加载失败"？**  
A: `today.json` 尚未生成。请先手动触发一次 Actions，或本地运行 `python scripts/fetch.py` 后提交。

**Q: 某个仓库显示 `—`（delta 为空）？**  
A: 归档中该仓库只有一天数据，第二天起即可正常显示新增。

**Q: GitHub API 提示 rate limit？**  
A: 未鉴权时限速 60 次/小时。Actions 已自动传入 `GITHUB_TOKEN`（5000 次/小时），正常不会触发。本地调试时可手动设置 `GITHUB_TOKEN` 环境变量。

**Q: 如何增加/删除追踪的仓库？**  
A: 编辑 `data/repos.json`，提交推送后下次 Actions 运行时自动生效。

---

## 系统边界

**v1.0 做的事：**
- 追踪预先选定的 10~15 个 AI Coding 仓库
- 每日自动抓取并归档 Star 数
- 展示当日 Star 排行榜 + 近 7 天趋势折线图

**v1.0 不做的事：**
- 不做用户登录、收藏、评论
- 不自动发现新仓库（手动维护列表）
- 不使用后端数据库
- 不做移动端适配
- 不展示 commit / 贡献者等额外维度
