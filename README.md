# silicon-vision-pipeline · 硅基视域图文流水线

「硅基视域」（AI / 科技 / 商业 / 数码频道）的日更自媒体内容流水线，一条龙覆盖：

> **热点选题 → 写文章 → 合规审查 → 配图 → 公众号排版 HTML → 小红书卡片**

这是一个 **WorkBuddy / Claude Skills 格式**的 skill（根目录 `SKILL.md`）。

---

## 安装

把整个目录放进你的技能目录，任选其一：

- **用户级**（推荐，全局可用）：`~/.workbuddy/skills/silicon-vision-pipeline`
- **项目级**：`<你的项目>/.workbuddy/skills/silicon-vision-pipeline`

```bash
git clone https://github.com/li-cai666/silicon-vision-pipeline.git \
  ~/.workbuddy/skills/silicon-vision-pipeline
```

重启会话后，说「跑一遍选题」「今日选题」「写公众号文章」即可触发。

---

## 工作流

```
①选题(10条) → ②选1条⏸ → ③a出两篇骨架 →⏸选1篇 → ③b展开全文+润色
   →⏸确认 → ④合规审查⏸ → ⑤配图(⏸选风格 → 自动跑完) → ⑥公众号HTML⏸ → ⑦小红书卡片⏸
```

`⏸` = **硬卡点**，停下来等你确认，绝不自动往下（唯一例外：你明确说「一路到底」）。

---

## 依赖

### 1. 依赖的其他 skill（**不在本仓库内**，需自行安装）

| skill | 用途 | 用于环节 |
|---|---|---|
| `aihot` | AI 圈热点源（热榜 / 精选） | ① 选题 |
| `khazix-writer` | 卡兹克风格长文（第 1 篇骨架） | ③a |
| `humanizer-zh` | 中文润色，去空话去模板腔 | ③b |
| `ai-seo-zh` | 可引用结构自判（GEO/AEO） | ③b |
| `guizang-material-illustration` | 材料风配图 | ⑤ 配图 |
| `ian-xiaohei-illustrations` | 小黑手绘风配图 | ⑤ 配图 |
| `guizang-social-card-skill` | 小红书卡片生成 | ⑦ 卡片 |

### 2. 运行环境

- **Python 3.8+**，需 `Pillow`（图片压缩、卡片拼图 QA）
- **Node.js**，需 `puppeteer-core`（卡片 HTML → PNG）
- 其余脚本零依赖，仅用标准库

---

## 目录结构

```
SKILL.md                                 # 路由与硬约束（入口）
references/workflow.md                   # 各环节详细操作手册
assets/rules/wechat-review-slice.md      # 微信规范精简切片（12 条高频条款）
assets/rules/wechat-op-rules.md          # 微信规范全文
assets/gzh-preset-moyu-ticket.html       # 公众号排版基线模板（票据风）
scripts/                                 # 全部脚本 0 token
  hotlist.py         三平台热榜（微博/B站/抖音）
  grab_img.py        抓取网页图片
  check_text.py      敏感词扫描
  extract_rules.py   生成规范切片
  gzh_postprocess.py 公众号 HTML 一键达标
  wrap_preview.py    生成预览页
  make_contact_sheet.py  卡片拼图 QA
  shot_cards.js      卡片 HTML → PNG
```

---

## 重要说明

- **本仓库不包含敏感词库。** `SKILL.md` 里提到的 `assets/vocabulary/`（25000+ 词）因内容与体积原因未分发，使用 ④ 合规审查前请自行准备词库文件放入该目录，否则 `check_text.py` 无法运行。
- `assets/rules/wechat-op-rules.md` 为公开平台规范整理，版权归原平台所有，仅作个人查阅用。
- 本 skill 会自动调用多个第三方 skill，请自行确认其可用性与授权。

---

## License

[MIT](LICENSE)
