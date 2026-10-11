# 硅基视域流水线 · 详细操作手册

本文件在需要执行具体环节时按需读取，不常驻上下文。
SKILL.md 是路由与硬约束，本文件是细节：打分锚点、脚本参数、挖图手法、子 skill 清单。

## 环节① 选题 · 详细

### 数据源 A：hotlist.py（微博/B站/抖音）
- 调用：`python scripts/hotlist.py 30`（30 = 每平台条数）
- 零依赖标准库，UA+Referer 伪装，分别请求：
  - 微博 `weibo.com/ajax/side/hotSearch` → `data.realtime`
  - B站 `api.bilibili.com/x/web-interface/search/square` → `data.trending.list`
  - 抖音 `iesdouyin.com/web/api/v2/hotsearch/billboard/word/` → `word_list`

### 数据源 B：aihot（AI 圈）
- 加载 `aihot` skill 后按其 SKILL.md 路由调用
- 常用：`/api/v1/hot-topics`（当前最热）、`/api/v1/items?mode=selected&window=24h`
- 无需 Key，匿名只读

### 打分锚点

四维各 1–10 分，加权求和排序。权重由 coreyhaines31/marketingskills 的 `content-strategy` 改造而来（原版面向 B2B SaaS，不适合公众号日更）。

| 维度 | 权重 | 打分锚点 |
|---|---|---|
| 时效热度 35% | 24h 内是否还在涨 | 10=今日爆发且持续发酵；5=两天前旧闻；2=已凉 |
| 硅基视域契合 30% | AI/科技/商业/数码？读者是科技人群？ | 10=核心选题；5=边缘领域；2=偏离频道 |
| 可展开深度 20% | 能否写出信息增量 | 10=有独家解读空间；5=只能复述新闻；2=一句话就没了 |
| 素材充足度 15% | 有官方文档/数据/权威信源？ | 10=有原始报告或公告；5=二手转述；2=只能靠印象 |

要点：
- **时效高但其余三项低的要压后**。爆款但没料可写，写出来必然是空话。
- **素材充足度低不意味不能写**，要在理由里说明「只能做快讯，深度有限」，让用户知情选择。
- 列表按总分排序，但明确告诉用户可从任意位置选。
- 软提示：素材充足 + AI/科技类 → 理由里点一句「适合做可引用结构」，不加分、不影响排序。

## 环节③ 写文章 · 详细

分两段走：**③a 出骨架 → ⏸用户选 → ③b 展开全文**。
这么拆是为了省掉一整篇全文 + 一遍润色（旧流程「两篇全文 + 两遍润色」是全流程最重的一步，而被弃的那篇是纯沉没成本）。

### ③a 出两篇骨架（每篇 ≤150 字）

- 两篇各给三样：**标题** + **开头 hook**（1–2 句）+ **3–4 段小标题列表**
- 第 1 篇「卡兹克风格」→ 加载 `khazix-writer`；第 2 篇「AI 直出」→ 直接写，默认观点鲜明、信息密度高
- ⛔ **骨架阶段不许铺全文**。小标题要能看出这篇的取舍（挑 2–3 个点深写），不是把选题拆平摊
- 输出后**停下等用户选 1 篇**，不自动往下

### ③b 展开全文（500–1500 字）

- 只展开**被选中的那一篇**，写成 500–1500 字（正文中文字数）
- 快讯/单一事件 → 500–800；现象解读/带数据 → 800–1200；深度多案例 → 1200–1500（封顶）
- **不许目测字数**，写完必跑（贴出给用户前就要核对）：
  ```bash
  python -c "import io,re;t=io.open('文章.md',encoding='utf-8').read().replace('图片','');print(len(re.findall(r'[\u4e00-\u9fff]',t)))"
  ```

### humanizer-zh（强制环节）
选中那篇展开后**必须**加载 `humanizer-zh` 润色：去空话、去重复、去模板腔，保留事实、确定程度和作者声音。用户明确要求此步不可跳过。润色后如果掉出 500 字下限，补一段实质内容，不要靠注水凑字。

### ai-seo-zh（模型自判）
AI/科技类硬核选题、素材充足度高时才加载。做法：结论段独立成句、数据段标信源与时间、对比处用表格、文末加 3–5 条问答。
注意：公众号正文不被 AI 抓取，可抽取段落的作用是让读者能整段截图转发；真要影响 AI 引用，得把核心观点同步一份到知乎/掘金等可抓取平台。

### 两条红线
- ⛔ **多方向选题必须取舍**：用户一次给 6 个方向时，每个都展开必然超字数。1200 字平摊 6 段 = 每段 200 字 = 全是废话。只挑 2–3 个最有反差感的点深写。优先级「有矛盾感的」>「重要的」，如「结案≠到账」优于完整条目清单。
- ⛔ **案例必须核对，不许按结构编造**：真实事故——看到条目四栏结构（成本/说人话/收益/来源）后，按结构编了「系安全气囊」「维生素 D」两个条目写进文章，而仓库第 1 章全文 5.4 万字里这两个词**零命中**，真实条目是「系安全带，前排后排都系」。**看到结构 ≠ 内容真实存在。**

### 硬卡点
③a 骨架出完 → **停下等用户选 1 篇**；③b 全文 + 润色后 → **必须立即停止**，把**选中那篇的完整正文贴在对话里**，等用户确认，才进入④。严禁未经选择就展开、未经确认就审查/配图/转 HTML/做卡片。

### 回退：用户要旧流程时
用户明确说「两篇都要全文」「先看两篇完整版」→ 跳过 ③a，直接按老办法两篇各写全文 + 各过一遍 humanizer，一次贴出二选一。此时才回到「一次消耗两篇生成量」的模式。

## 环节④ 合规审查 · 详细

### 4.1 敏感词扫描（脚本，0 token）
```bash
python scripts/check_text.py --target_file "<文章.md路径>"
```
词库 `assets/vocabulary/`（13 分类 25000+ 词）。输出命中词 + 行号 + 摘录；无命中提示 "No sensitive words found"。

### 4.2 平台规范审查（读切片，不读全文）
- **读 `assets/rules/wechat-review-slice.md`**（~1.9k tokens），它含 3.3 诱导 / 3.12 欺诈网赚 / 3.27 非真人自动化创作 / 3.28 套路化模板 / 4.1 侵权 / 4.8 过度营销 / 4.9 不实信息 / 4.11 煽动夸大 / 4.15 极限词 / 4.20 未标广告 / 4.21 标题正文不符 / 4.24 未标来源
- 切片由 `scripts/extract_rules.py` 生成（可加 `--clauses` / `--max-lines` 调），勿手改
- 需要完整原文时，按切片里标的行号回查，别整读：
  ```bash
  sed -n "121,191p" assets/rules/wechat-op-rules.md
  ```
- **不要写脚本做关键词匹配**——违规判定依赖上下文，字面匹配大量误报
- 标题单独看一遍（标题党、仿冒系统消息是高频违规点）
- 输出：条款号+条款名 / 风险等级 / 原文位置+摘录 / 可直替换的修改建议；结论给「能否发布 + 必须改的项」
- 高危项改完重审，直到通过或用户确认接受

> 小红书/抖音/视频号暂无本地规范文件，以公众号规范 + 通用敏感词库为准。

## 环节⑤ 配图 · 详细

### 0. 先让用户选风格（⑤ 唯一卡点）

- **生成前必须停下，让用户选风格**：材料风 `guizang-material-illustration` / 小黑手绘 `ian-xiaohei-illustrations`
- 可以按选题调性给一句**推荐理由**帮用户决定，但**不许替用户定**
- ⛔ 用户选完风格之前，不许开始生成
- 选完之后**一路做完，不再问**：定配图策略 → 生成 3–5 → 下载权威图 1–3 → 逐张 Read 检查

### grab_img.py
```bash
python scripts/grab_img.py "<文章URL>" <输出目录> [最小字节]
```
默认最小字节 20000（过滤图标/占位图）。解析 img 的 src + data-original/data-src 懒加载，协议补全去重。JS 动态渲染页会返回「未发现图片」，用下面的 curl 兜底。

### curl 兜底挖图（0 token）
```bash
# 1. 浏览器 UA 抓 HTML（很多"JS 动态页"其实 curl 就能拿到）
curl -s -L --compressed -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0" "<URL>" -o /tmp/page.html
# 2. grep 图片直链（相对路径 /images/... 也可能是原图，Next.js 站点常见）
grep -oE '(https?://[^" ]+|/images/[^" ]+)\.(jpg|jpeg|png|webp)' /tmp/page.html | sort -u
# 3. 带 Referer 下载，避免 CDN 拒直连
curl -s -L --compressed -A "Mozilla/5.0" -H "Referer: <源站域名>" "<图片URL>" -o out.jpg
# 4. 必须验文件头，错的改扩展名
```
- 挖图优先级：官方博客/新闻稿（IR 页常有 social_image/og:image）> **首发媒体题图**（The Verge、TechCrunch 等，TechCrunch 正文常注明首发源）> 二手媒体图
- **图要有信息量**：❌ 排除手机实拍、通用产品图、纯氛围图 —— 这类图占版面不加分。✓ 要官方 logo 特写、官方题图、官方文档截图、机构配图
- **海外官网常抓不到**：Anthropic 等站点在本机网络下 curl 无响应、WebFetch 返回空、r.jina.ai 代理 502。此时直接改走权威媒体转载图，并在图注标明来源（如「图：The Verge 官方题图」），不要卡住反复重试
- `grep og:image` 定位文章主图最快：`grep -oE '<meta[^>]*og:image[^>]*>' page.html`
- 命名技巧：官方图文件名常带语义（如 `ff_lisa_cropped_16x9.png`），按关键词筛 grep 结果
- 含查询串的 CDN 直链（如 `?w=1600&crop=...`）在 bash 里会被截断，**改用 Python urllib + 手拼 Referer 下载**

### 文件头对照表（扩展名一定要改对）
| 头 4 字节 | 真格式 |
|---|---|
| `\x89PNG` | .png |
| `\xFF\xD8` | .jpg |
| `GIF8` | .gif |
| `RIFF` | .webp |

### ImageGen 生成
- 工具 ImageGen（DeferExecuteTool），每张约 5–10 credits。**风格已由用户选定后，直接生成，不报 credit、不再等确认**
- 材料风：瑞士编辑部 3D 插图，米白底 + IKB 蓝点缀，16:9
- 小黑手绘：纯白底黑线稿 + 少量红橙批注，16:9。**争议/情绪化/荒诞感选题，推荐理由优先给小黑风**（最终由用户选）
- **生成后必须逐张 Read 检查**：中文错字、顺序画反、元素缺失都要重生成。顺序类（如「警告→限流→限制→暂停→终止账号」）极易画反，prompt 里要逐级写明每级对应位置
- **ImageGen 出的图右下角带模型水印**，需裁掉底部约 5-6%：
  ```python
  im.crop((0, 0, w, int(h*0.95)))
  ```
- 转 JPEG q90 后体积小一个量级（PNG 1536px → 200KB，JPEG → 40KB）
- 所有图留到⑦复用

## 环节⑥ 公众号 HTML · 详细

### 路径 A：基线模板（默认，省 ~13k tokens）
1. 复制 `assets/gzh-preset-moyu-ticket.html`，替换 `<span leaf>` 里的正文与 `{{IMG:xxx}}` 占位名
2. 后处理一键达标：
   ```bash
   # ⚠️ 必须用带 Pillow 的 venv python，不要用系统 python
   "C:/Users/15856/.workbuddy/binaries/python/envs/default/Scripts/python.exe" \
     scripts/gzh_postprocess.py 模板.html -o 输出.html --assets <素材目录> --body 16
   ```
   做四件事：`justify→left`；`font-size:14px` → 16px（小字标注行自动跳过）；大留白 clamp（margin-bottom>24→18、margin-top>48→40、padding>40→32，另有 8 条实测精确映射）；图片压 1080px JPEG q82 后 base64 内嵌。
   校验不通过直接 exit 1：无 justify 残留 / 无 `{{IMG:}}` 残留 / 无相对路径 src。
   - `--no-img` 只改样式（此时跳过图片校验）
   - 图片缓存落 `.gzh_img_cache/`，重跑不重复压缩
   - **换图后必须 `rm -rf .gzh_img_cache`**，否则会用旧缓存
   - ⛔ **不要用系统 `python` 跑**：脚本里`except ImportError` 会静默走「原样内嵌不压缩」分支，产物 7.9MB 而非 700KB，且**不报错**。实测同一批图：系统 python 7.9MB → venv 713KB
3. `python scripts/wrap_preview.py 终版.html -o 预览.html` 生成带复制按钮的预览页，两个文件都拷 E 盘交付目录

### 路径 B：换主题（只在基线模板不合适时）
1. 只读 `theme-index.md` 挑主题，再读目标 `theme-*.md`
2. **先出 1 屏样板（200 字）给用户确认风格，再排全篇**——避免整篇重写
3. 排完照样跑 `gzh_postprocess.py`，别手改（手改会漏，橄榄手记和禅意风都漏过）

### 发布标准检查表
- [ ] 正文 15 或 16px
- [ ] 全文无 `text-align:justify`
- [ ] 图片已 base64 内嵌（无 `assets/` 相对路径）
- [ ] 间距在紧凑档（段落 14–18px）
- [ ] 文件大小约 1–1.5MB
- [ ] 提醒用户粘贴前清空编辑器旧内容

## 环节⑦ 小红书卡片 · 详细

### 只读这 4 个文件
`references/platform-specs.md`（1.5k）→ `references/theme-presets.md`（1.7k）→ `references/layout-recipes.md`（11.6k）→ `assets/template-{swiss|editorial}-card.html`（10k）。其余 18 个参考文件（live-photo / map / portrait-fill / background-systems / screenshot-treatment / README.en …）用到再说。

### 复用⑤的图
- 封面页 → 主图；数据页 → 数据对比图；案例页 → 权威下载图/实截图
- 图片改 ASCII 名拷进卡片 `assets/`，`<img src="assets/xxx.png">` 配 `.frame-img` / `.fit-contain`
- 竖图用 fit-contain 完整呈现，方图用方裁相框

### 截图导出
```bash
NODE_PATH="C:/Users/15856/.workbuddy/binaries/node/workspace/node_modules" \
  node scripts/shot_cards.js "<卡片index.html>" "<输出目录>" "section.poster.xhs"
```
- 前置：`npm install puppeteer-core`（装到 node workspace，仅首次）
- 每个 poster 加 `data-title="xhs-01-cover"`，导出文件名才有语义（直接写在模板里，别事后逐个改）
- 脚本内已 `await document.fonts.ready` + sleep 1.5s，路径含中文自动 URL 编码

### QA（拼图 + 密度，别逐张读）
```bash
python scripts/make_contact_sheet.py <输出目录> -o sheet.jpg   # 7 张拼一张，一次看完
python scripts/make_contact_sheet.py <输出目录> --density       # 垂直填充率 / 顶底空隙
```
- 填充率 <75% 或底部空隙 >12% → 该页补内容重排（加真实数据条、结论块，或用 `justify-content:space-between` 均匀分布，别用 flex:1 上下夹击）
- 拼图看完后，只对有问题的单张单独 Read
- QA 重点：数字是否换行（换行改列宽重渲）、图片是否溢出画布

## 子 skill 清单

| 环节 | skill / 脚本 | 加载时机 |
|---|---|---|
| AI 资讯 | aihot | 需要 AI 圈数据时 |
| 热榜 | hotlist.py | 需要三平台热榜时 |
| 卡兹克文 | khazix-writer | ③a 出骨架 / ③b 展开（第 1 篇） |
| **润色** | **humanizer-zh** | **③b 强制，选中那篇展开后必跑** |
| 可引用结构 | ai-seo-zh | ③模型自判（硬核 + 素材足才用） |
| 合规 | check_text.py + wechat-review-slice.md | ④必做 |
| 手绘配图 | ian-xiaohei-illustrations | 观点/隐喻图 |
| 材料配图 | guizang-material-illustration | 数据/资讯图（默认） |
| 图表 | lieflat-charts | 用户明确要 Mono 灰阶 HTML 时 |
| 抓图 | grab_img.py | 权威图/难生成图 |
| 公众号 | gzh-design | ⑥换主题时（基线模板够用就不加载） |
| 卡片 | guizang-social-card-skill（唯一） | ⑦ |
| 卡片截图 | shot_cards.js | ⑦导出 PNG |
| 卡片 QA | make_contact_sheet.py | ⑦导出后 |

## 省 token 要点

- 抓数据/敏感词/格式后处理/拼图全走脚本（0 token）
- 子 skill 用到才加载；卡片只读 4 个文件；规范只读切片
- 排版优先复用基线模板，换主题先出样板再全量
- 决策点先问用户（返工一次 ≈ 15k，问一句 ≈ 0.1k）
- 每环节产出后停一下等确认（除非用户明确要一路到底）
