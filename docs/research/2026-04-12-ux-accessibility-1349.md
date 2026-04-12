# Research: UX Retention + Accessibility — 2026-04-12 13:49

## 1. TOEFL App UX — 留存与激励

### 已实装（✅）
- 连续练习记录（streak 计数，study plan 标记已完成日）
- 个人最佳徽章（WritingResult ★ delta）
- 自适应练习（BuildSentence 错题池）
- 实时进度（Home dashboard、Progress sparkline）

### 未实装 — 高价值

**① 每日提醒通知**（高留存杠杆）
- Duolingo 核心留存驱动：连续日提醒 + streak 中断恐惧
- 纯前端方案：`Notification.requestPermission()` + `ServiceWorker` 定时推送
- 需要 HTTPS（即部署后才可实现）

**② 2-5 分钟微练习模式**（降低进入摩擦）
- 当前最短练习 = 7 分钟 BuildSentence，对疲惫用户门槛高
- 建议：Home 页增加"Quick Drill"入口（随机 3 道 BuildSentence 题，无计时）
- 实现复杂度：低（复用现有组件，SESSION_SIZE=3 参数化）

**③ 词汇 Flashcard 模式**（Notebook 生词本扩展）
- 现有生词本已有 word + meaning
- Anki 式翻转卡片（点击 word → 显示 meaning）几乎零改动
- 用 FSRS 算法追踪复习间隔是完整实现，但纯翻转卡片 30min 可完成

---

## 2. React SPA 无障碍（Accessibility）

### 当前缺口（未实装）

| 问题 | 影响 | 修复方案 | 难度 |
|------|------|---------|------|
| 路由切换无焦点管理 | 键盘用户切换页面后焦点丢失 | `useEffect` + `ref.focus()` on route change | S |
| Word-chip 拖拽无键盘等价 | 无法键盘操作 BuildSentence | React Aria `useDragAndDrop` 或点击已实装（实际是点击而非拖拽） | M |
| 无 skip link | 键盘用户每页须 tab 过整个侧边栏 | 首个 focusable 元素设 "Skip to main" | S |
| 模态框无 focus trap | 确认弹窗（Submit?）可 tab 出去 | `aria-modal + focus trap` | S |
| 无 `aria-live` 分数播报 | 屏幕阅读器无法获得提交结果 | `aria-live="polite"` on score | S |

### 关键发现
- BuildSentence 实际是**点击交互**（非拖拽），已天然支持键盘（click = Enter/Space on button）
- 最高价值修复：`aria-live` 分数播报 + 路由焦点管理（各约 10 行代码）

---

## 行动优先级（下一自主任务候选）

| 优先级 | 任务 | 工作量 |
|--------|------|--------|
| 🔴 用户决策 | 部署 Vercel（vercel.json 已就绪，需账号）| 用户操作 |
| 🟡 可自主 | Quick Drill 模式（Home 3 题入口）| 1h |
| 🟡 可自主 | Notebook flashcard 翻转 | 30min |
| 🟢 可自主 | aria-live 分数播报 + skip link | 30min |
| 🟢 可自主 | 路由切换焦点管理 | 20min |

**Sources**: react-aria.adobe.com/dnd, mintlify.com React Router Accessibility,
medium.com (Suresh Kumar — Focus Traps & ARIA Live Regions),
allaccessible.org WCAG 2.2 AA React guide
