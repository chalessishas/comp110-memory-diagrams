# Learn Module Improvements Research

**Date**: 2026-04-06
**Context**: Chronicle project learn module -- progressive lesson delivery, streaming generation, chunk-based pedagogy, DashScope optimization

---

## 1. Supabase Realtime for Progressive Chunk Delivery

- **RLS compatibility**: Supabase Realtime `postgres_changes` fully supports Row Level Security. Every change event is checked against RLS policies for each subscribed user. However, this means N subscribers = N policy evaluations per INSERT, creating a potential bottleneck. RLS check is cached per connection for channel subscriptions, but postgres_changes re-evaluate per event.
  - Source: [Supabase Realtime Authorization](https://supabase.com/docs/guides/realtime/authorization), [Postgres Changes docs](https://supabase.com/docs/guides/realtime/postgres-changes)

- **Latency**: Real-world latency is typically **under 100ms** for message delivery. Postgres changes are processed on a **single thread** to maintain ordering, so compute upgrades have limited effect. Complex RLS policies with joins/function calls increase connection time significantly.
  - Source: [Supabase Realtime Benchmarks](https://supabase.com/docs/guides/realtime/benchmarks)

- **Free tier limits**: **200 concurrent Realtime connections** on the free plan. Messages per second are also capped per plan tier. Connections auto-reconnect via supabase-js if temporarily disconnected due to throughput limits.
  - Source: [Realtime Limits](https://supabase.com/docs/guides/realtime/limits), [Realtime Pricing](https://supabase.com/docs/guides/realtime/pricing)

- **Architecture implication**: For lesson chunk delivery (one user subscribing to their own lesson row), RLS overhead is minimal (1 subscriber = 1 check). The single-thread bottleneck only matters at scale (100+ concurrent lesson generations). 200 concurrent connections is sufficient for early-stage use.

- **Alternative**: Supabase **Broadcast** channel bypasses database entirely and has no RLS overhead or single-thread limitation. Better for pure push scenarios where persistence isn't needed during streaming.

## 2. Vercel AI SDK Streaming for Lesson Generation

- **`streamObject` function**: AI SDK Core provides `streamObject` which returns a `partialObjectStream` -- an async iterable yielding progressively-built JSON objects validated against a Zod schema. The client-side `useObject` hook consumes these streams directly in React components.
  - Source: [AI SDK streamObject reference](https://ai-sdk.dev/docs/reference/ai-sdk-core/stream-object), [useObject reference](https://ai-sdk.dev/docs/reference/ai-sdk-ui/use-object)

- **Output modes**: Three modes available -- `object` (single structured output), `array` (stream complete array elements one-by-one, ideal for lesson chunks), and `enum`. Array mode streams only **complete elements** as they arrive, preventing layout shifts in UI.
  - Source: [AI SDK 3.4 announcement](https://vercel.com/blog/ai-sdk-3-4)

- **DashScope/Qwen compatibility**: A community provider `qwen-ai-provider` exists (`import { createQwen } from 'qwen-ai-provider'`). It wraps DashScope's OpenAI-compatible endpoint (`https://dashscope-intl.aliyuncs.com/compatible-mode/v1`). Alternatively, use the standard `@ai-sdk/openai` provider with custom `baseURL` pointing to DashScope.
  - Source: [Qwen community provider](https://ai-sdk.dev/providers/community-providers/qwen), [DashScope OpenAI compatibility](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)

- **Practical pattern for lessons**: Use `streamObject` in array mode with a Zod schema defining a lesson chunk (title, content, quiz question). Each chunk streams as a complete unit. Frontend renders chunks progressively using `useObject`. No need for Supabase Realtime at all for the streaming path.

- **Caveat**: `streamObject` requires the model to support structured output or tool-use for reliable schema adherence. Qwen models support function calling, so this should work. Test with `qwen-plus` first as it has the best instruction-following.

## 3. Chunk-Based E-Learning Best Practices

- **Optimal chunk size**: Working memory processes **4 +/- 2 information chunks** simultaneously. Microlearning research consistently recommends **5-15 minutes per chunk**, which translates to roughly **300-800 words of instructional text** per chunk (assuming ~150 wpm reading speed for learning material).
  - Source: [eLearning Industry - Mastering Content Breakdown](https://elearningindustry.com/mastering-content-breakdown-enhancing-learning-through-chunking)

- **Retrieval practice frequency**: Embedding quizzes after each chunk significantly improves retention. A 2022 study (Sana & Yan) found **interleaved quizzes outperformed blocked quizzes by ~9 percentage points** (63% vs 54% on final tests). Both beat no-quiz conditions (47%). Recommendation: 1-2 retrieval questions per chunk, mixing topics from current and previous chunks.
  - Source: [Interleaving Retrieval Practice Promotes Science Learning (Sana & Yan, 2022)](https://pdf.retrievalpractice.org/spacing/InterleavedRetrievalPracticePromotesScienceLearning_SanaYan_2022.pdf)

- **Hybrid blocked + interleaved approach**: A 2025 study (Hwang) found that **pure interleaving can overwhelm low-achieving learners**. Best approach: start with blocked practice (quiz on current chunk topic only), then progressively introduce interleaved questions mixing previous topics. This "hybrid" approach produced the most robust long-term retention across ability levels.
  - Source: [Hwang 2025 - Language Learning](https://onlinelibrary.wiley.com/doi/10.1111/lang.12659)

- **Spacing effect**: Meta-analysis across 9 STEM courses found **d = 0.54 effect size** for distributed (spaced) vs massed practice. Bi-weekly spaced quizzes significantly outperformed massed quizzes. For a lesson module, this means revisiting earlier material in later sessions matters more than intensive single-session study.
  - Source: [STEM spaced retrieval meta-analysis 2024](https://link.springer.com/article/10.1186/s40594-024-00468-5)

- **Recommended structure for a lesson**: 4-6 chunks per lesson, each chunk 300-500 words + 1 recall question (blocked). After every 2-3 chunks, add 1 interleaved question referencing earlier material. End-of-lesson summary quiz with 3-5 interleaved questions spanning all chunks.

## 4. DashScope API Optimization

- **`max_tokens` for speed**: DashScope supports `max_tokens` through both native and OpenAI-compatible APIs. Limiting output tokens directly reduces generation time and cost. For lesson chunks of ~400 words, setting `max_tokens: 800` (tokens > words) prevents runaway generation.
  - Source: [DashScope Text Generation](https://www.alibabacloud.com/help/en/model-studio/text-generation)

- **Streaming with `incremental_output`**: Native DashScope API supports `stream=True` with `incremental_output=True` for delta-only chunks (like OpenAI's streaming). The OpenAI-compatible endpoint supports standard SSE streaming. Both work with Vercel AI SDK's streaming functions.
  - Source: [DashScope Streaming docs](https://www.alibabacloud.com/help/en/model-studio/stream)

- **Batch API at 50% cost**: DashScope provides an OpenAI-compatible Batch API. Upload JSONL files, process asynchronously during off-peak hours, results returned when complete. **50% cost reduction** vs real-time inference. Supported models: qwen-max, qwen-plus, qwen-flash, qwen-turbo. Ideal for pre-generating lesson content in bulk.
  - Source: [DashScope Batch API](https://www.alibabacloud.com/help/en/model-studio/batch-interfaces-compatible-with-openai/)

- **Model selection for lessons**: `qwen-plus` offers the best quality/cost ratio for structured content generation. `qwen-turbo` is 5-10x cheaper but less reliable for complex schemas. `qwen-flash` is the newest budget option. For lesson generation where quality matters, use `qwen-plus` for real-time and batch pre-generation.

- **Cost optimization strategy**: Pre-generate common lesson outlines via Batch API (50% savings). Use real-time streaming only for personalized/on-demand content. Cache generated lessons in Supabase to avoid re-generation.

---

## Recommended Next Steps

1. **Use Vercel AI SDK `streamObject` in array mode** (highest impact, lowest effort) -- Stream lesson chunks directly to frontend via `useObject` hook. Each array element = one lesson chunk with content + quiz. No need for Supabase Realtime in the streaming path. Use the `qwen-ai-provider` community package or configure `@ai-sdk/openai` with DashScope baseURL.

2. **Implement hybrid retrieval practice** -- Structure each lesson as 4-6 chunks, 300-500 words each. Add 1 blocked recall question per chunk + 1 interleaved question every 2-3 chunks. End with 3-5 mixed review questions. This follows the Hwang 2025 hybrid approach that works across ability levels.

3. **Set `max_tokens` per chunk generation** -- Limit to ~800 tokens per chunk call to prevent slow/expensive runaway outputs. This alone can cut generation time by 40-60% for content that would otherwise over-generate.

4. **Adopt Batch API for course pre-generation** -- For standard course content (not personalized), use DashScope Batch API at 50% cost. Pre-generate lesson libraries during off-peak hours and store in Supabase. Reserve real-time streaming for on-demand/personalized lessons only.

5. **Reserve Supabase Realtime for collaboration features** -- Don't use postgres_changes for lesson streaming (AI SDK handles this better). Save Realtime for multi-user features like study groups, live teacher dashboards, or collaborative note-taking where database-driven pub/sub makes sense.
