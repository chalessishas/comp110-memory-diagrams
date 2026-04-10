# CourseHub Status

## [2026-04-10 04:42] Phase 5 — User-Requested Features (4 of 4 done ✓)

User's 4-feature request during exam prep sprint. All complete: exam scope filter → term cards → daily report → cross-course org (due-count badges).

### Dashboard Due-Count Badges (Feature 4) — Done [2026-04-10]
- `CourseCard.tsx` → client component; reads FSRS localStorage via `loadCards()` + `getDueCards()`
- `questionIds?: string[]` prop: server fetches question IDs by course, passes down to client
- Orange badge appears when `dueCount > 0`; 0-due cards show nothing (no visual noise)
- `dashboard/page.tsx`: single batch `questions` query grouped by course_id — no N+1 requests

### RLS Performance (014_rls_performance.sql) — Applied [2026-04-10]
- 8 tables updated: `auth.uid()` → `(select auth.uid())` in USING/WITH CHECK clauses
- Postgres now caches auth.uid() per statement instead of re-evaluating per row
- Biggest impact on `element_mastery`, `attempts`, `courses` (high row-count tables)

### Session Summary Modal (Feature 3) — Done [2026-04-10]
- `GET /api/courses/[id]/mastery-summary?since=ISO` — returns KPs where `level_reached_at >= since`
- `SessionSummaryModal.tsx` — shows session stats (questions/accuracy/time), streak 7-day grid, mastery level-ups, tomorrow preview
- Triggered from `review/page.tsx` when queue exhausts or ≥1 question answered
- No schema changes — reads existing `element_mastery` table via RLS-protected API

### Exam Scope Filter (Feature 1)
- `/api/courses/[id]/exam-scope/route.ts`: AI matches scope text to course KP IDs
- `spaced-repetition.ts`: `getExamScope()` / `setExamScope()` — per-course localStorage
- `review/page.tsx`: Scope banner, textarea input, filtered review queue
- Zero schema changes — scope stored client-side (temporary by nature)

### Term Explanation Cards (Feature 4)
- AI prompt updated: each chunk now outputs 2-5 `key_terms: [{term, definition}]`
- `TermTooltip.tsx`: Click underlined term → popover with definition (auto-positions above/below)
- `MarkdownRenderer.tsx`: Recursive `highlightTerms()` walks React children, wraps matches, skips code/math
- `lesson_chunks.key_terms` JSONB column added via migration
- Works for both CJK and Latin terms (no `\b` word-boundary dependency)

## [2026-04-07 13:50] Phase 4 — Evidence-Based Optimization (5 commits, all deployed)

Exam in 3 days (Apr 10). Applied evidence-based teaching research to existing architecture.

### SSE Streaming for Lesson Generation
- `generate-one/route.ts`: New streaming path (`stream: true`), events: outline → lesson → chunk → done
- `learn/page.tsx`: SSE consumer with `ReadableStream` reader, progressive chunk rendering
- `ChunkLesson.tsx`: `totalChunks` + `isStreaming` props, loading state between chunks
- Result: First chunk visible in ~5s vs ~15s full-page blank wait

### FSRS Exam-Day Retrievability Sort
- `getExamPriorityCards()`: Predicts per-card recall on exam date via `get_retrievability(card, examDate)`
- Cards sorted ascending (weakest first), new cards (reps===0) get retrieval=0 (highest priority)
- Cards ≥0.95 predicted recall skipped — time better spent on weak spots
- UI: per-card exam-day recall badge (red/yellow/green)

### Evidence-Based Interleaving
- `interleaveByKey()`: Bounded-lookahead greedy (window=5) interleaves cards by knowledge point
- Preserves FSRS weakest-first priority while avoiding same-KP adjacency
- Based on Brunmair & Richter 2019 meta-analysis (g=0.42 for interleaving)

### Concreteness Fading Prompts
- Lesson outline prompt: 4 chunks follow concrete → numerical → symbolic → transfer
- Per-chunk abstraction level instruction injected into generation prompt
- Based on Fyfe, McNeil & Borjas 2015

### Bug Fix: Exam Mode Re-sort
- Split useEffect into fetch (depends `[id]`) + sort (depends `[questions, examActive]`)
- Toggling exam mode now immediately re-sorts queue without page reload

### Research Produced
- `docs/research/2026-04-07-exam-countdown.md` — FSRS migration, monitoring, exam strategies
- `docs/research/2026-04-07-competitor-analysis.md` — 秘塔/NotebookLM/Anti-Gravity/Khanmigo comparison
- `docs/research/2026-04-07-evidence-based-analysis.md` — Full paper mapping (5 aligned mechanisms, 8 gaps, prioritized actions)

### Known Issues
- SRS data still in localStorage (Supabase migration deferred to post-exam)
- No adaptive difficulty (85% rule) — #1 post-exam priority
- SSE streaming untested with live AI call (build passes, deploy healthy)
- Vercel Git integration still broken (manual deploy)

## [2026-04-06 12:50] Phase 3 — Exam Prep Overhaul (11 commits, all deployed)

Calculus II midterm on April 10. Major improvements to learning system for exam readiness.

### FSRS Exam Mode
- `spaced-repetition.ts`: Lazy scheduler with exam-date-aware params (`retention=0.95`, `maximum_interval=daysToExam`)
- Review page: exam date picker UI, countdown banner ("考试模式 · N 天后考试")
- Boundary fix: exam mode stays active on exam day (`days >= 0`)

### Exam Prep Pipeline (12 topics, parallel)
- `exam-prep/route.ts`: Increased from 4→12 topic limit, parallel batches of 4 via `Promise.allSettled`
- Switched to `qwen3.5-plus` (19x faster than qwen-plus-latest)
- Fuzzy KP matching (substring containment fallback)
- `topics_failed` returned in API response
- Practice page: error handling, failed topics banner, Chinese i18n

### Interactive Lessons
- `ChunkLesson.tsx`: Progress tracking (useRef + useEffect → POST lesson_progress), remediation skip button, pretest remediation content fix
- `progress/route.ts` (new): Saves lesson completion + bumps element_mastery
- `learn/page.tsx`: refreshKey pattern for re-fetching mastery after lesson, error banner on generation failure

### Grading & Model
- `attempts/route.ts`: Fuzzy fill_blank grading (contains + numeric), normalized input
- `ChunkLesson.tsx`: Grading threshold aligned to 0.5, remediation_answer used correctly
- All text routes → `qwen3.5-plus` (exam-prep, regenerate, chat). Vision routes stay `qwen-plus-latest`

### Known Issues
- Vercel Git integration not auto-deploying (manual `npx vercel deploy --prod` works)
- SRS data in localStorage only (no cross-device sync)
- qwen3.5-plus untested with live AI call (build passes, zero runtime errors)

### DB Changes (prod Supabase)
- `lesson_chunks.checkpoint_type` constraint updated to include `fill_blank`
- 5 new outline_nodes (power series week + 4 KPs)
- 38 questions inserted, 12 orphans linked to KPs, 6 true_false fixed

## [2026-04-04 06:53] Phase 2 — UI 重构 + 新功能（未提交）

另一个 session 在 MVP 基础上做了大量改进（+2005 行，27 个文件修改，7 个新文件），尚未 commit：

### UI/UX 全面重构
- **设计系统重做**：从暖金色调（#c4a97d accent）切换到极简黑白灰（#101010 accent）。新增 radial-gradient 背景、frosted glass 卡片（backdrop-filter: blur）、更大圆角（28px）
- **登录页重构**：新增 Sign In / Create Account 双 tab 切换、auth error 展示（带 `AUTH_ERROR_MESSAGES` 映射）、`Suspense` boundary
- **新课流程增强**：新增 paste 模式（粘贴文本直接解析，不需要上传文件）、guest 模式预览（未登录也能试用 AI 解析）、preview 阶段展示 AI 生成的学习任务 + 题目预览
- **Dashboard 增强**：可能有新的卡片样式和布局

### 新功能：语音笔记 (Voice Notes)
- `src/components/VoiceNotesPanel.tsx` (595 行) — 浏览器端语音识别（SpeechRecognition API），支持录音转文字
- `src/app/course/[id]/notes/page.tsx` — Notes tab 页面
- `src/app/api/courses/[id]/notes/route.ts` — Notes CRUD API
- `src/app/api/courses/[id]/notes/organize/route.ts` — AI 整理笔记 API
- `src/lib/course-notes.ts` — 笔记数据层（CourseNoteRow 转换 + payload 构建）
- 支持：录音 → 转文字 → AI 提取重点/疑问 → 关联知识点 → 问答澄清

### 新功能：学习追踪器 (Study Tracker)
- `src/components/StudyTrackerPanel.tsx` (227 行) — 实时学习计时器
- `src/lib/study-tracker.ts` (134 行) — localStorage 持久化，按 mode 分类（solving/reviewing/studying/idle），20 秒闲置自动检测
- 按课程分别统计学习时长

### 新功能：错题本 (Wrong Answer Notebook)
- `src/components/WrongAnswerNotebook.tsx` (139 行) — 错题列表，展示最近答错的题目 + 正确答案 + 解析
- 支持标记 "needs_redo" / "fixed" 状态

### 新功能：学习蓝图 (Learning Blueprint)
- `src/components/LearningBlueprint.tsx` (131 行) — 知识点级别的学习建议卡片
- 展示每个知识点的掌握度、任务数、题目数、下一步建议

### 新功能：学习预览 API
- `src/app/api/preview/learning/route.ts` — 未登录用户也能预览 AI 生成结果

### 扩展的类型系统
- 新增类型：`StudyMode`, `NoteSource`, `CourseNote`, `OrganizedStudyNote` 等
- schemas.ts 新增笔记相关 Zod schema

---

## [2026-04-04 00:00] Qwen3.5-Plus + 自动 Pipeline
- 切换 AI 从 GPT-4.1 nano 到 Qwen3.5-Plus (DashScope OpenAI 兼容 API)
- 新增 Pipeline 3: 大纲 → 学习任务自动拆解 (read/practice/review × 优先级)
- 新增 Pipeline 4: 大纲 → 自动出题 (无需上传考卷)
- 新增 study_tasks 表 + RLS + generate API
- 新增 Study Tasks UI (进度条 + 优先级分组 + 勾选完成)
- 新课创建后自动触发 pipeline (fire-and-forget)

## [2026-04-03 23:06] Supabase 配置
- 创建 Supabase 项目 `course-hub` (us-east-1)
- 运行 001_initial_schema.sql + 002_study_tasks.sql
- .env.local 配置完成 (URL + anon key + service_role + DashScope key)
- 邮箱密码登录已加入（不依赖 Google OAuth）
- Dev server 可运行 (localhost:3002)

## [2026-04-03 02:47] MVP 代码完成
- 17 tasks, 15 commits, 35 源文件
- Next.js 16 + Supabase + Tailwind v4 + Zod + react-arborist + react-dropzone + Lucide
- 功能：Google/邮箱登录 → 多课仪表盘(归档) → 上传 syllabus(AI 解析大纲) → 上传真题(AI 出题) → 做题(即时反馈) → 掌握度热力图
- 5 张表 + RLS + Storage bucket

## [2026-04-03 02:04] 设计 + 调研完成
- 设计规格：`docs/superpowers/specs/2026-04-03-course-hub-design.md`
- 竞品分析：15+ 产品对比，三合一功能零直接竞品
- 技术选型：react-arborist, react-dropzone, adjacency list, RLS
- AI 成本对比：17 个模型，GPT-4.1 nano 最便宜，Qwen3.5-Plus 最优 vision
- 国产模型：22 个模型对比，推荐 Qwen3.5-Plus + Doubao Mini + GLM-4.7-Flash(免费)
- 部署研究：Vercel AI SDK 集成、学生产品分发、Supabase 部署模式

## 文件统计 (当前)
- 源文件：~60 个 (.ts/.tsx)
- API 路由：18+ 个 (including lessons/progress, exam-prep, generate-one)
- 数据库表：10+ 张 (+ lessons, lesson_chunks, lesson_progress, element_mastery, exam_dates)
- 数据库迁移：12 个 SQL 文件
- 研究文档：8+ 份 (docs/research/)
