# CourseHub Rate Limiter Migration — 执行报告

> 时间: 2026-04-09 14:04  
> 类型: Research Loop → 自主执行（无需用户介入）

---

## 已完成操作

### 1. `src/lib/rate-limit.ts` — 重写为 Upstash + 内存 fallback

**设计思路：**
- 本地开发：无 `UPSTASH_REDIS_REST_URL` / `UPSTASH_REDIS_REST_TOKEN` 时，自动退回 in-memory（开发体验不变）
- 生产环境：检测到 env 变量后，懒加载 `@upstash/ratelimit` + `@upstash/redis`，使用 sliding window
- `checkRateLimit` 签名由 `() => boolean` 改为 `async () => Promise<boolean>`（向后兼容，只需在调用处加 `await`）

### 2. 4 个 API 路由加 `await`

| 路由 | 改动 |
|------|------|
| `src/app/api/parse/route.ts` | `!checkRateLimit(...)` → `!await checkRateLimit(...)` |
| `src/app/api/courses/[id]/chat/route.ts` | 同上 |
| `src/app/api/courses/[id]/generate/route.ts` | 同上 |
| `src/app/api/preview/learning/route.ts` | 同上 |

### 3. `course-hub/vercel.json` — 新建

```json
{ "regions": ["hnd1"] }
```
将 Vercel Function 区域从 `iad1`（美东，→DashScope 延迟 500ms-2s）改为 `hnd1`（日本，→DashScope 延迟 50-100ms）。

### 4. Upstash 包已安装

`@upstash/ratelimit` + `@upstash/redis` 已 `npm install`，`package.json` 已更新。

---

## 用户仍需完成的操作

**在 Vercel 环境变量中添加（生产限流才能生效）：**

| 变量 | 来源 |
|------|------|
| `UPSTASH_REDIS_REST_URL` | [upstash.com](https://upstash.com) 免费 Redis 数据库 → REST API URL |
| `UPSTASH_REDIS_REST_TOKEN` | 同上 → REST API Token |

免费套餐：10,000 命令/天，完全足够 MVP 阶段。

---

## TypeScript 验证

`npx tsc --noEmit` → 0 错误。

---

## 遗留决策（用户需确认）

1. **Vercel Pro Plan** — AI 路由的 `maxDuration = 60` 在 Hobby plan 会被截断，必须升级
2. **Upstash 账号** — 需注册后获取 env 变量（5 分钟可完成）
3. **Qwen thinking mode** — `enable_thinking: false` 可节省 token，但效果未测试
4. **Supabase Auth 回调 URL** — 部署前需在 Supabase 控制台添加 `https://*.vercel.app/**`
