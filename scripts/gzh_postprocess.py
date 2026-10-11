#!/usr/bin/env python3
"""公众号排版 HTML 后处理：一键把 gzh-design 组件库输出改成木子的发布标准。

做四件事（都能单独关掉）：
  1. text-align:justify -> left      （微信检测器白名单只认 left/center/right）
  2. 正文字号提到 15/16px            （组件库默认 14px，木子要求字大）
  3. 大留白收紧                      （木子不要松松垮垮的版式）
  4. 图片压到 1080px JPEG 后 base64 内嵌（相对路径在预览和公众号粘贴后都不显示）

用法：
    python scripts/gzh_postprocess.py <模板.html> [-o 输出.html] [--assets 图片目录] [--body 16]
    python scripts/gzh_postprocess.py 模板.html --no-img      # 只改样式，不处理图片
    python scripts/gzh_postprocess.py 模板.html --no-spacing   # 不动间距

模板里图片用 {{IMG:文件名(不含扩展)}} 占位，或 src="assets/xxx.png" 相对路径，都会被替换。
图片缓存默认落在模板同目录 .gzh_img_cache/，重跑不重复压缩。

校验（失败 exit 1）：无 justify 残留、无 {{IMG:}} 残留、无相对路径 src。
"""
import argparse
import base64
import io
import os
import re
import sys

# 常见大留白值 -> 紧凑值（精确匹配优先，数值来自实测调过的版式）
SPACING_MAP = [
    ('margin-bottom: 26px', 'margin-bottom: 18px'),
    ('margin: 8px 16px 32px', 'margin: 4px 16px 18px'),
    ('margin: 0 16px 10px', 'margin: 0 16px 6px'),
    ('margin-top: 64px', 'margin-top: 40px'),
    ('margin: 40px 16px', 'margin: 28px 16px'),
    ('margin: 32px 16px 48px', 'margin: 24px 16px 32px'),
    ('padding: 36px 20px', 'padding: 28px 20px'),
    ('padding: 40px 24px', 'padding: 32px 24px'),
]

# 通用 clamp：(正则, 触发阈值, 压到几px)。只压明显过大的值，避免误伤已经紧凑的地方
CLAMPS = [
    (r'margin-bottom:\s*(\d+)px', 24, 18),
    (r'margin-top:\s*(\d+)px', 48, 40),
    (r'padding-bottom:\s*(\d+)px', 40, 32),
    (r'padding-top:\s*(\d+)px', 40, 32),
]

# 这些是小字标注（脚注/角标/元信息/编号），字号不动
PROTECT = re.compile(
    r'caption|foot|meta|note|badge|tag-|label|cell-nb|t-cat|t-meta|\bnum', re.I)

MIME = {b'\xff\xd8': 'image/jpeg', b'\x89PNG': 'image/png',
        b'GIF8': 'image/gif', b'RIFF': 'image/webp'}


def data_uri(path, cache_dir, max_width=1080, quality=82):
    """读图 -> 压到 max_width 的 JPEG -> base64 data URI，带缓存。"""
    name = os.path.splitext(os.path.basename(path))[0]
    os.makedirs(cache_dir, exist_ok=True)
    cached = os.path.join(cache_dir, name + '.jpg')
    if not os.path.exists(cached):
        raw = open(path, 'rb').read()
        try:
            from PIL import Image
            im = Image.open(io.BytesIO(raw))
            if im.mode in ('RGBA', 'P'):
                im = im.convert('RGB')
            w, h = im.size
            if w > max_width:
                im = im.resize((max_width, int(h * max_width / w)), Image.LANCZOS)
            im.save(cached, 'JPEG', quality=quality, optimize=True)
        except ImportError:
            # 没装 Pillow 就原样内嵌，不压缩
            open(cached, 'wb').write(raw)
    raw = open(cached, 'rb').read()
    mime = 'image/jpeg'
    for sig, m in MIME.items():
        if raw.startswith(sig):
            mime = m
            break
    return 'data:%s;base64,%s' % (mime, base64.b64encode(raw).decode())


def fix_align(html):
    html, n = re.subn(r'text-align:\s*justify', 'text-align:left', html)
    return html, n


def fix_font(html, body=16, min_body=15):
    """把正文 14px 提到 body；小字标注行跳过。"""
    out = []
    changed = 0
    for line in html.split('\n'):
        if re.search(r'font-size:\s*14px', line) and not PROTECT.search(line):
            line = re.sub(r'font-size:\s*14px', 'font-size:%dpx' % body, line)
            changed += 1
        out.append(line)
    return '\n'.join(out), changed


def fix_spacing(html):
    n = 0
    for old, new in SPACING_MAP:
        c = html.count(old)
        if c:
            html = html.replace(old, new)
            n += c
    hits = [0]
    for pattern, trigger, target in CLAMPS:
        def repl(m):
            v = int(m.group(1))
            if v <= trigger:
                return m.group(0)
            hits[0] += 1
            return m.group(0).replace('%dpx' % v, '%dpx' % target)
        html = re.sub(pattern, repl, html)
    return html, n + hits[0]


def inject_images(html, assets_dir, cache_dir):
    """替换 {{IMG:name}} 占位和 src="...相对路径"。"""
    n = 0

    def repl_placeholder(m):
        nonlocal n
        name = m.group(1)
        path = None
        for ext in ('.png', '.jpg', '.jpeg', '.webp'):
            p = os.path.join(assets_dir, name + ext)
            if os.path.exists(p):
                path = p
                break
        if not path:
            raise SystemExit('[gzh_postprocess] 找不到图片: %s (%s)' % (name, assets_dir))
        n += 1
        return data_uri(path, cache_dir)

    html = re.sub(r'\{\{IMG:([^}]+)\}\}', repl_placeholder, html)

    def repl_src(m):
        nonlocal n
        src = m.group(1)
        if src.startswith(('http', 'data:')):
            return m.group(0)
        path = os.path.join(assets_dir, os.path.basename(src))
        if not os.path.exists(path):
            return m.group(0)
        n += 1
        return 'src="%s"' % data_uri(path, cache_dir)

    html = re.sub(r'src="([^"]+)"', repl_src, html)
    return html, n


def verify(html, check_img=True):
    errs = []
    if re.search(r'text-align:\s*justify', html):
        errs.append('仍有 text-align:justify')
    if not check_img:
        return errs
    if '{{IMG:' in html:
        errs.append('仍有未替换的 {{IMG:}} 占位')
    for m in re.finditer(r'src="([^"]+)"', html):
        s = m.group(1)
        if s.startswith(('data:', 'http', '{{')):
            continue
        errs.append('仍有相对路径图片: ' + s[:60])
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('html')
    ap.add_argument('-o', '--out')
    ap.add_argument('--assets', help='图片目录，默认 html 同级的 assets/')
    ap.add_argument('--body', type=int, default=16, help='正文字号，15 或 16')
    ap.add_argument('--no-img', action='store_true')
    ap.add_argument('--no-spacing', action='store_true')
    ap.add_argument('--no-font', action='store_true')
    args = ap.parse_args()

    src = args.html
    html = io.open(src, encoding='utf-8').read()
    base = os.path.dirname(os.path.abspath(src))
    assets = args.assets or os.path.join(base, 'assets')
    cache = os.path.join(base, '.gzh_img_cache')

    html, align_n = fix_align(html)
    font_n = 0
    if not args.no_font:
        html, font_n = fix_font(html, args.body)
    space_n = 0
    if not args.no_spacing:
        html, space_n = fix_spacing(html)
    img_n = 0
    if not args.no_img:
        html, img_n = inject_images(html, assets, cache)

    errs = verify(html, check_img=not args.no_img)
    out = args.out or (os.path.splitext(src)[0] + '_post.html')
    io.open(out, 'w', encoding='utf-8').write(html)

    print('[gzh_postprocess] -> %s' % out)
    print('  justify->left : %d 处' % align_n)
    print('  字号提升      : %d 处 -> %dpx' % (font_n, args.body))
    print('  间距收紧      : %d 处' % space_n)
    print('  图片内嵌      : %d 张' % img_n)
    print('  文件大小      : %d KB' % (os.path.getsize(out) // 1024))
    if errs:
        for e in errs:
            print('  [ERROR] ' + e)
        sys.exit(1)
    print('  校验          : PASS')


if __name__ == '__main__':
    main()
