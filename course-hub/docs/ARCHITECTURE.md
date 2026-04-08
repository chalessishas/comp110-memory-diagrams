# CourseHub 架构文档

> AI 驱动的课程管理与自适应学习平台。上传课程大纲，自动生成知识树、练习题、学习计划和间隔复习系统。

---

## 1. 技术栈

### 核心框架

| 依赖 | 版本 | 用途 |
|------|------|------|
| `next` | 16.2.2 | App Router 全栈框架，SSR + API Routes |
| `react` / `react-dom` | 19.2.4 | UI 渲染（React 19，支持 Server Components） |
| `typescript` | ^5 | 类型系统 |

### 后端与数据

| 依赖 | 版本 | 用途 |
|------|------|------|
| `@supabase/supabase-js` | ^2.101.1 | Supabase 客户端（Auth + DB + Storage） |
| `@supabase/ssr` | ^0.10.0 | Next.js SSR 环境下的 Supabase Cookie 管理 |
| `zod` | ^4.3.6 | 运行时数据校验（API 入参、AI 输出解析） |

### AI 集成

| 依赖 | 版本 | 用途 |
|------|------|------|
| `ai` | ^6.0.145 | Vercel AI SDK 核心（`generateText`） |
| `@ai-sdk/openai` | ^3.0.50 | OpenAI 兼容适配器（实际连接 DashScope） |
| `@ai-sdk/react` | ^3.0.148 | React hooks（`useChat` 等） |

### 学习算法

| 依赖 | 版本 | 用途 |
|------|------|------|
| `ts-fsrs` | ^5.3.2 | FSRS 间隔复习算法（Free Spaced Repetition Scheduler） |

### UI 与渲染

| 依赖 | 版本 | 用途 |
|------|------|------|
| `tailwindcss` | ^4 | 原子化 CSS |
| `@tailwindcss/postcss` | ^4 | Tailwind PostCSS 插件 |
| `lucide-react` | ^1.7.0 | 图标库 |
| `react-markdown` | ^10.1.0 | Markdown 渲染 |
| `remark-gfm` | ^4.0.1 | GFM 语法支持（表格、任务列表等） |
| `remark-math` | ^6.0.0 | LaTeX 数学公式解析 |
| `rehype-katex` | ^7.0.1 | KaTeX 数学公式渲染 |
| `rehype-highlight` | ^7.0.2 | 代码语法高亮 |
| `react-dropzone` | ^15.0.0 | 文件拖拽上传 |

### 构建配置

```ts
// next.config.ts
experimental: {
  viewTransition: true,  // 启用 View Transitions API
}
```

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2017",
    "paths": { "@/*": ["./src/*"] }  // 路径别名
  }
}
```

---

## 2. 目录结构

```
src/
├── app/                    # Next.js App Router（路由 + API）
│   ├── api/                # 所有后端 API Routes
│   ├── auth/callback/      # OAuth 回调处理
│   ├── course/[id]/        # 课程详情页（多子路由）
│   ├── dashboard/          # 仪表盘 + 题库
│   ├── join/[token]/       # 课程分享加入页
│   ├── login/              # 登录/注册页
│   ├── new-course/         # 新建课程向导
│   ├── settings/           # 用户设置
│   ├── layout.tsx          # 根布局（I18nProvider + OnboardingGate）
│   ├── page.tsx            # / → redirect /dashboard
│   └── globals.css         # 全局样式变量 + Tailwind 入口
│
├── components/             # 所有 React 组件（扁平结构，无子目录）
│   ├── ChunkLesson.tsx     # 交互式分块课程
│   ├── CourseCard.tsx       # 课程卡片
│   ├── CourseTabs.tsx       # 课程页标签导航
│   ├── ExamCountdown.tsx    # 考试倒计时
│   ├── KnowledgeTree.tsx    # SVG 知识树可视化
│   ├── LearningBlueprint.tsx # 学习蓝图
│   ├── MarkdownRenderer.tsx # Markdown + LaTeX + 代码高亮渲染器
│   ├── MistakePatterns.tsx  # 错题模式分析
│   ├── OnboardingGate.tsx   # 新用户引导门控
│   ├── OnboardingWizard.tsx # 引导向导
│   ├── ProfileView.tsx      # 掌握度画像
│   ├── QuestionCard.tsx     # 答题卡（支持选择/填空/简答）
│   ├── StudyBuddy.tsx       # AI 聊天学习伙伴
│   ├── TodayView.tsx        # 今日任务视图
│   ├── TermTooltip.tsx      # 术语悬浮提示
│   └── ...                  # 其他 30+ 组件
│
├── lib/                    # 核心业务逻辑与工具
│   ├── ai.ts               # AI Pipeline 封装（6 条管线）
│   ├── schemas.ts           # Zod 校验 schema（含 AI 输出容错）
│   ├── i18n.tsx             # 国际化上下文 + 翻译字典
│   ├── rate-limit.ts        # 内存级 Rate Limiter
│   ├── spaced-repetition.ts # FSRS 间隔复习（localStorage）
│   ├── study-tracker.ts     # 学习时间追踪（localStorage）
│   ├── streaks.ts           # 学习连续天数（localStorage）
│   ├── mastery.ts           # V1 掌握度计算
│   ├── mastery-v2.ts        # V2 掌握度（5 级精细化）
│   ├── onboarding.ts        # 新用户引导状态（localStorage）
│   ├── usage-tracker.ts     # AI token 用量统计（localStorage）
│   ├── tracked-fetch.ts     # 包装 fetch 自动追踪 token 用量
│   ├── course-notes.ts      # 课程笔记工具函数
│   └── supabase/
│       ├── client.ts        # 浏览器端 Supabase 客户端
│       ├── server.ts        # 服务端 Supabase 客户端（读 cookies）
│       └── middleware.ts    # 中间件 session 刷新
│
└── types.ts                # 所有领域类型定义
```

---

## 3. 路由地图

### 页面路由

| 路由 | 文件 | 渲染模式 | 说明 |
|------|------|----------|------|
| `/` | `app/page.tsx` | SSR | `redirect("/dashboard")` |
| `/dashboard` | `app/dashboard/page.tsx` | CSR | 课程列表 + 今日概览 |
| `/dashboard/bank` | `app/dashboard/bank/page.tsx` | CSR | 跨课程题库收藏 |
| `/login` | `app/login/page.tsx` | CSR | 邮箱/Google 登录注册 |
| `/new-course` | `app/new-course/page.tsx` | CSR | 新建课程向导（3 步） |
| `/settings` | `app/settings/page.tsx` | CSR | 用户偏好、数据导出 |
| `/join/[token]` | `app/join/[token]/page.tsx` | CSR | 通过分享链接加入课程 |
| `/course/[id]` | `app/course/[id]/page.tsx` | CSR | 课程主页（Today 视图） |
| `/course/[id]/learn` | `app/course/[id]/learn/page.tsx` | CSR | AI 生成课程（分块交互式） |
| `/course/[id]/practice` | `app/course/[id]/practice/page.tsx` | CSR | 练习题 |
| `/course/[id]/review` | `app/course/[id]/review/page.tsx` | CSR | FSRS 间隔复习 |
| `/course/[id]/tree` | `app/course/[id]/tree/page.tsx` | CSR | 知识树可视化 |
| `/course/[id]/progress` | `app/course/[id]/progress/page.tsx` | CSR | 知识点掌握度 |
| `/course/[id]/library` | `app/course/[id]/library/page.tsx` | CSR | 课程资料库 |
| `/course/[id]/notes` | `app/course/[id]/notes/page.tsx` | CSR | 语音/文字笔记 |
| `/course/[id]/profile` | `app/course/[id]/profile/page.tsx` | CSR | 掌握度画像 |

### API 路由

| 路由 | 方法 | 说明 |
|------|------|------|
| `POST /api/parse` | POST | AI 解析大纲文件（PDF/图片） |
| `POST /api/preview/learning` | POST | 游客模式预览学习内容 |
| `GET/POST /api/courses` | GET, POST | 课程 CRUD |
| `GET/PUT/DELETE /api/courses/[id]` | GET, PUT, DELETE | 单课程操作 |
| `GET /api/courses/[id]/outline` | GET | 获取课程大纲树 |
| `POST /api/courses/[id]/generate` | POST | AI 生成课程内容（课件+任务+题目） |
| `POST /api/courses/[id]/generate-questions` | POST | AI 生成练习题 |
| `POST /api/courses/[id]/regenerate` | POST | 重新生成课程内容 |
| `GET/POST /api/courses/[id]/lessons` | GET, POST | 课程课件管理 |
| `POST /api/courses/[id]/lessons/generate-one` | POST | 单知识点课件生成 |
| `GET /api/courses/[id]/lessons/[lessonId]/chunks` | GET | 获取课件分块内容 |
| `GET/POST /api/courses/[id]/lessons/[lessonId]/progress` | GET, POST | 课件学习进度 |
| `POST /api/courses/[id]/chat` | POST | AI Study Buddy 对话 |
| `GET/POST /api/courses/[id]/notes` | GET, POST | 课程笔记 |
| `POST /api/courses/[id]/notes/organize` | POST | AI 整理笔记 |
| `POST /api/courses/[id]/uploads` | POST | 文件上传（试卷等） |
| `POST /api/courses/[id]/extract` | POST | AI 提取上传文件内容 |
| `GET/POST /api/courses/[id]/exams` | GET, POST | 考试日期管理 |
| `GET /api/courses/[id]/exam-prep` | GET | 考前复习任务生成 |
| `GET/POST /api/courses/[id]/exam-scope` | GET, POST | 考试范围标注 |
| `GET /api/courses/[id]/mastery` | GET | 获取掌握度数据 |
| `GET /api/courses/[id]/mistake-patterns` | GET | 错题模式分析 |
| `GET /api/courses/[id]/share` | GET | 生成课程分享链接 |
| `POST /api/courses/[id]/export-anki` | POST | 导出 Anki 卡组 |
| `POST /api/courses/fork` | POST | Fork 分享课程到自己账号 |
| `GET/POST /api/questions` | GET, POST | 题目 CRUD |
| `POST /api/questions/[id]/feedback` | POST | 题目质量反馈 |
| `POST /api/attempts` | POST | 提交答题记录 |
| `GET/POST/DELETE /api/bookmarks` | GET, POST, DELETE | 题目收藏 |
| `GET/POST /api/outline-nodes` | GET, POST | 大纲节点 CRUD |
| `PUT/DELETE /api/outline-nodes/[id]` | PUT, DELETE | 单节点操作 |
| `GET/POST /api/study-tasks` | GET, POST | 学习任务 |
| `PUT /api/study-tasks/[id]` | PUT | 更新任务状态 |
| `POST /api/upload` | POST | 通用文件上传 |
| `GET /auth/callback` | GET | OAuth 回调（code → session） |

---

## 4. 数据流

### 完整请求链路

```
浏览器 (React CSR)
  ↓ fetch / trackedFetch
Next.js API Route (app/api/*)
  ↓ createClient() (server-side Supabase)
  ↓ Zod schema 校验入参
  ↓ 业务逻辑
  ├──→ Supabase PostgreSQL (数据读写)
  ├──→ Supabase Storage (文件存储)
  └──→ DashScope API (AI 推理)
       ↓ Zod schema 校验 AI 输出
       ↓ extractJSON() 容错提取
  ↓ JSON Response
浏览器
  ↓ 状态更新 + 重新渲染
```

### AI Pipeline 管线（src/lib/ai.ts）

| 管线 | 函数 | 模型 | 输入 | 输出 |
|------|------|------|------|------|
| Pipeline 1 | `parseSyllabus` | `qwen-plus-latest`（视觉） | PDF/图片 base64 | `ParsedSyllabus`（课程结构树） |
| Pipeline 1b | `parseSyllabusText` | `qwen3.5-plus`（文本） | 纯文本大纲 | `ParsedSyllabus` |
| Pipeline 2 | `parseExamQuestions` | `qwen-plus-latest`（视觉） | 试卷 PDF + 知识点列表 | `ParsedQuestion[]` |
| Pipeline 3 | `generateStudyTasks` | `qwen3.5-plus` | 课程名 + 知识点 | `StudyTask[]` |
| Pipeline 4 | `generateQuestionsFromOutline` | `qwen3.5-plus` | 课程名 + 知识点 | `ParsedQuestion[]` |
| Pipeline 5 | `generateLesson` | `qwen3.5-plus` | 知识点 + 课程上下文 | 课件 Markdown |
| Pipeline 5b | `generateLessonChunks` | `qwen3.5-plus` | 知识点 | 分块交互式课件（Concreteness Fading） |
| Pipeline 6 | `organizeStudyNote` | `qwen3.5-plus` | 语音/文字笔记 + 知识点 | `OrganizedStudyNote` |

### AI 输出容错策略

```
AI 原始输出 (text)
  ↓ stripThinkBlocks() — 移除 qwen3.5 的 <think>...</think> 泄漏
  ↓ extractJSON() — 去除 markdown 代码围栏，正则提取 JSON 对象或数组
  ↓ JSON.parse()
  ↓ Zod schema.parse() — 宽松解析：
      - 类型字段模糊匹配（"MCQ" → "multiple_choice"）
      - 数值范围钳位（difficulty 钳位至 1-5）
      - 单值自动包装数组（string → [string]）
      - null 默认值填充
```

---

## 5. 认证体系

### 架构概览

```
浏览器请求
  ↓
Next.js Middleware (src/middleware.ts)
  ↓ updateSession() — 刷新 Supabase Auth cookie
  ↓ 匹配所有路由（排除静态资源）
  ↓
API Route / Page
  ↓ createClient() (server)
  ↓ supabase.auth.getUser() — 验证身份
```

### Middleware 配置

```ts
// src/middleware.ts
export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)"
  ],
};
```

中间件对**所有非静态资源请求**运行，调用 `updateSession()` 刷新 Supabase Auth 的 cookie token。不做路由拦截——未登录用户也能访问所有页面。

### 认证方式

| 方式 | 实现 |
|------|------|
| 邮箱 + 密码 | `supabase.auth.signUp()` / `signInWithPassword()` |
| Google OAuth | `supabase.auth.signInWithOAuth({ provider: "google" })` |
| OAuth 回调 | `/auth/callback` — `exchangeCodeForSession(code)` |

### 保护策略

**不使用路由级保护**。API 层面在需要时检查 `supabase.auth.getUser()`：
- 已登录用户：数据绑定 `user_id`，持久化到 Supabase
- 游客用户：功能完全可用，数据仅存 localStorage，支持后续登录后合并

---

## 6. AI 集成

### 模型配置

```ts
// src/lib/ai.ts
const qwen = createOpenAI({
  baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1",
  apiKey: process.env.DASHSCOPE_API_KEY,
});

const visionModel = qwen("qwen-plus-latest");   // 多模态（PDF/图片解析）
const textModel  = qwen("qwen3.5-plus");         // 纯文本（MoE, 17B 活跃参数，19x 快于 qwen-plus）
```

| 模型 | 用途 | 定价（每 M token） |
|------|------|---------------------|
| `qwen-plus-latest` | PDF/图片解析（Pipeline 1, 2） | $0.26 / $1.56 (input/output) |
| `qwen3.5-plus` | 文本生成（Pipeline 1b, 3-6） | 更低成本，MoE 架构 |

### 调用方式

使用 Vercel AI SDK 的 `generateText()` 函数，**非流式**。通过 `@ai-sdk/openai` 的 OpenAI 兼容层连接阿里云 DashScope API。

### Rate Limit

```ts
// src/lib/rate-limit.ts — 内存级限流
checkRateLimit(key: string, maxRequests = 5, windowMs = 60_000): boolean
```

- 默认：每 key **5 次/分钟**
- 基于 `Map` 的内存计数器，进程重启清零
- Vercel Serverless 环境下每个实例独立计数

### 限制

| 约束 | 值 | 说明 |
|------|-----|------|
| 文件大小上限 | ~15MB（20MB base64） | `MAX_BASE64_SIZE = 20 * 1024 * 1024` |
| AI 超时 | 55s | `AI_TIMEOUT_MS = 55_000`（当前已临时禁用 AbortSignal） |
| Think 块处理 | 自动剥离 | `stripThinkBlocks()` 移除 `<think>` 标签 |

### Token 追踪

```ts
// 客户端 trackedFetch() 从响应头读取 token 计数
// API Route 设置 x-input-tokens / x-output-tokens 响应头
// 写入 localStorage "coursehub.usage" 按天汇总
```

---

## 7. 国际化

### 实现方式

**纯前端字典方案**，无第三方 i18n 库。

```
I18nProvider (React Context)
  ↓ localStorage.getItem("coursehub.locale")
  ↓ translations[locale][key] ?? key  (fallback 为 key 本身)
```

### 支持语言

| 代码 | 语言 | 覆盖键数 |
|------|------|----------|
| `en` | English | ~200 |
| `zh` | 简体中文 | ~200 |

### 翻译键规范

```
命名空间.具体键
```

| 前缀 | 作用域 |
|------|--------|
| `nav.*` | 导航栏 |
| `dashboard.*` | 仪表盘 |
| `newCourse.*` | 新建课程 |
| `gen.*` | AI 生成进度 |
| `outline.*` | 大纲类型标签 |
| `tabs.*` | 课程页标签 |
| `today.*` | 今日任务 |
| `profile.*` | 掌握度画像 |
| `learn.*` | 学习视图 |
| `practice.*` | 练习 |
| `review.*` | 间隔复习 |
| `settings.*` | 设置页 |
| `login.*` | 登录/注册 |
| `exam.*` | 考试倒计时 |
| `streak.*` | 连续打卡 |
| `misc.*` | 通用文案 |

### 使用方式

```tsx
import { useI18n } from "@/lib/i18n";

function MyComponent() {
  const { t, locale, setLocale } = useI18n();
  return <h1>{t("dashboard.title")}</h1>;
}
```

### AI 输出国际化

AI 管线接受 `language?: string` 参数，在 prompt 中注入语言指令，生成对应语言的课程内容、题目和笔记。

---

## 8. 状态管理

### localStorage vs Supabase 分工

| 数据 | 存储位置 | localStorage Key | 说明 |
|------|----------|------------------|------|
| 课程/大纲/题目 | **Supabase** | — | 核心业务数据，登录后持久化 |
| 答题记录 | **Supabase** | — | `attempts` 表 |
| 课程笔记 | **Supabase** | — | `course_notes` 表 |
| 课件进度 | **Supabase** | — | `lesson_progress` 表 |
| 掌握度数据 | **Supabase** | — | `element_mastery` 表 |
| 间隔复习卡 | **localStorage** | `coursehub.review-cards` | FSRS 卡片状态（ts-fsrs） |
| 考试日期 | **localStorage** | `coursehub.exam-date` | 触发复习参数调整 |
| 考试范围 | **localStorage** | `coursehub.exam-scope` | 每课程知识点 ID 列表 |
| 学习时间 | **localStorage** | `coursehub.study-tracker` | 按天按模式统计（ms） |
| 连续打卡 | **localStorage** | `coursehub.streaks` | 天数、冻结次数、历史 |
| 语言设置 | **localStorage** | `coursehub.locale` | `"en"` / `"zh"` |
| 引导状态 | **localStorage** | `coursehub.onboarding` | 角色、学期、目标 |
| AI 用量统计 | **localStorage** | `coursehub.usage` | 按天 token 计数 |

### 设计原则

- **核心学习数据** → Supabase（跨设备同步、登录后持久）
- **本地偏好与统计** → localStorage（零延迟、离线可用、游客模式支持）
- 游客模式下所有数据存 localStorage，登录后核心数据写入 Supabase

---

## 9. 关键约束

### Vercel 部署限制

| 约束 | 限制值 | 影响 |
|------|--------|------|
| Serverless 函数超时 | **60s**（Pro 计划） | AI 生成课件需在 55s 内完成 |
| Request Body 大小 | **4.5MB** | PDF 上传需先 base64 编码，限制实际文件 ~3.3MB |
| Response Body 大小 | **4.5MB** | 大批量课件生成需分页 |
| Edge Function 超时 | 30s | 中间件必须轻量 |
| 冷启动 | ~500ms | 首次请求延迟 |

### AI 相关限制

| 约束 | 值 | 缓解措施 |
|------|-----|----------|
| 文件 base64 上限 | ~15MB | 前端校验 + 错误提示 |
| AI 超时 | 55s | `AI_TIMEOUT_MS`（当前 AbortSignal 已临时禁用） |
| 输出非 JSON | 常见 | `extractJSON()` + `stripThinkBlocks()` 容错 |
| 类型字段不一致 | 常见 | Zod transform 宽松解析 |
| Think 块泄漏 | qwen3.5 特有 | 自动剥离 `<think>` 标签 |

### 性能约束

| 约束 | 说明 |
|------|------|
| Rate Limit 内存级 | Serverless 实例间不共享，重启清零 |
| 无 CDN 缓存 | API 响应不缓存，每次实时计算 |
| 无 WebSocket | 所有通信为 HTTP 请求-响应 |
| localStorage 大小 | 浏览器限制 ~5-10MB，大量复习卡可能溢出 |

### 安全约束

| 项目 | 状态 |
|------|------|
| RLS (Row Level Security) | 依赖 Supabase RLS 策略限制数据访问 |
| API 鉴权 | 通过 `supabase.auth.getUser()` 验证，非强制 |
| 文件上传 | 仅接受 PDF/图片 MIME 类型 |
| CSRF | Supabase Auth cookie 自带 SameSite 保护 |
| 环境变量 | `DASHSCOPE_API_KEY` 仅服务端可用，`NEXT_PUBLIC_*` 仅 Supabase URL/匿名 Key |

---

## 领域模型关系

```
Course (1)
  ├── OutlineNode (N) — 树结构：week → chapter → topic → knowledge_point
  ├── Upload (N) — 上传的文件（大纲/试卷/笔记）
  ├── Question (N) — 练习题（可关联 knowledge_point）
  ├── StudyTask (N) — AI 生成的学习任务
  ├── Lesson (N) — AI 生成的课件
  │     └── LessonChunk (N) — 分块交互式内容
  ├── CourseNote (N) — 语音/文字笔记
  ├── ExamDate (N) — 考试日期 + 考试范围
  └── ElementMastery (N) — 知识点掌握度（V2，5 级）

User (1)
  ├── Course (N)
  ├── Attempt (N) — 答题记录
  ├── QuestionBookmark (N)
  ├── ChallengeLog (N) — 学习挑战日志
  ├── Misconception (N) — 易错点追踪
  └── LessonProgress (N)
```

---

## 环境变量

| 变量 | 作用域 | 说明 |
|------|--------|------|
| `NEXT_PUBLIC_SUPABASE_URL` | 客户端+服务端 | Supabase 项目 URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | 客户端+服务端 | Supabase 匿名 Key（RLS 生效） |
| `DASHSCOPE_API_KEY` | 仅服务端 | 阿里云 DashScope API 密钥 |
