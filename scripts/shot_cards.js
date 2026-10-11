// 通用卡片截图脚本：把社交卡片 HTML（含多个 section.poster）逐页导出为 PNG
// 依赖：puppeteer-core（装到 node workspace）+ 本机 Chrome
//
// 用法：
//   NODE_PATH="<node workspace>/node_modules" node shot_cards.js <index.html绝对路径> [输出目录] [选择器]
// 示例：
//   NODE_PATH="C:/Users/15856/.workbuddy/binaries/node/workspace/node_modules" \
//     node shot_cards.js "E:/xxx/卡片/index.html" "E:/xxx/卡片/output" "section.poster.xhs"
//
// 要点：
//   - HTML 绝对路径需 URL 编码（中文路径会出问题，见下方 encodePath）
//   - 文件名取 poster 内的 <title> 或 data-title 属性；无则按序号
//   - 竖版 3:4 默认 1080x1440；1:1 用 1080x1080（可用第 4 参数选）
const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';

function encodePath(p) {
  // 把 Windows 绝对路径转成 file:// URL 并 URL 编码（中文路径必须编码）
  p = p.replace(/\\/g, '/');
  if (!/^[a-zA-Z]:\//.test(p)) throw new Error('请传绝对路径: ' + p);
  return 'file:///' + encodeURI(p);
}

(async () => {
  const htmlPath = process.argv[2];
  const outDir = process.argv[3] || (path.dirname(htmlPath) + '/output');
  const selector = process.argv[4] || 'section.poster';
  if (!htmlPath) { console.error('用法: node shot_cards.js <html绝对路径> [输出目录] [选择器]'); process.exit(1); }

  fs.mkdirSync(outDir, { recursive: true });

  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: 'new',
    args: ['--no-sandbox', '--disable-gpu', '--force-device-scale-factor=1', '--hide-scrollbars', '--allow-file-access-from-files']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1080, height: 1440, deviceScaleFactor: 1 });
  await page.goto(encodePath(htmlPath), { waitUntil: 'networkidle0', timeout: 60000 });
  await page.evaluate(() => document.fonts.ready);
  await new Promise(r => setTimeout(r, 1500)); // 等 WebGL 背景挂载

  const posters = await page.$$(selector);
  console.log('找到 poster 数量:', posters.length);

  for (let i = 0; i < posters.length; i++) {
    // 优先用 poster 内的标题，其次 data-title，最后序号
    let name = await posters[i].evaluate(el => {
      const t = el.querySelector('title');
      if (t && t.textContent.trim()) return t.textContent.trim();
      if (el.dataset.title) return el.dataset.title;
      return '';
    });
    if (!name) name = 'card-' + String(i + 1).padStart(2, '0');
    // 去掉非法文件名字符
    name = name.replace(/[\\/:*?"<>|\s]+/g, '-');
    const buf = await posters[i].screenshot({ type: 'png' });
    fs.writeFileSync(path.join(outDir, name + '.png'), buf);
    console.log('已导出:', name + '.png', (buf.length / 1024).toFixed(0) + 'KB');
  }

  await browser.close();
  console.log('全部完成');
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
