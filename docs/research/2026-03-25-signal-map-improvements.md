# Signal-Map (hdmap.live) Improvement Research

**Date:** 2026-03-25
**Context:** Signal-Map 刚完成电台功能部署（DeepSeek 文案 + DashScope TTS + 20 首 CC0 音乐），运行在 Vercel Hobby plan。已知问题：Vercel Hobby cron 限制（每日一次）、announce API ~1MB base64 无缓存、移动端未优化、无自动化测试。

---

## 1. Vercel Hobby Plan Cron 限制绕过方案

### 核心发现

- **Vercel Hobby plan 限制：** 最多 2 个 cron job，且只能每日执行一次。尝试设置更高频率会导致部署失败。当前 `vercel.json` 配置 `"0 6 * * *"` 已是 Hobby plan 上限。
- **GitHub Actions 免费方案：** 可用 `schedule` 事件 + cron 表达式 `0 * * * *` 实现每小时触发，免费额度对公开仓库无限制、私有仓库 2000 分钟/月。缺点是高负载时段（整点）可能延迟数分钟，不保证精确执行。
- **Upstash QStash 免费方案：** 免费 tier 500 消息/天（~15,000/月），支持 cron 表达式 HTTP 触发。已有 Vercel Marketplace 集成，一键配置。对 Signal-Map 的 ingest（每小时一次 = 24 次/天）绰绰有余。

### 对 Signal-Map 的具体建议

**推荐方案：GitHub Actions（零成本、最简单）**

1. 创建 `.github/workflows/ingest-cron.yml`：
   ```yaml
   name: Hourly Ingest
   on:
     schedule:
       - cron: '15 * * * *'   # 避开整点高峰
     workflow_dispatch:         # 手动触发备用
   jobs:
     trigger:
       runs-on: ubuntu-latest
       steps:
         - run: |
             curl -s -X GET \
               "https://hdmap.live/api/cron/ingest?token=${{ secrets.ADMIN_TOKEN }}" \
               --max-time 90
   ```
2. 在 GitHub repo Settings > Secrets 中添加 `ADMIN_TOKEN`
3. `vercel.json` 中的 cron 配置可保留作为每日 fallback，或移除以简化

**备选方案：Upstash QStash**
- 适合需要更精确调度或需要重试机制的场景
- 通过 Vercel Marketplace 一键安装，用 `Upstash-Cron: 0 * * * *` header 配置
- 免费 tier 完全覆盖需求

**不推荐：cron-job.org 等第三方**
- 需要公开暴露 API endpoint（已有 token 保护所以可行，但增加了外部依赖）
- 可靠性不如 GitHub/Upstash

### Sources
- [Vercel Cron Jobs Usage & Pricing](https://vercel.com/docs/cron-jobs/usage-and-pricing)
- [Vercel Hobby Plan](https://vercel.com/docs/plans/hobby)
- [Free Cron Jobs with GitHub Actions](https://dev.to/anshuman_bhardwaj/free-cron-jobs-with-github-actions-31d6)
- [Upstash QStash Periodic Data Updates](https://upstash.com/blog/qstash-periodic-data-updates)
- [GitHub Actions Schedule Events](https://docs.github.com/actions/learn-github-actions/events-that-trigger-workflows)

---

## 2. Next.js 15 音频缓存最佳实践

### 核心发现

- **当前问题：** `/api/radio/announce` 每次请求都调用 DeepSeek + DashScope TTS，返回 ~1MB base64 JSON。`export const dynamic = "force-dynamic"` 完全禁用了缓存。同一时段内容不变，但每个用户都触发全量生成。
- **`unstable_cache` 方案：** 可将 DB 查询 + DeepSeek + TTS 合并为一个缓存函数，设置 `revalidate: 600`（10 分钟），首次请求后所有后续请求直接命中缓存。`unstable_cache` 不能直接在 Route Handler 体内使用，需抽取为独立函数。
- **`use cache` 指令（Next.js 15 新特性）：** 更现代的方案，但同样不能直接用在 Route Handler body 中，需要包装为 helper 函数。需要在 `next.config.ts` 中启用 `cacheComponents` 实验特性。

### 对 Signal-Map 的具体建议

**推荐方案：`unstable_cache` 包装（成熟、无需实验特性）**

```typescript
// src/lib/radio.ts 新增
import { unstable_cache } from "next/cache";

export const getCachedAnnouncement = unstable_cache(
  async (period: Period) => {
    // 1. 查询 upcoming events
    // 2. generateAnnouncementText(period, eventsDescription)
    // 3. synthesizeSpeech(text)
    // 4. return { period, text, audio }
  },
  ["radio-announce"],           // cache key prefix
  { revalidate: 600, tags: ["radio-announce"] }  // 10 分钟
);
```

Route Handler 简化为：
```typescript
export async function GET(req: NextRequest) {
  const period = validatePeriod(req) || getCurrentPeriod();
  const result = await getCachedAnnouncement(period);
  return NextResponse.json(result);
}
```

**额外优化：**
- 移除 `export const dynamic = "force-dynamic"`，让 Next.js 使用默认缓存行为
- 考虑将 base64 audio 改为 Supabase Storage URL（一次生成、存储、返回 URL），将响应体从 ~1MB 减少到 <1KB
- 设置 `Cache-Control` header：`s-maxage=600, stale-while-revalidate=300`，利用 Vercel Edge CDN 缓存

**投入产出比最高的改动：** 先加 `unstable_cache`（30 分钟工作量），可立即将 API 成本和延迟降低 95%+。Supabase Storage 方案可作为后续优化。

### Sources
- [Next.js unstable_cache API](https://nextjs.org/docs/app/api-reference/functions/unstable_cache)
- [Next.js use cache Directive](https://nextjs.org/docs/app/api-reference/directives/use-cache)
- [Next.js Caching Guide](https://nextjs.org/docs/app/getting-started/caching-and-revalidating)
- [Next.js Route Handlers](https://nextjs.org/docs/app/getting-started/route-handlers)

---

## 3. Leaflet 移动端优化

### 核心发现

- **Viewport 配置是第一步：** 没有正确的 viewport meta tag，移动浏览器会延迟 300ms 响应触摸事件。Leaflet 官方推荐 `<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />`。
- **触摸事件问题：** Leaflet CSS 默认设置 `.leaflet-container { touch-action: none; }`，在移动端可能导致页面滚动问题。Leaflet 2.0 alpha 已切换到 Pointer Events API，但 react-leaflet 仍绑定 Leaflet 1.x。
- **性能关键：** Signal-Map 有 1,236 个 GeoJSON polygons。react-leaflet 的 GeoJSON 组件在大数据量时比原生 Leaflet GeoJSON 慢 10 倍+。应使用 Leaflet 原生 canvas renderer 或在 viewport 外不渲染。

### 对 Signal-Map 的具体建议

**第一优先级：Viewport + CSS（15 分钟）**

1. 确认 `layout.tsx` 中有正确的 viewport meta tag（Next.js 15 用 `metadata.viewport` 配置）
2. 添加全局 CSS：
   ```css
   /* 消除移动端 tap delay */
   a, button, [role="button"] { touch-action: manipulation; }

   /* 移动端地图全屏 */
   @media (max-width: 768px) {
     .map-container { height: 100dvh; width: 100vw; }
     .sidebar { position: fixed; bottom: 0; height: 40vh; z-index: 1000; }
   }
   ```

**第二优先级：响应式布局重构（2-3 小时）**

- 桌面端：左侧 sidebar（360px）+ 右侧地图
- 移动端：全屏地图 + 底部抽屉式面板（可拖拽展开/收起）
- 参考 Google Maps 移动端交互模式：底部 sheet、上滑展开详情
- 使用 CSS `@media (max-width: 768px)` 切换布局，不需要 JS 检测

**第三优先级：GeoJSON 渲染优化（1-2 小时）**

- 对 1,236 个 polygons 使用 Leaflet canvas renderer：`<MapContainer preferCanvas={true}>`
- 实现 viewport-based rendering：只渲染当前可视区域内的建筑多边形
- 使用 `useMemo` 缓存 GeoJSON 数据转换，避免每次 render 重新计算

### Sources
- [Leaflet on Mobile](https://leafletjs.com/examples/mobile/)
- [Leaflet Touch Events Issue #5646](https://github.com/Leaflet/Leaflet/issues/5646)
- [Leaflet Responsive Sidebar](https://github.com/Turbo87/leaflet-sidebar)
- [Optimizing Leaflet Performance](https://medium.com/@silvajohnny777/optimizing-leaflet-performance-with-a-large-number-of-markers-0dea18c2ec99)
- [Chrome 300ms Tap Delay](https://developer.chrome.com/blog/300ms-tap-delay-gone-away)

---

## 4. 校园地图产品增长策略

### 核心发现

- **UNC Hello Heels 案例：** UNC 官方 Hello Heels app 在学生主导的重新设计后，从每周 10,000 PV / 6,000 用户暴涨到 90,000 PV / 37,000 用户。关键成功因素：(1) 在新生 orientation 期间推广，(2) 学生参与设计决策（advisory boards + focus groups），(3) 实用功能驱动（数字 One Card、公交、校园地图）。
- **HeelLife 是核心渠道：** UNC 有 822+ 学生组织在 HeelLife 平台上活跃。Student Life & Leadership (@sllunc) Instagram 有 4,683 粉丝。Daily Tar Heel 是校园媒体主渠道。
- **学生获取路径：** 学生通过 Instagram、Reddit (r/UNC)、orientation 活动、口碑四个主要渠道发现校园应用。98% 的 Hello Heels 用户表示会继续使用——关键是首次体验的「啊哈时刻」。

### 对 Signal-Map 的具体建议

**Phase 1：种子用户（目标 100 用户）**

1. **App Team Carolina 合作**：UNC 有官方学生开发团队 [App Team Carolina](https://appteamcarolina.com/)，联系他们展示 hdmap.live，寻求技术反馈 + 社交传播
2. **r/UNC subreddit 发帖**：标题类似 "I built a live campus event map for UNC — check out hdmap.live"，展示实际截图，邀请反馈
3. **Instagram / Daily Tar Heel**：联系 @sllunc 和 Daily Tar Heel，看能否做一个 "学生开发者" 故事

**Phase 2：产品-渠道匹配（目标 1,000 用户）**

1. **Orientation 推广**：联系 Student Affairs 将 hdmap.live 加入新生 orientation 资源列表（Hello Heels 的成功路径）
2. **HeelLife 事件聚合价值**：hdmap.live 已经抓取 HeelLife 数据，可以作为 "更好的 HeelLife 地图视图" 来定位——学生组织发布活动到 HeelLife，hdmap.live 自动展示在地图上
3. **CLE 学分追踪是杀手功能**：很多学生需要追踪 CLE（Cultural/Experiential Learning）学分，如果 hdmap.live 能清晰显示哪些活动给 CLE 学分，这就是独特的用户获取钩子

**Phase 3：增长飞轮**

- 用户提交事件 → 更多内容 → 更多用户 → 更多提交
- 电台功能是差异化亮点（没有竞品有校园电台），适合口碑传播
- 考虑 PWA 化 + "Add to Home Screen" 提示，降低安装门槛

### Sources
- [UNC Hello Heels App Drives Student Engagement](https://www.insidehighered.com/news/student-success/college-experience/2026/01/14/uncs-app-redesign-drives-student-engagement)
- [CarolinaGO Mobile App](https://its.unc.edu/project/carolinago-mobile-app-created-for-unc-chapel-hill-by-students/)
- [App Team Carolina](https://appteamcarolina.com/)
- [HeelLife Organizations](https://heellife.unc.edu/organizations)
- [UNC Student Life & Leadership Instagram](https://www.instagram.com/sllunc/)

---

## 优先级排序

| 优先级 | 改动 | 工时 | 影响 |
|--------|------|------|------|
| P0 | `unstable_cache` 包装 announce API | 30 min | 消除 95% 重复 API 调用，省钱省延迟 |
| P0 | GitHub Actions hourly cron | 20 min | 数据新鲜度从 24h → 1h |
| P1 | Viewport meta + touch-action CSS | 15 min | 移动端基本可用 |
| P1 | 移动端响应式布局 | 2-3 hr | 移动端用户体验质变 |
| P2 | r/UNC + App Team Carolina 推广 | 1 hr | 种子用户获取 |
| P2 | GeoJSON canvas renderer | 1 hr | 移动端性能优化 |
| P3 | Supabase Storage 存储 TTS 音频 | 2 hr | 彻底解决 base64 传输问题 |
| P3 | Orientation 推广计划 | ongoing | 长期用户增长 |
