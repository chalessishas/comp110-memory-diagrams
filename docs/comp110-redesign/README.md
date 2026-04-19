# COMP110-26s Redesign · Phase 1 交付包

> Kris Jordan 的 UNC COMP110 课程站（`https://comp110-26s.github.io/`）视觉更迭 + AI TA 浮层设计规格。
> **Phase 1（当前）**：设计稿 + 规格 + 数据契约 + TA 配套规则，锁定交付给 DeepSeek / Cursor 实现 Phase 2。
> **Phase 2（等 DeepSeek）**：Next.js 15 + Tailwind v4 生产实现。Phase 1 本目录任何文件都不需要跑 `npm install`，纯规格。

---

## 🔰 从哪里开始读？

**如果你是 DeepSeek/Cursor/Claude 接手 Phase 2**：按以下顺序读 4 份文件就够：

1. [`DESIGN_BRIEF.md`](DESIGN_BRIEF.md) — 先读这个。设计决策表 + tokens + 逐区说明 + DeepSeek prompt 模板 + 踩坑提醒。
2. [`mockup.html`](mockup.html) — 浏览器打开（`open mockup.html`）。视觉参考，不要逐像素复刻，要按 Tailwind 体系重建。
3. [`agenda.json`](agenda.json) — TypeScript 类型推导源。所有 URL 已对 `comp110-26s.github.io` 实测 200。schema 自描述。
4. [`socratic_ta_examples.md`](socratic_ta_examples.md) + [`memory_diagrams_rubric.md`](memory_diagrams_rubric.md) — 仅当实现 AI TA 浮层（Phase 2.5/3）时读。

**如果你是用户 / 评估者**：读 `DESIGN_BRIEF.md` §1（项目目标）和 §3（设计系统 Tokens）前 20 行就能判断方向是否对齐。

---

## 📦 交付清单（5 份文件）

| 文件 | 体积 | 角色 | 核心价值 |
|------|------|------|---------|
| `mockup.html` | 28.7 KB | 视觉原型（单文件 HTML + inline CSS） | Carolina 黄品牌化 / 6 色徽标体系 / Hero 进度环 / 浮层 AI TA FAB |
| `DESIGN_BRIEF.md` | 13.4 KB | Phase 2 交接主文档 | 设计决策表 / tokens / 页面结构 / DeepSeek prompt 模板 / 完整 Socratic system prompt |
| `agenda.json` | 10.1 KB | 数据契约（JSON schema 样本） | TypeScript 类型源 / AI TA runtime context 注入规格 / 所有 URL 已实测 200 |
| `memory_diagrams_rubric.md` | 7.8 KB | Kris v0 规则结构化 + v0 缺口分析 | TA 预评分器的权威规则源 + QZ01+ 需补齐的规则清单 |
| `socratic_ta_examples.md` | 8.2 KB | 6 个 Socratic 应答 few-shot + 反例集 | 防 LLM 在真实学生压力下 drift 的 calibration 集 |
| **合计** | **~68 KB** | | 零依赖的 Phase 2 完整起跑包 |

---

## 🎯 项目目标摘要

- **为什么做**：COMP110 现有站点（Kris 自搭）信息密度高但视觉扁平，agenda 倒序时间线对学生理解课程节奏不友好
- **视觉改什么**：色彩（Bootstrap blue → Carolina 黄）、层级（平铺列表 → Hero 进度环 + 筛选 chips + 时间线）、徽标（纯文字 → 6 色 type badge）
- **AI TA 浮层**：右下 FAB 展开 380×560 面板。Socratic 教学（从不给答案），注入课程上下文（`{{LESSON_ID}}` / `{{CURRENT_DATE}}` / `{{TOPICS_COVERED}}`），区别于通用 ChatGPT 的核心差异化点
- **不做什么**：不换域名、不拆架构、不动 Kris 的内容授权边界（DESIGN_BRIEF §5 建议 local-only 起步）

---

## 🚫 Phase 1 明确不包含（避免 DeepSeek 误解）

- ❌ Next.js 项目初始化（`package.json` / `next.config.js` / `.gitignore` / `src/` 结构）
- ❌ Tailwind config 翻译（DESIGN_BRIEF §3 的 tokens 够 DeepSeek 自己 `tailwind.config.ts` 翻译）
- ❌ 真实 API 路由（`/api/agenda` 等）
- ❌ AI TA 后端部署（OpenAI/Anthropic 账号、rate limit、auth）
- ❌ 完整 15 周 agenda 数据（`agenda.json` 只覆盖 week 13-15 作样本，全量由 Phase 2 scraper 从 `comp110-26s.github.io` 抓）
- ❌ cl15-cl33 slide 内容扒取（`memory_diagrams_rubric.md` §3 列了 QZ01-QZ03 的规则缺口，需 Phase 3 补）

---

## ⚠️ 已知风险（交给 Phase 2 实现者）

| 风险 | 位置 | 建议 |
|------|------|------|
| Kris 内容版权 | 整个项目 | DESIGN_BRIEF §5 — 先 local-only 跑 MVP，之后发邮件取得 Kris 书面授权再公网部署 |
| Panopto 深链无法代理 | `agenda.json` 中 `panopto` URL | 考虑替换为 YouTube review session recording（Kris 首页已链过 `youtu.be/jp1uWArLD6M`） |
| `agenda.json` 仅 3 周样本 | `sections.the_past` | Phase 2 写 scraper 抓 `https://comp110-26s.github.io/` 首页 + 按 item.id 反查真实 URL pattern（见 `agenda.json._schema.notes`） |
| v0 rubric 只覆盖 QZ00 | `memory_diagrams_rubric.md` §3 | Phase 3 接 Python Tutor API 或自搭 `trace_execution.py` 作后端 |
| AI TA drift | 所有 TA 相关 | 部署前必跑 `socratic_ta_examples.md` 6 个 test case，检查输出是否匹配「✅ 正确回复」 |

---

## 📏 验收标准（DeepSeek 产出 Phase 2 后回归测试）

1. **视觉**：桌面 1440×900 截图与 `mockup.html` 同分辨率截图对比，布局一致（允许字体/像素对齐差异）
2. **响应式**：`<920px` 断点下 sidebar 折叠到底部；`<640px` 下 filter chips 变横向滚动
3. **数据**：`agenda.json` 喂进去渲染无 `undefined` / 空字段 / 404 链接
4. **a11y**：`tab` 键能遍历所有可交互元素；`Esc` 关 TA panel；`prefers-color-scheme: dark` 自动切暗色
5. **AI TA**：6 个 `socratic_ta_examples.md` 测试用例人工过一遍，不命中反例集的任一 pattern
6. **性能**：First Contentful Paint < 1.5s（UNC 网校内网访问）

---

## 🗓️ Phase 1 完成时间线

- 2026-04-18 20:03 — opus-0418a 交付 mockup.html + DESIGN_BRIEF.md 初版
- 2026-04-18 20:12 — sonnet-0418f 补 Socratic system prompt 完整模板
- 2026-04-18 20:16 — opus-0418b 补 agenda.json + 注册 CLAUDE.md 项目表
- 2026-04-18 20:29 — opus-0418d 全量验证 agenda.json URL（9 个 404 → 全 200）
- 2026-04-18 20:34 — opus-0418e 扒 memory_diagrams_v0.pdf → rubric.md
- 2026-04-18 20:38 — opus-0418g/sonnet-0418l 并发生成 socratic_ta_examples.md
- 2026-04-18 20:42 — opus-0418h 锁 Phase 1（本文件 README.md）

**🔒 Phase 1 自此锁定**。后续 Progress Loop 非必要不再追加文件，等 DeepSeek 产出 Phase 2 后再按 feedback 迭代。

---

## 💬 联系

- 工作区维护：Claude Code 实例（Opus/Sonnet 并发）
- 项目录入：`/Users/shaoq/Desktop/VScode Workspace/CLAUDE.md` → `## Projects` 表
- 编年记录：`docs/chronicle/YYYY-MM-DD.md`
- 重大决策/卡点 → 发 Discord（`node ~/.claude/discord/send.js`）
