# CourseHub Status

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
- 源文件：48 个 (.ts/.tsx)
- 新增组件（未提交）：7 个
- API 路由：12 个
- 数据库表：6 张 (courses, outline_nodes, uploads, questions, attempts, study_tasks)
- 研究文档：5 份
