# AI 课程视频自动生成系统 — 设计规格

## 概述

输入课程主题（一个字符串），全自动输出带配音的板书动画视频（MP4）。零人工介入。

## 架构

四步管线，每步单一职责：

```
课程主题 (string)
    ↓
┌─────────────────────────┐
│  1. Script Generator     │  LLM (Claude / DeepSeek)
│     主题 → CourseScript  │  结构化 JSON：讲稿 + 板书指令
└──────────┬──────────────┘
           ↓
┌─────────────────────────┐
│  2. TTS Engine           │  Qwen TTS
│     讲稿 → 音频 + 时长   │  逐段合成，输出 .wav + 每段 duration
└──────────┬──────────────┘
           ↓
┌─────────────────────────┐
│  3. Board Renderer       │  Motion Canvas
│     指令 → 板书动画帧    │  按 TTS 时长对齐每段动画
└──────────┬──────────────┘
           ↓
┌─────────────────────────┐
│  4. Compositor           │  @motion-canvas/ffmpeg 或 FFmpeg
│     音频 + 视频 → MP4    │
└─────────────────────────┘
```

## 核心 JSON Schema

LLM 输出格式 — 系统的核心 API。所有板书操作都是声明式的，LLM 管语义，渲染器管空间。

```typescript
interface CourseScript {
  title: string;
  segments: Segment[];
}

interface Segment {
  narration: string;       // TTS 朗读的文本
  board: BoardAction[];    // 该段对应的板书指令序列
}

// ── MVP 操作集（6 个） ──────────────────────────

type BoardAction =
  | { type: "write_text"; id?: string; text: string }
  | { type: "show_formula"; id?: string; latex: string }
  | { type: "draw_arrow"; from: string; to: string }       // 引用已渲染元素的 id
  | { type: "highlight"; target: string; color?: string }   // 引用已渲染元素的 id
  | { type: "erase"; area: "all" | string }                 // "all" = 翻页清空；string = 擦除指定元素的 id
  | { type: "pause"; duration: number }

// ── 扩展操作集（3 个，图论 / 树 / FSM） ─────────

  | { type: "draw_graph"; nodes: GraphNode[]; edges: GraphEdge[] }
  | { type: "highlight_node"; id: string; color: string }
  | { type: "highlight_edge"; from: string; to: string; color: string }

interface GraphNode {
  id: string;
  label: string;
}

type GraphEdge = [string, string, string?];  // [from_id, to_id, label?]
```

### 设计决策

**为什么 JSON + 模板而非 LLM 直接生成代码：**
- 全自动要求零失败率。LLM 填 JSON schema 几乎不会出错（结构化输出），直接写 Motion Canvas 代码有 ~30% 失败率
- 解耦：换渲染引擎不影响 LLM 层，换 LLM 不影响渲染层
- 扩展新操作只改两处：schema 加一个 type + Motion Canvas 加一个模板组件

**为什么 draw_arrow 用 string 引用而非坐标：**
- LLM 不知道空间布局，不该猜坐标
- 渲染器维护元素注册表（id → 位置），自动计算箭头起止点
- 与 draw_graph 的 highlight_edge 设计一致：LLM 描述语义关系，渲染器解决空间问题

**为什么没有 draw_diagram：**
- `params: Record<string, unknown>` 是无类型的万能口子，LLM 输出不可控
- 需要图示场景时，按需设计专门的强类型操作（如 draw_graph），每个操作有明确的参数结构
- 6 个 MVP 操作覆盖 95% 的文字/公式板书场景；3 个扩展操作覆盖图论/树/FSM

## 渲染器架构

### 元素注册表

渲染器维护一个 `Map<string, RenderedElement>`，记录每个已渲染元素的 id 和位置。
- `write_text` / `show_formula` / `draw_graph` 渲染时自动注册
- `draw_arrow` / `highlight` 通过 id 查询目标位置
- `erase` 清除元素时同步清理注册表
- 元素未提供 id 时，渲染器自动生成（基于 type + 序号）

### 布局策略

- 文字/公式：从左上角开始，自动换行，像真实板书一样从上往下写
- 图（draw_graph）：使用 `d3-force` 或 `elkjs` 自动布局，LLM 只描述拓扑
- 板书满了：LLM 在切换大主题时插入 `erase("all")`，等效于"翻页"

### 视觉风格

- 背景：深绿色（黑板）或深灰色（灰板）
- 文字：白色，无衬线字体
- 公式：LaTeX 渲染，白色
- 高亮：黄色 / 红色叠加
- 整体风格：干净、学术、无花哨装饰

## TTS 对齐

采用**逐段合成**策略：

1. 遍历 `segments`，每段的 `narration` 单独调 Qwen TTS
2. 获得每段音频文件 + 精确时长（毫秒）
3. 将时长传给 Motion Canvas 渲染器，每段板书动画的总时长 = 该段语音时长
4. 板书动作在段内均匀分配时间，`pause` 操作消耗额外时间
5. 最终所有段的音频拼接 + 视频帧序列合成为 MP4

## 项目结构

```
course-video/
├── src/
│   ├── pipeline.ts          # 管线编排：串联四步
│   ├── script-generator.ts  # LLM 调用 + JSON 解析
│   ├── tts.ts               # Qwen TTS 封装
│   ├── renderer/
│   │   ├── project.ts       # Motion Canvas 项目入口
│   │   ├── scenes/
│   │   │   └── board.tsx    # 板书场景：解析 BoardAction 序列
│   │   ├── components/      # 每个操作一个组件
│   │   │   ├── WriteText.tsx
│   │   │   ├── ShowFormula.tsx
│   │   │   ├── DrawArrow.tsx
│   │   │   ├── Highlight.tsx
│   │   │   └── Erase.tsx
│   │   └── registry.ts     # 元素注册表
│   └── types.ts             # CourseScript / BoardAction 类型定义
├── cli.ts                   # CLI 入口
├── package.json
└── tsconfig.json
```

## CLI 接口

```bash
# 基本用法
npx course-video generate "微积分：极限的定义"
# → output/微积分-极限的定义.mp4

# 指定 LLM
npx course-video generate "图论：BFS 遍历" --model deepseek

# 指定输出目录
npx course-video generate "线性代数：矩阵乘法" --output ./videos/
```

## MVP 范围

### 做

- 6 个板书操作的模板渲染
- 逐段 TTS（Qwen）+ 时间对齐
- 黑板视觉风格
- CLI：主题 → MP4
- CourseScript JSON schema + 校验

### 不做（后续迭代）

- draw_graph 等扩展操作（第一轮扩展）
- Web UI
- 批量生成
- 手写体 / 粉笔笔画动画
- 多语言 / 多音色
- 视频模板 / 片头片尾

## 适用与不适用场景

### 适用

- 数学、物理、CS 等板书密集型学科
- 概念讲解、公式推导、定理证明
- 图论 / 树 / 状态机（扩展操作后）

### 不适用

- 文科叙事型内容（历史、文学）— 板书不是最佳载体
- 需要实物演示的场景（化学实验、生物解剖）
- 需要代码实时执行的编程教学
