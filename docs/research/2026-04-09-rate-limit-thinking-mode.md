# CourseHub 两个新风险：无效限流 + 思维链冗余 token

> 调研日期: 2026-04-09 12:04  
> 触发: Research Loop（第三次，每小时）  
> 依据上一份研究（2026-04-09-dashscope-abort-vercel-risks.md）

---

## 风险 3：`rate-limit.ts` 在 Vercel 上完全失效（P0 安全漏洞）

### 现状

`src/lib/rate-limit.ts`（全部代码）：

```ts
const requests = new Map<string, { count: number; resetAt: number }>();

export function checkRateLimit(key: string, maxRequests: number = 5, windowMs: number = 60_000): boolean {
  // ...in-memory logic
}
```

### 根本问题

Vercel Serverless Function 是**无状态**的：每次冷启动都是全新进程，并发请求可能命中不同的实例。**Module-scope `Map` 完全不会在实例之间共享。**

结果：
- 用户每秒发 100 次请求，每次都命中一个新实例 → rate limit 永远不触发
- AI API 费用无上限，任何人可无限消耗 DashScope 配额
- 这是部署后最先暴露的生产安全问题之一

### 验证方式

打开 DevTools → 快速连续点击"生成"按钮 → 检查 network tab，应该没有 429 响应。

### 修复方案

**推荐：Upstash Redis + `@upstash/ratelimit`**

Upstash 提供 HTTP-based Redis，专为 Vercel Serverless/Edge 设计，免费套餐 10,000 req/day，够 MVP 使用。

```bash
npm install @upstash/ratelimit @upstash/redis
```

```ts
// src/lib/rate-limit.ts（替换）
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

const ratelimit = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(5, "60 s"),
});

export async function checkRateLimit(key: string): Promise<boolean> {
  const { success } = await ratelimit.limit(key);
  return success;
}
```

**环境变量**（Vercel Dashboard 新增两个）：
- `UPSTASH_REDIS_REST_URL`
- `UPSTASH_REDIS_REST_TOKEN`

注意：现有调用点需从同步改为 `await`（所有 API routes 里的 `checkRateLimit()` 调用前加 `await`）。

**备选（0 依赖）：Vercel KV**  
Vercel 自带 KV（底层也是 Upstash），可在 Storage tab 直接创建，通过 `@vercel/kv` 使用。

---

## 风险 4：qwen3.5-plus 思维链 token 无谓消耗（P2 成本优化）

### 现状

`src/lib/ai.ts` 第 22-24 行：

```ts
export function stripThinkBlocks(text: string): string {
  return text.replace(/<think>[\s\S]*?<\/think>/g, "").trim();
}
```

qwen3.5-plus 是混合思维模型，默认在输出中插入 `<think>...</think>` 块（思维链）。问题：

1. **Token 浪费**：思维链 token 被计费（输出价格 $1.56/M），JSON 生成任务完全不需要扩展推理
2. **延迟增加**：思维链可长达几百 token，增加首 token 延迟
3. **JSON 腐坏风险**：如 `extractJSON()` 正则对特殊思维链内容有边缘情况

### 解决方案

通过 `extra_body` 传入 `enable_thinking: false`，对应 Alibaba Cloud 文档 [deep-thinking](https://www.alibabacloud.com/help/en/model-studio/deep-thinking) 中的 hybrid mode 参数。

**AI SDK (`@ai-sdk/openai`) 写法**：

```ts
// 在每个 generateText 调用中添加：
const { text } = await generateText({
  model: textModel,
  messages: [...],
  // Disable thinking mode: saves tokens + reduces latency
  // qwen3.5-plus is a hybrid model — thinking is unnecessary for JSON generation
  experimental_providerMetadata: {
    openai: {
      extra_body: {
        enable_thinking: false,
      },
    },
  },
});
```

或者在模型初始化时全局禁用（更简洁）：

```ts
const textModel = qwen("qwen3.5-plus", {
  // Disable thinking mode globally for this model instance
  // Required for JSON tasks: avoids <think> block corruption + saves output tokens
  extraBody: { enable_thinking: false },
});
```

### 已知风险

- **agno issue #4290**：有报告称 DashScope 上 `enable_thinking=False` 在部分情况下不生效，仍返回 `<think>` 块。如果禁用后仍出现 `<think>` 内容，保留 `stripThinkBlocks` 作为防御性后备。
- **模型版本依赖**：`qwen3.5-plus` 是别名，会随 Alibaba 更新指向新版本，`enable_thinking` 行为可能随版本变化。

### 建议

先在本地测试一个 pipeline（如 `generateStudyTasks`）加上 `enable_thinking: false`，观察：
1. 输出是否还含 `<think>` 块
2. 响应时间是否缩短
3. JSON 是否完整

---

## 风险汇总（4 个已记录风险）

| # | 风险 | 优先级 | 是否阻断上线 |
|---|------|--------|------------|
| 1 | DashScope 端点区域 vs API Key 不匹配 | P0 | 取决于 Key 来源 |
| 2 | AbortSignal 全部注释 → 函数静默挂起 | P1 | 否，但会产生费用 |
| 3 | `rate-limit.ts` 在 Vercel 上完全失效 | P0 | 否，但会产生安全漏洞 |
| 4 | qwen3.5-plus 思维链 token 浪费 | P2 | 否 |

---

## 行动优先级

1. **立即（上线前）**：确认 DashScope Key 来源 → 选择正确端点
2. **上线前**：把 `rate-limit.ts` 换成 Upstash（需要用户创建 Upstash 账号 + 获取 token）
3. **上线后 Week 1**：恢复 AbortSignal（改为 `AbortSignal.timeout(55000)`，根因是 DashScope 延迟高）
4. **可选**：测试 `enable_thinking: false`，若有效则删除 `stripThinkBlocks` 逻辑

---

## Sources

- [Upstash Ratelimit for Vercel](https://upstash.com/blog/edge-rate-limiting)
- [Vercel template: ratelimit-with-upstash-redis](https://vercel.com/templates/next.js/ratelimit-with-upstash-redis)
- [Alibaba Cloud: deep thinking models](https://www.alibabacloud.com/help/en/model-studio/deep-thinking)
- [DashScope enable_thinking bug report](https://github.com/agno-agi/agno/issues/4290)
- [upstash/ratelimit-js](https://github.com/upstash/ratelimit-js)
