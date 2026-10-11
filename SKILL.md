---
name: silicon-vision-pipeline
description: 硅基视域自媒体图文流水线。当木子需要「每日热点选题 → 写文章 → 配图/图表 → 公众号 HTML → 小红书卡片」的一站式内容生产时使用。触发词：跑一遍选题、今日选题、给我今天的图文、热点选题、写公众号文章、出小红书卡片、内容流水线。覆盖科技/AI/商业/数码领域。按需调用子技能，用不到的环节不硬凑。
agent_created: true
metadata:
  author: 木子（硅基视域）
  version: "1.3.1"
---

# 硅基视域图文流水线

「硅基视域」频道（AI/科技/商业/数码）的日更内容生产线。

本文件**只做路由**：流程、卡点、每步做什么、读哪个文件。**所有操作细节在 `references/workflow.md`**，走到哪个环节才读，不要提前加载。

## 流程与卡点

```
①选题(10条) → ②选1条⏸ → ③a出两篇骨架 →⏸选1篇 → ③b展开全文+humanizer →⏸确认
  → ④合规审查⏸ → ⑤配图(⏸选风格 → 自动跑完) → ⑥公众号HTML⏸ → ⑦小红书卡片⏸
```

- ⏸ = **硬卡点**：停下等用户确认，绝不自动往下。唯一例外：用户明确说「一路到底」。
- ⑤ 只有一个卡点：**生成前先让用户选风格**；选完直接跑完（定策略 → 生成 → 下载权威图 → 检查），不报 credit、不再等确认。
- ③ 拆成两段是为了省掉「一整篇全文 + 一遍润色」的无用生成（见 workflow.md 环节③）。

## 每步做什么 / 读什么

| 环节 | 做什么 | 读 / 跑 |
|---|---|---|
| ① 选题 | 四维打分（时效 35 / 契合 30 / 深度 20 / 素材 15）后排序，出 10 条带理由的清单 | `scripts/hotlist.py 30` + `aihot` skill；细则见 workflow.md ①② |
| ② 选 1 条 | 停下等用户 | — |
| ③a 骨架 | 两篇各出「标题 + hook + 3–4 段小标题」，每篇 ≤150 字 | `khazix-writer`（第 1 篇） |
| ③b 展开 | 只把**选中的那篇**写成 500–1500 字，再过一遍 `humanizer-zh` | 字数脚本 + `humanizer-zh`；`ai-seo-zh` 模型自判 |
| ④ 合规 | 敏感词扫描 + 平台规范审查 | `scripts/check_text.py` + `assets/rules/wechat-review-slice.md` |
| ⑤ 配图 | 先让用户选风格 → 生成 3–5 → 下载 1–3 → 逐张检查 | `guizang-material-illustration` / `ian-xiaohei-illustrations`；`scripts/grab_img.py` |
| ⑥ HTML | 复用票据基线模板换正文 → 一键后处理 → 生成预览页 | `assets/gzh-preset-moyu-ticket.html`；`scripts/gzh_postprocess.py`、`wrap_preview.py` |
| ⑦ 卡片 | 3:4 卡片，风格五选一（Swiss / Editorial / B1 快讯 / B2 编号教程 / B3 公众号仿卡），复用⑤的图，截图导出 + 拼图 QA | `guizang-social-card-skill`（B 系列加读其 `references/brand-content-styles.md`）；`scripts/shot_cards.js`、`make_contact_sheet.py` |

## 铁律（每次改稿前扫一遍）

- **③b 之前绝不进 ④**；③b 完成后必须把**全文原文贴在对话里**（不是摘要、不是「已写入文件请查看」）。
- **字数 500–1500，绝不超 1500**；③a 骨架每篇 ≤150 字，不许在骨架阶段铺全文。
- **`humanizer-zh` 强制**：选中那篇展开后必过一遍，不可跳过。
- **⑤ 只问风格**：生成前停下让用户选（材料风 / 小黑手绘），选完一路做完——不报 credit、不再等确认；**生成图必须逐张 Read 检查**（错字 / 顺序画反 / 元素缺失要重生成）。
- **文件名一律 ASCII**（配图与卡片素材）。
- ⑥ 正文 **15 或 16px**、**严禁 `text-align:justify`**、图片必须 base64 内嵌；后处理**必须用带 Pillow 的 venv python**（用系统 python 会静默不压缩）。
- ⑦ 只读 4 个必要文件，**必须复用⑤的配图**，QA 用拼图不逐张 Read。
- 全流程：**多案例必须取舍**（不平摊）、**案例数据必须核对过**（禁止按结构编造）。

## 决策点（必须问用户，不猜）

1. 选题：10 条里选哪条
2. ③a 之后：两篇骨架里选哪篇展开
3. ③b 之后：确认全文，才进 ④
4. ⑤ 配图：**生成前先让用户选风格**（材料风 / 小黑手绘）
5. ⑥ 排版：主题 / 字号 / 密度（或用票据风基线）
6. ⑦ 卡片：风格五选一（Swiss / Editorial / B1 快讯 / B2 编号教程 / B3 公众号仿卡），拿不准时问

## 文件导航

| 路径 | 内容 | 何时读 |
|---|---|---|
| `references/workflow.md` | 各环节完整手册：打分锚点、字数脚本、挖图手法、脚本参数、子 skill 清单 | 执行任一环节前 |
| `assets/rules/wechat-review-slice.md` | 微信规范精简切片（~3k tokens，12 个高频条款） | ④ |
| `assets/rules/wechat-op-rules.md` | 规范全文 82KB | 仅按切片标注的行号 `sed -n` 回查 |
| `assets/gzh-preset-moyu-ticket.html` | 公众号排版基线模板 | ⑥ |
| `assets/vocabulary/` | 敏感词库 25000+ 词 | 仅脚本读取 |

## 脚本（全部 0 token）

`hotlist.py` 三平台热榜 · `grab_img.py` 抓网页图 · `check_text.py` 敏感词扫描 · `extract_rules.py` 生成规范切片 · `gzh_postprocess.py` 排版一键达标 · `wrap_preview.py` 预览页 · `make_contact_sheet.py` 卡片拼图 QA · `shot_cards.js` 卡片 HTML → PNG
