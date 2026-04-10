# CourseHub — API-Only Backend Skeleton

## 快速概览

| 维度 | 值 |
|------|-----|
| 框架 | Next.js 16 (App Router) — API routes only, 无前端 |
| 数据库 | Supabase PostgreSQL (项目: `zubvbcexqaiauyptsyby`) |
| 认证 | Supabase Auth (cookie-based SSR, base64url + "base64-" prefix) |
| AI | Qwen 3.5-Plus via DashScope (国内端点 `dashscope.aliyuncs.com`) |
| 部署 | Vercel (60s API timeout) |

## 当前状态

前端已全部删除（2026-04-09），只保留 34 个 API routes + 后端 lib。等待前端重建。

## 目录结构

```
src/
  app/
    layout.tsx          ← 空壳（Next.js 必须有）
    api/                ← 34 个 API routes
      courses/          ← CRUD + outline + generate + exams + exam-prep + exam-scope + share + ...
      questions/        ← GET/POST + quality-check + feedback
      attempts/         ← 答题提交 + 自动批改
      parse/            ← 大纲/考试文本解析
      bookmarks/        ← 题目收藏
      upload/           ← 文件上传
      outline-nodes/    ← 大纲节点 CRUD
      preview/          ← 学习预览
  lib/
    ai.ts               ← AI 调用入口（Qwen wrapper + extractJSON balanced-brace parser）
    schemas.ts           ← Zod schema（AI 输出校验，answer 支持 string/number/boolean/object）
    mastery-v2.ts        ← FSRS 掌握度计算
    mastery.ts           ← 旧版掌握度
    spaced-repetition.ts ← 间隔重复调度
    rate-limit.ts        ← API 限流
    course-notes.ts      ← 笔记处理
    supabase/            ← client.ts / server.ts / middleware.ts
  types.ts              ← TypeScript 类型定义
tests/
  e2e-backend.ts        ← 端到端 API 测试（3 场景）
  ai-benchmark/         ← 多模型质量对比框架
```

## 数据模型

```
User → Course → OutlineNode (tree, parent_id) → knowledge_point → ElementMastery (FSRS)
                 ├── Question → Attempt (自动批改)
                 ├── StudyTask (AI 生成)
                 ├── Lesson → LessonChunk → LessonProgress
                 ├── ExamDate (考试日期 + KP 关联)
                 ├── Upload → AI 内容提取
                 ├── CourseNote (语音笔记 → AI 整理)
                 └── ShareToken
```

## 已知约束

- **Vercel 60s timeout**: AI 生成必须控制批次（generate-questions: 5 KP/call, exam-prep: 6 topics/call）
- **DashScope 国内端点**: API key 是国内区域的，必须用 `dashscope.aliyuncs.com` 不是 `-intl`
- **Qwen 只支持 Chat Completions API**: 必须用 `qwen.chat("model-name")`，不是 `qwen("model-name")`（后者默认走 /responses 端点，Qwen 不支持）
- **Qwen 的 json_schema response_format 要求 prompt 里必须出现 "json" 字样** — 否则报错 `'messages' must contain the word 'json'`
- **Qwen OpenAI compat 不接受 `type: "file"` content block**: 只支持 text/image_url/video。PDF 必须服务端 pdf-parse 提取文本后再发给 text model
- **questions.flagged 列不存在**: migration 014 未应用，quality-check 和 feedback 路由会 500
- **Supabase SSR cookie**: 格式为 base64url + "base64-" prefix，chunk at 3180 chars
- **regenerate/exam-prep 本地 dev 会 timeout**: 这些路由需要翻译或生成大量内容，本地 Next.js dev 很慢。生产环境 Vercel 60s 限制下也可能挂

## 已修复的 Bug（2026-04-09 ~ 2026-04-10）

1. outline PUT 409: 新课程首次保存版本冲突 → 跳过空课程检查
2. questions.flagged: 查询引用不存在的列 → 移除 flagged 过滤
3. extractJSON 贪婪正则: AI 输出后追加文本 → balanced-brace parser
4. answer schema 类型: AI 返回 number/object/null → z.unknown + transform
5. exam-prep timeout: 12 topics batch 4 → 6 topics batch 3
6. **Chat 500 → streaming**: `/chat` 返回 SSE stream，测试端需用 `text/event-stream` 处理
7. **Feedback FK 违反**: 问题 ID 过期 → scenario 9 改为从 DB 直接 re-fetch
8. **Cleanup 401**: JWT 长任务后过期 → 改用 `supabaseAdmin` 直接删除
9. **AI JSON 解析 escape 错误**: LaTeX `\frac` 等破坏 JSON.parse → `sanitizeJSONEscapes` + `safeJSONParse` 回退
10. **Qwen 模型调用方式错误**: `qwen("xxx")` 默认走 Responses API → 改用 `qwen.chat("xxx")`
11. **Extract 路由的文件格式**: 原来用 `type: "file"` content block（Qwen 不支持）+ `qwen-plus-latest` 是纯文本模型 → 改用 `pdf-parse` 服务端提取文本 + `qwen3.5-plus`
12. **Qwen `response_format: json_schema` 要求 "json"**: prompt 里补上 "Return JSON"

## E2E 测试覆盖（47/52 routes 通过）

**全部通过 (11 个 scenario)**:
- Scenario 1: Create course → Parse syllabus → Save outline → Generate questions → List
- Scenario 2: Create exam → Match scope → Exam prep (timeout on dev)
- Scenario 3: Submit attempts (correct + wrong) → Check mastery
- Scenario 4: Bookmarks CRUD → Chat (streaming) → Get exams
- Scenario 5: Course CRUD → Outline node CRUD → Study task PATCH
- Scenario 6: Share token → Fork course → Revoke share
- Scenario 7: Generate lesson (AI) → List → Get chunks → Progress tracking
- Scenario 8: Organize note (AI) → Save note
- Scenario 9: Feedback (×3) → Quality check → Mistake patterns → Anki export → Delete exam
- Scenario 10: Upload PDF → List → Extract (AI with pdf-parse) → Delete → Preview learning
- Scenario 11: Generate study tasks → Regenerate (AI heavy, dev timeout)

**已知不稳定**:
- `exam-prep`: 本地 dev 6 topics × 3 parallel AI calls > 2min，Vercel 生产环境 60s hard limit 可能挂
- `regenerate`: 翻译 30+ KPs + 生成 tasks/questions，本地 dev 通常 > 3min timeout
- 这两个路由需要异步化（Trigger.dev 或类似）才能在生产环境可靠
