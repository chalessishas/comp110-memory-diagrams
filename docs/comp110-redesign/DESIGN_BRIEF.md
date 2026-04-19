# COMP110-26s 站点视觉更迭 · 设计规格

> 这份文档是给 **Claude Design / DeepSeek / 任意 AI** 作为 prompt 或实现参考的设计规格。
> 参考实现：`./mockup.html`（开浏览器直接看）
> 原站：https://comp110-26s.github.io/

---

## 一、项目目标

把 Kris Jordan 的 COMP110 站点（Bootstrap 遗风 · 2024 视觉）升级为 **2026 现代教育站** 美学，同时：

1. **保留 Kris 的品牌 DNA**（Carolina 黄 · 温暖语气 · 「Made with 💛 in Chapel Hill」）
2. **加一个 AI TA 入口**（右下角浮层，不打扰 Kris 原本的内容层级）
3. **原站结构 1:1 对应**：`agenda / resources / support / syllabus / team110` 五段导航保留
4. **纯设计稿**，不含业务逻辑、不含真实后端调用

---

## 二、设计决策（为什么这么做）

### 保留
| 元素 | 为什么保留 |
|------|-----------|
| 黄色作为品牌色 | Kris 的 💛 是情感符号，是 COMP110 区别于其他 CS 课的"温度" |
| 倒序 / 正序混合的 agenda | "On the Horizon → This Week → The Past" 三段式是 Kris 的教学节奏隐喻 |
| badge 类型体系 (CL/LS/EX/QZ/CQ/FN) | 学生已经用了一学期，换 badge 设计但不换语义 |
| 五段顶部导航 | 不重构信息架构，只换皮 |

### 推翻
| 元素 | 为什么推翻 |
|------|-----------|
| Bootstrap 网格 + 默认字体 | 2025+ 的教育产品普遍迁移到 Inter / Geist 这类现代 sans-serif |
| 链接蓝色为主色 | 过于程序员味，让内容被 UI 分心 |
| 纯文字列表的 agenda | 没有日期 / 类型 / 状态的视觉层次，学生扫不过来 |
| "Dark Mode" 按钮 | 浏览器的 `prefers-color-scheme` 已成标准，默认跟随系统 |

### 新增
| 元素 | 为什么新增 |
|------|-----------|
| 进度环 (82% · Week 13 of 15) | 给学生一个"我还剩多少"的感官锚点 |
| 过滤 chip (All / Lectures / Exercises / Quizzes) | 临近期末学生只想看 QZ / EX 的时候不用滚到底 |
| Timeline / Grid / Week 三视图 | 可选，符合学生不同时间点的使用模式 |
| `is-today` 高亮 + `TODAY` 徽标 | 每天打开就知道今天要干什么 |
| 状态标签 (Submitted / Attended / Due in X days) | 把 Gradescope 的完成度映射到站点 |
| 右侧 sidebar: Next up + Quick Links + Topic Index | 随时随地能跳到期末复习资源 |
| 右下角 AI TA FAB | 真正的差异化点，见下方专章 |

---

## 三、设计系统 Tokens

### 颜色

```css
/* Light */
--bg: #FAF8F3;          /* 象牙白，比纯白温暖，类似 Kris 原站的米色纸感 */
--bg-elev: #FFFFFF;     /* 卡片层 */
--ink: #171717;         /* 主文本 */
--ink-2: #4B4B4B;       /* 次文本 */
--ink-3: #8B8B8B;       /* 辅助文字 */
--line: #E7E3DA;        /* 分隔线，偏暖米色 */
--brand: #F5B700;       /* Carolina 黄，主品牌色 */
--brand-soft: #FFF5D6;  /* 黄的背景变体 */
--accent: #0E6BA8;      /* 深蓝做正文链接 */
--danger: #B23A48;      /* Quiz / 紧急截止 */
--ok: #2E7D5B;          /* Submitted / Done */

/* Dark 版本跟随 prefers-color-scheme，色温保持暖调 */
```

### 字体

- 主字体：`Inter` / `SF Pro Text`（回退到系统 sans）
- 数字：`font-variant-numeric: tabular-nums`（日期对齐）
- 等宽：`JetBrains Mono`（badge / 代码 / 元信息）
- 字号：body 15px / h1 40px / caption 11-12px
- 字重：400 body / 600 item title / 700 section head & nav / 800 badges

### 空间

- 圆角：卡片 14px / 按钮 10px / chip 999px (pill)
- 阴影：`0 1px 2px rgba(0,0,0,.04), 0 8px 24px rgba(23,23,23,.06)` 作为浮层基准
- 栅格：max-width 1200px · 主内容 `1fr 280px`（sidebar 280）
- 断点：920px 以下折叠 sidebar

### 动效

- 只在 hover 和状态切换时用 `transition: all .15s`
- TA FAB 的 `pulse` 动画（脉冲呼吸光圈，2.5s 周期）
- 避免滚动视差、入场动画这类"炫技"

---

## 四、页面结构（逐块说明）

### 1. 顶部导航（sticky）
- 左：`brand-mark` (黄色方块 `110`) + 两行文字 `COMP110 / Spring 2026 · Kris Jordan`
- 中：五个 pill-style 链接
- 右：搜索图标 + 主题图标（两个 `btn-icon`）
- 使用 `backdrop-filter: blur(12px)` 做毛玻璃半透明

### 2. Hero 区
- eyebrow（小徽标 + 课程描述）
- 大标题：保留 Kris 的原意但加个人化 `"An itinerary for learning to code from zero, in Python."`
- 右侧：Progress Ring（环形进度 + "Week 13 of 15"）

### 3. 过滤与视图切换
- chip 行：All / Lectures / Lessons / Exercises / Quizzes / Cancelled
- 右侧：Timeline / Grid / Week 三态切换
- 当前 mockup 只实现 Timeline 视图

### 4. Agenda 主区（左 8/12 栏）

#### 4.1 On the Horizon (即将到来)
每条 `day-group` = 左列日期 + 右列 items
- date 显示为 `Apr 30` (大) + `Thu` (小) + 可选 TODAY badge
- item 左侧 badge（颜色按类型） + 中间标题和资源链接 + 右侧状态

#### 4.2 This Week
今日用 `is-today` 高亮（黄色渐变背景 + TODAY badge）

#### 4.3 The Past (折叠)
默认折叠，点击展开。避免一打开就看到 48 条历史。

### 5. Sidebar（右 4/12 栏）
- Card: Next up（两条最近的截止项 + 左侧颜色 bar 表紧急度）
- Card: Quick Links（Gradescope / Ed / OH / Memory Diagram / Python Tutor）
- Card: Topic Index（六大主题跳转）

### 6. Footer
- 保留 "Made with 💛 in Chapel Hill · UNC Department of Computer Science"
- 右侧三个外链：Feedback / Source / Honor Code

### 7. AI TA 浮层（核心差异化）

**收起态**：右下 24px 的 pill-shaped FAB
- 黑底 · 黄色呼吸脉冲点 · 白字 "Ask COMP110 TA"
- 不遮住任何内容，有 hover 上浮动效

**展开态**：380px × 560px 的面板
- 头部：黄色 avatar "TA" + "COMP110 TA · Online · Knows your whole syllabus"
- Context 条：`You're on CL33 · CSV Data Analysis. TA context loaded: slides, past lectures, Python cheat sheet.`
  - **关键**：TA 面板应该随当前页面 context 自动切换，这是它优于 ChatGPT 的核心
- 消息区：AI 消息偏左（浅色气泡）+ 我的消息偏右（黑底）
- 快捷建议按钮：Help with EX08 / Draw a memory diagram / Final exam study plan
- 输入框 + 黄色发送按钮

**交互原则**（喂给 DeepSeek 时务必附带）：
- TA 禁止直接给 exercise 答案（UNC Honor Code）
- TA 必须用 Socratic 风格（提问引导）
- TA 引用课程资源时用 `<code>` 格式化符号名

### Socratic AI TA System Prompt 完整模板

> 直接复制以下内容作为 `messages[0].role = "system"` 的 content。  
> `{{...}}` 占位符在 Next.js 运行时由当前页面 context 注入。

```
You are the AI Teaching Assistant for COMP110: Introduction to Programming in Python at UNC Chapel Hill, taught by Kris Jordan.

=== CURRENT CONTEXT ===
Today's date: {{CURRENT_DATE}}
Current lesson: {{LESSON_ID}} — {{LESSON_TITLE}}
Available resources for this lesson: {{RESOURCE_LIST}}
Student is currently viewing: {{CURRENT_PAGE}}
=== END CONTEXT ===

=== COURSE IDENTITY ===
COMP110 uses Python 3.12. Core topics covered so far (Week {{CURRENT_WEEK}} of 15):
{{TOPICS_COVERED}}

Assignment types:
- CL (Class Lecture): in-class exercises, auto-graded on Gradescope
- LS (Lesson): pre-class reading/coding tasks
- EX (Exercise): multi-part take-home assignments
- QZ (Quiz): timed assessments
- CQ (Challenge Question): optional hard extensions

=== YOUR ROLE ===
You are a Socratic TA. Your job is to help students think, not to think for them.

NEVER:
- Give the direct solution to any CL, LS, or EX problem
- Write complete functions or loops that solve a student's assignment
- Debug their code for them by pointing to the exact line and fix
- Reveal expected output or test cases for graded work

ALWAYS:
- Ask a clarifying question before assuming what the student is stuck on
- Guide with smaller sub-questions ("What does this line do when x is 0?")
- Point to the relevant concept first ("This is related to the notion of mutation vs. reassignment — which do you think is happening here?")
- Celebrate partial understanding before pushing further
- Reference specific course vocabulary (e.g., "expression", "statement", "call stack frame", "heap", "reference") so students build the right mental model

WHEN A STUDENT ASKS ABOUT MEMORY DIAGRAMS:
Memory diagrams in COMP110 follow strict rules. Always ask the student to walk you through their diagram first. Key rules to probe for:
- Stack frames are drawn per function call, not per variable
- Each frame has a Return Address and local variables only
- Heap objects (lists, dicts, objects) live outside all frames with an arrow from the variable
- After a function returns, its frame is erased — test whether the student accounts for this

TONE:
- Warm but intellectually rigorous (Kris's own style)
- Short responses (3–6 sentences unless explaining a concept)
- End each message with exactly one question to keep the student thinking
- Never say "Great question!" or "Of course!"

=== LANGUAGE POLICY ===
Reply in the same language the student used. If the student writes in Chinese, respond in Chinese but keep all Python keywords, identifiers, and COMP110 item IDs (EX08, CL33, etc.) in English.
```

**Runtime context injection** (Next.js implementation note):
```typescript
// In your API route or server component:
const systemPrompt = SYSTEM_PROMPT_TEMPLATE
  .replace('{{CURRENT_DATE}}', new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }))
  .replace('{{LESSON_ID}}', currentItem.id)           // e.g. "CL33"
  .replace('{{LESSON_TITLE}}', currentItem.title)      // e.g. "CSV Data Analysis"
  .replace('{{RESOURCE_LIST}}', currentItem.resources.join(', '))
  .replace('{{CURRENT_PAGE}}', pagePath)               // e.g. "/resources"
  .replace('{{CURRENT_WEEK}}', String(currentWeek))    // e.g. "13"
  .replace('{{TOPICS_COVERED}}', topicsSoFar.join('\n'));
```

---

## 五、DeepSeek / Claude Design Prompt 模板

直接复制下面这段喂给任何 AI：

```
我要把 https://comp110-26s.github.io/ 重新设计一版，产出一个 Next.js 15 (App Router) + Tailwind v4
项目，目标：

1. 视觉风格参考附件 mockup.html（Inter 字体 · Carolina 黄 #F5B700 作为品牌色 · 暖米色背景
   #FAF8F3 · 圆角 14px · 卡片化 agenda）
2. 页面结构：/ (agenda) · /resources · /support · /syllabus · /team110 五页
3. agenda 数据来自 docs/comp110-redesign/agenda.json（或从 comp110_repository_manifest.json 提取）
4. badge 语义配色：CL=黄 · LS=蓝 · EX=绿 · QZ=红 · CQ=紫 · FN=黑金
5. Sticky top nav + 左主右侧栏布局 + 右下 AI TA 浮层
6. AI TA 浮层先做 UI shell，API 接入 DeepSeek 的 chat/completions，system prompt 里
   注入当前页面 context（课程、日期、当前 item）
7. 支持 prefers-color-scheme 自动暗黑模式，不做 toggle
8. 不做服务端渲染式的登录（Vercel 部署够用）
9. 真实 embedding 检索以后再加，先把 UI 搭起来

禁止做的事：
- 不要加真实的 Gradescope / Panopto 集成（UNC SSO 私有）
- 不要实现自动评分
- 不要抄袭 Kris 的内容文字（只照 mockup 的视觉与交互，真实文案用 placeholder）
- 不要加分析追踪（Plausible / GA 都不加，先跑通）
```

---

## 六、下一步建议

| 阶段 | 要做 | 谁做 |
|------|------|------|
| Phase 1 · 设计 | ✅ 本 mockup + DESIGN_BRIEF | Claude Code（已完成） |
| Phase 2 · 实现 | Next.js 脚手架 + 五页骨架 + TA 浮层 UI | DeepSeek-Coder |
| Phase 3 · 数据 | agenda.json 从 repository_manifest.json 生成 | 任意脚本 |
| Phase 4 · AI TA | system prompt + DeepSeek API 接入 + RAG 用 pgvector | DeepSeek / Cursor |
| Phase 5 · 授权 | 发邮件给 Kris Jordan 说明非商用研究用途 | 主人 |

---

## 七、踩坑提醒

1. **Kris 原站的 badge 链接有位置错位**（CL07 指向 cl06.pdf 等），重建时按实际文件名来，不要照抄原站链接。
2. **所有历史学期 `.md` 源被 gitignore**，只能拿 HTML。HTML → Markdown 转换时 SVG 图标会变成破 alt，清理一遍。
3. **memory_diagrams_v0.pdf 的规则要单独喂给 AI TA 作为 rubric**，不是一般内容，是考试评分标准。
4. **不要追 Gradescope autograder**，那是闭源 SaaS，学生端也看不到，照做没意义。
5. **"Dark Mode 按钮" 别抄**，用 `prefers-color-scheme` media query 就够，省一个组件。
6. **Tailwind v4 配置方式彻底变了**（2026-04 确认）：不要生成 `tailwind.config.ts`，改用 CSS `@theme {}` 块定义 tokens；PostCSS 插件换成 `@tailwindcss/postcss`；安装命令：`npm install tailwindcss@latest @tailwindcss/postcss@latest`。把 mockup.html 里的 CSS 变量（`--color-brand: #F5B700` 等）直接翻译到 `@theme {}` 即可，一一对应无需重写逻辑。

---

## 八、文件清单

```
docs/comp110-redesign/
├── DESIGN_BRIEF.md      ← 本文件（handoff 规格）
└── mockup.html          ← 静态 HTML 原型（浏览器打开即可）
```

可选补充（主人需要再说）：
- `agenda.json`（结构化数据，从已扒的 JSON 生成）
- `tailwind.config.ts`（把上面的 tokens 翻成 Tailwind theme）
- `components.md`（按 shadcn/ui 风格拆每个组件的 props）
