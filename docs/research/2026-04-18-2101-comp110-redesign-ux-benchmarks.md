# COMP110 Redesign — 2026 Visual & Pedagogical Benchmarks

**调研时间**：2026-04-18 21:01–21:25  
**调研目的**：为 `comp110-redesign` Phase 2（Next.js 15 + Tailwind v4）实施者 DeepSeek 提供可直接照搬或可证伪的外部参考。Phase 1 已锁定 Carolina 黄 + 暖米主色、Hero 进度环、右侧 Next-Up 栏、右下 AI TA FAB（Socratic 不直接给答案）。这份文档的任务不是重新讨论方向，而是用真实案例把方向「压实」。  
**方法**：WebSearch + WebFetch 实地抓取 HTML，每条 finding 带 URL + 对 Phase 2 的具体影响。不可验证内容标 `[UNVERIFIED]`。

---

## 1. 教育类网站 UI/UX 趋势 2026

### 1.1 Bento Grid 已从「新鲜感」变成「事实标准」

- **URL**：<https://desinance.com/design/bento-grid-web-design/>  
  **发现**：2026 年进入「Bento 2.0」——夸张的圆角（12–24px）、细腻的 hover/scroll micro-interaction、模块间留白统一 12–24px。已被教育平台、SaaS dashboard 普遍采用。  
  **对我们的启示**：Phase 1 mockup 的 Hero + 右侧 Next-Up 其实已经是小型 bento；Phase 2 应把 mockup 的 agenda 区从「表格」进一步模块化成 bento（周 card、type badge、due 徽标独立成块），圆角统一用 `rounded-2xl`（16px）或 `rounded-3xl`（24px）。

- **URL**：<https://www.galaxyux.studio/blog/bento-grids-the-new-standard-for-modular-ui-design/>  
  **发现**：Bento 的核心不是「都切成小块」而是**非对称大小**——大卡片承载主信息，小卡片作补充。全部同尺寸等于退化成普通 grid，反而失去 bento 的识别度。  
  **对我们的启示**：Hero 进度环卡（大）＋ 右侧 Next-Up 三条栏（小）＋ 下方 Week 卡（中）构成三段尺寸梯度。DeepSeek 实施时不要把所有 week 切成等宽等高，「当前周」卡必须显著大于「过去周」卡（建议 2:1 面积比）。

- **URL**：<https://landdding.com/blog/blog-bento-grid-design-guide>  
  **发现**：Bento 的常见翻车是「超过 12–15 张卡同时在视野内」，认知负荷直接崩盘。  
  **对我们的启示**：COMP110 有 15 周课，**不允许**把 15 周全部堆在首屏。做法：首屏只展示「当前周 + 前后两周」共 3 张卡 + 「查看全部 15 周」CTA 进入 `/agenda` 页面。这与 Phase 1 `agenda.json` 的 `currentWeek` 字段天然耦合。

### 1.2 Kinetic Typography + Variable Fonts 取代「静态 Hero 图」

- **URL**：<https://midrocket.com/en/guides/ui-design-trends-2026/>  
  **发现**：2026 年主流 Hero 不再放 stock photo/illustration，而是**可变字体**的大标题 + 滚动时字重/宽度联动变化（variable font axis 动画）。CSS `font-variation-settings` + `IntersectionObserver` 即可。  
  **对我们的启示**：Phase 1 Hero 里「Week 13 / 15」进度环 + 课程名可用 Inter Variable 或 Recursive Variable 实现：滚动到 Hero 时 weight 从 400 → 800，宽度从 narrow → wide。无需引入动画库，<100 行 JS。

- **URL**：<https://elements.envato.com/learn/ux-ui-design-trends>  
  **发现**：2026 年主题词是 **Calm Interfaces + Transparent AI + End of Visual Theatrics**——过度动画、装饰性粒子、3D shader 开始被视为「噪音」，设计回归冷静的信息密度。  
  **对我们的启示**：不要做 GSAP 滚动叙事或 Three.js 背景。Phase 2 的视觉差异化应来自**信息设计**（进度环、urgency 条、type badge 体系）而不是「运动」。这对 DeepSeek 是减负：省掉一整类依赖。

### 1.3 Neobrutalism 在高校语境「有限回归」

- **URL**：<https://colorwhistle.com/neo-brutalism-higher-education-web-ux/>  
  **发现**：2024–2026 间，部分「进步型高校站」把 Neobrutalism 当差异化武器：厚边框（2–4px 实线黑）、硬阴影（4px 4px 0 #000 偏移不模糊）、高饱和撞色、裸露 system font。  
  **对我们的启示**：Carolina 黄 #F5B700 + 暖米 #FAF8F3 的组合天然接近 brutalist 调性。可以**选择性**借用：type badge 边框用 2px 黑、badge 阴影用 hard shadow（`box-shadow: 3px 3px 0 #000`），但不要整站 brutalism——UNC 是老牌学校，过度前卫会伤品牌。

- **URL**：<https://www.nngroup.com/articles/neobrutalism/>  
  **发现**：NN/G 警告 neobrutalism 的可达性陷阱：对比度过高反而引发视觉疲劳，硬边框 + 高饱和对色弱不友好。  
  **对我们的启示**：Phase 2 必须在 DESIGN_BRIEF 中明确 **WCAG 2.2 AA 合规**，对 #F5B700 黄配白字要检查——黄白对比度只有 ~1.7，必须改成黄底黑字（`text-neutral-900 on bg-[#F5B700]`）。

### 1.4 Glassmorphism 活着，Neumorphism 当调味

- **URL**：<https://www.zignuts.com/blog/neumorphism-vs-glassmorphism>  
  **发现**：2026 年 Glassmorphism 因 Apple Liquid Glass 被重新激活，在 AI chat 面板、导航 overlay 上广泛使用。Neumorphism 不再做整体风格，只当局部 tactile 点缀。  
  **对我们的启示**：**AI TA FAB 的 380×560 面板应用 glassmorphism**（`backdrop-filter: blur(20px)` + `bg-white/70` + `border border-white/40`），这样在 agenda 表格/bento 上层悬浮时不切断上下文。Neumorphism 仅保留在「提交作业」按钮的 pressed 状态。

### 1.5 可访问性成为基础设施，不是功能

- **URL**：<https://www.wearetenet.com/blog/ui-ux-design-trends>  
  **发现**：European Accessibility Act 2025-06 生效 + WCAG 2.2 要求：reduced-motion、keyboard-first、高对比模式是出厂默认，不是「无障碍页」一个选项。  
  **对我们的启示**：所有 Framer Motion / CSS 动画都要包 `@media (prefers-reduced-motion: reduce)` fallback；AI TA FAB 必须可 Tab 聚焦 + Esc 关闭 + `aria-expanded`；type badge 不允许只用颜色区分（加 icon 或简短文字）。

---

## 2. Bootstrap → 现代化重构最佳实践

### 2.1 增量迁移 > 大爆炸重写

- **URL**：<https://st6.io/blog/migrating-from-bootstrap-to-tailwind-part-3/>  
  **发现**：ST6 Studio 把 Tailwind 先**叠加**在 Bootstrap 之上（两套 CSS 并存），页面级逐步替换，边迁移边发布新 feature。零停机。  
  **对我们的启示**：COMP110 是活跃运行的课，不能直接断开原站。建议 Phase 2 在新 Next.js 项目里重写（`comp110-26s-next`），不碰原 Jekyll 仓库，上线后做 DNS 切流 + 保留原站 `/legacy/*` 作为历史页。

- **URL**：<https://medium.com/@vdaubry/how-we-migrated-16k-lines-of-html-css-from-bootstrap-to-tailwind-using-claude-code-4d2c4c3dff64>  
  **发现**：一位开发者用 Claude Code 迁移 16K 行 Bootstrap → Tailwind，耗时约 2 天（原估 2 周）。关键：**保持 HTML 结构不动，只替换 class 字符串**，再用 diff 回归测试。  
  **对我们的启示**：如果 DeepSeek 选择渐进改造而非重写，可以让它先对 `mockup.html` 做 class 替换生成 React 组件，而不是从零写。但因为我们的 mockup 是纯 HTML 没有原 Bootstrap 包袱，重写反而更省事。

- **URL**：<https://www.vantage.sh/blog/bootstrap-tailwind-migration>  
  **发现**：Vantage 从 Bootstrap 迁到 Tailwind 的动机是「bloat + debug 难」——`.btn.btn-primary.btn-lg.me-2` 这种组合在 DevTools 里极难追溯源头；Tailwind 的 utility class 在 DOM 里就是最终样式，0 推理成本。  
  **对我们的启示**：DeepSeek 写组件时**不要**把 Tailwind class 打包成自定义 class（`.course-card-primary`），保持原始 utility 写法，AI/人读都更快。仅在**三处以上重复**时抽成 `@apply` 或 React 组件。

### 2.2 迁移常见坑

- **URL**：<https://omid.dev/2024/05/22/migrate-css-bootstrap-to-tailwind/>  
  **发现**：Bootstrap 的 JS 组件（Modal/Dropdown/Offcanvas）在 Tailwind 里没有等价实现——必须引 Headless UI 或 Radix。不提前规划会踩全套坑。  
  **对我们的启示**：AI TA FAB 面板（open/close/focus trap）不要自己造轮子，直接用 **Radix Dialog**（非模态变体）或 **shadcn/ui Sheet**，一个组件解决键盘可达性 + 遮罩 + 动画。

- **URL**：<https://www.digitalapplied.com/blog/tailwind-css-v4-migration-new-features-guide>  
  **发现**：Tailwind v4 抛弃 JS config，改用 `@theme` CSS 指令定义 token；内置 Lightning CSS（Rust），构建速度 2–10x；production CSS 比 v3 小 70%。  
  **对我们的启示**：Phase 2 直接用 Tailwind v4，在 `globals.css` 里用 `@theme` 定义 Carolina 黄、6 色 type badge、暖米背景：
  ```css
  @theme {
    --color-carolina: #F5B700;
    --color-warm-paper: #FAF8F3;
    --color-type-lecture: #2563EB;
    /* ... */
  }
  ```
  DeepSeek 只要读 `DESIGN_BRIEF.md` 的 token 表直接 copy-paste。

### 2.3 Jekyll/GitHub Pages → Next.js 迁移

- `[UNVERIFIED]` 未找到专门针对 Jekyll→Next.js 的高信度迁移指南；但 Next.js 15 的 **Static Export**（`output: 'export'`）可以输出到 GitHub Pages 兼容的 `out/` 目录，URL 结构与 Jekyll 兼容（`/agenda/week-13/`），迁移风险可控。  
  **对我们的启示**：仓库命名建议 `comp110-26s-next`，GitHub Pages + 自定义域名 `comp110.cs.unc.edu`（需找 Kris Jordan 拿 CNAME 权限——这条要标给主教师做）。

---

## 3. 同类高校 CS 入门课站 Benchmark

实地抓取了 7 个站点的首页，关键观察整理如下：

### 3.1 Berkeley CS61A — 信息密度冠军

- **URL**：<https://cs61a.org/>  
  **实测**：水平导航（Lectures / Syllabus / Ed / Office Hours / Contact + 下拉 Links / Resources / Guides / Staff）；Hero 是课名 + 上课时间一句话；**反向时间序公告**占首屏大面积；Schedule 用**纯表格**（Week / Date / Topic / Chapter / Lab & Discussion / HW & Project）；链接全蓝色下划线。  
  **亮点**：公告置顶、deadline 文字嵌入公告内（「Scheme Checkpoint 1 is due tomorrow」）。  
  **痛点**：表格里一行塞 6 列，移动端必定横滚；0 视觉 hierarchy 之外的 urgency 线索。  
  **对我们的启示**：学「公告时间序」但**改造成**右侧 Next-Up 面板（Phase 1 已有）。拒绝「一行 6 列表格」——按周切 card，每 card 内部纵向列出 lab/hw/project。

### 3.2 Stanford CS106B — 学院派克制

- **URL**：<http://web.stanford.edu/class/cs106b/>  
  **实测**：左侧展开式 sidebar（Course/Lectures/Sections/Assignments/Exams）；Stanford 红 + 黑字 + 蓝链接的严格三色；staff 以 grid 照片墙；**日历外包给 Google Sheets**（一个 📅 Omni-Grid 链接跳出去）；作业用 emoji 区分（🌱 Recursion Etudes）。  
  **亮点**：无多余装饰，加载极快；emoji 成为视觉速读锚点。  
  **痛点**：没有任何 urgency／progress 提示；日历外挂是「反 UX」——学生每次想看 deadline 要跳三次。  
  **对我们的启示**：emoji 作为 type prefix 是可以借用的轻量手段（在中文/英文里都通用），但**必须和 type badge 颜色体系绑定**（如 🧪 = 蓝 badge = Lab，📖 = 紫 badge = Reading）。Phase 1 已有 6 色体系，加 emoji 是 0 成本增强。

### 3.3 Harvard CS50 / CS50x — 模块化 + AI 内嵌标杆

- **URL**：<https://cs50.harvard.edu/x/> ＋ <https://cs50.harvard.edu/x/weeks/0/>  
  **实测**：左侧 sidebar（Week 0–10 线性列表）；per-week 页是**分级列表**（Lecture / Shorts / Problem Set 嵌套），每个资源多种格式（audio/PDF/HDR video/subtitles）。**视觉上是 CS50.ai 链接 + 鸭子 icon**，但 CS50.ai 是独立站 <https://cs50.ai>，不是 iframe 嵌入。整体仍是「功利主义信息架构」，不华丽。  
  **亮点**：格式冗余（同一份素材提供 audio + HDR + SDR + YouTube + 中英字幕）是真正的 accessibility 旗舰；学生想要啥都有。  
  **痛点**：首页信息扁平，week 0 和 week 10 视觉权重相同，不帮学生建立「当前进度」概念。  
  **对我们的启示**：（1）格式冗余值得学——COMP110 每周课要至少提供 slides PDF + 录屏 + 转写。（2）AI TA 集成**不学 CS50 的独立站模式**——我们用 FAB 内嵌在课程页，学生不用跳出上下文。

### 3.4 UMich EECS 183 — 最接近 COMP110 的参考模型

- **URL**：<https://eecs183.github.io/eecs183.org/>  
  **实测**：水平导航（Schedule/Piazza/Office Hours/Resources/Staff/Gradescope/Canvas/Google Drive）；「This Week」+「Current Projects and Labs」双分区首屏；week schedule 用 **表格** 但资源卡用 **icon + 图片**（zybooks、Visual Studio、XCode）。  
  **亮点**：「This Week」分区 = 学生每天第一眼就知道要干啥，这正是 Phase 1 mockup 已经做的事。  
  **痛点**：GitHub Pages 托管 → 纯静态 → 没有进度个性化；配色是 UMich 蓝/黄很朴素但未现代化处理。  
  **对我们的启示**：UMich 在「本周视图」这件事上已经对路了，COMP110 把它做得更**视觉化**（进度环 + urgency bar + type badge）就能形成差异。这是低风险 + 高差异的切入点。

### 3.5 Stanford CS106A / CMU 15-112 / MIT 6.100A — 「学院派低调」范式

- **URL**：<https://cs106a.stanford.edu/>（302 → web.stanford.edu/class/cs106a/）/ <https://www.cs.cmu.edu/~112/> / <https://introcomp.mit.edu/spring25/information>  
  **实测**：共同特征——水平/侧边导航、单色极简、无动画、无进度、无 AI TA 直接内嵌（MIT 6.100A 有 AI Tutor 链接但藏在 Help 菜单下）。MIT 6.100A 甚至在 footer 放 ASCII cat。  
  **亮点**：可靠、快、可读；教师维护简单。  
  **痛点**：都是 2015–2020 年代审美。信息设计=内容罗列，不帮学生做优先级判断。  
  **对我们的启示**：COMP110 重构的「市场空白」正是这里——主流 CS 入门站没有一个做**视觉化 urgency + 进度感**。这是可辩护的差异化方向（见 Top 5 推荐 #1）。

### 3.6 共性总结（7 站）

| 维度 | 主流现状 | COMP110 Phase 2 差异化机会 |
|------|---------|----------------------------|
| 导航 | 水平链接或左 sidebar | 保持水平（UNC 传统），但加「当前周」badge |
| 颜色 | 校色 + 蓝链接，基本 2 色 | Carolina 黄 + 暖米 + 6 色 type badge |
| 日程 | 表格 or 外挂 Google Sheets | Bento 周卡 + urgency 可视化 |
| 进度 | 无 | 进度环 + 已完成周数 |
| AI TA | 外链或无 | 内嵌 FAB，Socratic 不直接给答案 |
| 可达性 | 基础合规 | WCAG 2.2 AA + reduced-motion |
| 公告 | 反向时间序列表 | 右侧 Next-Up urgency bar（优先级≠时间序） |

---

## 4. AI TA / 课程 AI 助教集成模式

### 4.1 CS50 Duck：Socratic 内嵌的黄金标准

- **URL**：<https://cs50.readthedocs.io/cs50.ai/> ＋ <https://cs50.harvard.edu/college/2023/fall/notes/ai/>  
  **实测**：基于 Azure OpenAI + 自建 vector DB（存课程讲义/offerings）的 RAG；独立 UI <https://cs50.ai> + VS Code 扩展 `ddb50.vsix`；**pedagogical guardrails 不让它直接给答案**。201k 用户，9.4M prompt 总量，35k/天活跃。  
  **对我们的启示**：这是目前**唯一已公开**的「Socratic 课程内嵌 AI」大规模实践。Phase 1 的 `socratic_ta_examples.md` 正确模仿了其策略（show, don't tell），Phase 2 实施时可直接 system prompt 借鉴。

- **URL**：<https://dl.acm.org/doi/10.1145/3626253.3635427>（ACM SIGCSE 2024: Teaching CS50 with AI）  
  **发现**：CS50 团队的关键结论——**Few-shot prompt > 通用模型 fine-tune** 在「维持 Socratic 风格」这件事上 ROI 更高；用户反馈持续闭环（thumbs up/down）是质量的关键。  
  **对我们的启示**：Phase 2 不要一开始就 fine-tune 模型；用 system prompt + 10–20 个 few-shot 例子（Phase 1 `socratic_ta_examples.md` 已经有骨架）跑到 MVP，等真实学生数据累积后再考虑微调。

- **URL**：<https://cs.harvard.edu/malan/publications/fp0627-liu.pdf>（Improving AI in CS50, 2025）  
  **发现**：CS50 在 2024–2025 的迭代里发现：**纯 Socratic 有时让弱学生卡死**——完全不给答案会挫败感爆表。改良是**分级给示意**（hint → pseudo-code → 关键 function 签名，但永不给完整代码）。  
  **对我们的启示**：Phase 1 `socratic_ta_examples.md` 只示范了「永不给答案」模式，这在 CS50 实战被证伪。补一个**三级 hint 策略**：L1 反问「这里你试了什么」→ L2 给出思考方向「考虑递归基准情形」→ L3 给伪代码但不给 Python。

### 4.2 Khanmigo：另一条 Socratic 道路

- **URL**：<https://www.khanmigo.ai/learners>  
  **实测**：GPT-4 基座；UI 是**侧边栏 chat**（不是 FAB），和课程内容并列；TTS/STT 双向语音；**主动向学生发问**而不是等学生问。  
  **对我们的启示**：侧边栏式固然好（更「共现」课程内容），但会吃屏幕宽度——COMP110 信息密度已经高，**FAB 模式更合适**。保留 Khanmigo 的一个长处：TTS 朗读 AI 回复，可用浏览器原生 `SpeechSynthesis` API 免费实现（零成本亮点）。

### 4.3 MIT 6.100A AI Tutor：低调路线

- **URL**：<https://introcomp.mit.edu/spring25/information>  
  **实测**：AI Tutor 仅作为 `Help` 下拉菜单的一个链接，`[UNVERIFIED]` 未抓取到具体 UI，但从 IA 判断是**链接跳转**模式，非内嵌。  
  **对我们的启示**：MIT 的保守路线是「可选工具」而不是首页英雄。COMP110 定位应该比 MIT 更激进（AI TA 是 Hero 的一部分），但要留退路：右下 FAB 允许用户**永久折叠**（localStorage 记状态），尊重不想用 AI 的学生。

### 4.4 UI 位置：FAB vs Sidebar vs Inline Widget

| 模式 | 优 | 劣 | 适用 |
|------|---|---|------|
| FAB（右下） | 不占布局、可全局 | 首次使用提示需要 onboarding | 信息密度高的站 ← COMP110 选此 |
| Sidebar（Khanmigo） | 和内容共现、常驻 | 吃屏幕 30–40% 宽度 | 内容相对稀疏的学习页 |
| Inline Widget（per-lecture 嵌入） | 上下文最精确 | 不能跨页面记忆 | 长篇阅读型课程 |
| 独立站（CS50.ai） | 无布局约束、可深度功能化 | 断开课程上下文 | 超大规模多课程复用 |

- **对我们的启示**：Phase 1 选 FAB 是对的。**首次访问要有气泡提示**（「Hi，我是 COMP110 的 AI 助教，试试问我：什么是 list comprehension？」），之后 localStorage 记住关闭状态。

### 4.5 学术诚信 + FERPA

- **URL**：<https://www.learnwise.ai/guides/ai-tutors-in-higher-education-the-complete-institutional-guide-2025>  
  **发现**：FERPA 对 AI tutor 的核心要求——**不把学生 PII 发给第三方训练**。OpenAI Enterprise/Azure OpenAI 有 zero-retention 条款可满足；直接用个人 API key 不满足。  
  **对我们的启示**：Phase 2 后端必须走 **Azure OpenAI**（UNC 应有 institutional tier）或 Anthropic Claude w/ zero-retention；不要用 `OPENAI_API_KEY` 个人 key 直连 OpenAI.com 公开 API。这条要写进 DESIGN_BRIEF 的「安全与合规」章节。

- **URL**：<https://teaching.cornell.edu/generative-artificial-intelligence/ai-academic-integrity>  
  **发现**：2025 年主流高校的 AI 政策——禁用**外部 AI**（ChatGPT/Claude 公众版），但**明确允许**课程自建 AI（若其遵循 Socratic + 不给答案）。CS50 就是此模式。  
  **对我们的启示**：AI TA 面板底部永久展示一行小字「本 AI 助教遵守 COMP110 学术诚信政策，遵循 Socratic 式引导，不提供完整代码答案」，类似 CS50 的免责声明。

---

## 5. 附加发现：Duolingo 式进度激励（低 ROI 但值得评估）

- **URL**：<https://www.orizon.co/blog/duolingos-gamification-secrets>  
  **发现**：Duolingo 的留存机制核心是 **streak（连续天数）+ XP + 损失厌恶（连续断档痛）**。2025 年 4770 万 DAU。  
  **对我们的启示**：COMP110 是**有限周期的 for-credit 课**，不是自愿学习 app。照搬 streak 会适得其反（学生 GPA 压力已够大，再加游戏化压力 = 焦虑）。**不建议**抄 streak 系统。可以借用「**完成度进度环**」（13/15 周 = 82%）作为**正向反馈**但不绑定「断档惩罚」。

---

## 6. Top 5 可执行建议（按 ROI 排序交给 DeepSeek）

### #1 Bento 化 agenda + 「当前周」高强度视觉差分（最高 ROI）

- **为什么**：主流 CS 入门站都是表格（61A/183）或外挂 Sheet（106B），视觉化 agenda 是**真正的差异化**。Bento 在 2026 是成熟模式，风险低。
- **怎么做**：`<AgendaGrid>` 组件，当前周 card 为其他 card 的 2 倍面积 + Carolina 黄底 + 进度环；过去周灰度 60%；未来周空态 card。Tailwind：`grid grid-cols-12 gap-4`，当前周 `col-span-6`，其他 `col-span-3`。数据源：`agenda.json` 的 `currentWeek` 字段。
- **工时估算**：DeepSeek 1 晚上（6–8h）。

### #2 AI TA FAB + 三级 hint 系统 + 首次气泡引导

- **为什么**：这是 COMP110 相对所有对标站（除 CS50）的真正技术护城河，且 Phase 1 已有 `socratic_ta_examples.md` 骨架。
- **怎么做**：
  1. shadcn/ui `Sheet` 或 Radix `Dialog`（非模态）作为 FAB 面板
  2. System prompt 加三级 hint 策略（L1 反问 → L2 方向 → L3 伪代码）
  3. 后端走 Azure OpenAI（FERPA 要求）
  4. 首次访问气泡：「Hi，我是 COMP110 AI 助教」+ 右上关闭叉
  5. localStorage 记 `ai-ta-onboarded=true` 避免重复骚扰
  6. 面板底部永久免责声明
- **工时估算**：DeepSeek 1.5–2 天（含 prompt 迭代）。

### #3 Tailwind v4 `@theme` token 化设计系统（一次性基础设施）

- **为什么**：v4 的 CSS-first 配置让 token 和代码合一，DeepSeek 后续所有组件可直接 `bg-carolina` / `text-type-lecture` 引用。
- **怎么做**：在 `app/globals.css` 顶部用 `@theme { --color-carolina: #F5B700; ... }` 定义全部 token，从 `DESIGN_BRIEF.md` 一次性搬过来。
- **工时估算**：30 分钟。但所有后续组件都吃这份红利。

### #4 emoji-prefix + type badge 双编码（零成本可达性升级）

- **为什么**：CS106B 的 emoji 前缀 + Phase 1 的 6 色 badge，双编码后色弱学生也能识别 type，且 emoji 提高扫视速度（CS106B 实战验证）。
- **怎么做**：在 `agenda.json` 的每个 event 加 `emoji` 字段（Lecture=📖, Lab=🧪, Project=🛠️, Quiz=✍️, Reading=📚, Office Hours=💬）；渲染时 emoji + type badge 组合。
- **工时估算**：1 小时。

### #5 reduced-motion + WCAG 2.2 AA 工程化（合规基础，不做会被 UNC 驳回）

- **为什么**：UNC 作为公立学校必须 Section 508 合规，European Accessibility Act 2025-06 已生效若站点有海外访问也要合规。neobrutalism/glassmorphism 的亮点若不做可达性适配会出安全事故。
- **怎么做**：
  1. 所有动画包 `@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }`
  2. AI TA FAB 支持 Tab/Esc + `aria-expanded` + focus trap（Radix/Headless UI 免费提供）
  3. Carolina 黄 #F5B700 检查对比度——黄底只能配黑字（`#0a0a0a`），**禁用**黄底白字
  4. 所有 type badge 同时带 emoji + 文字，不只靠颜色
  5. Lighthouse Accessibility 分数目标 ≥ 95
- **工时估算**：DeepSeek 4–6h（主要是回归测试），但漏掉成本不可承受。

---

## 7. 未调研 / 需后续 Research Loop 继续跟进

- `[UNVERIFIED]` UNC 品牌指南对 Carolina 蓝 #7BAFD4 vs 我们选的 Carolina 黄 #F5B700 的官方态度（可能需问 Kris Jordan）
- `[UNVERIFIED]` CS50.ai 的具体 system prompt 是否公开（搜了没找到完整 prompt）
- `[UNVERIFIED]` UNC 是否有 Azure OpenAI institutional tier（问学校 IT）
- Phase 2 开工前需查：shadcn/ui 最新版本、Tailwind v4 在 Next.js 15 App Router 的完整配置（用 context7 MCP 查 docs）

---

## Sources（完整列表）

**教育类 UI/UX 趋势**：  
- <https://desinance.com/design/bento-grid-web-design/>  
- <https://midrocket.com/en/guides/ui-design-trends-2026/>  
- <https://www.wearetenet.com/blog/ui-ux-design-trends>  
- <https://elements.envato.com/learn/ux-ui-design-trends>  
- <https://www.galaxyux.studio/blog/bento-grids-the-new-standard-for-modular-ui-design/>  
- <https://landdding.com/blog/blog-bento-grid-design-guide>  
- <https://colorwhistle.com/neo-brutalism-higher-education-web-ux/>  
- <https://www.nngroup.com/articles/neobrutalism/>  
- <https://www.zignuts.com/blog/neumorphism-vs-glassmorphism>

**Bootstrap→Tailwind 迁移**：  
- <https://st6.io/blog/migrating-from-bootstrap-to-tailwind-part-3/>  
- <https://medium.com/@vdaubry/how-we-migrated-16k-lines-of-html-css-from-bootstrap-to-tailwind-using-claude-code-4d2c4c3dff64>  
- <https://www.vantage.sh/blog/bootstrap-tailwind-migration>  
- <https://omid.dev/2024/05/22/migrate-css-bootstrap-to-tailwind/>  
- <https://www.digitalapplied.com/blog/tailwind-css-v4-migration-new-features-guide>

**CS 入门课站点**：  
- <https://cs61a.org/>  
- <http://web.stanford.edu/class/cs106b/>  
- <https://cs50.harvard.edu/x/>  
- <https://cs50.harvard.edu/x/weeks/0/>  
- <https://eecs183.github.io/eecs183.org/>  
- <https://www.cs.cmu.edu/~112/>  
- <https://introcomp.mit.edu/spring25/information>  
- <https://comp110-26s.github.io/>

**AI TA 集成**：  
- <https://cs50.readthedocs.io/cs50.ai/>  
- <https://cs50.harvard.edu/college/2023/fall/notes/ai/>  
- <https://dl.acm.org/doi/10.1145/3626253.3635427>  
- <https://cs.harvard.edu/malan/publications/fp0627-liu.pdf>  
- <https://www.khanmigo.ai/learners>  
- <https://www.learnwise.ai/guides/ai-tutors-in-higher-education-the-complete-institutional-guide-2025>  
- <https://teaching.cornell.edu/generative-artificial-intelligence/ai-academic-integrity>  
- <https://www.nature.com/articles/s41598-025-97652-6>

**Duolingo 对照**：  
- <https://www.orizon.co/blog/duolingos-gamification-secrets>
