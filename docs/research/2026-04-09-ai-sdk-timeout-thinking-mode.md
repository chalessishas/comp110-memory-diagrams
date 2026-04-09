# AI SDK v6: Timeout API + Qwen Thinking Mode Disable

> 调研日期: 2026-04-09 15:01  
> 触发: Research Loop（第六次，每小时）  
> 背景: course-hub 使用 `ai@^6.0.145` + `@ai-sdk/openai@^3.0.50` + DashScope

---

## 1. AbortSignal.timeout → SDK native `timeout` 参数（已实施）

### 问题

`AbortSignal.timeout(N)` 在 AI SDK 中有已知 bug：
- **Issue #6502**: resumable stream + abortSignal 导致 stream 不停止
- **Issue #6422**: Vercel edge runtime 下 abort 不传播到 `generateText`
- **Issue #6823**: 与 resumable stream 结合时抛出 `[ResponseAborted: ]` 未捕获异常

### 修复

AI SDK v6 新增原生 `timeout` 参数，类型为：
```ts
type TimeoutConfiguration = number | {
  totalMs?: number;  // 整体超时
  stepMs?: number;   // 每步超时（multi-step 用）
  chunkMs?: number;  // 流块间超时（streaming 用）
};
```

**替换方案**（已执行，7 处）：
```ts
// 旧：
abortSignal: AbortSignal.timeout(AI_TIMEOUT_MS),

// 新：
timeout: AI_TIMEOUT_MS,  // 等价于 { totalMs: AI_TIMEOUT_MS }
```

TypeScript 验证通过（0 错误）。

---

## 2. Qwen3.5-plus 禁用思维链 `enable_thinking: false`（待实施，需测试）

### 背景

`qwen3.5-plus` 默认开启混合思考模式，输出 `<think>...</think>` 块。当前代码用 `stripThinkBlocks()` 清除，但 thinking tokens 仍计费（约增加 20-40% token 消耗）。

### 传参方式（DashScope API）

`enable_thinking` 是 DashScope 的自定义 body 字段，不在 OpenAI 标准规范中。

**`@ai-sdk/openai` 当前状态**：
- Issue #12461（2026-02）：OpenAI compatible provider 对 `providerOptions` 的处理方式仍在讨论中
- `providerOptions.openai` 目前不支持任意 body 字段的透传

**可行方案：自定义 fetch wrapper**

```ts
// 为 textModel 单独创建带 enable_thinking: false 的 provider
const qwenText = createOpenAI({
  baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1",
  apiKey: process.env.DASHSCOPE_API_KEY ?? "",
  fetch: async (url, init) => {
    if (init?.body && typeof init.body === "string") {
      const body = JSON.parse(init.body);
      body.enable_thinking = false;
      return fetch(url, { ...init, body: JSON.stringify(body) });
    }
    return fetch(url, init);
  },
});

const textModel = qwenText("qwen3.5-plus");
// visionModel 保留原有 qwen provider（不注入 enable_thinking）
```

### 实施前提

1. **本地测试**：确认 `enable_thinking: false` 对 JSON 输出质量无影响
   - 测试 `parseSyllabusText`、`generateStudyTasks`、`generateQuestionsFromOutline`
   - 确认输出不含 `<think>` 块（说明 API 生效）
   - 对比有/无 thinking 的输出质量

2. **费用估算**：thinking token 占比约 30%，按当前用量估算节省额

3. 测试通过后可在 `ai.ts` 中替换 `textModel` 的 provider

### 预期收益

- Token 成本降低 ~30%
- 延迟降低 ~1-3s（无需等待 think 块生成）
- `stripThinkBlocks()` 可移除（代码简化）

---

## 3. 其他发现

**`@ai-sdk/openai` `extraBody` 支持**：截至 2026-02，仍未有官方 `extraBody` 支持。Issue #12461 是相关 feature request，状态 open。workaround 是自定义 fetch（见上）。

**DashScope 国际端点**：
- 新加坡: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- 美国（弗吉尼亚）: `https://dashscope-us.aliyuncs.com/compatible-mode/v1`
- 中国: `https://dashscope.aliyuncs.com/compatible-mode/v1`（当前使用）

当前 `vercel.json` 已设为 `hnd1`（东京）→ 使用中国端点是合理的（延迟最低）。

---

## 优先级

| 项 | 优先级 | 状态 |
|----|--------|------|
| `timeout` 替换 `AbortSignal.timeout` | P1 | ✅ 已实施 |
| `enable_thinking: false` | P2 | ⏳ 待用户本地测试后实施 |
