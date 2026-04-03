# CourseHub — AI 驱动的课程管理工具

> 设计文档 | 2026-04-03 | 状态：Draft

## 背景

Canvas LMS 的 module 结构混乱，学生面对一学期 4-5 门课、每门课几十个 module，很难建立清晰的知识结构。现有工具（Quizlet、Knowt、StudyFetch）要么只做 flashcard，要么只做文档整理，没有任何产品同时做到：syllabus 解析 → 结构化课程 → 真题交互化 → 知识点掌握追踪。

## 产品定位

**一句话：** 上传 syllabus 和真题，AI 自动生成结构化课程 + 交互式练习 + 掌握度追踪。

**目标用户：** 美国大学生（起步），后续扩展到所有学生。

**核心价值：** 把散乱的课程材料变成可操作的学习路径。Canvas 告诉你"有什么"，CourseHub 告诉你"学什么、练什么、差什么"。

## 技术方案

**选型：** Next.js 16 全栈（方案 A）

| 层 | 技术 |
|----|------|
| 框架 | Next.js 16 (App Router) |
| 数据库 | Supabase (PostgreSQL + RLS) |
| Auth | Supabase Auth (Google OAuth) |
| 状态管理 | Zustand |
| 样式 | Tailwind CSS v4 |
| 图标 | Lucide React |
| AI | Claude API (vision + text) |
| 校验 | Zod |
| 部署 | Vercel |

**否决方案：**
- 方案 B（Vite SPA + Python FastAPI）：前后端分离增加部署复杂度，和现有项目栈不一致
- 方案 C（Next.js + Python 微服务）：MVP 阶段过度工程，后期如需可从方案 A 演进

## 用户流程

```
登录 → 仪表盘（所有课程卡片）
           │
           ├── [+ 新课程] → 上传 syllabus/拖入文件
           │      → AI 解析出课程名、教授、学期、大纲
           │      → 自动创建课程 + 填充大纲
           │      → 用户预览 & 确认（可编辑后再确认）
           │
           ├── [课程卡片] → 课程详情页
           │      ├── 大纲 Tab（按周/章节的知识点树，inline 编辑）
           │      ├── 题库 Tab（上传真题 → AI 转交互式题目）
           │      └── 进度 Tab（哪些知识点已掌握/未掌握）
           │
           └── [归档] → 已完成课程存档区
```

**新课创建流程：** 上传 syllabus 即创建课程。AI 自动提取课程元信息（标题、教授、学期）+ 大纲结构。用户在预览页确认或修改后，课程正式创建。不需要先手动填课程名再上传。

## 页面结构

| 页面 | 路由 | 作用 |
|------|------|------|
| Dashboard | `/dashboard` | 当前学期所有课程卡片 + 归档入口 + 全局进度概览 |
| Course Detail | `/course/[id]` | 单门课的大纲/题库/进度三个 Tab |
| Practice Mode | `/course/[id]/practice` | 做题界面：选择题、填空题、简答题，答完即时反馈 |
| Progress | `/course/[id]/progress` | 知识点掌握热力图 + 学习历史 |
| Upload | 嵌入 Course Detail | 拖入任何文件 → AI 自动识别类型 → 解析结果预览 → 确认导入 |
| Settings | `/settings` | 账号管理、学期设置、归档管理 |

## 数据模型

### Course
| 字段 | 类型 | 说明 |
|------|------|------|
| id | uuid | PK |
| user_id | uuid | FK → auth.users |
| title | text | 课程名 |
| description | text? | 课程描述 |
| professor | text? | 教授名 |
| semester | text? | 如 "Fall 2026" |
| status | text | "active" \| "archived" |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

### OutlineNode（知识点树）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | uuid | PK |
| course_id | uuid | FK → courses |
| parent_id | uuid? | FK → outline_nodes (自引用，构成树) |
| title | text | 节点标题 |
| type | text | "week" \| "chapter" \| "topic" \| "knowledge_point" |
| content | text? | 知识点描述/详细内容 |
| order | int | 同级排序 |

### Upload（用户上传文件）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | uuid | PK |
| course_id | uuid | FK → courses |
| file_url | text | Supabase Storage URL |
| file_name | text | 原始文件名 |
| file_type | text | "pdf" \| "ppt" \| "image" \| "text" \| "other" |
| upload_type | text | "syllabus" \| "exam" \| "practice" \| "notes" \| "other" |
| parsed_content | jsonb? | AI 解析结果 |
| status | text | "pending" \| "parsing" \| "done" \| "failed" |
| created_at | timestamptz | 上传时间 |

### Question（AI 生成的题目）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | uuid | PK |
| course_id | uuid | FK → courses |
| source_upload_id | uuid? | FK → uploads（来源文件） |
| knowledge_point_id | uuid? | FK → outline_nodes（关联知识点） |
| type | text | "multiple_choice" \| "fill_blank" \| "short_answer" \| "true_false" |
| stem | text | 题干 |
| options | jsonb? | 选项（选择题用） |
| answer | text | 正确答案 |
| explanation | text? | 解析 |
| difficulty | int | 1-5 |
| created_at | timestamptz | 创建时间 |

### Attempt（答题记录）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | uuid | PK |
| user_id | uuid | FK → auth.users |
| question_id | uuid | FK → questions |
| user_answer | text | 用户答案 |
| is_correct | boolean | 是否正确 |
| answered_at | timestamptz | 答题时间 |

## AI Pipeline

### Pipeline 1: 文件解析（通用）

任何文件上传后：
1. 检测文件类型（PDF/PPT/图片/文本）
2. PDF/图片 → Claude Vision 直接读取；文本/Markdown → 直接传入
3. AI 判断文件类型（syllabus/exam/practice/notes）
4. 根据类型走不同的后续 pipeline

### Pipeline 2: Syllabus → 课程大纲

```
上传文件 → Claude Vision 读取
  → Prompt: 提取课程结构，输出 OutlineNode[] JSON
  → Zod 校验
  → 写入 DB
  → 前端展示可编辑的知识点树
```

输出 schema：
```typescript
type OutlineOutput = {
  title: string
  description: string
  professor?: string
  semester?: string
  nodes: {
    title: string
    type: "week" | "chapter" | "topic" | "knowledge_point"
    children?: OutlineOutput["nodes"]
    content?: string
  }[]
}
```

### Pipeline 3: 真题/练习 → 交互式题目

```
上传考试/练习文件 → Claude Vision 读取
  → Prompt: 识别所有题目，转为结构化格式，保留原题 + 补充解析
  → Zod 校验 Question[]
  → AI 自动匹配已有知识点（通过 outline 语义匹配）
  → 写入 DB
  → 前端以交互式卡片展示
```

### Pipeline 4: 掌握度计算

```
用户完成题目 → 聚合每个知识点的答题记录
  → 掌握度 = 最近 10 次答题正确率（不足 10 次按实际次数计算）
  → 分级：掌握(>80%) / 需复习(40-80%) / 薄弱(<40%)
  → 更新 Dashboard 热力图
```

纯计算逻辑，不需要调 AI API。

## 目录结构

```
course-hub/
├── src/
│   ├── app/
│   │   ├── page.tsx                          # Landing → redirect to dashboard
│   │   ├── dashboard/page.tsx                # 多课仪表盘
│   │   ├── course/[id]/
│   │   │   ├── page.tsx                      # 课程详情（Outline tab 默认）
│   │   │   ├── practice/page.tsx             # 做题界面
│   │   │   └── progress/page.tsx             # 进度追踪
│   │   ├── api/
│   │   │   ├── parse/route.ts                # AI 解析文件
│   │   │   ├── generate-questions/route.ts   # AI 生成题目
│   │   │   ├── courses/route.ts              # 课程 CRUD
│   │   │   └── progress/route.ts             # 答题记录
│   │   └── layout.tsx                        # Sidebar + Auth guard
│   ├── components/
│   │   ├── CourseCard.tsx                     # 课程卡片
│   │   ├── OutlineTree.tsx                   # 可折叠知识点树
│   │   ├── QuestionCard.tsx                  # 做题卡片
│   │   ├── FileDropzone.tsx                  # 拖拽上传
│   │   ├── ProgressGrid.tsx                  # 知识点掌握热力图
│   │   └── Sidebar.tsx                       # 左侧导航
│   ├── lib/
│   │   ├── supabase.ts                       # Auth + DB client
│   │   ├── ai.ts                             # Claude API wrapper
│   │   ├── schemas.ts                        # Zod schemas
│   │   └── file-utils.ts                     # 文件类型检测
│   ├── store/
│   │   └── course-store.ts                   # Zustand
│   └── types.ts                              # TypeScript interfaces
├── supabase/
│   └── migrations/
│       └── 001_initial_schema.sql
├── next.config.ts
├── tailwind.config.ts
└── package.json
```

## UI 设计原则

- **风格：** 暖色调，和 chronicle 一致（off-white 底色、soft shadows、无 emoji）
- **图标：** Lucide React
- **布局：** 左侧 sidebar（课程列表 + 导航）+ 右侧主内容区
- **上传：** 拖拽为主，支持任何文件格式，AI 自动识别类型
- **做题：** 逐题模式（MVP 不做组卷），一题一屏，答完立即显示对错 + 解析，点击切换下一题
- **进度：** 知识点热力图（绿/黄/红色块），直观而非数字轰炸
- **归档：** Dashboard 底部折叠区，一键归档/恢复
- **字体：** 系统字体栈，不用自定义字体
- **响应式：** MVP 优先桌面端，不做移动适配

## MVP 边界

### 包含
- Google 登录（Supabase Auth）
- 多课仪表盘 + 课程 CRUD + 归档
- 上传任意文件 → AI 生成课程大纲
- 大纲手动编辑/调整（inline 编辑，类似 Notion 块编辑：点击编辑标题/内容、拖拽排序、增删节点）
- 上传真题/练习 → AI 转交互式题目
- 做题 + 即时反馈 + 解析
- 知识点掌握度追踪 + 热力图
- 文件管理（查看已上传文件、删除）

### 不包含（后续版本）
- AI 自动搜索历年真题（需要爬虫/数据源，Phase 2）
- 社区共享题库（需要内容审核，Phase 2）
- 实时协作 / 分享课程给同学
- 移动端适配
- 跨课知识点关联
- Spaced repetition 算法（先用简单正确率统计）
- Canvas LMS API 集成

## 风险

| 风险 | 影响 | 缓解 |
|------|------|------|
| Claude API 成本 | 每次文件解析消耗 token | 缓存解析结果，不重复解析同一文件 |
| PDF 解析质量 | 扫描件/手写内容可能识别差 | Claude Vision 已经很强，加上用户预览确认 |
| 知识点自动关联准确度 | AI 可能把题目关联到错误的知识点 | 用户可手动纠正关联 |
| 版权 | 上传考题的法律风险 | MVP 只做私有存储，不公开分享 |

## 竞品对标

详见 `docs/research/2026-04-03-ai-study-tool-competitive-analysis.md`

核心结论：Quizlet（题库交互）、Knowt（笔记→题目）、StudyFetch（syllabus 解析）各做了一部分，但无任何产品同时做到 syllabus 解析 + 真题交互化 + 掌握度追踪的完整闭环。
