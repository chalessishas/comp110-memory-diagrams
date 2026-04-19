# COMP110 Phase 2 Implementation Starter · Next.js 15 + Tailwind v4

**时间**: 2026-04-18 22:15
**目标读者**: DeepSeek-Coder / Cursor
**范围**: 五页骨架 + AI TA UI shell（无后端集成）

---

## 1. 依赖安装（精确版本）

```bash
npm create next-app@15 --typescript --tailwind comp110-26s
npm install tailwindcss@4.0 @tailwindcss/postcss@4.0
```

**删除**: `tailwind.config.ts`（v4 不使用）
**保留**: `package.json`, `tsconfig.json`, `next.config.ts`

---

## 2. Tailwind v4 配置变更（相比 v3）

### globals.css 完全替换

```css
@import "tailwindcss";

@theme {
  --color-brand: #F5B700;
  --color-brand-soft: #FFF5D6;
  --color-bg: #FAF8F3;
  --color-bg-elev: #FFFFFF;
  --color-ink: #171717;
  --color-ink-2: #4B4B4B;
  --color-ink-3: #8B8B8B;
  --color-line: #E7E3DA;
  --color-accent: #0E6BA8;
  --color-danger: #B23A48;
  --color-ok: #2E7D5B;
  --radius-sm: 10px;
  --radius-md: 14px;
  --radius-pill: 999px;
}
```

### postcss.config.js

```js
export default {
  plugins: { "@tailwindcss/postcss": {} },
};
```

### 关键破坏性变更

| v3 | v4 | 说明 |
|----|----|----|
| `bg-gradient-to-r` | `bg-linear-to-r` | CSS 原生渐变命名 |
| `border`（默认 currentColor）| `border`（默认 `--color-gray-200`）| 边框颜色默认值变了 |
| `tailwind.config.ts` | CSS `@theme {}` | 配置文件废弃 |

---

## 3. Next.js 15 目录结构

```
app/
├── layout.tsx           # root: <html>, <body>, providers
├── page.tsx             # / agenda
├── resources/page.tsx
├── support/page.tsx
├── syllabus/page.tsx
└── team110/page.tsx

components/
├── layout/TopNav.tsx    # sticky header · 5 pills + icons
├── layout/SideBar.tsx   # 280px right column
├── agenda/AgendaFilter.tsx   # All/Lectures/Exercises chip row ('use client')
├── agenda/ViewToggle.tsx     # Timeline/Grid/Week
├── agenda/DayGroup.tsx       # date + items grid
├── ai-ta/TAButton.tsx   # FAB with pulse ('use client')
├── ai-ta/TAPanel.tsx    # modal 380×560
└── badges/BadgeIcon.tsx

lib/
├── constants.ts         # agenda data, color maps
├── types.ts             # BadgeType, AgendaItem, etc.
└── cn.ts                # clsx wrapper
```

---

## 4. Next.js 15 注意事项

1. **Server Components by default** — `page.tsx` / `layout.tsx` 是 Server Component；有 `useState` / `onClick` 的组件必须加 `'use client'`
2. **无 getServerSideProps** — 在 Server Component 内直接 `fetch()` 或 `import` 静态 JSON
3. **Dark mode** — 用 `prefers-color-scheme` media query，不做 toggle（Phase 2 无需 JS 切换）
4. **Vercel 自动识别** — 无需额外配置，`git push` 即部署

---

## 5. 三个最高风险点

### 风险 1：Tailwind v4 渐变命名
**问题**: mockup.html 里用了 `gradient-to-r`，v4 改名了
**行动**: 全局搜 `gradient-to-` → 替换为 `linear-to-`
**验收**: Hero 进度圆环和渐变背景无黑色 fallback

### 风险 2：AI TA Panel 的 z-index
**问题**: FAB z-50、panel z-40 → panel 在 FAB 后面；侧边栏 920px 断点与模态框重叠
**行动**:
```
FAB: z-50 → panel: z-60 → overlay: z-50
useEffect(() => { document.body.style.overflow = 'hidden' })
```
**验收**: 移动端 + 桌面端均正常显示

### 风险 3：Agenda Filter 的 Server/Client 边界
**问题**: filter 状态需要 `useState`，但 `page.tsx` 是 Server Component
**行动**: `AgendaContainer`（server，fetch data）→ `<AgendaClient items={agenda} />`（client，持有 filter state）
**验收**: 切换 filter 不触发全页刷新

---

## 6. Badge 颜色映射

```typescript
const badgeColors = {
  CL: { bg: 'bg-brand',       text: 'text-white' },  // 黄
  LS: { bg: 'bg-accent',      text: 'text-white' },  // 蓝
  EX: { bg: 'bg-ok',          text: 'text-white' },  // 绿
  QZ: { bg: 'bg-danger',      text: 'text-white' },  // 红
  CQ: { bg: 'bg-purple-600',  text: 'text-white' },  // 紫
  FN: { bg: 'bg-gray-900',    text: 'text-brand' },  // 黑+金
};
```

---

## 7. 执行清单

- [ ] 初始化 Next.js 15 + Tailwind v4 骨架
- [ ] 迁移 mockup.html card 样式 → Tailwind utilities
- [ ] 构建 TopNav / SideBar / Footer 布局组件
- [ ] 实现 5 页路由结构（占位内容）
- [ ] AgendaFilter + ViewToggle UI
- [ ] TAButton FAB + TAPanel 模态框（mock chat，无 API）
- [ ] 测试 dark mode + 920px 断点响应式
- [ ] 验证 v4 渐变 utilities 构建无报错
- [ ] 推到 `comp110-26s` repo，`/docs` 保留 Phase 1 mockup 作参考

**Phase 3 起点**: 骨架通过视觉 QA 后，迁移 mockup.html 内容到 agenda.json schema。

---

## 来源

- [Tailwind CSS v4 Upgrade Guide](https://tailwindcss.com/docs/upgrade-guide)
- [Next.js 15 App Router Best Practices 2025](https://medium.com/better-dev-nextjs-react/inside-the-app-router-best-practices-for-next-js-file-and-directory-structure-2025-edition-ed6bc14a8da3)
