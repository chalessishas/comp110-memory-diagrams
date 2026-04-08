# CourseHub 编码规范手册

> 本文件从项目实际代码中提取，不是理想化的规范。所有规则均有代码实例佐证。
> 新代码必须遵循这些约定。如需打破约定，在 PR 中说明理由。

---

## 1. 文件与目录结构

```
src/
├── app/                    # Next.js App Router
│   ├── api/               # API 路由 (每个端点一个 route.ts)
│   ├── course/[id]/       # 课程相关页面
│   ├── dashboard/         # 仪表盘
│   └── globals.css        # 全局 CSS 变量 + ui-* 类
├── components/            # 所有 React 组件 (扁平结构，无子目录)
├── lib/                   # 工具库 (无 UI 依赖)
├── contexts/              # React Context (仅 i18n)
└── types.ts               # 全局类型定义 (单文件)
```

**规则：**
- 组件放 `components/`，不分子目录（当前 31 个文件，50+ 时再考虑分组）
- 工具函数放 `lib/`，每个主题一个文件
- 类型定义集中在 `types.ts`，不分散到各组件
- 页面文件只做数据获取和组件组装，不写业务逻辑

---

## 2. 命名规范

| 类别 | 规范 | 示例 |
|------|------|------|
| 组件 | PascalCase | `CourseCard`, `StudyTaskList` |
| 函数 | camelCase | `calculateMastery`, `todayKey` |
| 事件处理 | `handle` 前缀或 `on` 前缀 | `handleSubmit`, `onAnswer` |
| 布尔状态 | `is`/`has`/`can` 前缀 | `isBookmarked`, `hasExam`, `canSubmit` |
| 常量 | UPPER_SNAKE_CASE | `STORAGE_KEY`, `QUESTION_TYPE_I18N_KEYS` |
| 类型/接口 | PascalCase | `QuestionCardProps`, `MasteryLevel` |
| CSS 类 | `ui-` 前缀 + kebab-case | `ui-panel`, `ui-button-primary` |
| CSS 变量 | `--` 前缀 + kebab-case | `--accent`, `--text-primary` |
| 文件名 | PascalCase (.tsx) / kebab-case (.ts) | `CourseCard.tsx`, `rate-limit.ts` |
| i18n 键 | dot 分隔 | `nav.dashboard`, `questionCard.multipleChoice` |

---

## 3. 导入顺序

```tsx
// 1. React / Next.js 内置
import { useState, useEffect } from "react";
import Link from "next/link";
import { redirect } from "next/navigation";

// 2. 第三方库
import { BookOpen, Clock } from "lucide-react";
import { createBrowserClient } from "@supabase/ssr";

// 3. 类型导入 (用 import type)
import type { Course, Question } from "@/types";

// 4. 本地工具库
import { createClient } from "@/lib/supabase/server";
import { calculateMastery } from "@/lib/mastery";

// 5. 本地组件
import { CourseCard } from "@/components/CourseCard";
```

**规则：**
- 类型导入必须用 `import type`，不与值导入混合
- 路径别名统一用 `@/` (映射到 `src/`)
- 不使用相对路径 (`../lib/xxx`)

---

## 4. 组件声明模式

### 服务端页面 (SSR)

```tsx
// src/app/course/[id]/page.tsx
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";

export default async function CourseDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  // 数据获取 ...
  return <div>...</div>;
}
```

### 客户端组件

```tsx
// src/components/QuestionCard.tsx
"use client";

import { useState } from "react";
import type { Question } from "@/types";

interface QuestionCardProps {
  question: Question;
  onAnswer: (id: string, answer: string, isCorrect: boolean) => void;
  bookmarked?: boolean;
}

export function QuestionCard({ question, onAnswer, bookmarked = false }: QuestionCardProps) {
  const [submitted, setSubmitted] = useState(false);
  // ...
}
```

### 简单组件 (内联 Props)

```tsx
export function CourseCard({ course }: { course: Course }) {
  return <div>...</div>;
}
```

**规则：**
- 服务端页面用 `export default async function`
- 客户端组件用 `"use client"` + 命名导出 `export function`
- Props 少于 3 个 → 内联类型；3+ 个 → 独立 `interface`
- 不使用 `React.FC`、`React.memo`（除非有性能问题）

---

## 5. 样式约定

### 优先级

1. **Tailwind 类** — 布局、间距、flex/grid、响应式
2. **CSS 变量 (inline style)** — 颜色、阴影、圆角等主题相关值
3. **ui-* 类** — 语义化组件样式 (在 globals.css 中定义)

### 示例

```tsx
{/* Tailwind 负责布局，CSS 变量负责颜色 */}
<div
  className="flex items-center gap-2 px-3 py-1.5 rounded-xl"
  style={{
    backgroundColor: "var(--bg-muted)",
    color: "var(--text-primary)",
    border: "1px solid var(--border)",
  }}
>
  <BookOpen size={16} />
  <span>课程名称</span>
</div>

{/* 或直接用 ui-* 类 */}
<div className="ui-panel p-6">
  <button className="ui-button-primary">开始学习</button>
</div>
```

### 动态颜色映射

```tsx
// 用 Record 对象做颜色映射，不写 if-else
const priorityColors: Record<number, string> = {
  1: "var(--danger)",
  2: "var(--warning)",
  3: "var(--text-secondary)",
};

<div style={{ borderLeftColor: priorityColors[task.priority] }} />
```

**禁止：**
- 不使用 CSS Modules (`*.module.css`)
- 不使用 styled-components / Emotion
- 不硬编码十六进制颜色值（必须通过 CSS 变量引用）
- 例外：掌握度/优先级等专用色用 rgba() 带透明度

---

## 6. API 路由模式

```tsx
// src/app/api/courses/route.ts
import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function GET() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { data, error } = await supabase
    .from("courses")
    .select("*")
    .eq("user_id", user.id);

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json(data);
}

export async function POST(req: Request) {
  // 1. 认证检查
  // 2. 解析请求体
  // 3. Zod schema 校验
  // 4. 业务逻辑
  // 5. 返回结果
}
```

**规则：**
- 每个 API 路由只导出 HTTP 方法函数 (`GET`, `POST`, `PATCH`, `DELETE`)
- 认证检查必须在第一行
- 输入校验用 Zod `safeParse()`
- 错误返回标准格式 `{ error: string }`
- 状态码: 200 成功 / 201 创建 / 400 参数错 / 401 未认证 / 404 不存在 / 500 服务端错

---

## 7. 状态管理

### 分层策略

| 数据类型 | 存储位置 | 理由 |
|----------|----------|------|
| 用户账号、课程、知识点 | Supabase (PostgreSQL) | 核心业务数据，需要持久化 + 跨设备 |
| 学习时间、打卡、复习卡片状态 | localStorage | 高频读写，离线可用，非关键数据 |
| 页面临时状态 | React useState | 随组件生命周期，不持久化 |
| 用户偏好 (语言、角色) | localStorage | 读多写少，本地即可 |

### localStorage 工具函数模式

```tsx
// src/lib/streaks.ts
const STORAGE_KEY = "coursehub.streaks";

interface StreakData {
  currentStreak: number;
  lastStudyDate: string;
  // ...
}

function getStreakData(): StreakData {
  if (typeof window === "undefined") return defaultData();  // SSR 防护
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : defaultData();
  } catch {
    return defaultData();
  }
}

function saveStreakData(data: StreakData): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}
```

**规则：**
- localStorage key 统一 `coursehub.` 前缀
- 每个 localStorage 工具独立一个文件
- 必须有 `typeof window === "undefined"` 守卫 (SSR 兼容)
- 读取必须 try-catch (数据可能损坏)

---

## 8. 错误处理

### 服务端页面

```tsx
// 缺数据 → redirect，不 throw
if (!user) redirect("/login");
if (!course) redirect("/dashboard");
```

### API 路由

```tsx
// 输入校验失败 → 400
const parsed = schema.safeParse(body);
if (!parsed.success) {
  return NextResponse.json({ error: parsed.error.flatten() }, { status: 400 });
}

// Supabase 查询失败 → 500
const { data, error } = await supabase.from("courses").select("*");
if (error) {
  return NextResponse.json({ error: error.message }, { status: 500 });
}
```

### 客户端组件

```tsx
// fetch 调用 → try-catch + 用户友好提示
try {
  const res = await fetch(`/api/courses/${id}`);
  if (!res.ok) throw new Error("Failed");
  const data = await res.json();
  setCourse(data);
} catch {
  setError("加载失败，请重试");
}
```

**规则：**
- 不写空 catch
- 不在 API 路由中 try-catch 整个函数体（让每个错误点独立处理）
- 客户端 fetch 必须检查 `res.ok`

---

## 9. AI 集成规范

```tsx
// src/lib/ai.ts — 统一 AI 调用入口
import { createOpenAI } from "@ai-sdk/openai";

const qwen = createOpenAI({
  baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1",
  apiKey: process.env.DASHSCOPE_API_KEY!,
});

// 所有 AI 函数集中在 ai.ts + schemas.ts
// 使用 Zod schema 校验 AI 输出
```

**规则：**
- 所有 AI 调用通过 `src/lib/ai.ts` 中的函数
- AI 输出必须用 Zod schema 校验 (在 `schemas.ts` 中定义)
- 流式响应通过 Vercel AI SDK 的 `streamText()`
- Rate limit 通过 `src/lib/rate-limit.ts` 控制
- AI 函数命名: `generate*`, `parse*`, `organize*`

---

## 10. 国际化 (i18n)

```tsx
// 使用方式
import { useI18n } from "@/lib/i18n";

function MyComponent() {
  const { t } = useI18n();
  return <button>{t("nav.dashboard")}</button>;
}

// 或用 T 组件
import { T } from "@/components/T";
<T k="nav.dashboard" />
```

**规则：**
- 所有用户可见文字必须通过 `t()` 或 `<T />` 渲染
- 翻译键用 dot 分隔: `{页面/组件}.{元素}`
- 新增文字时同步添加 EN + ZH 翻译
- 学科术语不翻译（保持双语标注）

---

## 11. 禁止事项

| 禁止 | 理由 |
|------|------|
| `console.log` 到生产代码 | 用户可见 |
| 硬编码颜色 `#4f46e5` | 必须用 `var(--accent)` |
| `any` 类型 | 用具体类型或 `unknown` |
| `// TODO` 无 issue 编号 | 要么修要么删 |
| 内联 Supabase 查询在组件中 | 通过 API 路由或服务端页面 |
| 相对路径导入 `../lib/xxx` | 用 `@/lib/xxx` |
| `React.FC` | 用 `function` 声明 |
| CSS Modules / styled-components | 用 Tailwind + CSS 变量 |
| 在 API 路由中返回 HTML | 只返回 JSON |
| `window.confirm()` 做删除确认 | 用组件内 inline 确认 UI |
