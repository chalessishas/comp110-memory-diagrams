# Research Loop 03:01 — chronicle 项目下一步方向

**时间**：2026-04-17 03:01
**研究动机**：跨日首个 chronicle-focused research。项目 1 个月前（03/18 附近）assemble，最近 commit 5 天前 (touch support)。主人未动，值得确认下一步方向。
**定位**：**主人自用的个人知识管理**（CanvasApp 有 4 个种子节点 Learning/Projects/Health/Ideas，非多人 SaaS，无 collaborator invite 逻辑）。

---

## 1. 2026 市场证据（3 次 WebSearch）

### E1. 无限画布分层清晰
2026 市场分 3 层：
- **快速绘图**：Excalidraw / tldraw
- **企业协作**：Miro
- **知识管理**：AFFiNE（开源 + AI）/ Heptabase（$10/mo）/ OmniCanvas（$5/mo）

**对 chronicle**：知识管理层的成熟商业产品在 $5-10/月定价，功能包括 folder/tag/full-text search + 空间布局。chronicle 当前 feature 和它们重叠，但**是自用**——无商业化压力。
URL: https://omnicanvasnotes.com/blog/reviews/best-infinite-canvas-apps-2026/

### E2. Canvas 2D vs WebGL 性能门槛
- **WebGL zoom/pan 0.01ms vs Canvas 2D 1.2ms**（~100× gap on heavy scenes）
- **Canvas 2D 首次加载快**：15ms vs WebGL 40ms
- **Hybrid 方案**：Canvas 2D 首屏 → WebGL 替换交互

**对 chronicle**：当前 Canvas 2D + quadtree 空间索引（`src/canvas/quadtree.ts`）已是正确架构。只有**节点数超 ~500** 时 zoom/pan 才感明显卡顿。主人节点少时无需升级。
URL: https://semisignal.com/a-look-at-2d-vs-webgl-canvas-performance/

### E3. tldraw SDK 内建多人协作
tldraw SDK 支持 thousands of objects + live cursors + 协同编辑 + cursor chat，React-based 每个 element 是 React component。

**对 chronicle**：**不适用**——chronicle 是主人自用，不需 multi-user infra。但 tldraw 的 React-component-per-element 架构值得借鉴：当前 chronicle 的 CanvasRenderer 直接 draw 到 Canvas 2D，节点复杂 UI（markdown、嵌套）实现成本高。
URL: https://tldraw.dev/

---

## 2. chronicle 在 2026 坐标系的位置

| 维度 | chronicle 现状 | 2026 SOTA (Heptabase / OmniCanvas) |
|-----|---------------|------------------------------------|
| 目标用户 | **主人自用** | 付费用户 |
| 定价 | 0（自用） | $5-10/月 |
| 渲染 | Canvas 2D + quadtree | Excalidraw engine / React-based |
| 同步 | Supabase 单用户跨设备 | Supabase 或自建 + 多人协作 |
| 内容单元 | 节点（title + content） | Card / Page / Tag / Backlink |
| Search | SearchBar 有 | Full-text + tag + backlink |
| Mobile | 5 天前加 touch support | Full responsive |

**Gap 分析**（仅对"主人自用体验"有意义的）：
1. 节点内容单元还是简单 text，没有 Heptabase 的 **markdown 渲染 + 嵌入 / backlink**
2. 没有 **daily notes** / 时间轴视图（Heptabase 核心差异化）
3. 没有 **tag / filter 视图** 叠加在画布上
4. mobile touch 刚加，手势（pinch-zoom、two-finger pan）验证程度未知

---

## 3. 3 条可操作方向

### A. UX 功能借鉴（推荐，2-4 天工作量）
**内容**：从 Heptabase 借 2 个低成本 UX：
1. ~~**Markdown 渲染节点内容**~~ — **已存在**，见 `src/components/EditorOverlay.tsx` 用 Tiptap + StarterKit 做富文本编辑 (headings / bold / italic / lists)，`node.content` 是 HTML 字符串。Turn 12 原 research 未读代码误判为 plain text，此处作废。
2. **Tag filter**（节点加 tags 字段 + Toolbar 加 tag chip 筛选，~1.5 天）
3. **Daily notes** 自动创建 today-node（开 app 时，~0.5 天）

**风险**：低。全是 UI 层，不改 canvas core 和 Tiptap editor。
**收益**：标签筛选让多 domain 节点（Learning/Projects/Health/Ideas）更易导航；daily notes 让 chronicle 变 "每日思考 + 知识沉淀" 复合工具。

### B. Canvas → Hybrid WebGL 升级（only if 节点 > 500）
**内容**：React Three Fiber 替换 CanvasRenderer，保留 Canvas 2D UI layer。
**门槛**：主人当前节点数未知。4 种子 → 估计实际 <100，WebGL 无必要。
**风险**：中。改动 canvas core，可能引入 regression。
**不推荐**：成本高收益小。

### C. Mobile 手势深化（touch support 续集）
**内容**：pinch-zoom / two-finger pan / long-press context menu。
**门槛**：5 天前已加 touch support，需主人实测哪些手势 missing。
**推荐**：等主人用移动设备几次后再决定。

### 不做
- **多人协作 / CRDT / Yjs** — chronicle 是主人自用，加这套显著增加 infra + bug 面积且无价值
- **AI 集成（auto-connect nodes）** — Heptabase/AFFiNE 已做，跟随模式，且无 differentiation
- **开源对外** — 主人无此表态，不应自作主张

---

## 4. 下一步命令（主人回来时）

**Min 30 分钟路径**（方向 A 的 daily notes，最小可行）：
```bash
cd "/Users/shaoq/Desktop/VScode Workspace/chronicle"
# 在 src/store/sync.ts 的 seedStarterNodes 逻辑旁加 ensureTodayNode()
# 检查 store 里是否有 today-YYYY-MM-DD node，没有就创建
# 在 CanvasApp mount 时调用 ensureTodayNode()
npm run dev
# 测试：打开 app 看是否自动多了今日节点
```

如果 daily notes 通过，继续 tag filter（需要改 schema 或在 content metadata 里加 tags）。

~~原推荐的 react-markdown~~ 作废（Tiptap 已在）。

---

## 5. 不是 research 的观察

**chronicle 是主人多项目里**：
- Signal-Map = 已部署生产（hdmap.live）
- TOEFL = 主人自用练习工具
- ai-text-detector = 等训练 + 可能商业化
- **chronicle = 主人自用知识管理**（和 TOEFL 同类但不同 domain）

前两类项目（生产 / 自用工具）已深挖数十 turn；ai-text-detector 今日推进到可执行 POC；**chronicle 是今日最少关注但可能对主人日常使用频率最高的项目**（如果主人用它做笔记）。值得阶段性优先级上调。

---

## Sources

- [Best Infinite Canvas Apps 2026 — OmniCanvas](https://omnicanvasnotes.com/blog/reviews/best-infinite-canvas-apps-2026/)
- [WebGL vs 2D Canvas — semi/signal](https://semisignal.com/a-look-at-2d-vs-webgl-canvas-performance/)
- [tldraw SDK](https://tldraw.dev/)
- [Supabase Realtime Multiplayer Edition](https://supabase.com/blog/supabase-realtime-multiplayer-general-availability)
- [Excalidraw vs tldraw comparison — Oreate AI](https://www.oreateai.com/blog/tldraw-vs-excalidraw-finding-your-digital-sketchpad-sweet-spot/60b6daa05d25787c2db0675d5f7d9471)
