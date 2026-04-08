# CourseHub 组件文档

> 共 31 个组件，全部位于 `src/components/`，按功能分为 7 个类别。

---

## 目录

1. [核心布局](#1-核心布局)
2. [课程展示](#2-课程展示)
3. [学习功能](#3-学习功能)
4. [内容管理](#4-内容管理)
5. [进度追踪](#5-进度追踪)
6. [用户内容](#6-用户内容)
7. [工具组件](#7-工具组件)

---

## 1. 核心布局

### Sidebar

**文件**: `src/components/Sidebar.tsx`
**行数**: ~137 行
**类型**: 客户端 (`"use client"`)

**用途**: 全局顶部导航栏，包含 Logo、页面链接、用户登录/登出、语言切换、移动端汉堡菜单。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| courses | `Course[]` | 是 | - | 用户的课程列表（用于筛选活跃课程） |
| isAuthenticated | `boolean` | 是 | - | 是否已登录 |
| userEmail | `string \| null` | 否 | - | 用户邮箱 |

**依赖**:
- 使用的 CSS 类: `ui-sidebar-wrapper`
- 使用的 CSS 变量: `--bg-muted`, `--accent`, `--accent-light`, `--text-primary`, `--text-secondary`, `--border`
- 外部库: `lucide-react`（LayoutDashboard, Plus, LogOut, LogIn, Bookmark, Settings, Menu, X）
- 内部依赖: `UsagePanel`, `StreakBadge`, `useI18n`, `createClient`（Supabase）
- API 调用: 无直接调用（登出通过 Supabase client）

**状态管理**:
- `useState`: `mobileOpen`（移动菜单开关）
- `useI18n()`: 多语言 locale/setLocale/t
- `usePathname()`: 当前路由高亮
- `useRouter()`: 登出后跳转

**使用示例**:
```jsx
<Sidebar courses={courses} isAuthenticated={true} userEmail="user@example.com" />
```

---

### CourseTabs

**文件**: `src/components/CourseTabs.tsx`
**行数**: ~36 行
**类型**: 客户端 (`"use client"`)

**用途**: 课程详情页的三栏 Tab 导航（Today / Learn / Profile）。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| courseId | `string` | 是 | - | 课程 ID，用于构建路由 |

**依赖**:
- 使用的 CSS 类: `ui-tab-row`, `ui-tab`, `ui-tab-active`
- 外部库: `lucide-react`（CalendarCheck, BookOpen, BarChart3）
- 内部依赖: `useI18n`

**状态管理**:
- `usePathname()`: 判断当前激活 tab

**使用示例**:
```jsx
<CourseTabs courseId="abc123" />
```

---

### OnboardingGate

**文件**: `src/components/OnboardingGate.tsx`
**行数**: ~26 行
**类型**: 客户端 (`"use client"`)

**用途**: 包裹 children，首次访问时拦截并展示 OnboardingWizard；onboarding 完成后直接渲染子内容。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| children | `React.ReactNode` | 是 | - | 被包裹的页面内容 |

**依赖**:
- 内部依赖: `isOnboardingComplete`（`@/lib/onboarding`）, `OnboardingWizard`

**状态管理**:
- `useState`: `showOnboarding`, `mounted`（防止 SSR 水合不匹配）
- `useEffect`: 挂载后检查 onboarding 状态

**使用示例**:
```jsx
<OnboardingGate>
  <DashboardContent />
</OnboardingGate>
```

---

### OnboardingWizard

**文件**: `src/components/OnboardingWizard.tsx`
**行数**: ~266 行
**类型**: 客户端 (`"use client"`)

**用途**: 四步引导流程——选择角色、输入学期、选择学习目标、确认摘要。收集偏好后存储到 localStorage。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| onComplete | `() => void` | 是 | - | 引导完成后的回调 |

**依赖**:
- 使用的 CSS 类: `ui-panel`, `ui-badge`
- 使用的 CSS 变量: `--accent`, `--accent-light`, `--bg-surface`, `--bg-primary`, `--bg-muted`, `--border`, `--text-primary`, `--text-secondary`
- 外部库: `lucide-react`（ArrowRight, Check, Globe, GraduationCap, Calendar, Target, Sparkles）
- 内部依赖: `saveOnboarding`, `useI18n`

**状态管理**:
- `useState`: `step`（当前步骤索引）, `prefs`（OnboardingPreferences 对象）

**使用示例**:
```jsx
<OnboardingWizard onComplete={() => setShowOnboarding(false)} />
```

---

## 2. 课程展示

### CourseCard

**文件**: `src/components/CourseCard.tsx`
**行数**: ~43 行
**类型**: 服务端（无 `"use client"`）

**用途**: Dashboard 上的课程卡片，展示课程标题、教授、学期，点击进入课程详情。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| course | `Course` | 是 | - | 课程对象（来自 types.ts） |

**依赖**:
- 使用的 CSS 类: `ui-panel`, `ui-kicker`
- 使用的 CSS 变量: `--bg-muted`, `--border`, `--text-primary`, `--text-secondary`, `--text-muted`, `--accent`
- 外部库: `lucide-react`（ArrowUpRight, BookOpen）, `next/link`

**状态管理**: 无

**使用示例**:
```jsx
<CourseCard course={{ id: "1", title: "Calculus II", professor: "Dr. Smith", semester: "Spring 2026", ... }} />
```

---

### TodayView

**文件**: `src/components/TodayView.tsx`
**行数**: ~118 行
**类型**: 客户端 (`"use client"`)

**用途**: 课程 Today 标签页的主视图，按优先级展示今日学习任务列表（紧急学习、考前复习、FSRS 复习等）。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| tasks | `TodayTask[]` | 是 | - | 今日任务列表（本地接口类型） |
| courseId | `string` | 是 | - | 课程 ID |

**依赖**:
- 使用的 CSS 类: `ui-panel`, `ui-badge`
- 使用的 CSS 变量: `--success`, `--text-secondary`, `--border`
- 外部库: `lucide-react`（AlertTriangle, RotateCcw, Calendar, BookOpen, Target, Check, Upload）, `next/link`
- 内部依赖: `useI18n`, `StreakBadge`

**状态管理**: 无额外状态（纯展示）

**使用示例**:
```jsx
<TodayView tasks={todayTasks} courseId="abc123" />
```

---

### ArchiveButton

**文件**: `src/components/ArchiveButton.tsx`
**行数**: ~46 行
**类型**: 客户端 (`"use client"`)

**用途**: 课程操作按钮组——归档/恢复和删除课程。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| courseId | `string` | 是 | - | 课程 ID |
| status | `string` | 是 | - | 当前课程状态（"active" / "archived"） |

**依赖**:
- 使用的 CSS 类: `ui-button-secondary`
- 使用的 CSS 变量: `--text-secondary`
- 外部库: `lucide-react`（Archive, ArchiveRestore, Trash2）
- API 调用: `PATCH /api/courses/{courseId}`（切换状态）, `DELETE /api/courses/{courseId}`（删除）

**状态管理**:
- `useRouter()`: 刷新页面或跳转 dashboard

**使用示例**:
```jsx
<ArchiveButton courseId="abc123" status="active" />
```

---

### RegenerateButton

**文件**: `src/components/RegenerateButton.tsx`
**行数**: ~44 行
**类型**: 客户端 (`"use client"`)

**用途**: 课程内容语言重新生成按钮（汉化/英文化课程）。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| courseId | `string` | 是 | - | 课程 ID |

**依赖**:
- 使用的 CSS 变量: `--border`, `--text-secondary`
- 外部库: `lucide-react`（Languages, Loader2）
- 内部依赖: `useI18n`
- API 调用: `POST /api/courses/{courseId}/regenerate`

**状态管理**:
- `useState`: `loading`, `done`

**使用示例**:
```jsx
<RegenerateButton courseId="abc123" />
```

---

### ShareButton

**文件**: `src/components/ShareButton.tsx`
**行数**: ~56 行
**类型**: 客户端 (`"use client"`)

**用途**: 生成课程分享链接并提供一键复制。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| courseId | `string` | 是 | - | 课程 ID |

**依赖**:
- 使用的 CSS 变量: `--border`, `--bg-muted`, `--text-secondary`, `--success`
- 外部库: `lucide-react`（Share2, Copy, Check, Loader2）
- API 调用: `POST /api/courses/{courseId}/share`

**状态管理**:
- `useState`: `shareUrl`, `loading`, `copied`
- 使用 `navigator.clipboard.writeText` 复制

**使用示例**:
```jsx
<ShareButton courseId="abc123" />
```

---

## 3. 学习功能

### ChunkLesson

**文件**: `src/components/ChunkLesson.tsx`
**行数**: ~365 行
**类型**: 客户端 (`"use client"`)

**用途**: 分块课程学习器。支持逐步推进、checkpoint 问答（MCQ / 填空 / 开放题 / 代码）、补救内容、进度保存。核心教学引擎组件。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| chunks | `LessonChunk[]` | 是 | - | 课程分块数组 |
| courseId | `string` | 是 | - | 课程 ID |
| lessonId | `string` | 是 | - | 课时 ID |
| totalChunks | `number` | 否 | chunks.length | SSE 流式生成时的总块数 |
| isStreaming | `boolean` | 否 | false | 是否正在流式接收 |

**依赖**:
- 使用的 CSS 类: `ui-panel`, `ui-button-primary`, `ui-textarea`
- 使用的 CSS 变量: `--accent`, `--accent-light`, `--success`, `--danger`, `--warning`, `--border`, `--bg-muted`, `--text-secondary`, `--text-muted`
- 外部库: `lucide-react`（Check, X, Loader2, ChevronRight）
- 内部依赖: `MarkdownRenderer`, `useI18n`, `recordActivity`（streaks）
- API 调用: `POST /api/courses/{courseId}/lessons/{lessonId}/progress`

**状态管理**:
- `useState`: `currentChunkIndex`, `checkpointState`（Record 管理每个 chunk 的答题状态）
- `useRef`: `progressSaved`（防止重复保存）
- `useEffect`: 完成时自动保存进度

**使用示例**:
```jsx
<ChunkLesson chunks={lessonChunks} courseId="abc" lessonId="les1" totalChunks={10} isStreaming={true} />
```

---

### QuestionCard

**文件**: `src/components/QuestionCard.tsx`
**行数**: ~237 行
**类型**: 客户端 (`"use client"`)

**用途**: 单题练习卡片。支持单选、判断、填空、简答。提交后展示正确答案和解释，支持收藏和反馈。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| question | `Question` | 是 | - | 题目对象（不含答案） |
| onAnswer | `(questionId: string, answer: string, isCorrect: boolean) => void` | 是 | - | 答题回调 |
| bookmarked | `boolean` | 否 | false | 初始收藏状态 |

**依赖**:
- 使用的 CSS 类: `ui-panel`, `ui-kicker`, `ui-button-primary`, `ui-textarea`
- 使用的 CSS 变量: `--accent`, `--success`, `--danger`, `--border`, `--bg-muted`, `--text-primary`, `--text-secondary`
- 外部库: `lucide-react`（Check, X, Bookmark, Loader2）
- 内部依赖: `updateCard` / `Rating`（spaced-repetition）, `recordActivity`（streaks）, `useI18n`
- API 调用: `POST /api/attempts`, `POST /api/bookmarks`, `DELETE /api/bookmarks`, `POST /api/questions/{id}/feedback`

**状态管理**:
- `useState`: `selected`, `submitted`, `textAnswer`, `isBookmarked`, `feedbackGiven`, `revealedAnswer`, `revealedExplanation`, `isCorrect`, `submitting`

**使用示例**:
```jsx
<QuestionCard question={q} onAnswer={(id, ans, correct) => console.log(correct)} bookmarked={false} />
```

---

### MarkdownRenderer

**文件**: `src/components/MarkdownRenderer.tsx`
**行数**: ~137 行
**类型**: 客户端 (`"use client"`)

**用途**: Markdown 渲染器，支持 GFM 表格、数学公式（KaTeX）、代码高亮、术语自动高亮弹窗。内置 MathErrorBoundary 降级。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| content | `string` | 是 | - | Markdown 文本 |
| terms | `TermDefinition[] \| null` | 否 | null | 术语定义数组，匹配后用 TermTooltip 包裹 |

**依赖**:
- 使用的 CSS 类: `prose-custom`
- 使用的 CSS 变量: `--accent`, `--bg-muted`, `--text-secondary`
- 外部库: `react-markdown`, `remark-gfm`, `remark-math`, `rehype-katex`, `rehype-highlight`, `katex/dist/katex.min.css`
- 内部依赖: `TermTooltip`

**状态管理**: 无（纯渲染 + ErrorBoundary）

**使用示例**:
```jsx
<MarkdownRenderer content="## Hello\n$E=mc^2$" terms={[{ term: "energy", definition: "..." }]} />
```

---

### TermTooltip

**文件**: `src/components/TermTooltip.tsx`
**行数**: ~89 行
**类型**: 客户端 (`"use client"`)

**用途**: 内联术语弹窗。点击带虚线下划线的术语文字，弹出定义气泡（自动判断上下方向）。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| term | `TermDefinition` | 是 | - | 术语对象（含 term 和 definition） |
| children | `React.ReactNode` | 是 | - | 触发文字 |

**依赖**:
- 使用的 CSS 变量: `--accent`, `--bg-surface`, `--border`, `--text-secondary`

**状态管理**:
- `useState`: `open`, `above`（弹出方向）
- `useRef`: 触发元素和弹出层引用
- `useEffect`: 计算位置、绑定外部点击关闭
- `useCallback`: `handleClickOutside`

**使用示例**:
```jsx
<TermTooltip term={{ term: "Gradient", definition: "..." }}>Gradient</TermTooltip>
```

---

### StudyBuddy

**文件**: `src/components/StudyBuddy.tsx`
**行数**: ~161 行
**类型**: 客户端 (`"use client"`)

**用途**: 固定在右下角的 AI 对话助手浮窗。基于 Vercel AI SDK 的 useChat，支持快捷问题和流式回复。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| courseId | `string` | 是 | - | 课程 ID |
| courseTitle | `string` | 是 | - | 课程标题（显示在聊天头部） |

**依赖**:
- 使用的 CSS 变量: `--accent`, `--bg-surface`, `--bg-muted`, `--border`, `--text-primary`, `--text-secondary`
- 外部库: `lucide-react`（MessageCircle, Send, X, Loader2, Bot）, `@ai-sdk/react`（useChat）, `ai`（DefaultChatTransport, isTextUIPart）
- API 调用: 通过 transport 连接 `/api/courses/{courseId}/chat`

**状态管理**:
- `useState`: `open`, `input`
- `useRef`: `messagesEndRef`（自动滚动到底部）
- `useChat()`: messages, sendMessage, status

**使用示例**:
```jsx
<StudyBuddy courseId="abc123" courseTitle="Linear Algebra" />
```

---

## 4. 内容管理

### OutlineTree

**文件**: `src/components/OutlineTree.tsx`
**行数**: ~288 行
**类型**: 客户端 (`"use client"`)

**用途**: 可编辑的课程大纲树。支持重命名（双击编辑）、添加子节点、删除节点、修改后触发重新生成。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| nodes | `OutlineNode[]` | 是 | - | 大纲节点平铺数组 |
| courseId | `string` | 是 | - | 课程 ID |

**导出函数**: `buildTree(nodes)` -- 将平铺节点构建成树形结构

**依赖**:
- 使用的 CSS 类: `ui-panel`, `ui-empty`
- 使用的 CSS 变量: `--accent`, `--success`, `--danger`, `--bg-muted`, `--border`, `--text-primary`, `--text-secondary`
- 外部库: `lucide-react`（ChevronRight, ChevronDown, Plus, Trash2, Pencil, Check, X, Loader2, Sparkles）
- 内部依赖: `useI18n`
- API 调用: `PATCH /api/outline-nodes/{id}`, `DELETE /api/outline-nodes/{id}`, `POST /api/outline-nodes`, `POST /api/courses/{courseId}/generate`

**状态管理**:
- `useState`: `localNodes`（本地节点副本）, `dirty`（是否修改过）, `regenerating`
- `useCallback`: handleUpdate, handleDelete, handleAdd

**使用示例**:
```jsx
<OutlineTree nodes={outlineNodes} courseId="abc123" />
```

---

### OutlinePreview

**文件**: `src/components/OutlinePreview.tsx`
**行数**: ~83 行
**类型**: 客户端 (`"use client"`)

**用途**: 只读的课程大纲预览树（解析上传 syllabus 后展示结构），带展开/折叠和类型标签。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| nodes | `ParsedOutlineNode[]` | 是 | - | 已解析的大纲节点（嵌套结构） |

**依赖**:
- 使用的 CSS 类: `ui-panel`
- 使用的 CSS 变量: `--text-primary`, `--text-secondary`, `--text-muted`, `--bg-muted`, `--border`, `--border-strong`
- 外部库: `lucide-react`（ChevronRight, ChevronDown）
- 内部依赖: `useI18n`

**状态管理**:
- `useState`: `expanded`（每个 TreeNode 内部）

**使用示例**:
```jsx
<OutlinePreview nodes={parsedSyllabus.nodes} />
```

---

### LearningBlueprint

**文件**: `src/components/LearningBlueprint.tsx`
**行数**: ~131 行
**类型**: 服务端（无 `"use client"`）

**用途**: 学习蓝图卡片，将知识点按学习流程排列展示（最多 6 个），显示掌握度、剩余任务、下一步行动。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| courseId | `string` | 是 | - | 课程 ID |
| items | `LearningBlueprintItem[]` | 是 | - | 蓝图数据项（本地接口类型） |

**依赖**:
- 使用的 CSS 类: `ui-panel`, `ui-kicker`, `ui-copy`, `ui-button-secondary`, `ui-badge`
- 使用的 CSS 变量: `--border`, `--text-primary`, `--text-secondary`
- 外部库: `lucide-react`（ArrowRight, BookOpenText, PenLine, RotateCcw）, `next/link`
- 内部依赖: `masteryColors`, `masteryLabels`（`@/lib/mastery`）

**状态管理**: 无

**使用示例**:
```jsx
<LearningBlueprint courseId="abc123" items={blueprintItems} />
```

---

### KnowledgeTree

**文件**: `src/components/KnowledgeTree.tsx`
**行数**: ~198 行
**类型**: 客户端 (`"use client"`)

**用途**: SVG 可视化知识点掌握度图谱。圆圈大小和颜色反映掌握级别，带进度环和动画。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| nodes | `KnowledgeNodeData[]` | 是 | - | 知识点数据（本地接口类型） |
| courseId | `string` | 是 | - | 课程 ID |

**依赖**:
- 使用的 CSS 类: `ui-panel`, `ui-empty`
- 使用的 CSS 变量: `--border`, `--border-strong`, `--text-primary`, `--text-secondary`
- 颜色硬编码: `#16a34a`(mastered), `#f59e0b`(reviewing), `#ef4444`(weak)

**状态管理**:
- `useMemo`: 计算 SVG 节点布局位置（网格 + 抖动）

**使用示例**:
```jsx
<KnowledgeTree nodes={knowledgeNodes} courseId="abc123" />
```

---

### FileDropzone

**文件**: `src/components/FileDropzone.tsx`
**行数**: ~101 行
**类型**: 客户端 (`"use client"`)

**用途**: 文件上传拖拽区域，上传文件到服务端并返回存储路径。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| onFileUploaded | `(result: { storagePath, fileUrl, fileName, fileType }) => void` | 是 | - | 上传成功回调 |
| courseId | `string` | 否 | - | 课程 ID（附加到 FormData） |
| accept | `Record<string, string[]>` | 否 | - | 允许的文件类型 |

**依赖**:
- 使用的 CSS 类: `ui-panel`, `ui-kicker`
- 使用的 CSS 变量: `--accent`, `--border`, `--border-strong`, `--bg-muted`, `--text-primary`, `--text-secondary`, `--danger`
- 外部库: `react-dropzone`（useDropzone）, `lucide-react`（Upload, File, Loader2）
- API 调用: `POST /api/upload`（FormData）

**状态管理**:
- `useState`: `uploading`, `error`
- `useCallback`: onDrop

**使用示例**:
```jsx
<FileDropzone onFileUploaded={(data) => console.log(data)} courseId="abc123" />
```

---

## 5. 进度追踪

### ProgressGrid

**文件**: `src/components/ProgressGrid.tsx`
**行数**: ~75 行
**类型**: 客户端 (`"use client"`)

**用途**: 知识点掌握度方格图，色块表示掌握级别，hover 显示详情。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| data | `KPMastery[]` | 是 | - | 知识点掌握度数据（含 node, level, rate, total） |

**依赖**:
- 使用的 CSS 类: `ui-panel`, `ui-kicker`, `ui-copy`, `ui-empty`
- 使用的 CSS 变量: `--border`, `--text-primary`, `--text-secondary`, `--bg-surface`
- 内部依赖: `masteryColors`, `masteryLabels`（`@/lib/mastery`）

**状态管理**: 无

**使用示例**:
```jsx
<ProgressGrid data={kpMasteryData} />
```

---

### StudyTrackerPanel

**文件**: `src/components/StudyTrackerPanel.tsx`
**行数**: ~278 行
**类型**: 客户端 (`"use client"`)

**用途**: 学习时间追踪面板。自动检测用户活跃/空闲状态，按模式（solving/reviewing/studying/idle）分类计时，含每周柱状图。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| courseId | `string \| null` | 否 | - | 课程 ID（null 为全局统计） |
| activeMode | `"solving" \| "reviewing" \| "studying"` | 否 | - | 当前学习模式 |
| title | `string` | 否 | "Time Track" | 面板标题 |
| description | `string` | 否 | (默认描述文案) | 面板描述 |
| track | `boolean` | 否 | true | 是否激活计时 |
| className | `string` | 否 | "" | 额外 CSS 类 |

**依赖**:
- 使用的 CSS 类: `ui-panel`, `ui-kicker`, `ui-copy`, `ui-badge`, `ui-progress-track`, `ui-progress-bar`
- 使用的 CSS 变量: `--accent`, `--warning`, `--success`, `--bg-muted`, `--border`, `--text-primary`, `--text-secondary`
- 外部库: `lucide-react`（Activity, BookOpenText, Brain, Clock3, PauseCircle）
- 内部依赖: `recordStudyTime`, `getStudySummary`, `getWeeklySummary`, `formatDuration`, `STUDY_TRACKER_UPDATED_EVENT`

**状态管理**:
- `useState`: `summary`, `liveMode`
- `useRef`: `lastTickRef`, `lastInteractionRef`, `lastMouseMoveRef`
- `useMemo`: `breakdown`（模式分布数据）
- `useEffect`: 全局事件监听（pointerdown, keydown, scroll, touchstart, mousemove）、1 秒间隔计时、自定义事件监听
- localStorage: 通过 `study-tracker` 库读写

**使用示例**:
```jsx
<StudyTrackerPanel courseId="abc123" activeMode="solving" track={true} />
```

---

### StudyStatsCard

**文件**: `src/components/StudyStatsCard.tsx`
**行数**: ~119 行
**类型**: 客户端 (`"use client"`)

**用途**: 紧凑版学习时间统计卡片，展示每周柱状图、今日/本周/日均时间、模式分布条。

**Props**: 无

**依赖**:
- 使用的 CSS 变量: `--accent`, `--warning`, `--success`, `--border`, `--bg-surface`, `--text-primary`, `--text-secondary`
- 外部库: `lucide-react`（Clock3）
- 内部依赖: `getWeeklySummary`, `getAllTimeStats`, `formatDuration`, `STUDY_TRACKER_UPDATED_EVENT`

**状态管理**:
- `useState`: `weekly`, `allTime`
- `useEffect`: 监听 `STUDY_TRACKER_UPDATED_EVENT` 刷新
- localStorage: 通过 `study-tracker` 库读取

**使用示例**:
```jsx
<StudyStatsCard />
```

---

### StreakBadge

**文件**: `src/components/StreakBadge.tsx`
**行数**: ~127 行
**类型**: 客户端 (`"use client"`)

**用途**: 学习连续打卡徽章。点击展开弹窗，显示当前连续天数、每日目标进度条、本周日历圆点、冻结状态。

**Props**: 无

**依赖**:
- 使用的 CSS 变量: `--accent`, `--bg-surface`, `--bg-muted`, `--border`, `--text-primary`, `--text-secondary`
- 外部库: `lucide-react`（Flame, Shield, Target）
- 内部依赖: `getStreakData`, `getWeekHistory`, `useI18n`
- 自定义事件: `coursehub-streak-updated`

**状态管理**:
- `useState`: `data`（StreakData）, `open`（弹窗开关）, `week`（本周历史）
- `useEffect`: 监听 `coursehub-streak-updated` 事件
- localStorage: 通过 `streaks` 库读取

**使用示例**:
```jsx
<StreakBadge />
```

---

### ExamCountdown

**文件**: `src/components/ExamCountdown.tsx`
**行数**: ~119 行
**类型**: 客户端 (`"use client"`)

**用途**: 考试倒计时面板。展示即将到来的考试列表，支持添加和删除考试，按紧急程度变色。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| courseId | `string` | 是 | - | 课程 ID |
| exams | `ExamDate[]` | 是 | - | 初始考试日期列表 |

**依赖**:
- 使用的 CSS 类: `ui-panel`
- 使用的 CSS 变量: `--accent`, `--danger`, `--warning`, `--bg-muted`, `--border`, `--text-secondary`
- 外部库: `lucide-react`（Calendar, Plus, Trash2, AlertTriangle）
- 内部依赖: `useI18n`
- API 调用: `POST /api/courses/{courseId}/exams`, `DELETE /api/courses/{courseId}/exams`

**状态管理**:
- `useState`: `exams`（本地副本）, `adding`, `title`, `date`

**使用示例**:
```jsx
<ExamCountdown courseId="abc123" exams={examDates} />
```

---

### MistakePatterns

**文件**: `src/components/MistakePatterns.tsx`
**行数**: ~83 行
**类型**: 客户端 (`"use client"`)

**用途**: 薄弱知识点分析面板，展示错误率最高的 5 个知识点（含错误率条形图）。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| courseId | `string` | 是 | - | 课程 ID |

**依赖**:
- 使用的 CSS 变量: `--danger`, `--warning`, `--accent`, `--bg-muted`, `--text-primary`, `--text-muted`
- 外部库: `lucide-react`（AlertTriangle, TrendingDown）
- 内部依赖: `useI18n`
- API 调用: `GET /api/courses/{courseId}/mistake-patterns`

**状态管理**:
- `useState`: `patterns`（MistakePattern 数组）, `loading`
- `useEffect`: 组件挂载时 fetch 数据

**使用示例**:
```jsx
<MistakePatterns courseId="abc123" />
```

---

### StudyTaskList

**文件**: `src/components/StudyTaskList.tsx`
**行数**: ~167 行
**类型**: 客户端 (`"use client"`)

**用途**: 学习任务清单，按优先级分组（必须掌握/应该掌握/了解即可），支持切换完成状态。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| initialTasks | `StudyTask[]` | 是 | - | 初始任务列表 |

**依赖**:
- 使用的 CSS 类: `ui-panel`, `ui-kicker`, `ui-copy`, `ui-empty`, `ui-badge`, `ui-progress-track`, `ui-progress-bar`
- 使用的 CSS 变量: `--danger`, `--warning`, `--success`, `--border`, `--text-secondary`, `--border-strong`
- 外部库: `lucide-react`（Check, Circle, BookOpen, PenLine, RotateCcw, Loader2）
- 内部依赖: `useI18n`
- API 调用: `PATCH /api/study-tasks/{taskId}`

**状态管理**:
- `useState`: `tasks`（本地副本）, `toggling`（正在切换的任务 ID）

**使用示例**:
```jsx
<StudyTaskList initialTasks={studyTasks} />
```

---

## 6. 用户内容

### VoiceNotesPanel

**文件**: `src/components/VoiceNotesPanel.tsx`
**行数**: ~595 行
**类型**: 客户端 (`"use client"`)

**用途**: 语音笔记面板，项目中最大的组件。支持浏览器语音识别录入、AI 整理笔记、追问澄清问题、手动绑定知识点、保存。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| courseId | `string` | 是 | - | 课程 ID |
| knowledgePoints | `{ id: string; title: string }[]` | 是 | - | 可选知识点列表 |
| initialNotes | `CourseNote[]` | 是 | - | 已保存笔记列表 |

**依赖**:
- 使用的 CSS 类: `ui-panel`, `ui-kicker`, `ui-copy`, `ui-empty`, `ui-badge`, `ui-button-primary`, `ui-button-secondary`, `ui-input`, `ui-textarea`, `ui-icon-button`
- 使用的 CSS 变量: `--accent`, `--border`, `--text-secondary`
- 外部库: `lucide-react`（BrainCircuit, CheckCircle2, Languages, MessageCircleQuestion, Mic, NotebookPen, Save, Sparkles, Square, Tag）
- 内部依赖: `toCourseNote`, `toCourseNoteCreatePayload`（`@/lib/course-notes`）
- Web API: `window.SpeechRecognition` / `window.webkitSpeechRecognition`
- API 调用: `POST /api/courses/{courseId}/notes/organize`, `POST /api/courses/{courseId}/notes`

**状态管理**:
- `useState`: `notes`, `transcript`, `draft`, `clarificationAnswers`, `selectedKnowledgePointId`, `language`, `recordingTarget`, `interimText`, `isRecording`, `organizing`, `saving`, `error`, `status`, `lastInputSource`（共 15 个状态）
- `useRef`: `recognitionRef`
- `useEffect`: 初始化笔记/语言/清理录音

**使用示例**:
```jsx
<VoiceNotesPanel courseId="abc123" knowledgePoints={kps} initialNotes={notes} />
```

---

### WrongAnswerNotebook

**文件**: `src/components/WrongAnswerNotebook.tsx`
**行数**: ~139 行
**类型**: 服务端（无 `"use client"`）

**用途**: 错题本，展示做错的题目（含错误答案、正确答案、解释），最多显示 8 条并提供"去练习"入口。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| courseId | `string` | 是 | - | 课程 ID |
| items | `WrongAnswerNotebookItem[]` | 是 | - | 错题数据（本地接口类型） |

**依赖**:
- 使用的 CSS 类: `ui-panel`, `ui-kicker`, `ui-copy`, `ui-empty`, `ui-badge`, `ui-button-secondary`, `ui-button-ghost`
- 使用的 CSS 变量: `--border`, `--text-secondary`
- 外部库: `lucide-react`（AlertCircle, ArrowRight, CheckCircle2, RotateCcw）, `next/link`

**状态管理**: 无

**使用示例**:
```jsx
<WrongAnswerNotebook courseId="abc123" items={wrongItems} />
```

---

### ProfileView

**文件**: `src/components/ProfileView.tsx`
**行数**: ~171 行
**类型**: 客户端 (`"use client"`)

**用途**: 课程学习画像页面，展示 V2 掌握度概览（5 级进度条）、持续性弱点、已克服的误解、元认知准确度、本周统计。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| courseTitle | `string` | 是 | - | 课程标题 |
| totalKps | `number` | 是 | - | 总知识点数 |
| mastery | `(ElementMastery & { conceptTitle: string })[]` | 是 | - | 知识点掌握度数据 |
| misconceptions | `Misconception[]` | 是 | - | 误解记录 |
| metacognitionData | `{ student_self_rating, ai_confidence_rating, meta_cognition_match }[]` | 是 | - | 元认知数据 |
| weeklyAttempts | `number` | 是 | - | 本周答题次数 |

**依赖**:
- 使用的 CSS 类: `ui-panel`
- 使用的 CSS 变量: `--accent`, `--success`, `--warning`, `--danger`, `--border`, `--bg-muted`, `--text-primary`, `--text-secondary`, `--text-muted`
- 外部库: `lucide-react`（AlertTriangle, Check, Brain, Activity）
- 内部依赖: `useI18n`, `levelConfig`（`@/lib/mastery-v2`）

**状态管理**: 无额外状态（纯展示）

**使用示例**:
```jsx
<ProfileView courseTitle="Calc II" totalKps={30} mastery={m} misconceptions={mis} metacognitionData={meta} weeklyAttempts={42} />
```

---

## 7. 工具组件

### T

**文件**: `src/components/T.tsx`
**行数**: ~8 行
**类型**: 客户端 (`"use client"`)

**用途**: 最小化的 i18n 翻译组件，用于在 JSX 中直接渲染翻译字符串。

**Props**:
| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| k | `string` | 是 | - | i18n 翻译键 |

**依赖**:
- 内部依赖: `useI18n`

**状态管理**: 无

**使用示例**:
```jsx
<T k="nav.dashboard" />
```

---

### UsagePanel

**文件**: `src/components/UsagePanel.tsx`
**行数**: ~99 行
**类型**: 客户端 (`"use client"`)

**用途**: AI 用量统计面板，展示今日/本周的 API 调用次数、token 消耗、预估费用，含每周柱状图。

**Props**: 无

**依赖**:
- 使用的 CSS 变量: `--accent`, `--border`, `--bg-surface`, `--text-primary`, `--text-secondary`
- 外部库: `lucide-react`（Activity）
- 内部依赖: `getTodayUsage`, `getWeeklyUsage`, `estimateCost`, `formatTokens`（`@/lib/usage-tracker`）

**状态管理**:
- `useState`: `today`（UsageRecord）, `weekly`（UsageRecord[]）
- `useEffect`: 初始加载 + 30 秒定时刷新
- localStorage: 通过 `usage-tracker` 库读取

**使用示例**:
```jsx
<UsagePanel />
```

---

## 附录：组件统计

| 组件 | 行数 | 类型 | 分类 |
|------|------|------|------|
| VoiceNotesPanel | 595 | 客户端 | 用户内容 |
| ChunkLesson | 365 | 客户端 | 学习功能 |
| OutlineTree | 288 | 客户端 | 内容管理 |
| StudyTrackerPanel | 278 | 客户端 | 进度追踪 |
| OnboardingWizard | 266 | 客户端 | 核心布局 |
| QuestionCard | 237 | 客户端 | 学习功能 |
| KnowledgeTree | 198 | 客户端 | 内容管理 |
| ProfileView | 171 | 客户端 | 用户内容 |
| StudyTaskList | 167 | 客户端 | 进度追踪 |
| StudyBuddy | 161 | 客户端 | 学习功能 |
| WrongAnswerNotebook | 139 | 服务端 | 用户内容 |
| MarkdownRenderer | 137 | 客户端 | 学习功能 |
| Sidebar | 137 | 客户端 | 核心布局 |
| LearningBlueprint | 131 | 服务端 | 内容管理 |
| StreakBadge | 127 | 客户端 | 进度追踪 |
| ExamCountdown | 119 | 客户端 | 进度追踪 |
| StudyStatsCard | 119 | 客户端 | 进度追踪 |
| TodayView | 118 | 客户端 | 课程展示 |
| FileDropzone | 101 | 客户端 | 内容管理 |
| UsagePanel | 99 | 客户端 | 工具组件 |
| TermTooltip | 89 | 客户端 | 学习功能 |
| OutlinePreview | 83 | 客户端 | 内容管理 |
| MistakePatterns | 83 | 客户端 | 进度追踪 |
| ProgressGrid | 75 | 客户端 | 进度追踪 |
| ShareButton | 56 | 客户端 | 课程展示 |
| ArchiveButton | 46 | 客户端 | 课程展示 |
| RegenerateButton | 44 | 客户端 | 课程展示 |
| CourseCard | 43 | 服务端 | 课程展示 |
| CourseTabs | 36 | 客户端 | 核心布局 |
| OnboardingGate | 26 | 客户端 | 核心布局 |
| T | 8 | 客户端 | 工具组件 |

**总计**: 31 个组件 / ~4,730 行代码
- 客户端组件: 28 个
- 服务端组件: 3 个（CourseCard, LearningBlueprint, WrongAnswerNotebook）
