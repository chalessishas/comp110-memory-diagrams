# CourseHub 2.0 设计简报 — 所有重写必须遵循

## 美学方向
水彩柔和 · 日系文具感 · Notion 的克制 + 更温暖
不是"企业 SaaS"，是"让人想坐下来学习的地方"

## 核心原则
1. **柔 > 硬**：圆角更大，阴影更淡，边框更轻或无边框
2. **疏 > 密**：留白充足，元素之间有呼吸空间
3. **静 > 闹**：低饱和色，不用纯黑/纯白，文字层级靠灰度而非粗细
4. **少 > 多**：每个组件只保留必要元素，去掉装饰性细节

## 具体样式规范

### 圆角
- 卡片/面板: 20-24px (更圆润)
- 按钮: 12px (pill 感但不完全胶囊)
- 输入框: 12px
- 标签/Badge: 8px
- 小元素 (进度条圆点): 999px (全圆)

### 边框
- 卡片: 不用 border，用极淡 shadow 代替
  `box-shadow: 0 1px 4px rgba(0,0,0,0.03), 0 2px 8px rgba(0,0,0,0.02)`
- 输入框: 1px solid var(--border)，focus 时 border-color 变 accent
- 按钮: primary 无边框，secondary 有淡边框
- 分割: 用 gap/margin 代替 hr/border-bottom

### 阴影
- 比 1.0 更轻: 所有 shadow 透明度减半
- hover 不增加阴影（改为 translateY(-2px) 微浮起）
- 暗色主题: 无 shadow（用 border 替代层级感）

### 排版
- 标题: font-weight 600 (不用 700)，适当增大 letter-spacing
- 正文: font-weight 400, 16px, line-height 1.6
- 辅助: font-weight 400, 13px, var(--text-muted)
- 减少 UPPERCASE + letter-spacing（只在极小标签处使用）

### 按钮
- Primary: 纯色背景 (accent), 白字, 12px radius, 无边框, hover 稍深 + 微浮
- Secondary: bg-surface, border var(--border), 12px radius, hover bg-muted
- Ghost: 无背景无边框, hover bg-muted
- 大小: sm=32px / md=40px / lg=48px
- 间距: padding 0.5rem 1.25rem (横向更宽一点)

### 卡片 (.ui-panel)
- 背景: var(--bg-surface)
- 边框: 无 (用 shadow 替代)
- 圆角: 20px
- 内边距: 24px (p-6)
- hover: translateY(-2px), shadow 略增

### 标签 (.ui-badge)
- 背景: var(--bg-muted)
- 边框: 无 (去掉 border)
- 圆角: 8px
- 字号: 11px
- 字重: 500 (不用 600)

### 进度条
- 高度: 6px (从 4px 增加, 更柔和的比例)
- 圆角: 999px
- 轨道: var(--bg-muted)
- 填充: var(--accent)

### 输入框
- 背景: var(--bg-surface) (不用 bg-muted, 更干净)
- 边框: 1px solid var(--border)
- 圆角: 12px
- focus: border accent + 柔和外发光 0 0 0 3px var(--accent-light)

### 空状态
- 居中，大量留白
- 图标用 var(--text-muted), 48px
- 文案温和
- 不用 dashed border（太技术感），用纯背景 + 小图标

### 导航 (Sidebar)
- 顶部固定导航栏
- 毛玻璃背景
- Logo 左侧, 导航项居中, 用户操作右侧
- 活跃项: bg accent-light + accent 文字
- 移动端: 汉堡菜单展开

## 组件重写规则

1. **保留所有 props 接口不变** — 不改 TypeScript interface
2. **保留所有 state/effect/事件处理逻辑** — 不改业务代码
3. **只重写 return 语句中的 JSX** — 新的标签结构 + className + style
4. **用 Tailwind 类做布局** — flex, grid, gap, p-*, m-*, rounded-*
5. **用 CSS 变量做颜色** — var(--accent), var(--text-primary)
6. **不添加新依赖** — 只用 lucide-react 图标
7. **不添加新 state** — 除非是纯 UI 状态 (如 hover/expand)

## 禁止事项
- 禁止硬编码颜色 (#xxx, rgba 纯数字)
- 禁止 border 做卡片边界 (用 shadow)
- 禁止 font-weight 700 (最重只到 600)
- 禁止 uppercase + letter-spacing > 0.06em
- 禁止 80px+ 的 padding (最大 48px)
- 禁止用 shadow 做装饰 (shadow 只表示层级)
