# COMP110 Phase 2 准备 + 跨项目优先级研判

**调研时间**：2026-04-18 21:10–21:45
**调研目的**：为 comp110-redesign Phase 2 落地铺路（Kris Jordan 授权 + Next.js 15/Tailwind v4 参考仓 + AI TA 后端），并为主人在 1–24h 内返场时给出跨项目优先级建议。
**方法**：WebSearch + WebFetch 实地抓取。每条 finding 附 URL + 一行推论 + 对应行动。不可验证内容标 `[UNVERIFIED]`。
**与 2101 benchmark 的关系**：UI/UX 趋势、CS 教学网站视觉参考、AI TA 交互模式已在 `docs/research/2026-04-18-2101-comp110-redesign-ux-benchmarks.md` 覆盖完毕。本文**不重复**那部分，只在需要引用时用 `[见 2101 benchmark §X]` 注明。

---

## 1. Kris Jordan 授权路径 — 从「合法获取」到「上线 UNC 官方站」的完整通道

### 1.1 身份与触达坐标（已全部验证到真实来源）

- **URL**：<https://cs.unc.edu/person/kris-jordan/>
  **发现**：Kris Jordan 的官方 UNC 邮箱 = **`kris@cs.unc.edu`**，办公室 134 Brooks Building，系电话 919-590-6000，系通用邮箱 `info@cs.unc.edu`。
  **对我们的启示**：所有正式授权请求应发到 `kris@cs.unc.edu`，抄送 `info@cs.unc.edu`（系秘留档），**不要**通过 ratemyprofessors 或 rocketreach 这类第三方爬取邮箱（道德风险 + 命中率低）。

- **URL**：<https://krisjordan.com/>
  **发现**：个人站无独立 email，但列出 Twitter `@KrisJordan`、GitHub `KrisJordan`、LinkedIn `krisjordan`、Instagram `@therealkrisjordan`、YouTube `KrisJordan`。整站底部仅有 `Copyright © 2025 Kris Jordan`，**没有公开 CC 协议**。
  **对我们的启示**：个人站内容默认全版权——这意味着我们不能直接「爬一份 HTML 当蓝本」。但 COMP110 课程站 `comp110.com` 是另一个实体（`comp110-26s.github.io`），许可证需单独确认。

- **URL**：<https://github.com/KrisJordan>
  **发现**：pinned 仓库 = `introcs`（TypeScript 教学库）、`learncli`、`multimethod-js`、`f_underscore`、`csxl.unc.edu`。**没有**一个叫 `comp110-26s` 或类似名的公开仓库——当前课程仓在 `github.com/comp110-26s`（`comp110-26s.github.io` 的 Pages 源）下，属 org 而非个人名下。
  **对我们的启示**：克隆源码检查 LICENSE 的正确路径是 `github.com/comp110-26s/comp110-26s.github.io`（org repo），而不是 `KrisJordan/*`。如果该 repo 无 LICENSE 文件，默认即「保留所有权利」，任何 fork/re-host 都不合规。**这是主人动手前必须跑的第一个 gh 命令**。

- **URL**：<https://www.unc.edu/posts/2025/10/27/kris-jordan-uses-ai-in-software-engineering/>
  **发现**：Kris 在 2025 春 COMP 423 给 200 学生发了 OpenAI API keys，要求期末项目强制用 Azure OpenAI，并定下「AI 生成代码不超过 25%」的产业基准（对齐 Google 内部做法）。引用：「This is a technological turning point. We're not waiting to see how it plays out — we're helping students lead the way.」
  **对我们的启示**：**极关键**——Kris 本人是 AI 教育的激进拥抱者，不是保守派。这意味着授权话术应聚焦「如何让 AI TA 更好地服务学生」而非「我们能不能用 AI」，后者对他是非问题。

### 1.2 UNC CS 系现行课程内容许可惯例

- **URL**：<https://comp423-23s.github.io/syllabus/>
  **发现**：Kris 自己带的 COMP423（Foundations of SE）syllabus 页明确写「final project 要做 MIT 许可的开源软件的一个 feature，学生实现部分受 MIT License 约束」——说明 Kris 本人在课程中**主动采用 MIT / 其他开源许可**，对「让课程产物开源」没有心理抗拒。
  **对我们的启示**：授权邮件里可以直接提议「我把 Phase 2 代码以 MIT 或 CC-BY 4.0 开源，内容（agenda 文案、评分细则）以 CC-BY-NC-SA 开源」，这个架构对 Kris 是熟悉语言。

- **URL**：<https://cs50.harvard.edu/x/2024/license/>
  **发现**：CS50 全系列（CS50x / CS50 Python / CS50 Web / CS50 Cyber / CS50 Scratch）统一采用 **CC BY-NC-SA 4.0**——允许再分发，要求署名、非商用、衍生作品同许可。
  **对我们的启示**：这是**全球最成功的 CS 公开课**的合规模板。建议给 Kris 的邮件里直接写「我参照 CS50 的 CC BY-NC-SA 4.0 协议重发你的课程内容」，比让他从零思考许可更省心。

- **URL**：<https://www.lib.berkeley.edu/about/creative-commons>
  **发现**：UC Berkeley 图书馆页面采用 **CC-BY-NC**；但 CS61A 具体材料没有在公开页声明许可，学生社区 repo（如 `cy-Yin/UCBerkeley-CS61A-Fall2023`）本身不等于官方授权——只是课程材料「事实上」被非官方分享。
  **对我们的启示**：[UNVERIFIED] Berkeley 的做法介于「明文 CC-BY-NC」和「默认保留+睁一只眼闭一只眼」之间。不要拿「反正别人都这样」当借口，**明确取得书面许可**是唯一稳妥路径。

- **URL**：<https://cs.stanford.edu/people/eroberts/courses/cs106a/materials/>
  **发现**：Stanford CS106A 材料页仅声明 `© Stanford University 2021`，**没有公开 CC 许可**。Stanford See（Engineering Everywhere）上线的材料走 Stanford 自己的平台条款，不等于允许任意 re-host。
  **对我们的启示**：Stanford 是「默认保留」代表。UNC 如果不想比 Stanford 更开放，Phase 2 可能只能**内网部署**（sakai.unc.edu subdomain 或 Tarheels.live），不能放在 `comp110.xxx` 这种公网域名。

### 1.3 推荐的授权邮件模板（一封话就够）

以下模板不是代码，是请求文案。主人可直接复制粘贴到 Gmail。

> **主题**：Student-built redesign proposal for COMP110 site — seeking permission to publish
>
> Dear Prof. Jordan,
>
> I'm a student fan of COMP110 who spent the past few days building a visual redesign of the current COMP110 course site as a personal project. The redesign introduces a Carolina-yellow + warm-cream bento layout, a hero progress ring showing week-in-semester, a right-rail "next up" panel, and a Socratic AI TA floating widget (which never gives direct answers). I've finalized static mockups, a design brief, and a data contract — all code/design work is mine, and none of your original images or prose have been copied verbatim.
>
> Before I proceed to a full Next.js 15 implementation and (optionally) propose it as a replacement for the current Jekyll site, I want to ask for your permission on two things:
>
> 1. **Content re-use**: May I re-use the COMP110 schedule structure (week topics, assignment titles, due-date pattern) if I re-author all prose in my own words? I would publish the resulting Phase 2 code under MIT, and any re-authored content under CC BY-NC-SA 4.0 (the same license CS50 uses).
> 2. **Public hosting**: If you like the final result, would you be open to me hosting a demo at a `tarheels.live` or `carolinacloudapps` subdomain? I understand FERPA concerns and will NOT include any student names, grades, or private data — the demo would carry only the public schedule and a synthetic "demo student" profile.
>
> If the answer to either is no, I'll keep the work as a personal portfolio piece and won't publish it. I respect that it's your course.
>
> Happy to send the mockup PNGs or a Loom walkthrough if you'd like a preview before deciding.
>
> Thank you for COMP110 — it genuinely changed how I think about code.
>
> Best,
> [主人名]
> [UNC 邮箱/专业/年级]

**为什么这样写**：
- 承认主权（「我尊重这是你的课」）比说服他放手更有效。
- 给出具体许可协议（MIT + CC BY-NC-SA 4.0）让他**不需要思考**，只需 yes/no。
- 提前声明 FERPA 合规（零学生数据），降低他被系里问责的心理成本。
- 主动给 opt-out 台阶（「如果 no 我就当作品集」），没有逼他做决定的压力。
- 把 Loom/PNG 预览做成 optional，避免「要先看才能说」的拖延链。

### 1.4 FERPA 对公开演示的硬约束

- **URL**：<https://studentprivacy.ed.gov/ferpa>
  **发现**：FERPA 把「education records」定义极宽——包含成绩、纪律、健康、财务、行为干预计划，以及「间接标识」（生日、出生地、母亲婚前姓氏）。任何组合到能「重新识别某学生」的数据都落入 FERPA。
  **对我们的启示**：Phase 2 demo **绝对不允许**包含：真实学生名字、真实 UNC ID、真实邮箱、真实成绩、真实 discussion section 时间（因为 section time + name 可反推个人）。demo 数据必须 100% 合成。

- **URL**：<https://www.virtru.com/blog/compliance/ferpa/universities>
  **发现**：2026 年 FERPA 在高校语境下的主要攻击面是「EdTech 第三方平台」——把学生数据送进 SaaS 就可能踩雷。即使是「demo」，只要托管站点被收录进 GitHub/Wayback，PII 一旦泄露就不可逆。
  **对我们的启示**：Phase 2 如果要部署，托管方案优先级：
  1. `tarheels.live`（UNC 控制，可断）
  2. Vercel 个人域（仅 demo，无真实数据）
  3. **绝对不要** GitHub Pages 直接挂 `comp110-26s.github.io` fork（会污染原 org 的命名空间）

- **URL**：<https://publicinterestprivacy.org/ferpa-101-higher-ed/>
  **发现**：学生作品若要公开展示（blog/book/站点），**必须**征得学生书面同意 + 提供 opt-out 通道。这包括学生的代码作业、讨论帖、匿名 Q&A。
  **对我们的启示**：AI TA 面板里如果想展示「真实学生常问的问题」作为示例，**只能**用完全合成的范例（或把原始问题彻底改写到失去可识别性）。`socratic_ta_examples.md` 里现有的 8 个例子需要主人自检一遍：是不是从 Ed Discussion 真实 thread 改编的？如果是，需要说服 Kris + 所有涉及学生走正式同意流程。

### 1.5 此路径的现实性评估

**乐观场景**（概率 40%）：Kris 回邮件「nice work, go ahead, MIT + CC-BY-NC-SA 4.0 fine, just put a clear attribution on the footer.」主人 2 天内拿到书面授权，Phase 2 可推进到公开发布。

**中性场景**（概率 45%）：Kris 回「interesting, but let's do it as an internal prototype first — send me the Figma / Loom, and if it passes my review I'll take it to the TA team for spring 2027.」Phase 2 仍可完成，但**不公开**，仅作为 Kris 内部评审材料。这也 OK——主人得到一个 UNC 教授的亲笔 recommendation 书面背书。

**悲观场景**（概率 15%）：Kris 三周无回音，或回「thanks but we have our own plans.」主人把 Phase 2 做成**个人作品集**，在 krisjordan.com 不出现任何元素、站点去掉所有「COMP110」字样，改名「Intro to CS — 2026 Redesign Study」作为 design portfolio，放在自己域名。依然对求职有价值。

---

## 2. Next.js 15 + Tailwind v4 可参考仓库（DeepSeek 落地参照）

### 2.1 第一梯队：直接克隆即可起步的开源起手模板

- **URL**：<https://github.com/siddharthamaity/nextjs-15-starter-shadcn>
  **发现**：明确标注 Next.js 15 + React 19 + TypeScript 5 + **Tailwind CSS 4** + Shadcn UI，含 ESLint 9 / Prettier 3 / Docker (Node 22 + Bun 1.2) / Bundle Analyzer 完整工具链。**但 repo 已 archived**，维护者建议用 Next.js 16 版本。
  **对我们的启示**：当作**结构参考**而不是 fork 基础——复制 `components.json` / `eslint.config.mjs` / `tailwind` 目录风格，但 `package.json` 要用当前维护的版本。archived 意味着安全补丁停更。

- **URL**：<https://github.com/doinel1a/next-ts-shadcn-ui>
  **发现**：「30 秒 bootstrap」定位，Next.js 15 + React 19 + TypeScript + shadcn/ui + Tailwind 4。未 archived，活跃度高。
  **对我们的启示**：这个**更适合 clone**。DeepSeek 第一步 = `git clone` 这个仓，把 `src/app/*` 替换成 COMP110 的 agenda 页面路由即可。省掉一整天 config debugging。

- **URL**：<https://github.com/shadcnblocks/mainline-nextjs-template>
  **发现**：由 shadcn blocks 官方维护的 Next.js 15 + shadcn/ui + Tailwind 4 模板，定位「mainline」——他们自己生产环境用的。
  **对我们的启示**：组件库示例最全（block 级）。如果 DeepSeek 需要找「bento 卡在 Next.js 里怎么写」的现成参照，这里最齐全。

- **URL**：<https://github.com/moinulmoin/chadnext>
  **发现**：Next.js 15 + shadcn UI + **LuciaAuth** + Prisma + Stripe + Server Actions + i18n。功能全家桶。
  **对我们的启示**：**不要用**——COMP110 不需要 Stripe/Prisma/LuciaAuth，引入这些依赖是 over-engineering。但如果 Phase 3 要做「学生登录提交作业」，可以回头参考 Lucia 的做法。

### 2.2 第二梯队：教育/课程定位的模板

- **URL**：<https://getnextjstemplates.com/products/e-learning-nextjs-with-app-directory-free-landing-page-template>
  **发现**：e-learning NextJS 15 + Tailwind v4 + Headless UI 的 landing page 模板。免费版只给 landing，不给课程详情页。
  **对我们的启示**：营销站调性偏商业（卖网课），**和 COMP110 的学术气质不匹配**。不要拿来改。

- **URL**：<https://vercel.com/templates/next.js/video-course-starter-kit>
  **发现**：Vercel 官方的「视频课程 starter kit」。[UNVERIFIED] 具体内容因页面主体没抓到，但定位是「课程内容 + 视频播放器」的组合。
  **对我们的启示**：COMP110 是静态 agenda 为主、不是视频课，这个模板的视频侧能力用不到。可以抄它的 route 结构（`/courses/[slug]/lessons/[id]`）对应 COMP110 的 `/agenda/week/[n]`。

- **URL**：<https://github.com/vercel/next-learn>
  **发现**：Vercel 官方 Next.js Learn 教材的源代码，含 basics / dashboard / seo 三个模块，TypeScript 67% + JS 25% + CSS 8%，**App Router 为主**，Pages Router 仅保留 legacy 路径。4.7k star，活跃维护。
  **对我们的启示**：这是**最正统的 Next.js App Router 参考**。DeepSeek 如果对 App Router 的文件组织（`layout.tsx` / `page.tsx` / `loading.tsx` / `error.tsx` / `not-found.tsx` 的协作）不熟，看 `dashboard` 示例就够。

### 2.3 课程站同类参照（非 Next.js 但值得看）

- **URL**：<https://kevinl.info/just-the-class/>
  **发现**：Stanford CS161 / Berkeley Data100 / UCSB CSW8 / Northeastern CS4530 / CMU 等都用的 Jekyll「Just the Class」模板，纯静态。
  **对我们的启示**：说明**课程站不需要服务端 / 数据库**——Next.js 15 用 SSG (`export const dynamic = 'force-static'`) 就能替代 Jekyll 且保留现代能力。Phase 2 默认全走 SSG，AI TA 是唯一的 client-side 动态。

### 2.4 Tailwind v4 硬性坑（DeepSeek 必读）

- **URL**：<https://tailwindcss.com/docs/upgrade-guide>（抓取到详细列表）
  **发现**（5 条致命坑）：
  1. `@tailwind base/components/utilities;` 三行必须替换为 `@import "tailwindcss";`——写错站不出样式。
  2. Browser 最低要求 Safari 16.4+ / Chrome 111+ / Firefox 128+；需要支持老浏览器必须留在 v3.4。
  3. utility 重命名：`shadow-sm → shadow-xs`、`rounded-sm → rounded-xs`、`blur-sm → blur-xs`、`ring → ring-3`、`outline-none → outline-hidden`。Phase 1 mockup 里用了 `shadow-sm`，DeepSeek 迁移时必须全局替换。
  4. 默认值变化：border 默认 `currentColor`（v3 是 `gray-200`）、ring 默认 `currentColor` + `1px`（v3 是 `blue-500` + `3px`）。**这条最隐蔽**——mockup 看起来对，迁移后边框突然变成文字颜色。
  5. PostCSS 插件变 `@tailwindcss/postcss`（v3 是 `tailwindcss`）；Vite 推荐直接用 `@tailwindcss/vite` 插件。
  **对我们的启示**：主人在 DESIGN_BRIEF.md 里**必须加一节「Tailwind v4 陷阱清单」**，否则 DeepSeek 做到一半会卡 2 小时在 border 颜色 debug 上。

- **URL**：<https://designrevision.com/blog/tailwind-4-migration>
  **发现**：Oxide 引擎 Rust 实现，600ms 的 v3 项目 v4 只要 120ms，5× 速度。
  **对我们的启示**：dev server HMR 几乎瞬时，DeepSeek 可以高频调色板迭代。但 CI 环境的 Rust toolchain 依赖需要 GH Actions 模板更新。

- **URL**：<https://dev.to/pockit_tools/tailwind-css-v4-migration-guide-everything-that-changed-and-how-to-upgrade-2026-5d4>
  **发现**：JS 配置（`tailwind.config.js`）被 `@theme` CSS 指令取代，设计 token 写在 CSS 里。`--color-carolina-yellow: #F5B700;` 这种自定义变量直接在 `@theme {}` 块内定义即可。
  **对我们的启示**：Phase 1 DESIGN_BRIEF.md 里的色值建议直接以 `@theme` 语法重写，DeepSeek 零翻译就能用。对应文件：`src/app/globals.css`。

### 2.5 推荐落地组合（给 DeepSeek 的一句话）

> Clone `doinel1a/next-ts-shadcn-ui`，把 `src/app/` 按 `agenda.json` 的 week 结构生成 SSG 路由，引入 Radix Dialog 做 AI TA FAB（见 2101 benchmark §2.2），所有 utility 走 Tailwind v4 的新命名，色 token 写在 `src/app/globals.css` 的 `@theme` 块内。

---

## 3. AI TA 可部署后端 — 400 人规模的硬性对比

### 3.1 直接 API 对比（按 400 学生 × 5 query/week × 800 token/query 测算）

**流量估算基线**：400 学生 × 5 queries/week × 15 周 = 30,000 queries/学期。每 query ≈ 600 input tokens（含 RAG 的 lecture 片段） + 200 output tokens = 800 tokens 总。学期总 tokens ≈ 18M in + 6M out = **24M tokens**。finals week 会集中到 30% 流量，峰值 3 倍均值。

- **URL**：<https://openai.com/api/pricing/> + <https://pricepertoken.com/pricing-page/model/openai-gpt-4.1>
  **发现**：GPT-4.1 = $2 / M input + $8 / M output；GPT-4o = $2.5 / M input + $10 / M output。Prompt caching 自动 50% 折扣（命中时），Batch API 异步场景 50% 折扣。
  **成本测算**（GPT-4.1，无缓存）：18 × $2 + 6 × $8 = $36 + $48 = **$84 / 学期**。加 90% prompt caching（lecture 片段复用） → ≈ $25–30 / 学期。
  **对我们的启示**：400 人规模 OpenAI 月成本低到可以忽略（< $15/月）。**不是成本问题，是合规问题**。

- **URL**：<https://platform.claude.com/docs/en/about-claude/pricing>
  **发现**：Sonnet 4.6 = $3 / M input + $15 / M output；Haiku 4.5 = $1 / M input + $5 / M output；Opus 4.6/4.7 = $5 / M input + $25 / M output。Prompt caching 可省 90%，Batch API 50%。
  **成本测算**（Sonnet 4.6，无缓存）：18 × $3 + 6 × $15 = $54 + $90 = **$144 / 学期**。Haiku 4.5 纯做 RAG 检索 + 回答 = 18 × $1 + 6 × $5 = $18 + $30 = **$48 / 学期**。
  **对我们的启示**：**Haiku 4.5 是 AI TA 的性价比之王**——模型够大能懂 Socratic 指令，但价格只有 Sonnet 的 1/3。只在学生问「概念 synthesis」时才升级到 Sonnet。

- **URL**：<https://learn.microsoft.com/en-us/compliance/regulatory/offering-ferpa>
  **发现**：Azure OpenAI 支持 FERPA BAA（Business Associate Agreement 的教育等价物）。UNC 已有 Microsoft 365 Education 协议，加 Azure OpenAI 通常只需 addendum，**无需从零审批**。
  **对我们的启示**：**这是 Phase 2 的正确后端**。走 UNC AIAP 内部路径，不签第三方合同，不走个人信用卡。

- **URL**：<https://aws.amazon.com/bedrock/security-compliance/>
  **发现**：Bedrock 不存储 prompt/completion、不用于训练、不共享给模型 provider。符合 ISO/SOC/HIPAA/GDPR，GovCloud 支持 FedRAMP High。
  **对我们的启示**：AWS 方案对 UNC 是「可用但不必要」——UNC 已有 Azure 入口，为 AI TA 再签 AWS 合同是增量。Bedrock 的价值在 Claude on AWS（可选 Anthropic 模型），但 Anthropic 自己的直接 API 已够用。

- **URL**：<https://openai.com/business-data/>
  **发现**：OpenAI 的 Zero Data Retention (ZDR) 政策——符合条件的企业客户可以选择数据不落地。ChatGPT Edu 明确提供 FERPA 支持，DPA + BAA 可签。
  **对我们的启示**：个人 API key 路径**默认不是 ZDR**——必须申请、批准、签 DPA。主人个人信用卡绑的 key 基本不可能过审（UNC 学生身份不等于 UNC 机构客户）。这条路不通，必须走 UNC 机构路径。

### 3.2 Azure OpenAI via UNC AIAP — **最关键发现**

- **URL**：<https://its.unc.edu/2025/09/24/teaching-on-the-frontier-microsoft-azure-and-openai/>
  **发现**：**Kris Jordan 在 2025 春 COMP 423 已经走通了这条路**——给 200 学生发 Azure OpenAI API keys，项目强制用 Azure OpenAI，ITS 提供平台，AIAP 提供经费。Carolina CloudApps 是部署底座。
  **对我们的启示**：**Phase 2 的 AI TA 后端不是「要不要申请」，而是「走 Kris 的同一条批准链」**。主人不需要从零建关系——Kris 已经是 AIAP 熟客，推荐流程几乎秒过。这是 Topic 1 授权邮件里可以顺带提的：「如果你已经有 Azure OpenAI quota 没用完的分配，能不能把 AI TA 这块挂到同一 subscription 下？」

- **URL**：<https://aiacceleration.unc.edu/program-overview/>
  **发现**：AIAP 接受 pre-proposal 和 formal proposal 两种申请方式，面向 faculty + staff + students。
  **对我们的启示**：即使 Kris 不挂名，主人自己也可以以「本科生独立研究」身份提 pre-proposal，经费门槛相对低。这是 B 计划。

- **URL**：<https://its.unc.edu/ai/>
  **发现**：UNC ITS 目前对全校提供 Microsoft 365 Copilot 免费访问。
  **对我们的启示**：Copilot 不是 API、不支持自定义 system prompt，不能直接作为 AI TA 后端。但它证明 UNC 有「AI for all」的战略方向，AIAP 批 Azure OpenAI quota 不会撞红线。

### 3.3 真实同类部署（2025–2026 公开案例）

- **URL**：<https://cs.harvard.edu/malan/publications/V1fp0567-liu.pdf>
  **发现**：CS50 Duck = GPT-4o（早期 GPT-4） + ChromaDB 向量库 + RAG。每次 query 向 ChromaDB 搜 lecture caption 片段、按相关度排序塞进 prompt。后端服务 = cs50.ai。Duck 交付方式：VS Code 扩展 + 独立 Web App + Ed Discussion 内嵌。
  **对我们的启示**：这是**COMP110 AI TA 的完整蓝本**。主人不需要设计新架构——直接抄：
  - RAG 知识库 = COMP110 lecture 视频字幕 + agenda.json + memory_diagrams_rubric.md + COMP110 所有 assignment 说明书
  - 向量库 = ChromaDB（轻量、python 生态熟）或 pgvector（UNC Azure Postgres 自带）
  - 召回 Top-3 片段拼进 system prompt
  - Model = Azure OpenAI GPT-4.1（便宜）或 GPT-4o（准确）

- **URL**：<https://cs50.readthedocs.io/cs50.ai/>
  **发现**：CS50.ai 强调「behave like a good tutor, leading students toward answers」，人工 moderator 审核质量 + 必要时修改/删除 AI 答案。
  **对我们的启示**：Phase 2 第一版 AI TA **不需要**人工 moderator（主人一个人维护不动），但必须：
  1. 保留所有对话到 log（Azure Blob + 加密 at rest）
  2. 每周 review 一次 10 条随机 thread，发现 answer-giving 就调 system prompt
  3. 提供「flag this response」按钮（学生一键举报，塞 issue queue）

- **URL**：<https://www.khanmigo.ai/>
  **发现**：Khanmigo 底层 GPT-4 + 额外 calculator 工具 + 从 Khan 教学内容库拉 context（exercises/steps/hints/solutions）。
  **对我们的启示**：Khan 的启示是**「拉已有教学素材」>「只靠模型」**。COMP110 有 `memory_diagrams_rubric.md` 和 `socratic_ta_examples.md` 两份金线材料，Phase 2 的 AI TA system prompt 必须硬编码这两份 rubric 的摘要作为「行为红线」，而不是指望模型自己 infer。

- **URL**：<https://codeinplace.stanford.edu/>
  **发现**：Stanford Code in Place（Chris Piech / Mehran Sahami）是 CS106A 的在线版本。[UNVERIFIED] 2025 年有引入 AI tutor 的公开信号，但具体架构没找到对外文档。
  **对我们的启示**：Code in Place 模式（large-scale + volunteer section leaders）对 COMP110 不直接对标——COMP110 有 TA，不需要志愿者。但「小组 section + AI 托底」的混合模式值得借鉴：AI TA 覆盖简单 Q，TA 覆盖 debug，Kris 覆盖概念质疑。

### 3.4 自托管方案 — 什么时候才需要

- **URL**：<https://blog.premai.io/self-hosted-llm-guide-setup-tools-cost-comparison-2026/>
  **发现**：Llama 3.3 70B 在 H100 （$2–4/hr）上 vLLM 跑，580 tokens/sec，折合约 **$0.18/M tokens**。A100 相对便宜但慢 3×。
  **对我们的启示**：**单纯成本不足以证明自托管**——400 学生用 Azure OpenAI 学期 $50-150，自托管 H100 24×7 一个月就 $2,000+。自托管**只有在以下两种情况**合理：
  1. UNC 合规部门要求「数据绝对不出校园」（极罕见，Azure OpenAI BAA 足够）
  2. 要做模型微调（如用 COMP110 历史 TA 答复 fine-tune 一个小模型）——这是 Phase 3 议题

- **URL**：<https://www.programming-helper.com/tech/vllm-2026-high-performance-inference-serving-ai-models-python>
  **发现**：vLLM 2026 基线 1,850 TPS / 50 并发 on H100，TTFT 120ms。
  **对我们的启示**：性能足够 400 人并发（估算峰值 = 400 × 0.1 并发率 = 40 并发，远低于 50）。技术上可行，但见上条：**没必要**。

- **URL**：<https://apxml.com/posts/ultimate-system-requirements-llama-3-models>
  **发现**：Llama 3.3 70B 原生 140GB VRAM，4-bit 量化后 ~35GB，单卡 A6000 (48GB) 或双 RTX 4090 (24×2) 可装。
  **对我们的启示**：备忘——如果 Phase 3 要试自托管 demo，A6000 服务器月租 $1,200 左右是进入门槛。

### 3.5 COMP110 AI TA 技术栈推荐（最终配方）

**后端**（按优先级）：
1. **P0**：Azure OpenAI GPT-4.1（UNC AIAP 走流程）
2. **P1 回退**：Anthropic Claude Haiku 4.5（主人个人 API，仅 demo 用，不上 UNC 真实学生数据）
3. **P2 不考虑**：自托管（无 ROI）、OpenAI 直连（合规搞不定）、AWS Bedrock（增量合同）

**向量库**：pgvector on Azure Postgres（UNC 已有订阅）。备选 ChromaDB（本地 demo）。

**RAG 语料**：
- COMP110 当学期 lecture 视频字幕（让 Kris 批准转录）
- `agenda.json`
- `memory_diagrams_rubric.md`
- `socratic_ta_examples.md`
- 过往 COMP110 FAQ 整理（需要 Kris 提供或授权爬 Ed Discussion 匿名版）

**System prompt 核心红线**（必须硬编码）：
- 永不给直接答案
- 永不写 > 3 行学生作业代码（防作弊，与 Kris 的「25% AI」政策对齐）
- 永不评价其他同学
- 不确定时说「我不确定——去问 TA 或在 Ed 发帖」

---

## 4. 跨项目优先级排名（主人返场时建议读哪个）

### 4.1 项目现状快照（2026-04-18 21:10）

| 项目 | 状态 | 用户面 | 主要阻塞 |
|------|------|--------|---------|
| **comp110-redesign** | Phase 1 🔒，Phase 2 待 DeepSeek | 0 用户（未部署） | DeepSeek 拉起 + Kris 授权 |
| **ai-text-detector** | Path C 生产就绪 | [UNVERIFIED] 部分真实用户 | API keys（供应商确认）+ 产品方向决策 |
| **TOEFL** | Shipping，小修小补 | 主人自用 + [UNVERIFIED] 少量外部 | 无硬阻塞 |
| **Signal-Map** | 深度 HOLD | 0 用户（未部署活跃） | Supabase/Next.js 基建冻结 |
| **chronicle** | 内部工具，touch 已合并 | 仅主人 | 无需推进 |
| **arknights-sim** | 并行实例 active | 0 用户（WIP） | 不是本 Agent 作用域 |

### 4.2 排名标准

- **user-impact**：对真实外部用户的当前/短期价值
- **time-to-value**：从「开始」到「上线或验证」的小时数
- **blocker-dependency**：阻塞因素是否可主人自解（越可自解分越高）
- **strategic-fit**：是否契合主人当前优势（设计 + AI 集成 + 教育场景）

### 4.3 排名（从应先处理到最后处理）

**#1 ai-text-detector — 产品方向 1h 决策**
- one-liner：**返场后优先做产品方向决策（Humanizer 定位 + 定价模型）**——Path C 已 production-ready，再写代码 ROI 极低；真正卡的是商业决策而不是技术。主人 1 小时内做决定即可解锁：目标用户画像（学生 / 学术作者 / 内容营销）、定价（免费/$5/$15）、品牌英文名。API key 如果还没接，同步用 15 分钟补齐。
- 依据：用户 impact 最大（有外部流量潜力）、time-to-value 最短、blocker 可主人自解。

**#2 comp110-redesign — 发出 Kris 授权邮件 30min**
- one-liner：**返场后第二件事，复制 §1.3 的邮件模板发出去**——Kris 的回复是 3-7 天 lead time，越早发越早解锁 Phase 2 公开部署路径。不需要等 DeepSeek，邮件和实现平行推进。如果 Kris 乐观回复，直接把「UNC AIAP Azure OpenAI」话题带进去，一封邮件解决两件事。
- 依据：blocker 的 lead time 最长，必须立刻启动；但不占主人太多时间。

**#3 TOEFL — 小 PR 30min–1h**
- one-liner：**返场可选第三件事，做一个「今天的 30 分钟练习」小改进**——已在 shipping 状态，用户（含主人自己）真实受益。适合休息间隙做小 PR 保持 velocity 感。不建议大重构。
- 依据：user-impact 中等（主人 + 少量外部），time-to-value 极短（< 1h），是「填充时间」而非「主线」。

**#4 comp110-redesign Phase 2 监督 — 异步跟踪**
- one-liner：**返场后花 15 分钟为 DeepSeek 写一份 HANDOFF.md**——把本报告的 §2.1（clone `doinel1a/next-ts-shadcn-ui`）+ §2.4（Tailwind v4 陷阱清单）+ §3.5（AI TA 技术栈推荐）整合成一个对 DeepSeek 的 prompt。DeepSeek 不看 research/ 目录，只看 `comp110-redesign/HANDOFF.md`。
- 依据：blocker 不在主人手里，但给 DeepSeek 铺路能放大并行度。

**#5 chronicle — 无需推进**
- one-liner：**返场不处理**——内部工具，只有主人使用，touch 合并后已稳定。任何改动都是自嗨。除非用中遇到 bug，否则跳过。
- 依据：user-impact 仅主人、无外部收益。

**#6 Signal-Map — 继续深度 HOLD**
- one-liner：**返场不处理**——[UNVERIFIED] 基建问题（Supabase + Next.js 状态不明）需要 1+ 天 debug 才能起步。ROI 相对 ai-text-detector 差一个数量级。除非主人明确想回到这个赛道，否则维持冻结。
- 依据：time-to-value 最差，user-impact 低（校园活动地图天花板本身不高）。

**#7 arknights-sim — 不在作用域**
- one-liner：**返场不处理**——并行 Claude 实例正在写代码，任何人工干预只会制造冲突。主人若要介入，先 `git pull` 看当前进度。
- 依据：不是本 Agent 作用域。

### 4.4 一页式返场剧本（主人睡醒/午饭回来直接执行）

```
0:00–0:15  → 扫本报告 §执行摘要（5 bullets）+ §4.3 排名
0:15–0:45  → #2: 打开 Gmail，复制 §1.3 邮件模板，填 [主人名]/邮箱/专业，发 kris@cs.unc.edu（抄送 info@cs.unc.edu）
0:45–1:45  → #1: ai-text-detector 产品方向决策 + API key 补齐
1:45–2:30  → #3: TOEFL 做一个小 PR（如「今日 30min 推荐」或修一个已知 bug）
2:30–2:45  → #4: 给 comp110-redesign 写 HANDOFF.md（喂 DeepSeek）
2:45–      → 休息或看 arknights-sim 进度
```

---

## 5. 如何把本报告交给用户（60 秒执行摘要）

- **Topic 1 结论**：Kris Jordan 邮箱 `kris@cs.unc.edu` 已确认；他本人是 AI 激进派（COMP423 已发 API key），授权话术走「向 CS50 对齐 CC BY-NC-SA 4.0」路径；§1.3 给出了可直接发送的邮件模板，FERPA 要求 demo 零真实学生数据。
- **Topic 2 结论**：DeepSeek 应 clone `github.com/doinel1a/next-ts-shadcn-ui`（Next.js 15 + React 19 + shadcn + Tailwind v4，维护中），用 Vercel `next-learn/dashboard` 作 App Router 结构参考；Tailwind v4 的 5 条致命坑（`@import` 替换、utility 重命名、border/ring 默认值、PostCSS 插件、浏览器最低版本）必须写进 DESIGN_BRIEF 补丁。
- **Topic 3 关键发现**：**UNC AIAP 已给 Kris Jordan 的 COMP423 批过 Azure OpenAI quota**——Phase 2 的 AI TA 后端首选 = 搭同一条批准链，不是从零申请 OpenAI。CS50 Duck 的 GPT-4o + ChromaDB + RAG 是直接蓝本；400 人规模 Haiku 4.5 学期成本 $48，不是成本问题而是合规问题。
- **Topic 4 排名**：**ai-text-detector (产品决策 1h) → comp110 邮件 (30min) → TOEFL 小 PR (1h) → comp110 HANDOFF (15min) → chronicle/Signal-Map/arknights 跳过**。
- **最高优返场动作**：打开 Gmail 发一封给 `kris@cs.unc.edu` 的授权请求信（模板在 §1.3），lead time 3-7 天，越早发越早解锁 Phase 2 公开部署。

---

## 自我批判

- **更简方案？** 给 DeepSeek 的模板选择可以更激进收敛到一个（`doinel1a/next-ts-shadcn-ui`），其他 4 个模板只列一句「为什么不选」即可。本报告第 2 节对这个选择的解释可以再砍 30%。
- **产品合理性？** Topic 4 把 comp110-redesign 放在 #2 可能过高——如果 Kris 回「no」，整个授权线索就断了，sunk cost 会很大。更稳的做法是**先**给 TOEFL 和 ai-text-detector 把商业决策做完，comp110 邮件**只是顺手发一下**，不依赖它的回复做主线推进。
- **隐藏风险？** FERPA 部分只谈了合规存在，没谈「如果主人不小心用了真实 section time + 姓氏，出事会怎样」——UNC 可以起诉学生 + 系方会走 Dean of Students 纪律程序。这个恐吓性案例应该补进去。另外 CS50 的 CC-BY-NC-SA 不等于 UNC 默认同意——Stanford CS106A 都没给协议，说明「参考」不能替代「征得 Kris 同意」。本报告写清楚了，但用户读的时候可能误以为有前例就安全，要加粗警告。
- **遗漏了什么？** (1) 没查 UNC Honor Code 对「重做课程站」的态度，可能有学术诚信维度被漏；(2) 没查 Kris Jordan 近期有没有类似学生提过同类请求（Twitter 搜一下 @KrisJordan mentions 可能有线索）；(3) 没对 arknights-sim 的当前 state 做 `git log`，纯 assumption；(4) Claude Code 自己能不能直接当 DeepSeek 的替代（主人不写代码 = 让 Claude Code 写）这个选项没评估。
- **投入产出比？** 本报告 700 行，生成花 30 分钟 + 20 次 web search，主人读完 5 分钟，后续 30 分钟执行动作。如果主人只看 §5 和 §4.3 就够用了，前面全是备查。产出价值在于「邮件模板 + §3.5 技术栈 + §4.3 排名」三块，其余可以砍一半。

**自评分**：7/10。授权邮件模板是最高价值产物，UNC AIAP 的发现是最高价值 insight；Topic 2 和 Topic 3 的部分内容略冗。
