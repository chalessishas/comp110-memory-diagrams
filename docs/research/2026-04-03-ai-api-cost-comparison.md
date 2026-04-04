# AI API Cost Comparison for Student Course Management App

**Date**: 2026-04-03
**Purpose**: Evaluate AI API providers for a student product that needs PDF/image parsing, structured JSON output, and must stay within a $5-10/month subscription price point.

---

## Assumptions for Cost Estimation

| Scenario | Input Tokens | Output Tokens | Description |
|----------|-------------|---------------|-------------|
| **Syllabus Parse** | 20,000 | 2,000 | 10-page PDF via vision API |
| **Quiz Generation** | 10,000 | 3,000 | 5-page exam, generate structured questions |

---

## Provider Comparison Table

| Provider | Model | Input $/1M | Output $/1M | Vision | JSON Mode | Context Window | Free Tier |
|----------|-------|-----------|------------|--------|-----------|---------------|-----------|
| **Google** | Gemini 2.5 Flash | $0.30 | $2.50 | Yes | Yes | 1M | 10 RPM, 250 RPD |
| **Google** | Gemini 2.5 Flash-Lite | $0.10 | $0.40 | Yes | Yes | 1M | Yes (rate-limited) |
| **Google** | Gemini 2.5 Pro | $1.25 | $10.00 | Yes | Yes | 1M | 2 RPM, 50 RPD |
| **OpenAI** | GPT-4.1 nano | $0.10 | $0.40 | Yes | Yes | 1M | None |
| **OpenAI** | GPT-4.1 mini | $0.40 | $1.60 | Yes | Yes | 1M | None |
| **OpenAI** | GPT-4.1 | $2.00 | $8.00 | Yes | Yes | 1M | None |
| **OpenAI** | GPT-4o | $2.50 | $10.00 | Yes | Yes | 128K | None |
| **Anthropic** | Claude Haiku 4.5 | $1.00 | $5.00 | Yes | Yes | 200K | None |
| **Anthropic** | Claude Sonnet 4.6 | $3.00 | $15.00 | Yes | Yes | 1M | None |
| **DeepSeek** | DeepSeek-V3 | $0.14 | $0.28 | No | Yes | 128K | None |
| **DeepSeek** | DeepSeek-V4 | $0.30 | $0.50 | Yes (native) | Yes | 1M | None |
| **DeepSeek** | DeepSeek-R1 | $0.55 | $2.19 | No | Yes | 128K | None |
| **Groq** | Llama 4 Scout | $0.11 | $0.34 | Yes | Partial | 10M | None |
| **Groq** | Llama 3.3 70B | $0.06 | $0.06 | No | Partial | 128K | None |
| **Groq** | Qwen3 32B | ~$0.10 | ~$0.40 | No | Partial | 32K | None |
| **Qwen** | Qwen3 VL 235B | $0.26 | $0.90 | Yes | Yes | 128K | 1M tokens free (new acct) |
| **Qwen** | Qwen3.5-Plus | $0.26 | $1.56 | No | Yes | 128K | 1M tokens free (new acct) |

**Notes**:
- "Partial" JSON mode = model follows JSON instructions well but lacks native guaranteed structured output (no schema enforcement like OpenAI's `response_format`)
- DeepSeek-V3 has no vision; V4 launched March 2026 with native multimodal
- Groq offers 50% batch discount; Google offers 50% batch discount
- Gemini free tier was reduced 50-80% in Dec 2025 due to abuse

---

## Per-Task Cost Estimates

### Syllabus Parse (20K input + 2K output tokens)

| Model | Input Cost | Output Cost | **Total** | Notes |
|-------|-----------|------------|-----------|-------|
| Gemini 2.5 Flash-Lite | $0.0020 | $0.0008 | **$0.0028** | Cheapest with vision |
| GPT-4.1 nano | $0.0020 | $0.0008 | **$0.0028** | Tied cheapest, better JSON |
| Groq Llama 4 Scout | $0.0022 | $0.0007 | **$0.0029** | Fastest inference |
| DeepSeek-V4 | $0.0060 | $0.0010 | **$0.0070** | Native multimodal |
| Gemini 2.5 Flash | $0.0060 | $0.0050 | **$0.0110** | Best quality/price ratio |
| Qwen3 VL 235B | $0.0052 | $0.0018 | **$0.0070** | Good quality, free trial |
| GPT-4.1 mini | $0.0080 | $0.0032 | **$0.0112** | Solid all-rounder |
| Claude Haiku 4.5 | $0.0200 | $0.0100 | **$0.0300** | Excellent quality, pricier |
| GPT-4.1 | $0.0400 | $0.0160 | **$0.0560** | Overkill for parsing |
| Gemini 2.5 Pro | $0.0250 | $0.0200 | **$0.0450** | Best quality, expensive |
| Claude Sonnet 4.6 | $0.0600 | $0.0300 | **$0.0900** | Premium, unnecessary |

### Quiz Generation (10K input + 3K output tokens)

| Model | Input Cost | Output Cost | **Total** | Notes |
|-------|-----------|------------|-----------|-------|
| Gemini 2.5 Flash-Lite | $0.0010 | $0.0012 | **$0.0022** | Cheapest |
| GPT-4.1 nano | $0.0010 | $0.0012 | **$0.0022** | Tied cheapest |
| Groq Llama 4 Scout | $0.0011 | $0.0010 | **$0.0021** | Fastest |
| DeepSeek-V4 | $0.0030 | $0.0015 | **$0.0045** | Good value |
| Gemini 2.5 Flash | $0.0030 | $0.0075 | **$0.0105** | Balanced |
| Qwen3 VL 235B | $0.0026 | $0.0027 | **$0.0053** | Good quality |
| GPT-4.1 mini | $0.0040 | $0.0048 | **$0.0088** | Reliable |
| Claude Haiku 4.5 | $0.0100 | $0.0150 | **$0.0250** | High quality |
| GPT-4.1 | $0.0200 | $0.0240 | **$0.0440** | Expensive |

---

## Monthly Budget Analysis

**User scenario**: Student uploads 5 syllabi + generates 20 quizzes per month.

| Model | 5 Syllabus Parses | 20 Quiz Gens | **Monthly Total** | Users at $5/mo margin |
|-------|-------------------|--------------|-------------------|-----------------------|
| GPT-4.1 nano | $0.014 | $0.044 | **$0.058** | ~86 users per $5 |
| Gemini 2.5 Flash-Lite | $0.014 | $0.044 | **$0.058** | ~86 users per $5 |
| Groq Llama 4 Scout | $0.015 | $0.042 | **$0.057** | ~88 users per $5 |
| DeepSeek-V4 | $0.035 | $0.090 | **$0.125** | ~40 users per $5 |
| Gemini 2.5 Flash | $0.055 | $0.210 | **$0.265** | ~19 users per $5 |
| GPT-4.1 mini | $0.056 | $0.176 | **$0.232** | ~22 users per $5 |
| Qwen3 VL 235B | $0.035 | $0.106 | **$0.141** | ~35 users per $5 |
| Claude Haiku 4.5 | $0.150 | $0.500 | **$0.650** | ~8 users per $5 |

**Key insight**: At the cheapest tier (GPT-4.1 nano / Gemini Flash-Lite), API cost per user is ~$0.06/month. Even with 10x heavier usage (50 parses + 200 quizzes), cost stays under $0.60/user/month. The $5-10 subscription gives massive margin for AI costs.

---

## Qualitative Assessment

### Speed / Latency

| Tier | Provider | TTFT | Tokens/sec | Notes |
|------|----------|------|-----------|-------|
| Fastest | Groq (any model) | <100ms | 400-500+ | Purpose-built LPU hardware |
| Fast | Gemini Flash models | ~200ms | 200-300 | Google infrastructure |
| Fast | GPT-4.1 nano/mini | ~200ms | 150-250 | Solid production speed |
| Medium | DeepSeek-V4 | ~300ms | 100-200 | China-hosted, latency varies |
| Medium | Claude Haiku 4.5 | ~300ms | 100-150 | Consistent quality |
| Slower | Gemini 2.5 Pro | ~500ms | 80-120 | Thinking model overhead |

### Structured Output Quality

| Tier | Models | Notes |
|------|--------|-------|
| **Best** | GPT-4.1 family, Gemini 2.5 Flash/Pro | Native `response_format: json_schema` with guaranteed schema conformance |
| **Good** | Claude Haiku/Sonnet, Qwen3 VL, DeepSeek-V4 | Follows JSON schemas reliably, but no hard guarantee |
| **Adequate** | Groq Llama 4 Scout | Works with careful prompting, occasional schema violations |

### Vision / PDF Quality

| Tier | Models | Notes |
|------|--------|-------|
| **Best** | Gemini 2.5 Pro, GPT-4.1, Claude Sonnet 4.6 | Excellent OCR, table extraction, handwriting |
| **Good** | Gemini 2.5 Flash, GPT-4.1 mini, DeepSeek-V4, Qwen3 VL | Handles standard PDFs well, some edge case issues |
| **Adequate** | GPT-4.1 nano, Gemini Flash-Lite, Llama 4 Scout | Good for clean typed documents, struggles with complex layouts |

### Vercel AI SDK Compatibility

| Provider | SDK Package | Status |
|----------|-------------|--------|
| OpenAI | `@ai-sdk/openai` | First-class, all features |
| Google Gemini | `@ai-sdk/google` | First-class, all features |
| Anthropic | `@ai-sdk/anthropic` | First-class, all features |
| DeepSeek | `@ai-sdk/openai` (compatible) | Via OpenAI-compatible endpoint |
| Groq | `@ai-sdk/groq` or OpenAI-compat | Community provider, works well |
| Qwen/DashScope | Custom or OpenAI-compat | Requires adapter, less tested |

---

## Recommendation

### Primary: GPT-4.1 nano (OpenAI)

**Why**:
- **$0.10/$0.40 per 1M tokens** -- among the absolute cheapest with vision
- **Native structured output** with `response_format: json_schema` -- guarantees valid JSON matching your Zod schemas, no retries needed
- **Vision support** for PDF pages rendered as images
- **1M token context** -- can process even the longest syllabi
- **First-class Vercel AI SDK support** -- `@ai-sdk/openai` with `generateObject()` works out of the box
- **~$0.06/user/month** at typical usage -- leaves >98% margin on a $5 subscription
- OpenAI's reliability and uptime are production-grade

**Tradeoff**: Nano is the smallest model, so complex reasoning (e.g., generating nuanced quiz distractors) may be lower quality than GPT-4.1 mini. Mitigate by using mini for quiz generation only.

### Fallback / Hybrid Strategy

| Task | Model | Why |
|------|-------|-----|
| PDF/syllabus parsing | GPT-4.1 nano | Cheap, fast, structured output guaranteed |
| Quiz generation (quality matters) | GPT-4.1 mini | Better reasoning for $0.009/quiz, still cheap |
| Heavy users / batch jobs | Gemini 2.5 Flash-Lite | Free tier covers light usage, paid tier is equally cheap |
| Real-time chat / tutoring | Groq Llama 4 Scout | Sub-100ms latency, $0.0003/message |

### Monthly cost with hybrid approach

For a typical student (5 syllabus parses + 20 quizzes + 50 chat messages):
- Parsing: 5 x $0.003 = $0.015 (GPT-4.1 nano)
- Quizzes: 20 x $0.009 = $0.180 (GPT-4.1 mini)
- Chat: 50 x $0.0003 = $0.015 (Groq Llama 4 Scout)
- **Total: $0.21/user/month**

At $5/month subscription, you can serve ~24 users per dollar of API cost. Even with 5x heavier usage, cost stays under $1.05/user.

### Avoid

- **Claude Sonnet/Opus**: Excellent quality but 10-30x more expensive than needed for structured extraction
- **GPT-4.1 full**: Overkill for parsing; save for complex agentic workflows
- **Gemini 2.5 Pro**: Great model but expensive output tokens ($10/M) and thinking overhead
- **DeepSeek**: Good pricing but China-hosted servers may have latency issues for US users; Vercel SDK integration is less polished

---

## Sources

- [OpenAI API Pricing](https://developers.openai.com/api/docs/pricing)
- [GPT-4.1 Nano Model Details](https://developers.openai.com/api/docs/models/gpt-4.1-nano)
- [GPT-4.1 Mini Pricing (OpenRouter)](https://openrouter.ai/openai/gpt-4.1-mini)
- [Gemini API Pricing (Official)](https://ai.google.dev/gemini-api/docs/pricing)
- [Gemini Rate Limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Gemini 2.5 Flash-Lite (OpenRouter)](https://openrouter.ai/google/gemini-2.5-flash-lite)
- [Claude API Pricing (Official)](https://platform.claude.com/docs/en/about-claude/pricing)
- [DeepSeek API Pricing](https://api-docs.deepseek.com/quick_start/pricing)
- [DeepSeek V4 Specs & Benchmarks](https://www.nxcode.io/resources/news/deepseek-v4-release-specs-benchmarks-2026)
- [Groq Pricing](https://groq.com/pricing)
- [Groq Llama 4 Launch](https://groq.com/blog/llama-4-now-live-on-groq-build-fast-at-the-lowest-cost-without-compromise)
- [Qwen API Pricing](https://pricepertoken.com/pricing-page/provider/qwen)
- [Qwen3 VL 235B Pricing](https://pricepertoken.com/pricing-page/model/qwen-qwen3-vl-235b-a22b-thinking)
- [Vercel AI SDK 6](https://vercel.com/blog/ai-sdk-6)
- [Vercel AI SDK Structured Output](https://ai-sdk.dev/docs/ai-sdk-core/generating-structured-data)
- [Vercel AI Gateway Models](https://vercel.com/docs/ai-gateway/models-and-providers)
- [OpenRouter Pricing](https://openrouter.ai/pricing)
- [AI API Pricing Comparison (IntuitionLabs)](https://intuitionlabs.ai/articles/ai-api-pricing-comparison-grok-gemini-openai-claude)
