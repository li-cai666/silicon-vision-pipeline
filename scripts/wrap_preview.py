# -*- coding: utf-8 -*-
"""给公众号排版终版 HTML套一层带复制按钮的预览页（SKILL.md 提到的 wrap_preview.py 实际不存在）。"""
import io, sys, webbrowser

src, out = sys.argv[1], sys.argv[2]
body = io.open(src, encoding='utf-8').read()

page = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>公众号排版预览</title>
<style>
  *{box-sizing:border-box}
  body{margin:0;background:#f0f0ef;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif}
  .bar{position:sticky;top:0;z-index:99;background:#1a1a1a;color:#fff;padding:12px 16px;display:flex;
       align-items:center;gap:14px;justify-content:space-between;box-shadow:0 2px 8px rgba(0,0,0,.2)}
  .bar b{font-size:14px;font-weight:600;letter-spacing:.5px}
  .bar .meta{font-size:11px;color:#9ca3af}
  button{background:#059669;color:#fff;border:0;border-radius:4px;padding:9px 20px;font-size:13px;
         font-weight:700;cursor:pointer;letter-spacing:1px}
  button:active{background:#047857}
  .tip{background:#fffbeb;color:#92400e;font-size:12px;padding:9px 16px;border-bottom:1px solid #fde68a;line-height:1.6}
  .wrap{padding:20px 12px 60px}
  #art{background:#fff;max-width:677px;margin:0 auto;padding:0 0 24px}
</style>
</head>
<body>
  <div class="bar">
    <div>
      <b>公众号排版预览 · 摸鱼票据风</b>
      <div class="meta">正文 16px · 无 justify · 图片已base64 内嵌 · 粘贴前请先清空编辑器旧内容</div>
    </div>
    <button onclick="copyArt()">复制正文</button>
  </div>
  <div class="tip">复制后到公众号编辑器粘贴。若图片不显示，先点「复制正文」，再在编辑器里手动粘贴一次以触发图片上传。</div>
  <div class="wrap"><div id="art">__BODY__</div></div>
<script>
function copyArt(){
  const el=document.getElementById('art');
  const r=document.createRange();r.selectNodeContents(el);
  const s=getSelection();s.removeAllRanges();s.addRange(r);
  let ok=false;
  try{ok=document.execCommand('copy');}catch(e){}
  if(!ok && navigator.clipboard){navigator.clipboard.writeText(el.innerText);}
  const b=event.target,o=b.textContent;
  b.textContent=ok?'已复制 ✓':'请手动复制';
  setTimeout(()=>b.textContent=o,1600);
}
</script>
</body>
</html>
'''

io.open(out, 'w', encoding='utf-8').write(page.replace('__BODY__', body))
print('[wrap_preview] ->', out)
webbrowser.open('file:///' + out.replace('\\\\', '/'))
