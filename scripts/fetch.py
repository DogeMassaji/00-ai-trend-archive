#!/usr/bin/env python3
"""
fetch.py — 每日抓取 AI Coding 仓库 Star 数并归档
"""

import json
import os
import sys
from datetime import datetime, timezone

import requests

REPOS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "repos.json")
ARCHIVE_FILE = os.path.join(os.path.dirname(__file__), "..", "docs", "data", "archive.json")
TODAY_FILE = os.path.join(os.path.dirname(__file__), "..", "docs", "data", "today.json")

GITHUB_API = "https://api.github.com/repos/{}"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

# 若环境变量中有 GITHUB_TOKEN 则使用，避免未鉴权时的 60 次/小时限制
_token = os.environ.get("GITHUB_TOKEN", "")
if _token:
    HEADERS["Authorization"] = f"Bearer {_token}"


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def fetch_stars(full_name: str) -> int:
    url = GITHUB_API.format(full_name)
    resp = requests.get(url, headers=HEADERS, timeout=15)
    if resp.status_code == 404:
        print(f"  [WARN] 仓库不存在或已私有: {full_name}", file=sys.stderr)
        return -1
    resp.raise_for_status()
    return resp.json()["stargazers_count"]


def main() -> None:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"[fetch] 开始抓取，日期={today}")

    repos: list[dict] = load_json(REPOS_FILE)
    archive: list[dict] = load_json(ARCHIVE_FILE)

    # 抓取今日数据
    today_stars: dict[str, int] = {}
    for repo in repos:
        full_name = repo["full_name"]
        try:
            stars = fetch_stars(full_name)
            today_stars[full_name] = stars
            print(f"  {full_name}: {stars:,} stars")
        except requests.HTTPError as exc:
            print(f"  [ERROR] {full_name}: {exc}", file=sys.stderr)
            today_stars[full_name] = -1

    # 去重：若今日记录已存在则覆盖（幂等）
    archive = [rec for rec in archive if rec.get("date") != today]
    archive.append({"date": today, "repos": today_stars})
    archive.sort(key=lambda r: r["date"])

    # 找到昨日数据以计算新增
    yesterday_stars: dict[str, int] = {}
    if len(archive) >= 2:
        yesterday_stars = archive[-2]["repos"]

    # 构造今日排行榜
    today_list = []
    for repo in repos:
        full_name = repo["full_name"]
        stars = today_stars.get(full_name, -1)
        prev = yesterday_stars.get(full_name, -1)
        delta = (stars - prev) if (stars >= 0 and prev >= 0) else None
        today_list.append(
            {
                "full_name": full_name,
                "description": repo.get("description", ""),
                "stars": stars,
                "delta": delta,
            }
        )

    # 按今日新增降序，若无新增数据则按总 Star 降序
    today_list.sort(
        key=lambda r: (r["delta"] is not None, r["delta"] or 0, r["stars"]),
        reverse=True,
    )

    today_output = {"date": today, "repos": today_list}

    save_json(ARCHIVE_FILE, archive)
    save_json(TODAY_FILE, today_output)
    print(f"[fetch] 完成，已写入 archive.json 和 today.json")


if __name__ == "__main__":
    main()
