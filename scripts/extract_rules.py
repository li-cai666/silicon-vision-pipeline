#!/usr/bin/env python3
"""从 wechat-op-rules.md 抽取高频审查条款，生成精简切片 wechat-review-slice.md。

用法：
    python scripts/extract_rules.py                 # 默认条款集，输出到 assets/rules/
    python scripts/extract_rules.py --clauses 4.9,4.11 --max-lines 12

设计目的：合规审查每次读 31.4KB 全文要 ~19k tokens，实际只对照十来个条款。
切片文件约 2-4KB（~1.5k tokens），省 ~17k。条款末尾附行号索引，
有争议时用 sed -n 'A,Bp' 回查全文，不必整读。
"""
import argparse
import io
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FULL = os.path.join(BASE, 'assets', 'rules', 'wechat-op-rules.md')
OUT = os.path.join(BASE, 'assets', 'rules', 'wechat-review-slice.md')

DEFAULT_CLAUSES = [
    '3.3', '3.12', '3.27', '3.28',
    '4.1', '4.8', '4.9', '4.11', '4.15', '4.20', '4.21', '4.24',
]


def parse_sections(lines):
    """返回 [(clause_no, title, start_line(0-based), end_line)]"""
    heads = []
    for i, line in enumerate(lines):
        m = re.match(r'^#{2,4}\s+(\d+\.\d+)\s+(.*)', line)
        if m:
            heads.append((m.group(1), m.group(2).strip(), i))
    sections = []
    for idx, (no, title, start) in enumerate(heads):
        end = heads[idx + 1][2] if idx + 1 < len(heads) else len(lines)
        sections.append((no, title, start, end))
    return sections


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--clauses', default=','.join(DEFAULT_CLAUSES))
    ap.add_argument('--max-lines', type=int, default=6,
                    help='单条款最多保留行数，超出截断并提示回查全文')
    ap.add_argument('--out', default=OUT)
    args = ap.parse_args()

    wanted = [c.strip() for c in args.clauses.split(',') if c.strip()]
    lines = io.open(FULL, encoding='utf-8').read().split('\n')
    sections = {no: (title, s, e) for no, title, s, e in parse_sections(lines)}
    by_chapter = {}
    for no, title, s, e in parse_sections(lines):
        by_chapter.setdefault(no, (title, s, e))

    buf = [
        '# 微信运营规范 · 审查精简切片',
        '',
        '> 由 `scripts/extract_rules.py` 从 `wechat-op-rules.md` 自动抽取，勿手工编辑。',
        '> 条目后标注 `全文行号 A-B`，需要完整原文时用 `sed -n "A,Bp" assets/rules/wechat-op-rules.md` 回查。',
        '> 切片未覆盖的条款（1/2/5/6/7/8/9 章及 3、4 章其余条款）默认不审查；',
        '> 若文章涉及注册、认证、数据使用、支付、商标等场景，再按行号回查对应章节。',
        '',
    ]

    chapters = [('3', '微信公众账号行为规范'), ('4', '公众号和服务号发送内容规范')]
    for ch, ch_title in chapters:
        buf.append('## 第 %s 章 %s' % (ch, ch_title))
        buf.append('')
        for no in wanted:
            if not no.startswith(ch + '.'):
                continue
            if no not in by_chapter:
                buf.append('### %s（未在全文定位到，需回查）' % no)
                buf.append('')
                continue
            title, s, e = by_chapter[no]
            body = [ln for ln in lines[s + 1:e] if ln.strip()]
            truncated = len(body) > args.max_lines
            body = body[:args.max_lines]
            buf.append('### %s %s' % (no, title))
            buf.append('')
            for ln in body:
                buf.append(ln.strip())
            if truncated:
                buf.append('')
                buf.append('（节选，全文行号 %d-%d，完整原文用 sed 回查）' % (s + 1, e))
            buf.append('')

    io.open(args.out, 'w', encoding='utf-8').write('\n'.join(buf))
    size = os.path.getsize(args.out)
    cn = len(re.findall(r'[\u4e00-\u9fff]', '\n'.join(buf)))
    print('written %s  %d bytes, %d 汉字, ~%d tokens'
          % (args.out, size, cn, int(cn / 1.4)))


if __name__ == '__main__':
    main()
