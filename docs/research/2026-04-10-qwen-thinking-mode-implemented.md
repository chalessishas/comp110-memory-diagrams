# CourseHub: Qwen3.5-plus 思维链禁用 — 已实施

> 日期: 2026-04-10 04:28  
> 触发: Research Loop（第八次）+ 搜索结论确认

---

## 实施方案（已合并到 main）

`@ai-sdk/openai` 的 `createOpenAI` 支持 `fetch` 参数作为中间件，在请求发出前修改 body。

```ts
// src/lib/ai.ts
const qwenText = createOpenAI({
  baseURL: DASHSCOPE_BASE,
  apiKey: process.env.DASHSCOPE_API_KEY ?? "",
  fetch: async (url, init) => {
    if (init?.body && typeof init.body === "string") {
      try {
        const body = JSON.parse(init.body);
        body.enable_thinking = false;
        return fetch(url, { ...init, body: JSON.stringify(body) });
      } catch { /* fall through */ }
    }
    return fetch(url, init ?? {});
  },
});

const textModel = qwenText("qwen3.5-plus"); // thinking disabled
// visionModel 用原始 qwen，不注入 enable_thinking
```

## DashScope API 官方确认

官方文档确认：在 OpenAI 兼容模式下，`enable_thinking` 通过请求 body 传递：
```json
{ "enable_thinking": false }
```
不是 `chat_template_kwargs`（旧版参数，现已废弃）。

## 预期效果

| 指标 | 变化 |
|------|------|
| Token 消耗 | 减少 ~30%（thinking token 不再计费）|
| 延迟 | 减少 ~1-3s（不等待 think 块）|
| JSON 解析 | 更稳定（无 `<think>` 污染风险）|
| `stripThinkBlocks` | 保留（routes 有自己的 qwen 实例仍需要）|

## 影响范围

**受益路由**（使用 `ai.ts` 中的 `textModel`）：
- `parseSyllabusText` — 大纲解析
- `generateStudyTasks` — 学习任务生成  
- `generateQuestionsFromOutline` — 自动出题
- `generateLesson` — 课程内容生成
- `generateLessonOutline` / `generateSingleLessonChunk` — 交互课程
- `organizeStudyNote` — 语音笔记整理

**不受影响**（有独立 qwen 实例，仍用思维链）：
- `exam-prep/route.ts` — 考试准备
- `exam-scope/route.ts` — 考试范围分析
- `regenerate/route.ts` — 课程重新生成

这三个路由输出复杂 JSON，thinking 可能提高准确率，暂保留。

## 参考

- [DashScope Deep Thinking Docs](https://www.alibabacloud.com/help/en/model-studio/deep-thinking)
- [DashScope OpenAI Compatibility](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
