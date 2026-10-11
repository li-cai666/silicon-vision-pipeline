# -*- coding: utf-8 -*-
"""
多平台热榜聚合脚本（零依赖，仅标准库）
覆盖：微博热搜 / B站热搜 / 抖音热点
输出：Markdown 清单，可直接喂给 gzh-design / 小红书卡片技能
用法：python hotlist.py [条数]
"""
import json
import sys
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10


def get(url, referer=None):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Referer": referer or "",
        "Accept": "application/json, text/plain, */*",
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))


def weibo(n):
    d = get("https://weibo.com/ajax/side/hotSearch", "https://weibo.com/")
    items = d["data"]["realtime"]
    out = []
    for it in items[:n]:
        word = it.get("word", "").strip("#")
        out.append(f"- {word}（热度 {it.get('num', 0)}）")
    return out


def bilibili(n):
    d = get("https://api.bilibili.com/x/web-interface/search/square?limit=30",
            "https://www.bilibili.com/")
    items = d["data"]["trending"]["list"]
    out = []
    for it in items[:n]:
        out.append(f"- {it.get('show_name', it.get('keyword', ''))}（热度 {it.get('heat_score', 0)}）")
    return out


def douyin(n):
    d = get("https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/")
    items = d.get("word_list", [])
    out = []
    for it in items[:n]:
        out.append(f"- {it.get('word', '')}（热度 {it.get('hot_value', 0)}）")
    return out


def main():
    sections = [
        ("微博热搜", weibo),
        ("B站热搜", bilibili),
        ("抖音热点", douyin),
    ]
    lines = ["# 今日多平台热榜\n"]
    for name, fn in sections:
        lines.append(f"\n## {name}")
        try:
            rows = fn(N)
            if not rows:
                lines.append("- （暂无数据）")
            else:
                lines.extend(rows)
        except Exception as e:
            lines.append(f"- （抓取失败：{type(e).__name__}）")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
