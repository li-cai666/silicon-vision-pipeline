#!/usr/bin/env python3
"""卡片/配图 QA 助手：把多张 PNG 拼成一张 contact sheet，一次看完，省逐张读图的 token。

1080x1440 的卡片单张约 1.5-2k tokens，逐张 Read 7 张 ≈ 12k；
拼成一张 1600px 宽的 sheet 只要一次 Read（约 1.5-2k）。

用法：
    python scripts/make_contact_sheet.py <图片目录> [-o sheet.jpg] [--cols 3] [--width 1600]
    python scripts/make_contact_sheet.py <图片目录> --density   # 只报内容覆盖率，不拼图

--density：估算每张图的**垂直填充率**（内容块占画布高度的比例）。
小红书 3:4 卡要求内容覆盖 >= 75% 画布高，意思是内容要从顶部铺到底部，
不能在下半截留一大片空白。判定方法：缩略后逐行扫描，找出有内容像素的
首行与末行，跨度 / 总高 = 填充率；同时报顶部/底部空隙，方便定位空白在哪。

注意别用"非背景像素占比"当指标——白底黑字的卡片文字像素只占 10-30%，
会全部误判为内容不足，但那其实只是留白多的正常版式。
"""
import argparse
import io
import os
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit('[contact_sheet] 需要 Pillow: pip install Pillow')

EXTS = ('.png', '.jpg', '.jpeg', '.webp')


def list_images(d):
    fs = [f for f in os.listdir(d) if f.lower().endswith(EXTS)]
    # 自然排序，保证 xhs-01/02/... 顺序
    fs.sort()
    return [os.path.join(d, f) for f in fs]


def vertical_fill(path, thresh=25, rows=240):
    """返回 (填充率, 顶部空隙, 底部空隙)，都是 0-1 的比例。

    逐行扫描缩略图，某行只要有一个像素明显偏离背景色就算"有内容"。
    """
    im = Image.open(path).convert('RGB')
    w, h = im.size
    corners = [im.getpixel(p) for p in
               ((2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3))]
    bg = tuple(sum(c[i] for c in corners) // 4 for i in range(3))
    small = im.resize((160, rows), Image.LANCZOS)
    px = small.load()
    filled = []
    for y in range(rows):
        hit = False
        for x in range(160):
            p = px[x, y]
            if (abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2])) > thresh:
                hit = True
                break
        filled.append(hit)
    idx = [i for i, v in enumerate(filled) if v]
    if not idx:
        return 0.0, 1.0, 1.0
    first, last = idx[0], idx[-1]
    fill = (last - first + 1) / rows
    return fill, first / rows, (rows - 1 - last) / rows


def make_sheet(paths, out, cols=3, width=1600, cell_h=560, label=True):
    n = len(paths)
    rows = (n + cols - 1) // cols
    cell_w = width // cols
    sheet = Image.new('RGB', (cell_w * cols, cell_h * rows), (245, 245, 245))
    draw = ImageDraw.Draw(sheet)
    for i, p in enumerate(paths):
        im = Image.open(p).convert('RGB')
        im.thumbnail((cell_w - 20, cell_h - 30), Image.LANCZOS)
        x = (i % cols) * cell_w + (cell_w - im.width) // 2
        y = (i // cols) * cell_h + 24
        sheet.paste(im, (x, y))
        if label:
            draw.text(((i % cols) * cell_w + 8, (i // cols) * cell_h + 6),
                      os.path.basename(p), fill=(60, 60, 60))
    sheet.save(out, 'JPEG', quality=80, optimize=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dir')
    ap.add_argument('-o', '--out', default='contact-sheet.jpg')
    ap.add_argument('--cols', type=int, default=3)
    ap.add_argument('--width', type=int, default=1600)
    ap.add_argument('--density', action='store_true', help='只报内容覆盖率')
    ap.add_argument('--min-ratio', type=float, default=0.75,
                    help='3:4 卡内容覆盖率下限，低于此值标 LOW')
    args = ap.parse_args()

    paths = list_images(args.dir)
    if not paths:
        sys.exit('[contact_sheet] 目录里没有图片: ' + args.dir)

    if args.density:
        print('%-28s %8s %8s %8s  %s' % ('文件', '填充率', '顶空隙', '底空隙', '判定'))
        low = 0
        for p in paths:
            fill, top, bottom = vertical_fill(p)
            bad = fill < args.min_ratio or bottom > 0.12
            if bad:
                low += 1
            print('%-28s %7.1f%% %7.1f%% %7.1f%%  %s'
                  % (os.path.basename(p), fill * 100, top * 100, bottom * 100,
                     'LOW' if bad else 'OK'))
        print('\n%d 张，%d 张需要补内容（填充率 < %.0f%% 或底部空隙 > 12%%）'
              % (len(paths), low, args.min_ratio * 100))
        return

    make_sheet(paths, args.out, args.cols, args.width)
    print('[contact_sheet] %d 张 -> %s  (%d KB)'
          % (len(paths), args.out, os.path.getsize(args.out) // 1024))
    print('一次 Read 这张 sheet 即可完成 QA；发现问题的单张再单独 Read。')


if __name__ == '__main__':
    main()
