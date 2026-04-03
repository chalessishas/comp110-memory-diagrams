# AI 课程视频自动生成系统 -- 技术栈调研

日期：2026-04-01

---

## 1. Motion Canvas 最新版本和 API 稳定性

### 核心发现

- **当前版本：v3.17.2**（最后发布于 2024 年 12 月，距今约 15 个月无新版本）。npm 上 @motion-canvas/core、@motion-canvas/2d、@motion-canvas/ui 均停在 3.17.2。
- **API 稳定性**：v3.x 系列经历过多次 breaking changes（bootstrap 函数移除、`scene.transition()` 重命名为 `useTransition`、大量类型重命名以避免冲突）。但 3.x 内部近期无重大 breaking change，API 已趋于稳定。
- **@motion-canvas/ffmpeg 导出**：官方提供 `@motion-canvas/ffmpeg` 包，`npm install --save @motion-canvas/ffmpeg` 安装后在 Vite 配置中加入 `ffmpeg()` 插件即可。支持音轨嵌入、Fast Start 优化（Web 播放优化）。FFmpeg 二进制随包自动安装，无需手动配置。新项目默认包含此导出器。

### 对项目的价值

- FFmpeg 导出器开箱即用，可直接将 Motion Canvas 场景渲染为 MP4，省去手动拼帧的工作。
- v3 API 已稳定 15 个月无变动，选型风险低。

### 局限性

- **项目活跃度下降**：15 个月无新发布，GitHub 维护频率待确认。如果遇到 bug 可能需要自己 fork 修。
- **非 headless 渲染**：Motion Canvas 主要依赖浏览器环境（Vite dev server），headless 批量渲染需要额外配置（Puppeteer/Playwright 驱动或 CLI 方案）。
- 文档中缺少大规模批量生成的最佳实践。

### 来源

- [Motion Canvas Update Guide](https://motioncanvas.io/docs/updating/)
- [GitHub Releases](https://github.com/motion-canvas/motion-canvas/releases)
- [Video (FFmpeg) Docs](https://motioncanvas.io/docs/rendering/video/)
- [@motion-canvas/ffmpeg npm](https://www.npmjs.com/package/@motion-canvas/ffmpeg)
- [DeepWiki: Rendering and Export](https://deepwiki.com/motion-canvas/motion-canvas/6-rendering-and-export)

---

## 2. Motion Canvas 中 LaTeX 渲染方案

### 核心发现

- **Motion Canvas 内置 `Latex` 组件**：官方提供 `<Latex>` 节点，通过 `tex` 属性传入 LaTeX 字符串即可渲染数学公式。支持 `fill`（颜色）和 `fontSize`（大小）属性控制样式。
- **动画支持**：将公式拆分为字符串数组（如 `['x^2', '+', '2x', '+', '1']`），即可实现逐部分的 deletion / insertion / transformation 动画，非常适合板书"逐步推导"的效果。
- **底层实现**：内置组件使用 MathJax 将 LaTeX 转为 SVG 再渲染到 Canvas 上。也有社区方案使用 KaTeX（更快但 LaTeX 命令覆盖较少）。

### 对项目的价值

- **核心需求完美匹配**：板书课程的数学公式渲染 + 逐步动画是最关键功能，Motion Canvas 原生支持，零额外集成成本。
- 公式拆分为数组的设计与 LLM 生成结构化 JSON 的架构天然契合 -- LLM 直接输出公式分段数组即可驱动动画。

### 局限性

- MathJax SVG 渲染在大量公式场景下可能有性能问题（每个公式都要调 MathJax 编译）。
- LaTeX 命令覆盖范围受 MathJax 版本限制，极端冷门的 LaTeX 包可能不支持。
- 公式拆分粒度需要 LLM 准确把控，拆分不当会导致动画不自然。

### 来源

- [Motion Canvas LaTeX Docs](https://motioncanvas.io/docs/latex/)
- [GitHub Issue #190: LaTeX component](https://github.com/motion-canvas/motion-canvas/issues/190)
- [GitHub Issue #482: LaTeX Tweening](https://github.com/motion-canvas/motion-canvas/issues/482)
- [KaTeX Official](https://katex.org/)

---

## 3. Qwen TTS API

### 核心发现

- **最新模型系列：Qwen3-TTS**（2026 年 1 月 22 日开源，同步上线阿里云百炼平台 API）。可用模型：
  - `qwen3-tts-instruct-flash`：指令控制版，支持自然语言描述语气/情感
  - `qwen3-tts-flash`：基础快速版
  - `qwen3-tts-vd`：Voice Design（用文字描述生成新声音）
  - `qwen3-tts-vc`：Voice Clone（3 秒参考音频即可克隆）
  - 各模型均有 `-realtime` 实时流式变体
- **逐段合成**：支持 buffer 模式 -- 先将文本加入缓冲区，再逐段触发合成。适合对停顿和断句有精细控制的场景（如新闻播报、课程讲解）。
- **时长返回**：API 响应中包含 `duration` 字段（单位：秒，如 `"duration": 9.816875`），可用于同步动画时间轴。
- **延迟**：端到端合成延迟低至 97ms（流式模式）。
- **语言**：支持中/英/日/韩/德/法/俄/葡/西/意 10 种语言 + 粤语/四川话/闽南语等方言。
- **定价**：阿里云百炼按输入音频秒数计费（输出不计费）；第三方平台（fal.ai）约 $0.07/1000 字符。

### 对项目的价值

- **buffer 模式 + duration 返回**是核心匹配点：LLM 生成讲稿分段 -> 逐段调 TTS -> 拿到每段时长 -> 驱动 Motion Canvas 时间轴，形成完整 pipeline。
- Voice Design 功能可以让用户"用文字描述想要的讲师声音"，无需录音。
- 流式低延迟适合未来做实时预览。

### 局限性

- 阿里云 API 需要中国大陆账号和实名认证，海外调用需用国际版或第三方平台（fal.ai / Replicate）。
- 数学术语/公式朗读的准确性未知（如 "$\int_0^1 f(x)dx$" 的发音），可能需要 LLM 先将公式转为自然语言描述。
- 长段落一次性合成可能有长度限制，需实测单次调用的最大文本量。
- 开源模型（Qwen3-TTS-12Hz-1.7B-Base）本地部署需要 GPU 资源。

### 来源

- [Qwen-TTS API 文档（阿里云）](https://help.aliyun.com/zh/model-studio/qwen-tts-api)
- [实时语音合成文档](https://help.aliyun.com/zh/model-studio/qwen-tts-realtime)
- [Qwen3-TTS GitHub](https://github.com/QwenLM/Qwen3-TTS)
- [Qwen3-TTS 开源公告](https://qwen.ai/blog?id=qwen3tts-0115)
- [fal.ai Qwen3 TTS](https://fal.ai/models/fal-ai/qwen-3-tts/text-to-speech/0.6b)
- [阿里云模型定价](https://www.alibabacloud.com/help/en/model-studio/model-pricing)

---

## 4. d3-force / elkjs 在 Motion Canvas 中的集成

### 核心发现

- **无现成集成方案**：搜索未找到任何 d3-force 或 elkjs 与 Motion Canvas 直接集成的案例或插件。这是一个需要自建的桥接层。
- **elkjs 定位**：elkjs 纯粹计算布局坐标，不负责渲染。输入图结构（nodes + edges + layoutOptions），输出带坐标的节点和边路由信息。返回 Promise。
  - 支持多种算法：layered（适合有向图/层级结构）、force（物理模拟）、tree（树状）
  - 常见用法：`elk.layout(graph)` -> 拿到 `{x, y}` 坐标 -> 映射到渲染框架
- **d3-force 定位**：力导向布局，通过 `simulation.tick()` 逐帧计算节点位置。适合有机/自然的图布局。
- **集成策略**：
  1. 用 elkjs/d3-force 计算节点坐标（纯计算，不涉及渲染）
  2. 将坐标映射为 Motion Canvas 的 `Node` / `Circle` / `Line` 等 2D 组件的位置属性
  3. 用 Motion Canvas 的 `tween` / `spring` 动画系统驱动从无到有、或从旧布局到新布局的过渡动画

### 对项目的价值

- 课程中涉及图论、数据结构、神经网络架构等内容时，需要自动布局图/网络结构。elkjs 的 layered 算法特别适合展示有向图（如计算图、流程图）。
- d3-force 适合展示无固定方向的关系图（如社交网络、知识图谱）。
- 两者都是纯计算库，与 Motion Canvas 的渲染管线无冲突。

### 局限性

- 需要自己写桥接层：elkjs 坐标 -> Motion Canvas 节点位置 + 边绘制。这是一次性工作但需要一定工程量。
- d3-force 的 tick-based 模拟需要适配 Motion Canvas 的帧同步机制（generator-based yield）。
- 布局算法输出的坐标可能需要缩放/偏移以适配画布尺寸。
- elkjs 的 WASM 版本体积较大（~1.2MB），对前端打包有影响（但本项目是后端渲染，影响不大）。

### 来源

- [d3-force 文档](https://d3js.org/d3-force)
- [elkjs GitHub](https://github.com/kieler/elkjs)
- [elkjs npm](https://www.npmjs.com/package/elkjs)
- [ELK Demonstrators](https://rtsys.informatik.uni-kiel.de/elklive/)
- [DeepWiki: elkjs Usage Guide](https://deepwiki.com/kieler/elkjs/5-usage-guide)

---

## 5. 同类产品调研

### 5a. LLM + Manim 自动生成方案（开源，最直接的竞品/参考）

| 项目 | 架构 | 特点 |
|------|------|------|
| **[topic2manim](https://github.com/mateolafalce/topic2manim)** | 多 Agent 系统，输入主题 -> 自动生成 Manim 视频 | 与我们的架构最相似：主题 -> 结构化脚本 -> 动画代码 -> 视频 |
| **[Manimator](https://arxiv.org/html/2507.14306v1)** | LLM pipeline，输入论文/文本 -> 结构化场景描述 -> Manim 代码 -> 动画 | 有学术论文，两阶段 LLM 架构（理解 + 代码生成） |
| **[TheoremExplainAgent (TEA)](https://tiger-ai-lab.github.io/TheoremExplainAgent/)** | 双 Agent（Planner + Coder），生成 5 分钟以上定理讲解视频 | 学术级方案，Planner 生成叙事计划 + 旁白，Coder 生成 Manim 脚本 |
| **[Math-To-Manim](https://github.com/HarleyCoops/Math-To-Manim)** | 多 pipeline（Gemini 6-Agent Swarm / Kimi K2.5 Swarm） | 三条独立 pipeline 可选，链式思维推理增强 |
| **[manim-video-generator](https://github.com/rohitg00/manim-video-generator)** | 自然语言描述 -> GPT 生成 Manim 代码 -> 动画 | 最简单的单 LLM 调用方案 |

### 5b. 商业白板动画工具

| 产品 | 定位 | 与我们的差异 |
|------|------|-------------|
| **[Golpo AI](https://video.golpoai.com)** | Stanford 出身 / YC 支持，PDF/文档 -> 白板风格讲解视频 | 偏商业化白板风，不支持数学公式动画推导 |
| **[InVideo AI](https://invideo.io)** | 脚本 -> 白板风格视频（素材拼接式） | 基于素材库匹配，不是程序化生成 |
| **[HeyGen](https://heygen.com)** | 脚本 -> AI 数字人 + 白板内容 | 重点在数字人，板书能力弱 |
| **[Animaker](https://animaker.com/whiteboard)** | 白板动画模板工具 | 模板化，不支持数学公式 |

### 核心发现

- **LLM + Manim 是当前最活跃的技术路线**，已有至少 5 个开源项目和 1 篇学术论文。主流架构是「多 Agent：Planner + Coder」或「两阶段 LLM：理解 -> 代码生成」。
- **所有开源方案都用 Manim（Python），没有用 Motion Canvas（TypeScript）的**。我们选择 Motion Canvas 是差异化点，但也意味着没有现成参考代码。
- 商业工具以"素材拼接式白板动画"为主，不具备数学公式逐步推导能力。

### 对项目的价值

- topic2manim 和 TheoremExplainAgent 的架构设计可以直接借鉴：LLM 生成结构化中间表示（而非直接生成渲染代码），再由确定性程序转为动画。
- 两阶段 / 多 Agent 架构被反复验证有效，LLM 直接生成动画代码的可靠性不如先生成结构化 JSON 再映射。
- 差异化：我们用 Motion Canvas（TypeScript、Web 生态、内置 LaTeX 动画），竞品全用 Manim（Python）。

### 局限性

- Manim 生态更成熟，社区更大，LLM 训练数据中 Manim 代码远多于 Motion Canvas 代码。如果需要 LLM 直接生成渲染代码，Manim 有优势。
- 但我们的架构是 LLM 生成结构化 JSON（不是渲染代码），所以这个劣势被规避了。

### 来源

- [topic2manim GitHub](https://github.com/mateolafalce/topic2manim)
- [Manimator 论文](https://arxiv.org/html/2507.14306v1)
- [TheoremExplainAgent](https://tiger-ai-lab.github.io/TheoremExplainAgent/)
- [Math-To-Manim GitHub](https://github.com/HarleyCoops/Math-To-Manim)
- [manim-video-generator GitHub](https://github.com/rohitg00/manim-video-generator)
- [Golpo AI](https://video.golpoai.com)
- [Deep Dive: Creating Accurate Math Videos Using LLMs](https://aditya-advani.medium.com/deep-dive-creating-accurate-math-videos-using-llms-02db22ba1d2d)

---

## 6. 商业 AI 视频平台竞品深度分析（Avatar-based）

### 6a. Synthesia

- **定位**：企业培训 + 教育视频，AI 数字人驱动
- **定价**：Creator $18-29/月，700+ 数字人形象，175+ 语言，1080p 导出，支持 Voice Cloning
- **教育功能**：支持 LMS 集成（SCORM），但无原生测验/知识检查功能
- **局限**：以"talking head + slides"为主，不支持数学公式逐步推导动画

### 6b. HeyGen

- **定位**：营销 + 教育短视频，AI 数字人 + 脚本驱动
- **定价**：Creator $29/月，含 Custom Digital Twin、Unlimited Photo Avatars
- **教育功能**：支持多语言配音切换，适合多语言课程；但教育专用功能较弱
- **局限**：白板/板书能力几乎为零，重在人物出镜场景

### 6c. Colossyan

- **定位**：专注 L&D（Learning & Development）和教育培训
- **定价**：在 Synthesia 和 HeyGen 之间，Pro 计划含 Scenario Branching
- **教育功能**（差异化亮点）：
  - **原生测验和知识检查**：视频中可暂停出题，根据答案分支
  - **LMS 集成**：完成数据回传，支持 SCORM/xAPI
  - 这是 Synthesia 和 HeyGen 都没有的原生功能
- **局限**：同样不支持程序化数学动画

### 6d. 新兴课程生成平台

| 平台 | 特点 | 定价 |
|------|------|------|
| [X-Pilot](https://www.x-pilot.ai) | 100+ 教育 Motion Box 模板，20x 加速课程视频制作 | 免费 + 付费 |
| [Mootion](https://www.mootion.com) | 脚本/幻灯片/音频 -> 教育视频 | 未公开 |
| [AiCoursify](https://www.aicoursify.com) | 全流程 AI：课程大纲 + 课件 + 测验 + 配音 | 免费起步 |
| [Pictory AI](https://pictory.ai) | 文本/脚本 -> 视频（素材拼接式） | $19/月起 |
| [Coursebox](https://www.coursebox.ai) | AI 课程创建器，侧重 LMS 集成 | 免费起步 |

### 核心发现

- **所有商业平台都是"数字人 + 幻灯片"或"素材拼接"模式**，没有一个支持程序化数学公式推导动画。
- Colossyan 在教育领域最深耕（原生测验、LMS 集成），但核心仍是 avatar-based。
- **市场空白**：不存在一个工具能做到"输入教学主题 -> 输出 3Blue1Brown 风格板书推导视频"。这正是我们的定位。
- 商业平台定价集中在 $18-29/月/用户，如果我们的产品能达到类似质量，有明确的定价锚点。

### 来源

- [HeyGen vs Synthesia vs Colossyan 2026 对比](https://www.aimagicx.com/blog/heygen-vs-synthesia-vs-colossyan-avatar-comparison-2026)
- [Colossyan vs HeyGen vs Synthesia 功能对比](https://www.colossyan.com/posts/heygen-vs-synthesia)
- [2026 AI Avatar Toolkit 营销对比](https://marketingagent.blog/2025/11/12/the-2026-ai-avatar-toolkit-platform-comparison-for-marketers-synthesia-vs-heygen-vs-colossyan/)
- [Best Online Course Creation Tools 2026](https://aiavatar.tech.blog/2026/03/19/best-online-course-creation-tools-in-2026/)
- [12 Best AI Online Course Creators 2026](https://www.schoolmaker.com/blog/ai-online-course-creator)

---

## 7. Headless 渲染方案深度对比：Motion Canvas vs Revideo vs Remotion

### 7a. Motion Canvas 无头渲染现状

- **GitHub Issue #415**（"Render projects headlessly"）：2023 年 2 月提出，截至 2026 年 1 月仍 **OPEN**
- PR #595（`@motion-canvas/renderer` 包）仍为 **draft** 状态
- PR #631 已合并：支持 `?render` URL 参数在 Web UI 中触发渲染
- **现状**：官方不提供 CLI 或 headless API。要实现无头渲染，需要自己用 Puppeteer/Playwright 驱动浏览器访问 `localhost:9000/?render`
- **结论**：可行但需要自建 wrapper，非一等公民功能

### 7b. Revideo（Motion Canvas Fork，重点推荐）

- **定位**：Motion Canvas 的 fork，专为程序化视频生成设计
- **GitHub**：[redotvideo/revideo](https://github.com/redotvideo/revideo)，3.7k stars，1,124 commits
- **核心差异**：
  - **`renderVideo()` 函数**：直接在 Node.js 中调用，无需浏览器 UI
  - **可部署为 API**：支持部署到 Google Cloud Run 等 serverless 平台
  - **并行渲染**：渲染速度提升 70x（官方 benchmark）
  - **音频支持**：内置 `<Audio/>` 和 `<Video/>` 组件，渲染时自动混合音轨
- **与 Motion Canvas 的兼容性**：fork 自 Motion Canvas，核心 API 相同（场景/节点/动画系统），迁移成本低
- **局限**：
  - 社区比 Motion Canvas 小
  - 仍需 headless browser 做实际渲染（底层用 Puppeteer）
  - 文档较少

### 7c. Remotion

- **定位**：React 生态的程序化视频框架
- **定价**：免费（个人/3人以下团队），$100/月（4人+），$500/月（企业）
- **优势**：生态最成熟，React 开发者上手快，Lambda 云渲染支持
- **劣势**：
  - 基于 React 渲染，每帧需要 headless browser 截图 -> 比 Canvas API 慢
  - 不支持 Motion Canvas 的信号（signal）和生成器（generator）动画模型
  - LaTeX 支持需要第三方库
  - 许可证对商业团队有限制

### 推荐方案

**短期（MVP）**：用 Motion Canvas + Puppeteer wrapper 实现 headless 渲染。代码与 Motion Canvas 文档完全兼容，遇到问题社区资料多。

**中期（规模化）**：评估迁移到 Revideo。`renderVideo()` API + 并行渲染 + 音频混合 = 完美匹配 CLI pipeline 架构。迁移成本低（同源 API）。

**不推荐 Remotion**：React 渲染模型与板书动画的 imperative 风格不匹配，性能也不如 Canvas API 直接渲染。

### 来源

- [Motion Canvas Issue #415: Headless Rendering](https://github.com/motion-canvas/motion-canvas/issues/415)
- [Revideo GitHub](https://github.com/redotvideo/revideo)
- [Revideo: renderVideo() API](https://docs.re.video/api/renderer/renderVideo/)
- [Revideo: 70x Faster Rendering](https://re.video/blog/faster-rendering)
- [Remotion vs Motion Canvas 对比](https://www.remotion.dev/docs/compare/motion-canvas)
- [Remotion 定价](https://www.remotion.dev/docs/license)

---

## 8. TTS 开源模型 2026 全景对比

### 综合排名（教育旁白场景）

| 模型 | 参数量 | MOS | WER | 延迟 | 长文本稳定性 | 教育适用性 | 许可证 |
|------|--------|-----|-----|------|-------------|-----------|--------|
| **Qwen3-TTS** | 1.7B / 0.6B | 领先 | 1.835% (10语言) | 97ms (流式) | 优秀 | **最佳**（多语言 + 指令控制语气） | Apache 2.0 |
| **Kokoro** | 82M | 高（Arena #1） | 低 | <0.3s | 优秀（>3min） | 极佳（轻量、教育专优化） | Apache/MIT |
| **F5-TTS** | 中等 | 最均衡 | 低 | <7s | 优秀（>3min） | 优秀（情感保留强） | MIT |
| **CosyVoice 2** | 0.5B | 5.53 | 降低30-50% | 150ms (流式) | 好 | 好（中文强势） | Apache 2.0 |
| **Sesame CSM** | 1B | 4.7 | - | - | 好 | 一般（偏对话） | 开源 |
| **IndexTTS-2** | - | 高 | - | - | 好 | 好（情感/音色独立控制） | 开源 |
| **VibeVoice** | 1.5B | - | - | - | 极佳（90min/4人） | 好（超长文本） | - |

### 关键发现

1. **Qwen3-TTS 是教育场景最佳选择**：
   - 10 语言 1.835% WER 超越 ElevenLabs（商业）
   - `qwen3-tts-instruct-flash` 支持自然语言控制语气（"用耐心的教授口吻讲解"）
   - buffer 模式 + duration 返回 = 完美对接动画时间轴
   - 0.6B 模型可本地部署

2. **Kokoro 是极致性价比方案**：
   - 82M 参数在笔记本上实时运行
   - TTS Arena 排名第一
   - 训练成本仅 $1000（A100）
   - 教育旁白专项测试：18,000 字 12 个模块 < 3 分钟
   - 适合作为 Qwen3-TTS 的 fallback 或离线方案

3. **F5-TTS 是最均衡选手**：高 MOS + 低 WER + 强情感保留 + 长文本稳定。SpeechRole 评价为"最平衡的选择"。

4. **商业 API 仍有优势但差距在缩小**：ElevenLabs 在自然度上仍有微弱领先，但 Qwen3-TTS 在 WER 上已超越。开源模型的质量已达到商业可用水平。

### 推荐

- **主力 TTS**：Qwen3-TTS（API 调用或本地部署 0.6B）
- **离线 / 低资源 fallback**：Kokoro-82M
- **需要极致自然度时**：F5-TTS

### 来源

- [Qwen3-TTS Technical Report](https://arxiv.org/html/2601.15621v1)
- [Qwen3-TTS GitHub](https://github.com/QwenLM/Qwen3-TTS)
- [Best Open-Source TTS Models 2026 (BentoML)](https://bentoml.com/blog/exploring-the-world-of-open-source-text-to-speech-models)
- [F5-TTS Paper](https://arxiv.org/html/2410.06885v1)
- [CosyVoice 2 Paper](https://arxiv.org/html/2412.10117v2)
- [Kokoro-82M HuggingFace](https://huggingface.co/hexgrad/Kokoro-82M)
- [Kokoro TTS Review 2026](https://reviewnexa.com/kokoro-tts-review/)
- [Speech AI Benchmarks 2026 Leaderboard](https://www.codesota.com/speech)
- [Open-Source TTS Comparison (DigitalOcean)](https://www.digitalocean.com/community/tutorials/best-text-to-speech-models)
- [12 Best Open-Source TTS Models Compared](https://www.inferless.com/learn/comparing-different-text-to-speech---tts--models-part-2)
- [Best TTS APIs 2026 (Speechmatics)](https://www.speechmatics.com/company/articles-and-news/best-tts-apis-in-2025-top-12-text-to-speech-services-for-developers)

---

## 9. OpenStax 内容获取可行性

### CNX 平台现状

- **CNX 已退役**：OpenStax 发布 [Saying goodbye to CNX](https://openstax.org/blog/saying-goodbye-cnx) 博文，正式告别 CNX 平台
- **cnx-archive GitHub 仓库**：2024 年 12 月 3 日被 owner **归档（archived）**，变为只读
- **archive.cnx.org API**：原 API 结构为 `GET archive.cnx.org/contents/[id].json`，返回 JSON 元数据 + HTML 内容。但此域名的可用性不确定（仓库已归档）

### 当前内容获取方式

1. **openstax.org 直接访问**：教材内容仍在 openstax.org 上可读，但网站依赖 JavaScript 渲染（SPA），不方便爬取
2. **GitHub 源文件**：OpenStax 教材源文件以 **CNXML** 格式存储在 GitHub。可用 [cnxml2md](https://github.com/Ravenstine/cnxml2md) 转 Markdown
3. **Rex Web（阅读体验）**：[openstax/rex-web](https://github.com/openstax/rex-web) 是前端阅读器，可能有内部 API 可调用
4. **Open Search API**：[openstax/open-search](https://github.com/openstax/open-search) 提供书籍和练习内容的搜索 API（Swagger 文档可用）
5. **content-manager-approved-books**：[openstax/content-manager-approved-books](https://github.com/openstax/content-manager-approved-books) 存储了官方批准书籍的列表和元数据

### OpenStax 数学教材覆盖

OpenStax **没有** Discrete Mathematics 教材。其数学分类包括：
- Prealgebra, Elementary Algebra, Intermediate Algebra
- College Algebra, Algebra and Trigonometry
- Precalculus, Calculus (Vol 1-3)
- Statistics, Introductory Statistics
- Contemporary Mathematics

### 替代教材来源（离散数学）

| 教材 | 作者 | 特点 |
|------|------|------|
| [Discrete Mathematics: An Open Introduction (4th ed)](https://discrete.openmathbooks.org/) | Oscar Levin | 最主流的开源离散数学教材，CC-BY-SA，适合 CS 专业 |
| [Discrete Mathematics (LibreTexts)](https://math.libretexts.org/Bookshelves/Combinatorics_and_Discrete_Mathematics/Discrete_Mathematics_(Levin)) | Oscar Levin | 同一教材的 LibreTexts 镜像，API 友好 |
| [Applied Discrete Structures](http://applied-discrete-structures.wiki/) | - | 偏应用，覆盖枚举/递归/离散优化 |

### 推荐方案

1. **放弃 OpenStax API 作为主要内容源**：CNX 已退役，API 不稳定。不应依赖一个归档项目
2. **使用 LibreTexts API**：LibreTexts 有活跃的 API，覆盖大量开源教材（包括 Oscar Levin 的离散数学）
3. **直接使用开源教材 PDF/HTML**：Oscar Levin 的教材有 PDF、HTML、LaTeX 源码，可直接解析
4. **LLM 直接生成教学内容**：对于 MVP，不需要外部教材 API。LLM 本身对离散数学的知识覆盖已足够生成教学脚本

### 来源

- [OpenStax Math Subjects](https://openstax.org/subjects/math)
- [Saying goodbye to CNX (OpenStax Blog)](https://openstax.org/blog/saying-goodbye-cnx)
- [cnx-archive GitHub (Archived)](https://github.com/openstax/cnx-archive)
- [CNX Archive Content API Docs](https://github.com/openstax/cnx-archive/blob/master/docs/content_api_doc.md)
- [cnxml2md: CNXML to Markdown](https://github.com/Ravenstine/cnxml2md)
- [OpenStax Developer Hub](https://openstax.github.io/)
- [Discrete Mathematics: An Open Introduction](https://discrete.openmathbooks.org/)
- [OpenStax CNX Wikipedia](https://en.wikipedia.org/wiki/OpenStax_CNX)

---

## 10. Manim + AI 生态（直接竞品 / 技术参考）

### 活跃项目一览

| 项目 | Stars | 架构 | 关键特点 |
|------|-------|------|---------|
| [Generative Manim](https://generative-manim.vercel.app/) | 活跃 | LLM -> Manim 代码 | 支持 GPT-4o/Claude Sonnet，Web UI，最成熟的产品化方案 |
| [topic2manim](https://github.com/mateolafalce/topic2manim) | - | 多 Agent pipeline | GPT-5.2 + Manim Community，全自动零干预 |
| [manim-shorts](https://github.com/xtechsouthie/manim-shorts) | - | LangGraph + 双 RAG | 自愈代码合成，零人工干预，面向短视频 |
| [Manimator](https://github.com/HyperCluster-Tech/manimator) | - | 论文 -> 视觉讲解 | 有学术论文支撑（[arXiv](https://arxiv.org/html/2507.14306v1)） |
| [3brown1blue](https://pypi.org/project/3brown1blue/) | - | PyPI 包 | 22 种视觉模式提取自 3B1B 422 帧，安全 API wrapper |
| [manim-generator](https://github.com/makefinks/manim-generator) | - | Code-Writer + Reviewer 循环 | 执行日志反馈循环，自动修复错误 |

### 学术研究

- **[Large Language Model Approaches to Educational Video Generation Using Manim](https://link.springer.com/chapter/10.1007/978-3-032-07938-1_26)** (Springer, 2025): 研究 <10B 参数 LLM + PEFT 微调生成 Manim 代码的效果
- **[Manimator Paper](https://arxiv.org/html/2507.14306v1)**: 两阶段 pipeline（理解 -> 代码生成）的系统化方案

### 关键洞察

1. **LLM 直接生成 Manim 代码的可靠性仍是核心挑战**：所有项目都在解决同一个问题 -- LLM 生成的代码经常有语法错误或渲染异常。解决方案分两派：
   - **自愈循环**（manim-shorts, manim-generator）：执行 -> 报错 -> LLM 修复 -> 重试
   - **结构化中间表示**（我们的方案）：LLM 生成 JSON -> 确定性代码映射，绕过代码生成可靠性问题

2. **我们的 JSON Schema 方案是更稳健的路线**：竞品的"自愈循环"依赖 LLM 理解报错信息并修复，成功率不稳定。我们的"结构化 JSON -> 确定性映射"方案在可靠性上有结构性优势。

3. **Motion Canvas 在此领域是空白**：所有项目都基于 Manim（Python），没有 Motion Canvas（TypeScript）方案。这是蓝海，也意味着需要自建基础设施。

### 来源

- [Generative Manim](https://generative-manim.vercel.app/)
- [topic2manim GitHub](https://github.com/mateolafalce/topic2manim)
- [manim-shorts GitHub](https://github.com/xtechsouthie/manim-shorts)
- [Manimator GitHub](https://github.com/HyperCluster-Tech/manimator)
- [3brown1blue PyPI](https://pypi.org/project/3brown1blue/)
- [manim-generator GitHub](https://github.com/makefinks/manim-generator)
- [LLM + Manim 学术论文 (Springer)](https://link.springer.com/chapter/10.1007/978-3-032-07938-1_26)
- [Generative Manim: AI-Powered Video Creation (BrightCoding)](https://www.blog.brightcoding.dev/2026/02/22/generative-manim-ai-powered-video-creation-revolution)

---

## 综合结论与建议

### 技术栈可行性：高

整条 pipeline 的每个环节都有成熟方案：

1. **LLM -> 结构化 JSON**：已被多个开源项目验证，两阶段架构（Planner + Renderer 指令）最可靠
2. **Qwen TTS**：buffer 模式逐段合成 + duration 返回 = 完美的时间轴同步数据源。Kokoro-82M 作为轻量 fallback
3. **Motion Canvas**：内置 LaTeX 动画组件 + FFmpeg 导出 = 板书渲染和视频导出一站解决
4. **Headless 渲染**：短期 Puppeteer wrapper，中期迁移 Revideo（renderVideo API + 并行渲染）
5. **图布局**：elkjs 计算坐标 -> Motion Canvas 渲染，需自建桥接层但工程量可控
6. **教材内容**：OpenStax CNX 已退役，改用 LibreTexts API 或 LLM 直接生成

### 市场定位

- **差异化**：全市场没有"输入主题 -> 输出 3B1B 风格板书推导视频"的产品
- 商业 avatar 平台（Synthesia/HeyGen/Colossyan）不做数学动画
- 开源 Manim+AI 项目都用 Python，没有 TypeScript/Web 方案
- **定价锚点**：商业平台 $18-29/月，我们的技术成本更低（开源 TTS + 开源渲染引擎）

### 关键风险

| 风险 | 严重程度 | 缓解措施 |
|------|---------|----------|
| Motion Canvas 项目停止维护 | 中 | v3 API 已稳定；可迁移到 Revideo（同源 API）或 Manim |
| LLM 生成的 JSON 格式不稳定 | 高 | 定义严格的 JSON Schema + validation 层 |
| 数学公式 TTS 朗读不准确 | 中 | LLM 阶段增加"公式转自然语言"步骤 |
| Headless 批量渲染性能 | 中 | 短期 Puppeteer，中期 Revideo 并行渲染（70x 加速） |
| OpenStax API 不可用 | 低 | 已确认退役；改用 LibreTexts 或 LLM 生成内容 |
| Manim 生态竞品先发优势 | 中 | 我们的 JSON Schema 方案比"自愈循环"更可靠；TypeScript 生态触达不同开发者群体 |

### 推荐优先级

1. **P0 -- 先跑通最小闭环**：手写一个 Motion Canvas 场景（LaTeX 公式 + 文字动画）-> FFmpeg 导出视频，验证渲染质量
2. **P1 -- 接入 Qwen TTS**：一段文本 -> TTS 合成 -> 拿到 duration -> 硬编码到 Motion Canvas 时间轴
3. **P2 -- LLM 结构化输出**：定义 JSON Schema -> LLM 生成 -> 自动映射为 Motion Canvas 场景
4. **P3 -- Headless 渲染管线**：Puppeteer wrapper 实现 CLI 调用，评估 Revideo 迁移
5. **P4 -- 图布局集成**：elkjs 桥接层，按需开发
6. **P5 -- 教材内容集成**：LibreTexts API 对接（如需课程大纲结构化输入）
