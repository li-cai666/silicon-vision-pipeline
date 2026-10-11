# -*- coding: utf-8 -*-
"""
网页文章图片抓取下载脚本（零依赖，仅标准库）
用途：给定一个文章 URL，自动解析网页中的图片（含懒加载 data-original / data-src），
      筛选出高清大图并下载到本地。

用法：
    python grab_img.py <文章URL> [输出目录] [最小宽度]

示例：
    python grab_img.py "https://www.ithome.com/0/123/456.htm" ./images 600

说明：
    - 只下载 jpg/jpeg/png/webp/gif 等常见图片格式
    - 跳过 data: URI、base64、空地址
    - 自动把 //img.xxx 补全为 https://
    - 按文件名去重
"""
import os
import re
import sys
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

# 常见图片扩展名
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".avif")


def fetch_html(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": url,
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="ignore")


def extract_image_urls(html, page_url):
    """从 HTML 中提取图片 URL，优先 data-original/data-src（懒加载），其次 src。"""
    urls = []
    # 1) 懒加载属性
    for attr in ("data-original", "data-src", "data-lazy-src", "data-url"):
        urls += re.findall(attr + r'=["\']([^"\']+)["\']', html, re.I)
    # 2) 标准 img src
    urls += re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.I)

    seen, result = set(), []
    for u in urls:
        u = u.strip()
        if not u or u.startswith("data:") or u.startswith("#"):
            continue
        # 补全协议相对路径
        if u.startswith("//"):
            u = "https:" + u
        elif u.startswith("/"):
            from urllib.parse import urlparse
            p = urlparse(page_url)
            u = f"{p.scheme}://{p.netloc}{u}"
        # 只保留图片
        base = u.split("?")[0].lower()
        if not base.endswith(IMG_EXT):
            continue
        if u not in seen:
            seen.add(u)
            result.append(u)
    return result


def download(url, outdir):
    name = os.path.basename(url.split("?")[0])
    if not name or len(name) > 80:
        name = "img_" + str(abs(hash(url)))[:8] + ".jpg"
    path = os.path.join(outdir, name)
    if os.path.exists(path):
        return None, "skip"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": url})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read()
    with open(path, "wb") as f:
        f.write(data)
    return path, len(data)


def main():
    if len(sys.argv) < 2:
        print("用法: python grab_img.py <文章URL> [输出目录] [最小尺寸字节]")
        sys.exit(1)
    url = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else "./images"
    min_bytes = int(sys.argv[3]) if len(sys.argv) > 3 else 20000  # 默认过滤小于20KB的小图

    os.makedirs(outdir, exist_ok=True)
    print(f"[*] 抓取页面: {url}")
    html = fetch_html(url)
    urls = extract_image_urls(html, url)
    print(f"[*] 发现图片候选: {len(urls)} 个")

    if not urls:
        print("[!] 未发现图片，可能页面是 JS 动态渲染，需要浏览器工具")
        sys.exit(0)

    ok = 0
    for u in urls:
        try:
            path, size = download(u, outdir)
            if path is None and size == "skip":
                print(f"  - 已存在: {os.path.basename(u)}")
                ok += 1
                continue
            if size < min_bytes:
                os.remove(path)
                print(f"  - 跳过(小图 {size}B): {os.path.basename(u)}")
                continue
            print(f"  + 下载 {size//1024}KB -> {path}")
            ok += 1
        except Exception as e:
            print(f"  x 失败 {os.path.basename(u)}: {type(e).__name__}")

    print(f"\n[完成] 成功 {ok}/{len(urls)} 张，保存目录: {os.path.abspath(outdir)}")


if __name__ == "__main__":
    main()
