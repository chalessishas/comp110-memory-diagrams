# course-hub 下一步改善方向研究（2026-04-16）

自动由 Research Loop 18:28 触发，用户不在场。

## 一、执行摘要

1. **先稳后进**（本周）：修 Vercel 漂移 + 4 个 Supabase search_path + 开启 leaked password protection。Phase 6 已交付但用户看不到 = 零价值。
2. **B 面窄切入**（2-4 周）：砍掉"大纲解析通用 AI 学习"的模糊定位，聚焦"考试 6 周倒计时 + FSRS"一条线，对准本人（作者自用）+ 宿舍室友 20 人闭环。
3. **NotebookLM 化**（3-6 周）：接入 PDF/音频上传 → 分章自动出 FSRS 卡 + Voice Q&A。这是 2026 年学习产品的水位线，不做就掉队。
4. **社交化分发**（持续）：小红书 Build in Public 发"每天学习数据截图"，2026 小红书已是中国 AI 学习工具冷启动第一阵地。
5. **拒绝的事**：不做多用户协作、不做 LLM 切换、不做付费墙、不迁移数据库。

---

## 二、竞品横向对比

| 产品 | 定位 | 关键差异 | course-hub 可借鉴 |
|------|------|----------|--------------------|
| Khanmigo | K12 Socratic tutor | 不给答案，只追问；$4/月 | Teach-back 可加 Socratic 追问链 |
| ChatGPT Study Mode | 通用分步推理 | 内置 guided solving | 把 term card 接入 solving 模式 |
| NotebookLM 2.0 | 资料驱动零幻觉 | 50 源上传 + 自动 flashcard + podcast | **直接对标，做 PDF→FSRS 通道** |
| Duolingo Max | 语言 roleplay | AI 角色扮演 + Explain My Answer | Voice Notes 可升级为 Roleplay 模式 |
| RemNote | 笔记+SR+AI | SM-2/FSRS 双算法 + AI 出卡 + PDF 标注 | FSRS 已有，缺 PDF 标注 |
| StudyFetch | 讲座转卡 | 录音/PDF/slides 三入口 | SSE 可接语音转文字管线 |
| MintDeck | 学生向 SR | 极简 UI + 社区卡组 | 社区卡组值得抄 |
| SuperMemo MemoChat | 对话式 SR | 会话中插入复习 | 对话式复习是个空位 |
| Obsidian SRAI plugin | 笔记原生 FSRS | AI 生成 + FSRS | 提醒：FSRS 已成学习产品标配，不是护城河 |
| Kiwi AI | 考试专用 tutor | 针对统考场景 | 考试倒计时 UX 可对标 |

**结论**：course-hub 的 exam-day retrievability 排序（基于 Brunmair 2019 + Wilson 2019）在上述产品中无一覆盖，这是目前唯一的真护城河，要扩大。

---

## 三、2026 年 AI 教育趋势

**趋势 1：资料驱动（source-grounded）取代生成式**。
- 证据：NotebookLM 零幻觉 + 精准引用已成学生首选；ChatGPT Study Mode 也转向引用内源。
- 落地：course-hub 新增 `/api/ingest/pdf`，复用 chunk → Qwen structured output → FSRS 卡，引用回章节页码。3 天可做 MVP。

**趋势 2：Socratic / 过程干预取代答案给予**。
- 证据：Khanmigo 核心即 Socratic 追问，Claude Education Skills 全部基于 Cepeda 2006 等具名研究。
- 落地：teach-back 模块加两轮 follow-up（"你刚说了 X，那 Y 情况下呢？"），每轮限 40 字输出以控 Qwen 成本。

**趋势 3：Agent Loop + Skills**。
- 证据：Anthropic 已开源 108 个 evidence-based education skills（GarethManning repo）；AI SDK 原生支持 multi-step agent loop。
- 落地：把现有 prompt 散文重构为"lesson-planner / question-generator / explainer"三 skill，走 AI SDK v5 `experimental_agent`，不要自建 orchestrator。

**趋势 4：语音对话学习**。
- 证据：Duolingo Max Roleplay + SuperMemo MemoChat。Web Speech API 已有，缺转录后的结构化喂回。
- 落地：Voice Notes v2，录完后 Qwen 提取 3 个关键概念 → 自动生成 FSRS 卡。

---

## 四、技术栈前瞻

**已用且领先**：RSC 并行查询、SSE lesson streaming、ts-fsrs、AI SDK + Qwen。
**可采纳**：
- AI SDK RSC `createStreamableUI` 流 React 组件树——课程讲解页直接流组件（当前只流文本）。
- Next.js 16.2 AI dev-tools 终端调试，省掉 console.log。
- Supabase pgvector + RAG 做资料库检索（对标 NotebookLM 引用）。
- Zod schema → Qwen structured output（DashScope 已支持，注意 thinking mode 不支持）。

**不建议**：
- 迁 Neon/Turso：Supabase 的 auth+storage+realtime 捆绑值钱，切了要重写 3 个子系统。
- 自建 agent orchestrator：直接用 AI SDK loop。
- 换 GPT-4o/Claude：Qwen3.5-Plus 在结构化 JSON + 中文学科上够用，成本 1/10。

---

## 五、Learning Science 新弹药

1. **Spaced Retrieval = Spaced Repetition + Retrieval Practice**（Pan & Rickard meta 2024 复验 2025）：二者联用比任一单独 +25%。课程的 FSRS + teach-back 已接近，但 FSRS 复习时若只看答案不主动召回，退化为 SR。**落地**：FSRS 卡强制"先盲答再翻面"，记录盲答耗时进 mastery。
2. **Distributed Practice across Sessions**（Memory & Cognition 2022-2025）：多 session 分布显著优于单 session 内间隔。**落地**：exam prep 的 12 topics 从"一次排完"改"每日固定 3 题 + 昨日 2 题"。
3. **Pretesting Effect**（2025 医学教育 RCT，保留率 +15%）：学前先考再学。**落地**：每节课开头先出 2 道未学过的题，允许乱答，然后进入讲解。成本只是改 lesson 模板。
4. **Generation Effect 在 AI 辅助下的退化**（warning，2025 多篇）：学生让 AI 直答会削弱 generation effect。**落地**：explanation gating 已做（Kornell 2009），强化成"AI 答前必须写 ≥ 20 字自答"。

---

## 六、分发路径建议

**30 天**：小红书账号 `@course-hub-shaoq` 每日 1 条：① 本人掌握度热力图截图 + 一句学习洞察 ② 产品开发日志（Build in Public，2026 小红书 AI 孵化器模式已成范式）。目标 500 粉。
**60 天**：挑一门"大学生都考"的通用课（四六级/考研英语/408）做专用题库，扫描 B 站评论区主动 @ 求科目的用户。即刻同步发布。目标 50 周活。
**90 天**：找 2 位大学老师做免费试用（B2C2B 最小单元），换用户数据。拒绝做 Product Hunt——英文市场竞争饱和，2026 年中文学生 SEGment 性价比高 10 倍。

---

## 七、风险和反模式

- **不要做多用户协作**：个人开发者维护不起 realtime 冲突 + 权限矩阵。
- **不要做付费订阅**：50 用户以下谈 MRR 是自嗨，先做留存。
- **不要跟 LLM 风换模型**：每次换都要重跑 prompt 回归。
- **不要学 RemNote 做 all-in-one 笔记**：会背离"考试冲刺"主线。
- **不要把 i18n 扩到第三语言**：EN/ZH 已吃掉维护成本的上限。
- **Supabase security WARN 不修 = 定时炸弹**：leaked password protection 关掉等于把用户密码放在 rockyou.txt 旁边。

---

## 八、具体 Phase 7 建议

| # | 方向 | 难度 | 用户价值 | 证据强度 | 依赖 | 验证 |
|---|------|------|----------|----------|------|------|
| 1 | Supabase 5 WARN 全修 + Vercel prod rebase Apr11 | 4 小时 | 3 | 5 | 无 | Supabase advisor 清零 + /health 返回 Apr11 sha |
| 2 | PDF ingest → FSRS 卡管线（对标 NotebookLM） | 3 天 | 5 | 4 | pgvector + Qwen JSON mode | 本人上传一份 PDF 生成 ≥ 20 张正确卡 |
| 3 | 盲答强制 + 耗时入 mastery（Spaced Retrieval） | 1 天 | 4 | 5 | FSRS 表加 `blind_recall_ms` 列 | A/B：盲答组 7 日保留率 +10% |
| 4 | Pretesting：每课前 2 题未学过 | 0.5 天 | 3 | 4 | lesson template 改 | 对比用户完课率 |
| 5 | teach-back 两轮 Socratic follow-up | 1 天 | 4 | 4 | Qwen agent loop | 追问触发率 > 60% |
| 6 | Voice Notes v2：录音→概念抽取→自动卡 | 2 天 | 4 | 3 | Web Speech + Qwen extract | 3 分钟录音生成 ≥ 3 卡 |
| 7 | 小红书 Build in Public 自动日报 cron | 0.5 天 | 2 | 2 | Vercel cron + screenshot API | 每日 18:00 生成截图 |
| 8 | 公开 demo 账号（guest 增强版，预填数据） | 0.5 天 | 4 | - | 无 | 新访客 30 秒看到核心价值 |

**优先级**：1 > 8 > 3 > 2 > 4 > 5 > 6 > 7。#1 是阻断，#8 是分发必需，#3 ROI 最高（半天改代码换实证提升）。

---

## 九、引用

- https://pasqualepillitteri.it/en/news/745/best-ai-apps-for-studying-2026-kiwi-chatgpt-notebooklm
- https://www.youlearn.ai/blogs/best-ai-tutor-apps-college-students-2026
- https://felloai.com/top-12-ai-tools-for-students-to-study-smarter/
- https://nextjs.org/blog/next-16-2-ai
- https://ai-sdk.dev/docs/ai-sdk-rsc/streaming-values
- https://github.com/vercel/ai
- https://journals.zeuspress.org/index.php/IJASSR/article/view/425
- https://pubmed.ncbi.nlm.nih.gov/39250798/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12343689/
- https://link.springer.com/article/10.3758/s13421-022-01361-8
- https://www.obsidianstats.com/posts/2025-05-01-spaced-repetition-plugins
- https://www.mindomax.com/best-anki-alternatives-with-ai-in-2026
- https://studyboost.org/blog/anki-alternatives/
- https://calmops.com/indie-hackers/product-hunt-launch-guide/
- https://www.geekpark.net/news/362541
- https://zhuanlan.zhihu.com/p/1996405500003250248
- https://github.com/GarethManning/claude-education-skills
- https://claude.com/solutions/education
- https://www.alibabacloud.com/help/en/model-studio/qwen-structured-output
- https://www.datacamp.com/blog/qwen3-5
- https://www.bytebase.com/blog/neon-vs-supabase/
- https://www.pkgpulse.com/blog/neon-vs-supabase-vs-turso-2026
- https://makerkit.dev/blog/tutorials/best-database-software-startups
