# CourseHub 设计系统规范 v2.0

> **本文件是 CourseHub 所有前端页面的唯一视觉真相来源 (Single Source of Truth)。**
> 任何 AI 或人类在生成/开发 CourseHub 页面时，必须遵循本文件中的全部规范。
> 未覆盖的设计决策应基于本文件的原则推导，而不是凭感觉发挥。
>
> **使用方式：** 在让 AI 生成任何 CourseHub 页面时，将本文件作为系统 prompt 或上下文附件提供。
>
> **v2.0 更新：** 本版本与项目实际 `globals.css` / 组件代码完全对齐。颜色从蓝色系 (#3B6FE0) 修正为靛蓝 (#4f46e5)，CSS 变量从层级命名 (--color-primary-500) 改为语义命名 (--accent)，字体从 DM Sans 改为 Inter 系统栈，圆角上调一档，暗色模式标记为未实现。

---

## 第一章：不可违反的基础约束

### 1.1 语言规则

CourseHub 支持多语言，但任何单一页面上的语言必须**内部一致**。绝不允许同一页面出现中英混杂的 UI 控件。

```
规则 1: UI 控件文字
  按钮、标签、Tab、菜单项、Toast、placeholder、空状态文案
  → 全部跟随用户语言设置（i18n context）
  → 中文用户：「开始学习」「提交」「取消」
  → 英文用户："Start Learning" "Submit" "Cancel"
  → 同一页面绝不出现一半中文一半英文的控件

规则 2: 学科术语
  → 首次出现：中文名 (英文名)，如「递归 (Recursion)」
  → 后续出现：可以只用中文名
  → 知识树节点标签：中文名 + 英文名双行显示
  → 绝不纯翻译术语——「调用栈」单独出现可以，
    但首次必须标注「调用栈 (Call Stack)」

规则 3: AI 生成的教学内容
  → 跟随课程原始语言
  → 英文课出英文讲解，中文课出中文讲解
  → 不在同一段落内中英混用（术语标注除外）

规则 4: 代码和公式
  → 代码永远保持原文（变量名、关键词、注释语言跟随课程语言）
  → LaTeX 公式原样渲染
  → 代码块上方的说明文字跟随 UI 语言

规则 5: 绝不出现的情况
  ✗ 按钮「Submit」旁边是标签「用户名」
  ✗ placeholder 写 "Enter your email" 但 label 写「邮箱」
  ✗ Toast 通知突然切换语言
  ✗ 页面标题中文但面包屑导航英文
```

### 1.2 设计原则

```
原则 1: 功能优先于装饰
  每一个视觉元素都必须服务于功能。
  不加纯装饰性图标、不用渐变背景、不加无意义的插图。
  如果去掉某个元素后功能不受影响，那它不应该存在。

原则 2: 信息层级必须在 3 秒内可读
  用户扫一眼页面，3 秒内必须知道：
  (a) 我在哪（页面标题/面包屑）
  (b) 我该做什么（主行动按钮）
  (c) 当前状态是什么（进度/掌握度/倒计时）

原则 3: 一个页面只有一个主行动
  Today 页面的主行动 = 「开始」（最紧急的任务）
  Learn 页面的主行动 = 「继续」（下一个 Chunk）
  Profile 页面的主行动 = 「针对性练习」（最大弱点）
  不允许同一视觉权重的两个按钮并列争夺注意力。

原则 4: 颜色传递语义，不传递品牌
  绿色 = 掌握/通过 (--success: #059669)
  黄色 = 进行中/需注意 (--warning: #d97706)
  红色 = 薄弱/紧急 (--danger: #dc2626)
  靛蓝 = 主交互/新内容 (--accent: #4f46e5)
  灰色 = 未开始/禁用
  这些语义在整个产品中必须一致，绝不出现
  「这个页面的红色表示强调、那个页面的红色表示错误」

原则 5: 移动端不是桌面端的缩小版
  移动端有自己的布局规则（见第六章）。
  不允许直接缩放桌面端布局到手机屏幕。
```

---

## 第二章：设计令牌 (Design Tokens)

> **注意：** 以下 CSS 变量与 `src/app/globals.css` 完全一致。如有冲突，以 `globals.css` 为准。

### 2.1 颜色系统

```css
/* ═══ 实际使用的 CSS 变量 (Light Mode Only) ═══ */

/* 背景 — 暖白色调 */
--bg-primary:   #faf9f7;   /* 页面底色（暖灰白，非纯白） */
--bg-surface:   #ffffff;   /* 卡片/面板底色 */
--bg-muted:     #f3f2ef;   /* 次级底色（输入框默认态、灰底区域）*/
--bg-elevated:  #ffffff;   /* 浮层底色 */

/* 文字 — 高对比暖黑 */
--text-primary:   #111111; /* 标题、强调文字 */
--text-secondary: #555555; /* 正文 */
--text-muted:     #999999; /* 占位符、辅助标签、时间戳 */

/* 主色 — 深靛蓝（非蓝色） */
--accent:       #4f46e5;             /* 主交互色、主按钮 */
--accent-hover: #4338ca;             /* hover 态 */
--accent-light: rgba(79, 70, 229, 0.08);  /* 选中态背景 */
--accent-muted: rgba(79, 70, 229, 0.15);  /* 次级按钮 hover */

/* 语义色 — 状态反馈 */
--success: #059669;   /* 掌握/通过/正确 */
--warning: #d97706;   /* 进行中/注意/复习 */
--danger:  #dc2626;   /* 薄弱/紧急/错误 */

/* 边框 */
--border:        #e5e5e5;  /* 常规边框、分割线 */
--border-strong: #d4d4d4;  /* 强调边框 */

/* 阴影 — 分层深度 */
--shadow-sm:   0 1px 2px rgba(0, 0, 0, 0.04);
--shadow-md:   0 4px 12px rgba(0, 0, 0, 0.06);
--shadow-lg:   0 12px 40px rgba(0, 0, 0, 0.08);
--shadow-card: 0 1px 3px rgba(0, 0, 0, 0.04), 0 4px 12px rgba(0, 0, 0, 0.03);

/* 圆角 — 只有 3 档 */
--radius-sm: 8px;    /* 按钮内小元素、标签 */
--radius-md: 12px;   /* 中等元素 */
--radius-lg: 16px;   /* 卡片、面板 */

/* ═══ 专用色 (Mastery / Priority) ═══ */

/* 掌握度等级 */
--mastery-unseen:     #D4D4D4;  /* Level 0: 灰色 */
--mastery-exposed:    #F87171;  /* Level 1: 浅红 */
--mastery-practiced:  #FBBF24;  /* Level 2: 黄色 */
--mastery-proficient: #34D399;  /* Level 3: 绿色 */
--mastery-mastered:   #10B981;  /* Level 4: 深绿 + glow */

/* Today 优先级标签 */
--priority-urgent:    #DC2626;  /* 红 - 考前排雷 */
--priority-review:    #D97706;  /* 黄 - 到期复习 */
--priority-exam:      #EA580C;  /* 橙 - 即将考试 */
--priority-new:       #4f46e5;  /* 靛蓝 - 新内容（与 --accent 一致）*/
--priority-weakness:  #7C3AED;  /* 紫 - 弱点强化 */
```

> ⚠️ **暗色模式尚未实现。** 项目当前只有亮色模式。暗色模式的设计将在未来版本中定义。
> 在此之前，不要使用 `[data-theme="dark"]` 或任何暗色变量。

### 2.2 字体系统

```css
/* 字体家族 */
--font-sans: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif;
--font-mono: "JetBrains Mono", "Fira Code", monospace;

/*
  选择理由：
  - 系统字体栈优先加载，Inter 作为 fallback 保证跨平台一致性
  - 无需加载 Google Fonts，减少 LCP
  - JetBrains Mono: 代码字体，带连字，辨识度高
  注意: 项目中不使用 DM Sans 或 Noto Sans SC
*/

/* 字号阶梯 (1rem = 16px) */
--text-xs:   0.75rem;    /* 12px - 辅助标签、时间戳 */
--text-sm:   0.875rem;   /* 14px - 次要正文、表单标签 */
--text-base: 1rem;       /* 16px - 正文 */
--text-lg:   1.125rem;   /* 18px - 卡片标题 */
--text-xl:   1.25rem;    /* 20px - 区域标题 */
--text-2xl:  1.5rem;     /* 24px - 页面标题 */
--text-3xl:  1.875rem;   /* 30px - 大标题 (Landing 页) */

/* 行高 */
--leading-tight:  1.25;  /* 标题 */
--leading-normal: 1.5;   /* 正文（body 默认） */
--leading-relaxed: 1.75; /* 教学内容（长文阅读需要更大行高）*/

/* 字重 */
--font-normal:  400;     /* 正文 */
--font-medium:  500;     /* 标签、次按钮 */
--font-semibold: 600;    /* 小标题、主按钮 */
--font-bold:    700;     /* 大标题 */

/* 全局 letter-spacing */
body { letter-spacing: -0.01em; }
```

### 2.3 间距系统

```css
/* 基于 4px 网格 */
--space-0:   0;
--space-0.5: 2px;
--space-1:   4px;
--space-1.5: 6px;
--space-2:   8px;
--space-3:   12px;
--space-4:   16px;
--space-5:   20px;
--space-6:   24px;
--space-8:   32px;
--space-10:  40px;
--space-12:  48px;
--space-16:  64px;
--space-20:  80px;

/* 语义间距 */
--gap-inline:  var(--space-2);    /* 行内元素间距 (图标和文字) */
--gap-stack:   var(--space-4);    /* 垂直堆叠间距 (段落间) */
--gap-section: var(--space-8);    /* 区块间距 */
--gap-page:    var(--space-12);   /* 页面级间距 */

--padding-card:   var(--space-6); /* 卡片内边距 = 24px */
--padding-page-x: var(--space-6); /* 页面水平内边距（移动端 1.5rem, 桌面 2rem） */
--padding-page-y: var(--space-8); /* 页面垂直内边距 */
```

### 2.4 阴影

```css
/* 阴影只用于表示层级（浮起），不用于装饰 */
--shadow-sm:   0 1px 2px rgba(0,0,0,0.04);
--shadow-md:   0 4px 12px rgba(0,0,0,0.06);
--shadow-lg:   0 12px 40px rgba(0,0,0,0.08);
--shadow-card: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);

/* .ui-panel hover 时升级为 --shadow-md */
```

### 2.5 动画

```css
/* 全局过渡时间 */
--duration-fast:   160ms;  /* hover 变色、按钮交互 */
--duration-normal: 200ms;  /* 展开/折叠、进度条 */
--duration-slow:   300ms;  /* 页面过渡 */

/* 缓动 (实际项目统一用 ease) */
transition: all 160ms ease;         /* 按钮 */
transition: all 200ms ease;         /* 面板、卡片 */
transition: width 300ms ease;       /* 进度条 */

/* View Transitions API (Chrome/Edge) */
/* 侧栏 view-transition-name: sidebar — 页面切换时保持不动 */

/* 动画规则 */
/*
  1. 所有状态变化必须有过渡（不允许瞬变）
  2. hover/focus 用 160ms ease
  3. 内容展开/折叠用 200ms ease
  4. 页面级过渡用 200ms ease-out (page-enter keyframe)
  5. 不使用 ease-in（东西不该越动越快）
  6. prefers-reduced-motion 时降级为简单淡入淡出
*/
```

### 2.6 断点

```css
/* 只有一个关键断点 */
@media (min-width: 768px) {
  .ui-shell { padding: 2rem; }
}

/*
  布局策略：
  < 768px:  单列布局，底部导航栏，.ui-shell padding 1.5rem
  >= 768px: 顶部粘性导航，.ui-shell padding 2rem，最大宽度 1160px
*/
```

---

## 第三章：CSS 类体系 (ui-*)

> **核心概念：** CourseHub 用 Tailwind CSS v4 + CSS 变量 + `ui-*` 自定义类。
> 组件同时使用三种方式：Tailwind 工具类（布局/间距）、CSS 变量（颜色/阴影/圆角）、`ui-*` 类（语义化组件样式）。

### 3.1 全部 ui-* 类

```css
/* 布局 */
.ui-shell               /* 页面容器: width min(1160px, 100%), margin auto, padding 1.5rem/2rem */
.ui-sidebar-wrapper      /* 侧栏: view-transition-name: sidebar */

/* 面板/卡片 */
.ui-panel                /* 白底卡片: border, radius-lg, shadow-card, hover → shadow-md */
.ui-panel-muted          /* 灰底卡片: bg-muted */

/* 按钮 */
.ui-button-primary       /* 主按钮: accent bg, white, radius 10px, fw 600 */
.ui-button-secondary     /* 次按钮: border, bg-surface, radius 10px */
.ui-button-ghost         /* 幽灵按钮: transparent, text-secondary */
.ui-icon-button          /* 图标按钮: 40x40, border, bg-surface */

/* 表单 */
.ui-input                /* 输入框: bg-muted, radius 10px, focus → accent ring */
.ui-textarea             /* 文本域: 同上 + resize vertical */

/* 标签 */
.ui-badge                /* 小标签: border, bg-muted, 11px, fw 600, letter-spacing */
.ui-kicker               /* pill 标签: border, rounded-full, 11px, uppercase, 0.12em spacing */

/* 导航 */
.ui-tab-row              /* 选项卡容器: flex, gap 0.5rem, overflow-x auto */
.ui-tab                  /* 选项卡: border, bg-surface, radius-sm, 13px fw 600 */
.ui-tab-active           /* 选中态: border accent, bg accent-light, color accent */
.ui-segmented            /* 分段控制容器: grid, bg-muted, radius-md */
.ui-segment              /* 分段选项: transparent, text-secondary */
.ui-segment-active       /* 选中态: bg accent, white */

/* 进度 */
.ui-progress-track       /* 进度条轨道: h 4px, bg border, rounded-full */
.ui-progress-bar         /* 进度条填充: bg accent, transition width 300ms */

/* 工具 */
.ui-divider-label        /* 带文字分割线: flex, before/after hr */
.ui-empty                /* 空状态容器: dashed border, bg white/0.7, 居中 */
.ui-copy                 /* 正文段落: text-secondary, 15px */
```

### 3.2 按钮规范

```
按钮一律 border-radius: 10px（注意：不是 --radius-sm 的 8px）

分类：
  ui-button-primary   - accent 底白字，页面主行动，每页最多 1 个
  ui-button-secondary - border + bg-surface，次要行动
  ui-button-ghost     - 无背景无边框，文字按钮（用于"取消""跳过"）
  danger 变体         - #dc2626 底白字，危险操作（通过 inline style 实现）

尺寸：
  sm: 高度 32px, padding 0 12px, font-size 13px
  md: 高度 40px, padding 0.6rem 1.1rem, font-size 14px (默认)
  lg: 高度 48px, padding 0 24px, font-size 16px

状态：
  default  → 正常颜色
  hover    → translateY(-1px) + shadow-md (primary/secondary)
            → bg-muted (ghost)
  active   → translateY(0), shadow none
  disabled → opacity 0.5, cursor not-allowed

过渡：background-color 160ms ease, color 160ms ease, border-color 160ms ease,
      transform 160ms ease, box-shadow 160ms ease, opacity 160ms ease

规则：
  - 按钮文字不超过 4 个中文字 / 16 个英文字母
  - 图标按钮 (.ui-icon-button) 40x40px，必须有 aria-label
  - 相邻按钮间距 12px
  - Primary 和 Danger 不允许在同一行出现
```

### 3.3 输入框规范

```
.ui-input / .ui-textarea

共同属性：
  border: 1px solid var(--border)
  border-radius: 10px
  background: var(--bg-muted)
  padding: 0.65rem 0.85rem

focus 态：
  border-color: var(--accent)
  background: white
  box-shadow: 0 0 0 3px var(--accent-light)

规则：
  - label 在输入框上方，不使用浮动 label
  - placeholder 颜色 --text-muted (#999999)
  - 错误态: border-color --danger, 下方红色文字
```

### 3.4 标签规范

```
两种标签样式：

.ui-badge (方形标签):
  border: 1px solid var(--border)
  border-radius: 6px
  background: var(--bg-muted)
  padding: 0.2rem 0.5rem
  font-size: 11px, font-weight: 600, letter-spacing: 0.04em

.ui-kicker (pill 标签):
  border: 1px solid var(--border)
  border-radius: 999px
  padding: 0.4rem 0.75rem
  font-size: 11px, font-weight: 600
  letter-spacing: 0.12em, text-transform: uppercase

掌握度标签（通过 inline style 着色）：
  Level 0: bg rgba(0,0,0,0.04),  color #999999  「未学习」
  Level 1: bg rgba(239,68,68,0.08), color #dc2626  「已接触」
  Level 2: bg rgba(245,158,11,0.1), color #d97706  「练习中」
  Level 3: bg rgba(5,150,105,0.08), color #059669  「已熟练」
  Level 4: bg rgba(5,150,105,0.12), color #047857  「已精通」

优先级标签：
  紧急:   bg rgba(220,38,38,0.08),  color #dc2626
  复习:   bg rgba(217,119,6,0.08),  color #d97706
  即将考试: bg rgba(234,88,12,0.08), color #ea580c
  新内容: bg var(--accent-light),   color var(--accent)
  弱点:   bg rgba(124,58,237,0.08), color #7c3aed
```

### 3.5 进度条

```
.ui-progress-track:
  height: 4px
  border-radius: 999px
  background: var(--border)

.ui-progress-bar:
  height: 100%
  border-radius: inherit
  background: var(--accent)   /* 通用进度 */
  transition: width 300ms ease

语义色变体（通过 inline style）：
  0-40%:   --danger  (#dc2626)
  41-70%:  --warning (#d97706)
  71-100%: --success (#059669)

规则：
  - 进度条不使用渐变填充
  - 进度条最小宽度 4px（不为 0 时仍有视觉指示）
```

### 3.6 图标

```
图标库：Lucide React (lucide-react)

选择理由：
  - 一致的 2px 描边风格
  - 轻量（tree-shakable）
  - React 组件直接用

尺寸：
  sm: 16px (标签内)
  md: 20px (按钮内、导航项) (默认)
  lg: 24px (页面标题旁)

颜色：默认跟随相邻文字颜色 (currentColor)

常用图标映射：
  导航:     Home, Book, User, Settings, Search
  状态:     Check, X, AlertTriangle, Clock, Lock
  操作:     Plus, Minus, Edit, Trash, Share, Download
  学习:     Play, Pause, RotateCcw (重做), ArrowRight (继续)
  Streak:   Flame
  考试:     Timer, Calendar

规则：
  - 全部用描边式图标（不用填充式）
  - 图标和文字之间间距 8px
  - 纯图标按钮最小点击区域 40x40px (.ui-icon-button)
```

### 3.7 Toast 通知

```
位置：屏幕右上角（桌面）/ 顶部居中（移动端）
最多同时显示 3 条，新的推旧的上去。

变体：
  success: 左侧绿色竖条 + Check 图标
  error:   左侧红色竖条 + X 图标
  info:    左侧 accent 竖条 + Info 图标
  warning: 左侧黄色竖条 + AlertTriangle 图标

尺寸：
  宽度: 360px (桌面固定) / 100% - 32px (移动端)
  内边距: 12px 16px
  圆角: var(--radius-lg) = 16px
  阴影: var(--shadow-lg)

动画：
  进入: 从右侧滑入, 200ms ease
  退出: 向右淡出, 160ms ease

自动关闭：4 秒后自动消失。错误类 Toast 不自动关闭（需手动点 X）。
```

### 3.8 骨架屏 (Skeleton)

```
在内容加载时显示占位图形，替代 spinner。

颜色：
  背景: var(--border)
  闪烁高光: var(--bg-muted)
  动画: shimmer 1.5s infinite ease-in-out

形状规则：
  - 骨架屏的形状必须匹配将要加载的内容的真实形状
  - 连续 3 个文字行骨架的宽度应不同 (100%, 80%, 60%)
  - 加载超过 5 秒时在骨架屏下方显示文字提示
  - 永远不使用全屏 spinner
```

---

## 第四章：业务组件

### 4.1 课程卡片 (CourseCard)

```
文件: src/components/CourseCard.tsx
CSS 类: .ui-panel + .ui-kicker

结构：
  ┌─────────────────────────────────┐
  │  [课程名称]              [掌握度%] │
  │  [教授 · 学期]                    │
  │  [进度条 ███░░░ 62%]             │
  │  [考试倒计时 kicker]  [最近学习]   │
  └─────────────────────────────────┘

样式：
  容器: .ui-panel (border, radius-lg=16px, shadow-card)
  内边距: p-6 (24px)
  hover: -translate-y-0.5 + shadow-md
  名称: text-primary, fw 600
  百分比: --accent color
  副文字: --text-muted
  倒计时: .ui-kicker 样式，红色表示 <=3 天

规则：
  - 课程名称最多显示 2 行，超出截断
  - 没有考试时不显示倒计时标签
  - 点击整个卡片进入课程（不是只点标题）
```

### 4.2 任务卡片 (StudyTaskList)

```
文件: src/components/StudyTaskList.tsx
CSS 类: .ui-panel + .ui-kicker + .ui-progress-track/bar + .ui-empty

结构：
  ┌──────────────────────────────────────┐
  │  [优先级色条 4px]                     │
  │  [优先级标签]  [预估时间]              │
  │  [任务标题]                           │
  │  [任务描述]                           │
  │  [主行动按钮]                          │
  └──────────────────────────────────────┘

左侧色条: 4px, 颜色取自 priority 映射
  1 = --danger, 2 = --warning, 3 = --text-secondary

任务项: rounded-[24px], 背景 rgba(247,247,244,0.92)

规则：
  - Today 页面最多显示 5 张任务卡片
  - 如果有更多，底部显示「查看全部 N 项」
  - 完成一项后卡片动画消失
```

### 4.3 课程内容块 (ChunkLesson)

```
文件: src/components/ChunkLesson.tsx

内容区：
  最大宽度: 720px (居中)
  行高: 1.75 (教学内容用更大行高)
  段落间距: 16px
  代码块: 背景 --bg-muted, 圆角 --radius-sm=8px, padding 16px

术语标注（TermTooltip 组件）：
  视觉: 虚线下划线, hover 背景变为 --accent-light
  点击: 展开 tooltip，显示解释文字

规则：
  - 已完成的 Chunk 可以折叠但不消失
  - 当前 Chunk 始终完全展开
  - 未到达的 Chunk 不渲染
```

### 4.4 Checkpoint 组件 (QuestionCard)

```
文件: src/components/QuestionCard.tsx

通用外观：
  背景: var(--accent-light)
  圆角: var(--radius-lg) = 16px
  边框: 1px dashed var(--border-strong)

选择题 (MCQ)：
  选中: border accent, bg accent-light
  正确: bg rgba(5,150,105,0.08), border success
  错误: bg rgba(220,38,38,0.08), border danger

答题反馈：
  正确: bg success/0.08, 左侧绿色竖条 4px, 标题 "正确。"
  错误: bg danger/0.08, 左侧红色竖条 4px, 标题 "不太对。"

规则：
  - Checkpoint 不可跳过
  - 最多 3 次尝试后自动放行
  - 放行时显示完整解答
```

### 4.5 知识树 (KnowledgeTree)

```
文件: src/components/KnowledgeTree.tsx

掌握度指示器 (40x40px 圆形):
  Level 0: 空心圆, 描边 --mastery-unseen
  Level 1: 浅红填充, 描边 --mastery-exposed
  Level 2: 半填充, 描边 --mastery-practiced
  Level 3: 实心绿, 描边 --mastery-proficient
  Level 4: 实心深绿 + box-shadow glow, --mastery-mastered
```

### 4.6 复习卡片 (ReviewCard / FSRS)

```
卡片：
  最大宽度: 480px，居中
  背景: var(--bg-surface)
  圆角: var(--radius-lg) = 16px
  阴影: var(--shadow-md)

评分按钮排列 (底部横排等分):
  Again: bg rgba(220,38,38,0.08),  color --danger
  Hard:  bg rgba(217,119,6,0.08),  color --warning
  Good:  bg rgba(5,150,105,0.08),  color --success
  Easy:  bg var(--accent-light),   color --accent

每个按钮下方小字显示下次复习间隔

"显示答案"按钮: .ui-button-secondary 样式 (border + bg-surface)
```

### 4.7 Streak / 打卡 (StreakBadge)

```
文件: src/components/StreakBadge.tsx

结构：
  ┌──────────────────────────────────────┐
  │  [火焰 emoji/图标] 连续 N 天           │
  │  ●●●●○  (本周打卡点)                  │
  └──────────────────────────────────────┘

样式:
  容器: border + bg-surface + shadow-card
  圆角: rounded-xl / rounded-2xl
  已完成点: accent 色
  今天: accent 空心描边
  未来: border 色

颜色: amber (#f59e0b) 用于火焰高亮, green (#16a34a) 用于完成态
```

### 4.8 其他已实现组件

```
src/components/ 目录包含 31 个组件文件：

学习功能:
  ChunkLesson.tsx        — 课程内容分块显示
  QuestionCard.tsx        — 多题型测验 (MCQ/填空/简答/判断)
  MarkdownRenderer.tsx    — Markdown + KaTeX + 代码高亮
  StudyTaskList.tsx       — 今日任务清单
  StudyBuddy.tsx          — AI 对话助手

内容生成:
  OutlineTree.tsx         — 课程大纲树状图
  OutlinePreview.tsx      — 大纲预览
  LearningBlueprint.tsx   — 学习结构可视化
  KnowledgeTree.tsx       — 知识点树状图

进度追踪:
  ProgressGrid.tsx        — 进度网格（使用 masteryColors 中心映射）
  StudyTrackerPanel.tsx   — 学习活动追踪
  StudyStatsCard.tsx      — 统计卡片
  StreakBadge.tsx          — 连续打卡
  ExamCountdown.tsx       — 考试倒计时
  MistakePatterns.tsx     — 错误模式分析

用户内容:
  VoiceNotesPanel.tsx     — 语音笔记
  WrongAnswerNotebook.tsx — 错题本
  OnboardingWizard.tsx    — 课程创建引导
  ProfileView.tsx         — 用户资料

工具:
  TermTooltip.tsx         — 术语标注弹层
  FileDropzone.tsx        — 文件上传区域
  ShareButton.tsx / ArchiveButton.tsx / RegenerateButton.tsx
  OnboardingGate.tsx      — 认证守卫
  T.tsx                   — i18n 翻译组件
  UsagePanel.tsx          — API 使用量追踪
  Sidebar.tsx             — 顶部粘性导航
```

---

## 第五章：页面级布局

### 5.1 全局布局骨架

```
实际布局（所有尺寸）:

  ┌─ 粘性顶栏 (Sidebar.tsx) ─────────────────────┐
  │  [Logo]  [Today] [课程列表] [设置]  [头像]     │
  │  背景: rgba(250,249,247,0.92) + blur(16px)    │
  ├──────────────────────────────────────────────┤
  │                                               │
  │  .ui-shell                                    │
  │  width: min(1160px, 100%)                     │
  │  margin: 0 auto                               │
  │  padding: 1.5rem (< 768px) / 2rem (>= 768px) │
  │                                               │
  │    (页面内容)                                   │
  │                                               │
  └──────────────────────────────────────────────┘

导航项:
  当前项: bg accent-light, color accent, font-weight 700
  未选中: color text-secondary
  间距: px-3 py-1.5, gap-2

教学内容区 (Learn 页面): 最大宽度 720px, 居中

注意: 没有传统侧栏布局。导航在顶部，类似 Notion 的简洁导航。
```

### 5.2 页面过渡规范

```
基于 View Transitions API (Chrome/Edge):

进入动画 (page-enter):
  from: opacity 0, translateY(4px)
  to:   opacity 1, translateY(0)
  时长: 200ms ease-out

退出动画 (fade-out): opacity → 0, 150ms
侧栏: view-transition-name: sidebar, 页面切换时保持不动

.ui-shell > * 和 main > .ui-shell 子元素自动应用 page-enter 动画。

规则:
  - 不使用 Framer Motion (项目无此依赖)
  - 优先用 CSS View Transitions API
  - prefers-reduced-motion 时降级为简单淡入淡出
```

### 5.3 空状态设计

```
使用 .ui-empty 类:
  border: 1px dashed var(--border-strong)
  border-radius: var(--radius-md) = 12px
  background: rgba(255, 255, 255, 0.7)
  padding: 3rem 1.5rem
  text-align: center

空状态文案（中文）：
  无课程:    图标 BookOpen
             「还没有课程」
             「上传教学大纲或 PDF 开始学习」
             [上传文件] — .ui-button-primary

  无复习:    图标 CheckCircle
             「今天没有到期的复习」
             「可以学习新内容或者做练习」

  无弱点:    图标 TrendingUp
             「目前没有检测到持续弱点」
             「继续保持！」

规则：
  - 空状态永远居中显示
  - 不使用大插图
  - 文案语气温和正向
```

---

## 第六章：移动端适配规则

```
断点: 768px (唯一关键断点)

< 768px:
  - 顶部导航改为紧凑模式
  - .ui-shell padding 1.5rem
  - 课程卡片: grid → stack
  - 知识树: 缩小节点宽度
  - Checkpoint: 选项高度增加到 52px (触控友好)

字号调整:
  - 正文: 16px (不缩小)
  - 标题: 从 24px 降到 20px
  - 辅助文字: 从 12px 升到 13px

间距调整:
  - 页面水平内边距: 1.5rem
  - 卡片内边距: 16px

交互差异:
  - 没有 hover 态 (触屏设备)
  - 所有可点击元素最小 44x44px
  - 下拉菜单 → bottom sheet
  - tooltip → bottom sheet

禁止项:
  ✗ 水平滚动 (除了代码块和 .ui-tab-row)
  ✗ 固定宽度元素超出屏幕
  ✗ 依赖 hover 才能看到的信息
  ✗ 小于 13px 的文字
```

---

## 第七章：技术栈参考

```
框架:      Next.js 16 (App Router) + React 19 + TypeScript
样式:      Tailwind CSS v4 + CSS 变量 + ui-* 自定义类
AI/ML:     Vercel AI SDK (@ai-sdk/openai)
数据库:    Supabase (PostgreSQL)
间隔重复:  ts-fsrs
图标:      lucide-react
Markdown:  react-markdown + remark-gfm + remark-math + rehype-highlight + rehype-katex
国际化:    自定义 i18n context (EN/ZH)
验证:      zod
文件上传:  react-dropzone
```

---

## 第八章：使用方法

### 喂给 AI 时的 prompt 模板

当你需要让 AI 生成 CourseHub 的某个页面时，使用以下 prompt 结构：

```
请为 CourseHub 生成 [页面名称] 的 React 组件代码。

设计规范：
[粘贴本文件的第二章（设计令牌）和第三章（CSS 类体系）]

页面需求：
[描述这个页面的功能和包含的组件]

约束：
- 使用 Tailwind CSS v4 + CSS 变量 + ui-* 自定义类
- 使用 Lucide React 图标
- 使用系统字体栈 (-apple-system, Inter)
- 使用 JetBrains Mono 代码字体
- 颜色通过 var(--accent), var(--success) 等引用，不硬编码
- 所有 UI 文字使用 i18n，支持中/英切换
- 所有学科术语首次出现标注英文
- 不使用任何文件中未定义的颜色或字号
- 移动端 < 768px 时调整布局
```

---

## 附录：对照检查清单

每次完成一个新页面后，对照以下清单检查：

```
☐ 语言一致性: 页面上所有 UI 控件是否为同一语言？
☐ 颜色语义: 红/黄/绿/靛蓝/灰是否按照规范的语义使用？
☐ 字体: 是否使用了 Inter 系统栈？代码是否用 JetBrains Mono？
☐ CSS 类: 是否优先使用了 ui-* 类？
☐ 间距: 是否基于 4px 网格？卡片内边距是否为 24px？
☐ 圆角: 标签 8px、卡片 16px、按钮 10px 是否一致？
☐ 主行动: 页面上是否只有一个 .ui-button-primary？
☐ 空状态: 如果内容为空，是否使用了 .ui-empty？
☐ 加载态: 是否使用骨架屏而非 spinner？
☐ 移动端: 在 375px 宽度下是否可用？是否有 44px 最小点击区域？
☐ 动画: 是否有 160ms+ 过渡？是否检查了 prefers-reduced-motion？
☐ 无障碍: .ui-icon-button 是否有 aria-label？颜色对比度是否达标？
```
