# CourseHub — AI 驱动的课程学习平台

## 快速概览

| 维度 | 值 |
|------|-----|
| 框架 | Next.js 16 (App Router) + React 19 + TypeScript |
| 数据库 | Supabase PostgreSQL (项目: `zubvbcexqaiauyptsyby`) |
| 认证 | Supabase Auth (Email/密码 + Google OAuth + 游客模式) |
| AI | Qwen 3.5-Plus via DashScope (`@ai-sdk/openai` 适配) |
| 样式 | Tailwind CSS v4 + CSS 变量 + `ui-*` 自定义类 |
| 图标 | Lucide React (描边风格，不用 emoji) |
| 间隔重复 | ts-fsrs |
| i18n | 自定义 Context (EN/ZH) |
| 部署 | Vercel (60s API timeout) |

## 框架手册索引

| 手册 | 路径 | 职责 |
|------|------|------|
| 架构手册 | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | 技术栈、目录结构、路由、数据流、认证、AI 集成 |
| API 参考 | [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md) | 全部 33 个 API 端点的方法、参数、响应、错误码 |
| 组件手册 | [`docs/COMPONENTS.md`](docs/COMPONENTS.md) | 全部 31 个组件的 Props、依赖、状态、使用示例 |
| 设计系统 | [`docs/DESIGN_SYSTEM.md`](docs/DESIGN_SYSTEM.md) | CSS 变量、ui-* 类、颜色语义、字体、间距、组件视觉规范 |
| 编码规范 | [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md) | 命名、导入顺序、组件模式、样式、错误处理、禁止事项 |

> **规则：** 具体规范查手册，CLAUDE.md 只做索引。不在此文件中重复手册内容。

## 数据模型 (核心关系)

```
User
 └── Course
      ├── OutlineNode (adjacency list tree, parent_id 自引用)
      │    └── knowledge_point → ElementMastery (FSRS 掌握度追踪)
      ├── Question → Attempt (答题 + 自动批改)
      │    └── QuestionBookmark
      ├── StudyTask (AI 生成的学习任务)
      ├── Lesson → LessonChunk (AI 生成的分块课程)
      │    └── LessonProgress
      ├── ExamDate (考试日期 + 关联知识点)
      ├── Upload (文件上传 → AI 内容提取)
      ├── CourseNote (语音笔记 → AI 整理)
      ├── Misconception (错误概念追踪)
      └── ShareToken (课程分享链接)
```

## 关键入口文件

| 文件 | 职责 |
|------|------|
| `src/app/globals.css` | 全部 CSS 变量 + ui-* 类定义 (设计系统的唯一真相源) |
| `src/types.ts` | 全部 TypeScript 类型定义 |
| `src/lib/ai.ts` | AI 调用入口 (Qwen wrapper) |
| `src/lib/schemas.ts` | Zod schema (AI 输出校验) |
| `src/lib/mastery-v2.ts` | FSRS 掌握度计算 |
| `src/lib/i18n.tsx` | i18n Context + 翻译表 |

## 已知约束和坑

- **Vercel 60s timeout**: AI 生成类 API 必须控制批次大小 (如 generate-questions 每次最多 5 个 KP)
- **localStorage 数据**: 打卡、学习时间、复习卡片状态存在 localStorage，换设备会丢失
- **暗色模式**: 设计规范中有定义但项目未实现，不要引入 `data-theme` 相关代码
- **DM Sans**: 设计规范历史遗留，实际使用 Inter 系统字体栈
- **拖拽排序**: OutlineTree 有视觉提示但未接入实际 drag-drop
- **Web Speech API**: VoiceNotesPanel 仅 Chrome/Edge 完全支持
