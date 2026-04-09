# CourseHub P0 修复：Upstash Redis 替换 in-memory Rate Limiter

> 调研日期: 2026-04-09 13:03  
> 触发: Research Loop（第四次，每小时）  
> 依据: 2026-04-09-rate-limit-thinking-mode.md 中记录的 P0 漏洞

---

## 背景

`src/lib/rate-limit.ts` 用 `Map` 实现限流，在 Vercel Serverless 上完全失效（多实例不共享内存）。本报告提供具体实施方案。

---

## Vercel KV 现状（2025 年 12 月更新）

**重要：Vercel KV 已于 2024 年 12 月迁移合并到 Upstash Redis。**  
现在不再有单独的 "Vercel KV" 产品——Vercel Storage 中的 KV 就是 Upstash Redis 的封装。

两种接入方式：
1. **直接 Upstash**（推荐）：在 [upstash.com](https://upstash.com) 创建免费 Redis 数据库，获取 REST URL + Token
2. **Vercel Marketplace**：通过 Vercel Dashboard → Storage 添加 Upstash，环境变量自动填充

**定价**：免费套餐 10,000 命令/天，付费 $0.2/100K 命令。MVP 阶段免费套餐完全够用。

---

## 具体实施步骤

### Step 1: 安装依赖

```bash
npm install @upstash/ratelimit @upstash/redis
```

### Step 2: 替换 `src/lib/rate-limit.ts`

**当前（失效）实现**：
```ts
const requests = new Map<string, { count: number; resetAt: number }>();

export function checkRateLimit(key: string, maxRequests: number = 5, windowMs: number = 60_000): boolean {
  // in-memory only — broken in serverless
}
```

**替换为**：
```ts
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

// Sliding window: 5 requests per 60 seconds per key
const defaultLimiter = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(5, "60 s"),
  analytics: true, // tracks usage in Upstash dashboard
});

// Generate-specific: 1 request per 30s (dedup guard)
const generateLimiter = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(1, "30 s"),
});

export async function checkRateLimit(
  key: string,
  maxRequests: number = 5,
  windowMs: number = 60_000
): Promise<boolean> {
  // Use generate-specific limiter for generate keys
  const limiter = key.startsWith("generate:") ? generateLimiter : defaultLimiter;
  const { success } = await limiter.limit(key);
  return success;
}
```

### Step 3: 更新所有调用点（同步 → async）

当前所有 API route 中的调用是同步的：
```ts
if (!checkRateLimit(`generate:${id}`, 1, 30_000)) { ... }
```

改为 await：
```ts
if (!await checkRateLimit(`generate:${id}`, 1, 30_000)) { ... }
```

**需要修改的文件**（grep 结果）：
- `src/app/api/courses/[id]/generate/route.ts:42`
- 其他使用 `checkRateLimit` 的 routes（grep 全文确认）

### Step 4: 添加环境变量

**本地 `.env.local`**：
```env
UPSTASH_REDIS_REST_URL=https://your-db.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-token-here
```

**Vercel Dashboard**：Project Settings → Environment Variables → 添加上述两个变量到 Production + Preview

---

## 为什么选 Sliding Window 而非 Fixed Window？

- **Fixed Window**：在窗口边界处可能被突发请求打穿（如在 0:59 和 1:01 各发 5 个请求，实际 2 秒内发了 10 个）
- **Sliding Window**：任意连续 60s 内不超过 5 个请求，更精确
- `@upstash/ratelimit` 原生支持，无需 Lua 脚本

---

## 测试方法

```bash
# 本地快速验证（需要 .env.local 有 UPSTASH_REDIS_REST_URL + TOKEN）
# 连续快速调用同一 API，第 6 次应返回 429
for i in {1..7}; do
  curl -X POST http://localhost:3000/api/courses/test-id/generate \
    -H "Content-Type: application/json" \
    --cookie "..." && echo "Request $i: OK" || echo "Request $i: BLOCKED"
done
```

---

## 完整 P0-P2 修复优先级

| # | 风险 | 修复方案 | 前置条件 |
|---|------|--------|--------|
| P0 | Rate limit 失效 | 本文档 — Upstash 替换 | 创建 Upstash 账号 |
| P0 | DashScope 端点区域 | 确认 Key 来源（大陆 vs 国际版）| 用户确认 |
| P1 | AbortSignal 全部注释 | 改为 `AbortSignal.timeout(55000)` | 无 |
| P2 | thinking mode token 浪费 | `extraBody: { enable_thinking: false }` | 本地测试后 |

---

## Sources

- [Upstash Redis 官方文档](https://upstash.com/docs/redis/overall/getstarted)
- [Vercel Redis 迁移公告（2024-12）](https://vercel.com/docs/redis)
- [upstash/ratelimit-js GitHub](https://github.com/upstash/ratelimit-js)
- [Vercel + Upstash Rate Limiting 模板](https://vercel.com/templates/next.js/ratelimit-with-upstash-redis)
