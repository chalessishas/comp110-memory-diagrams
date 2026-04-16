# course-hub 补盲报告：反证据 + 冷启动 + 删功能（2026-04-16 19:25）

前置：这是对 18:28 研究的补丁，不重复结论。主线问题——prod exposure ≈ 0 时如何避免堆功能沉没。前一份报告有 confirmation bias（9 轮搜索全是支持 NotebookLM 趋势的证据），且对"产品没人用"这一事实避而不谈。

## 一、AI 辅助学习的反面证据（前报告只一句带过）

**PNAS 2025（Bastani et al.）关键发现**：近千名高中数学生 RCT，使用未加护栏的 GPT 辅助练习期间成绩 +48%，但 **撤掉 AI 后考试反降 17%**。原因是学生把"解题"外包给 AI，没建立 generation。对照：加了 teacher-designed hints 的 GPT Tutor 组无显著负面效应。

**Frontiers Psychology 2025（cognitive paradox）+ arXiv 2510.16019**：580 大学生调查 + 综述。AI 依赖 → 认知疲劳中介 → 批判性思维下降。年轻用户依赖更深，降幅更大。关键机制：metacognitive laziness——学生不再自问"我懂了吗"，直接外包。

**course-hub 踩到的具体坑**：

1. **Socratic follow-up 是锦上添花，不是要害**。要害是 **AI 直接给答案的路径是否还存在**。course-hub 当前 lesson/teach-back 仍在默认输出完整讲解；explanation gating（20 字自答）只在部分场景，FSRS 翻面前无盲答强制（前报告也列入 Phase 7 #3，但埋在中等优先级）。
2. **Pretesting（前报告 #4）的证据链其实比 PDF ingest 更硬**。PNAS + Frontiers 都指向"先产生困难，再给 AI"才有效——这是比对标 NotebookLM 更根本的设计原则。
3. **"Voice roleplay" 是反向踩坑**。对话式 AI 是 cognitive offloading 最严重的入口，Duolingo Max 在语言场景能成立是因为 production 本身是目标；在概念学习场景，语音聊天会把 generation 完全替换为 reception。前报告 Phase 7 #6 应该打问号。

## 二、0 → 20 用户冷启动实操

**事实基线**：Vercel 日志过去 1h 零访问 ≈ prod 只有主人自用。前报告"500 粉/50 周活"目标跨了 2-3 个量级。

**可执行路径（7 天内拿到 1-5 个真实用户）**：

1. **用自己做 case study，而不是卖产品**。Rebecca 案例：Indie Hackers 4 个月发 struggle + lesson → 67 付费用户。course-hub 的优势是主人本人正在备考——把"AI 导致考前 -17%" + "我做了一个强制 generation 的工具" 写成 1 篇 800 字小红书/V2EX/即刻 post（含 PNAS 引用 + 本人掌握度热力图截图）。这比 "Build in Public 日报 cron"（Phase 7 #7）ROI 高 10 倍。
2. **去别人的问题帖下答问题**。知乎/Reddit r/GetStudying 搜"AI 学习效果差/ChatGPT 复习不行"，每个问题回一段：引 PNAS → 讲清 generation effect → 给 course-hub 邀请链接。每天 2-3 条，1 周触达 ≥ 500 精准人。
3. **宿舍 5 人强制邀请**。不是"发链接等注册"，而是 **坐在他们旁边看他们用**——这是唯一能发现真正 UX 阻塞的方式。第一个 bug/困惑出现的位置 = 下周唯一该改的东西。
4. **不开 Product Hunt**（前报告已指出，同意）。但也 **不开小红书日报**——没有用户基数的日报是对空气讲话。

## 三、Phase 7 该砍什么

基于 exposure(E) × value(V) × cost(C) 评估。E ≈ 0 时，C < 4h 且 V ≥ 4 才值得做：

| # | 方向 | 判断 | 理由 |
|---|------|------|------|
| 1 | Supabase WARN + Vercel 漂移修 | **保留** | C=4h，V=5（阻断），无条件先做 |
| 2 | PDF ingest → FSRS 卡 | **砍** | C=3 天，E=0 时是堆功能；NotebookLM 对标是"已有用户在抱怨缺 PDF"才有意义，现在无信号 |
| 3 | 盲答强制 + 耗时入 mastery | **保留并升优先级**（从 #3 → #2） | C=1 天，V=5，证据最硬（PNAS 反证据直接支持） |
| 4 | Pretesting 每课前 2 题 | **保留并升优先级**（从 #4 → #3） | C=0.5 天，V=4，证据硬（Frontiers + Memory & Cognition） |
| 5 | Teach-back Socratic follow-up | **保留** | C=1 天，V=4 |
| 6 | Voice Notes v2 | **砍** | C=2 天，cognitive offloading 风险未评估，Chrome/Edge only 限制用户面 |
| 7 | 小红书 Build in Public 日报 cron | **砍** | C=0.5 天看似低，但 **日报对 0 粉账号是噪声**；应先手写 1 篇深度 post |
| 8 | Guest demo 账号 | **保留**（从 #8 升 #4） | C=0.5 天，V=4，无 demo 任何分发都失败 |

**删功能不等于闲着**。砍出的 3 天时间用于：写小红书长文 + 去 Reddit/知乎答问 + 约 5 位室友实测（产品内观察，不发链接）。

## 四、修正的优先级（vs 前报告）

| 顺序 | 前报告 | 本报告修正 | 差异说明 |
|------|--------|-----------|---------|
| 1 | Supabase/Vercel 修 | Supabase/Vercel 修 | 一致 |
| 2 | Guest demo (#8) | **盲答强制 (#3)** | 前报告埋没了证据最硬的项 |
| 3 | 盲答强制 (#3) | **Pretesting (#4)** | 同上 |
| 4 | PDF ingest (#2) | **Guest demo (#8)** | 先能被看见再谈高级功能 |
| 5 | Pretesting (#4) | **Socratic follow-up (#5)** | |
| 6 | Socratic follow-up (#5) | 写 1 篇 PNAS+掌握度长文 | 新增：分发而非代码 |
| 7 | Voice Notes (#6) | Reddit/知乎答问 1 周 | 新增：主动找用户 |
| — | 小红书日报 (#7) | **已砍** | 无粉发日报无意义 |
| — | PDF ingest (#2) | **暂缓** | 等 ≥ 5 真实用户要 PDF 再做 |
| — | Voice Notes (#6) | **暂缓** | offloading 风险未评估 |

**核心差异**：前报告是"功能路线图"，本报告把前 7 位的 3-4 位替换为"分发动作 + 证据最硬的小改动"。

## 五、引用（仅本次新搜）

- [PNAS: Generative AI without guardrails can harm learning](https://www.pnas.org/doi/10.1073/pnas.2422633122)
- [Wharton Knowledge: Without Guardrails, Generative AI Can Harm Education](https://knowledge.wharton.upenn.edu/article/without-guardrails-generative-ai-can-harm-education/)
- [Frontiers Psychology 2025: Cognitive paradox of AI in education](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2025.1550621/full)
- [arXiv 2510.16019: Impact of AI Tools on Learning Outcomes](https://arxiv.org/html/2510.16019)
- [Harvard Gazette 2025: Is AI dulling our minds?](https://news.harvard.edu/gazette/story/2025/11/is-ai-dulling-our-minds/)
- [Awesome Directories: Indie Hackers Launch Strategy 2025 (Rebecca case)](https://awesome-directories.com/blog/indie-hackers-launch-strategy-guide-2025/)
- [Volumetree: Feature creep killed my startup](https://www.volumetree.com/2026/03/30/feature-creep-killed-my-startup/)
