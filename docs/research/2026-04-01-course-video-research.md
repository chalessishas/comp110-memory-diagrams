# AI 课程视频自动生成 — 技术调研

> 2026-04-01 Research Loop 产出

## 1. 竞品空白确认

**商业 Avatar 平台**（Synthesia $18-29/月, HeyGen $29/月, Colossyan）全部是"数字人+幻灯片"模式，**不支持数学公式推导动画**。Colossyan 在教育领域最深（原生测验、LMS 集成）。

**Manim + AI 开源生态**活跃：Generative Manim、topic2manim、manim-shorts（LangGraph 零干预）、Manimator 等。**全部基于 Python/Manim，没有 TypeScript/Motion Canvas 方案**。

**市场空白**：不存在"输入主题 → 输出板书推导动画视频"的全自动产品。

## 2. Motion Canvas Headless 渲染 — 关键发现

- Motion Canvas 官方无头渲染（Issue #415）**仍 OPEN，无官方 CLI**
- **Revideo**（Motion Canvas fork, 3.7k stars）是最佳替代：提供 `renderVideo()` Node.js API、并行渲染 70x 加速、内置音频混合。API 与 Motion Canvas 同源，迁移成本低
- 推荐：直接用 Revideo 而非 Motion Canvas

## 3. TTS 选型

| 方案 | 优势 | 适用性 |
|------|------|--------|
| **Qwen3-TTS** | 10 语言 1.835% WER，buffer 模式返回 duration | 最佳选择，完美对接动画时间轴 |
| **Kokoro-82M** | 82M 参数可本地跑，TTS Arena 排名第一 | 极致性价比备选 |
| **F5-TTS** | 高 MOS + 低 WER + 声音克隆 | 均衡备选 |

## 4. OpenStax API — 已失效

- **archive.cnx.org 已退役**，cnx-archive 仓库 2024-12 归档为只读。之前的设计方案中依赖此 API 不可行。
- OpenStax **没有** Discrete Mathematics 教材
- 替代源：Oscar Levin《Discrete Mathematics: An Open Introduction》(CC-BY-SA) 或 LibreTexts API（需 token）

## 5. 对项目的影响

| 设计变更 | 原方案 | 新方案 |
|----------|--------|--------|
| 渲染器 | Motion Canvas | **Revideo**（有 headless API，不需要 Puppeteer hack） |
| 教材 API | OpenStax archive.cnx.org | MVP 不依赖外部教材 API，LLM 自由生成 + 可选 `--source` 本地文件 |
| TTS | Qwen TTS | 确认 Qwen3-TTS 是最佳选择（buffer 模式返回 duration） |

## 6. LaTeX 渲染方案（Revideo 内置组件 headless 崩溃后的替代）

**问题**：`@revideo/2d` 的 `Latex` 组件在 headless Puppeteer 中崩溃（Error: null）。

**解决方案**：Node.js 端用 `mathjax-full`（已安装）预渲染 LaTeX → SVG data URI，传给 Revideo 的 `Img` 组件。

```typescript
import { mathjax } from 'mathjax-full/js/mathjax.js';
import { TeX } from 'mathjax-full/js/input/tex.js';
import { SVG } from 'mathjax-full/js/output/svg.js';
import { liteAdaptor } from 'mathjax-full/js/adaptors/liteAdaptor.js';
import { RegisterHTMLHandler } from 'mathjax-full/js/handlers/html.js';
import { AllPackages } from 'mathjax-full/js/input/tex/AllPackages.js';

const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);
const tex = new TeX({ packages: AllPackages });
const svg = new SVG({ fontCache: 'none' }); // 'none' = 内联 path，SVG 自包含
const doc = mathjax.document('', { InputJax: tex, OutputJax: svg });

function texToSvgDataUri(latex: string): string {
  const node = doc.convert(latex, { display: true });
  const svgHtml = adaptor.innerHTML(node).replace(/currentColor/g, '#ffe066');
  return 'data:image/svg+xml;base64,' + Buffer.from(svgHtml).toString('base64');
}
```

- 零新依赖（mathjax-full@3.2.2 已是 @revideo/2d 的依赖）
- 同步函数，无网络调用
- 颜色通过字符串替换 `currentColor` → `#ffe066`，背景透明
- `fontCache: 'none'` 关键：让每个 SVG 自包含，不依赖外部缓存

**集成方式**：pipeline.ts 在 Step 3 前预渲染所有 LaTeX 公式为 data URI，通过 variables 传给 Revideo，board.tsx 用 `Img` 组件显示。

## 来源
- Revideo: GitHub revideo/revideo (Motion Canvas fork with headless rendering)
- Generative Manim: GitHub ai-christianson/generative-manim
- Manim-shorts: GitHub HarleyCoops/manim-shorts (LangGraph zero-intervention)
- Qwen3-TTS: Hugging Face Qwen/Qwen3-TTS
- OpenStax cnx-archive: GitHub openstax/cnx-archive (archived 2024-12)
