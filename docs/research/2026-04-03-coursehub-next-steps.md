# CourseHub Next Steps Research Report

> Date: 2026-04-03 | Context: CourseHub MVP complete (Next.js 16 + Supabase + Tailwind), evaluating GPT-4.1 nano migration for 90% cost savings

---

## Topic 1: Vercel AI SDK Integration

### 1.1 Structured JSON Output with GPT-4.1 nano

**Key finding:** Vercel AI SDK (v5+) provides `generateText` with `Output.object()` and Zod schemas to enforce structured JSON output. GPT-4.1 nano is available on Vercel AI Gateway and fully supports structured outputs.

**Code pattern (AI SDK 5/6):**

```typescript
import { generateText, Output } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const result = await generateText({
  model: openai('gpt-4.1-nano'),
  output: Output.object({
    schema: z.object({
      summary: z.string(),
      topics: z.array(z.string()),
      difficulty: z.enum(['easy', 'medium', 'hard']),
    }),
  }),
  prompt: 'Analyze this course material...',
});

// result.output is fully typed
```

**Gotcha:** With OpenAI structured outputs, use `.nullable()` instead of `.nullish()` or `.optional()` in Zod schemas -- OpenAI's strict JSON schema implementation rejects the latter two.

**Recommendation for CourseHub:** Use `@ai-sdk/openai` with `generateText` + `Output.object()` for all structured responses (syllabus parsing, quiz generation, study plan creation). This gives type-safe outputs with zero manual JSON parsing.

Sources:
- [AI SDK Core: generateObject reference](https://ai-sdk.dev/docs/reference/ai-sdk-core/generate-object)
- [OpenAI provider docs](https://ai-sdk.dev/providers/ai-sdk-providers/openai)
- [Structured Outputs with Vercel AI SDK](https://www.aihero.dev/structured-outputs-with-vercel-ai-sdk)
- [GPT-4.1 nano on Vercel AI Gateway](https://vercel.com/ai-gateway/models/gpt-4.1-nano)

### 1.2 PDF and Vision Input

**Key finding:** The Vercel AI SDK OpenAI provider natively supports both PDF and image inputs via the `file` and `image` content types in messages. PDFs can be passed as buffers, file IDs, or URLs.

**PDF input pattern:**

```typescript
import { readFileSync } from 'fs';

const result = await generateText({
  model: openai('gpt-4.1-nano'),
  output: Output.object({
    schema: z.object({
      title: z.string(),
      chapters: z.array(z.object({
        name: z.string(),
        topics: z.array(z.string()),
      })),
    }),
  }),
  messages: [{
    role: 'user',
    content: [
      { type: 'text', text: 'Extract the syllabus structure from this PDF.' },
      {
        type: 'file',
        data: readFileSync('./syllabus.pdf'),  // or a URL string
        mediaType: 'application/pdf',
      },
    ],
  }],
});
```

**Image input pattern:**

```typescript
const result = await generateText({
  model: openai('gpt-4.1-nano'),
  messages: [{
    role: 'user',
    content: [
      { type: 'text', text: 'Describe this diagram.' },
      { type: 'image', image: readFileSync('./diagram.png') },
      // or: { type: 'image', image: 'https://example.com/diagram.png' }
    ],
  }],
});
```

**Recommendation for CourseHub:** For syllabus PDF parsing, pass the file directly via the `file` content type. For photo-of-whiteboard or screenshot features, use the `image` content type. Both work in a single unified API call -- no separate upload step needed.

Sources:
- [OpenAI provider - PDF inputs](https://ai-sdk.dev/providers/ai-sdk-providers/openai)
- [AI SDK 4.2 - PDF support announcement](https://vercel.com/blog/ai-sdk-4-2)

### 1.3 Migration Path: @anthropic-ai/sdk to Vercel AI SDK

**Key finding:** This is not a version upgrade -- it's a library swap. The Vercel AI SDK abstracts the provider layer, so switching from Anthropic to OpenAI (or back) becomes a one-line model change.

**Migration steps for CourseHub:**

1. **Install packages:**
   ```bash
   npm install ai @ai-sdk/openai zod
   npm uninstall @anthropic-ai/sdk  # after migration complete
   ```

2. **Replace raw API calls.** Before (Anthropic SDK):
   ```typescript
   const response = await anthropic.messages.create({
     model: 'claude-sonnet-4-20250514',
     messages: [{ role: 'user', content: prompt }],
   });
   const text = response.content[0].text;
   const parsed = JSON.parse(text);  // manual parsing, fragile
   ```

   After (Vercel AI SDK):
   ```typescript
   const { output } = await generateText({
     model: openai('gpt-4.1-nano'),
     output: Output.object({ schema: myZodSchema }),
     prompt,
   });
   // output is already typed and validated
   ```

3. **Replace streaming calls** with `streamText` (drop-in replacement for SSE patterns).

4. **Environment variables:** Replace `ANTHROPIC_API_KEY` with `OPENAI_API_KEY` (the `@ai-sdk/openai` provider reads this automatically).

**Recommendation for CourseHub:** Migrate route-by-route. Start with the least critical endpoint (e.g., study tip generation), verify it works with GPT-4.1 nano, then migrate syllabus parsing, quiz generation, etc. Keep the Anthropic SDK as a fallback for 1-2 weeks.

Sources:
- [AI SDK Migration Guides](https://ai-sdk.dev/docs/migration-guides)
- [AI SDK 6 announcement](https://vercel.com/blog/ai-sdk-6)

### 1.4 Gotchas and Limitations

| Issue | Detail | Mitigation |
|-------|--------|------------|
| `.optional()` in Zod schemas | OpenAI strict mode rejects `.optional()` and `.nullish()` | Use `.nullable()` instead |
| AI SDK version confusion | v5 uses `generateObject`, v6 merges it into `generateText` with `Output` | Pick v5 (stable) or v6 (beta) and stick to one |
| GPT-4.1 nano quality | Cheapest model may underperform on complex reasoning | Test quiz generation quality; fall back to `gpt-4.1-mini` for hard tasks |
| PDF size limits | OpenAI has token limits on PDF content extraction | Chunk large PDFs before sending; consider pre-extracting text |
| Streaming structured output | `streamObject` (v5) / `streamText` with Output (v6) may not stream partial JSON reliably for all schemas | Use non-streaming `generateText` for structured output; stream only for chat |

---

## Topic 2: Student Product Distribution

### 2.1 Best Channels to Reach US College Students

**Key finding:** TikTok is the dominant discovery channel for Gen Z students, with 5x industry-average click-through rates (1.41% CTR for education campaigns). Reddit and YouTube serve as secondary research channels. Campus ambassadors remain the highest-trust offline channel.

**Channel ranking for CourseHub:**

| Channel | Cost | Trust | Scale | Priority |
|---------|------|-------|-------|----------|
| TikTok (organic + paid) | Low-Medium | High | High | **#1** |
| Campus ambassadors | Medium | Very High | Low-Medium | **#2** |
| Reddit (r/college, r/studytips) | Low | Medium | Medium | **#3** |
| Instagram/Threads | Medium | Medium | Medium | #4 |
| University partnerships | High effort | Very High | Medium | #5 (later) |

**Knowt case study:** Grew from thousands to 1.8M users spending under $20K on advertising over 1.5 years. Strategy: obsessive TikTok posting, optimizing for the first 3 seconds of each video. CEO quote: "If you build a really good product, eventually people will come."

**Recommendation for CourseHub:** Start with TikTok organic content (before/after study sessions, "how I organized my semester in 5 minutes" format). Recruit 3-5 campus ambassadors at the launch university. Post genuinely helpful content on Reddit -- not ads. Budget: $0 for first 1000 users (pure organic + product quality).

Sources:
- [AI Minds podcast with Knowt CEO Abheek Pandoh](https://deepgram.com/podcast/aiminds-029-abheek-pandoh-ceo-at-knowt-inc)
- [TikTok Search Takeover in College Marketing](https://thecampusagency.com/the-tiktok-search-takeover-what-it-means-for-college-marketing/)
- [Top Campus Ambassador Programs 2026](https://socialladderapp.com/blog/best-campus-ambassador-programs-2024/)
- [12 Higher Ed Marketing Trends 2026](https://www.brighterclick.com/blog-post/12-higher-education-marketing-trends-that-drive-enrollment-in-2026)
- [How to launch an app on a university campus](https://www.quora.com/How-do-you-effectively-launch-an-app-on-a-university-campus)

### 2.2 Pricing Model

**Key finding:** Freemium is the dominant model in student edtech, with 2-5% free-to-paid conversion rates. Hybrid models (freemium + subscription tiers) grow revenue 2.4x faster than single-model approaches.

**Competitor pricing (2026):**

| Product | Free Tier | Paid Tier | Price |
|---------|-----------|-----------|-------|
| Quizlet | Basic flashcards | Quizlet Plus (AI features, no ads) | $7.99/mo or $35.99/yr |
| Knowt | Notes, flashcards, community content | Knowt Plus (AI features, unlimited) | ~$5.99/mo |
| StudyFetch | Limited AI tutor sessions | Full AI tutor, all tools | ~$9.99/mo |

**Recommendation for CourseHub:**

- **Free tier:** 3 courses, basic syllabus parsing, limited AI queries (e.g., 20/month)
- **Pro tier ($4.99/mo or $29.99/yr):** Unlimited courses, unlimited AI, PDF upload, quiz generation, study plans
- **Why $4.99:** Undercut Quizlet/StudyFetch; students are extremely price-sensitive. The $29.99/yr price point works because it's less than a single textbook
- **Semester billing option:** $14.99/semester aligns with student mental model (they think in semesters, not months)

Sources:
- [EdTech Pricing Models](https://www.getmonetizely.com/articles/edtech-pricing-models-monetizing-education-technology-effectively)
- [Freemium and Subscription Models for EdTech](https://fastercapital.com/content/Freemium-and-subscription-models-for-edtech-services-Unlocking-Success--How-Freemium-Models-Drive-EdTech-Startups.html)
- [Quizlet Growth Strategy](https://canvasbusinessmodel.com/blogs/growth-strategy/quizlet-growth-strategy)
- [Product-led Growth in EdTech](https://dataconomy.com/2025/06/16/product-led-growth-in-edtech-how-gaiane-simonian-built-a-12-million-user-platform/)

### 2.3 Competitor First-User Acquisition Patterns

| Company | Early Growth Lever | Key Insight |
|---------|-------------------|-------------|
| **Quizlet** | SEO + existing mental model (digital flashcards replace physical ones) | Users need zero onboarding because they already understand flashcards |
| **Knowt** | TikTok obsession + COVID timing + AI-powered question generation | $20K ad spend for 1.8M users; product virality did the rest |
| **StudyFetch** | AI tutor differentiation + founder credibility | Reached 5M students by combining multiple AI tools (flashcards + notes + quizzes + tutor) into one platform |
| **Duolingo** | Gamification + freemium | 45M DAU free users, 5M+ converted to paid; proves freemium works at scale in education |

**Recommendation for CourseHub:** The pattern is clear -- build one killer feature that solves a real pain point (for CourseHub: "upload syllabus PDF, get your entire semester organized in 30 seconds"), make it free, and let TikTok/word-of-mouth spread it. Don't try to monetize until 1000+ active users.

---

## Topic 3: Supabase + Vercel Deployment Best Practices

### 3.1 Environment Variable Setup

**Key finding:** The Supabase Vercel integration auto-syncs all project env vars to Vercel. Use `NEXT_PUBLIC_` prefix only for browser-safe values (anon key, project URL). Never prefix secrets with `NEXT_PUBLIC_`.

**Required variables for CourseHub production:**

```
# Auto-synced by Supabase integration (browser-safe)
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...

# Server-only (set manually in Vercel dashboard)
SUPABASE_SERVICE_ROLE_KEY=eyJ...     # NEVER prefix with NEXT_PUBLIC_
OPENAI_API_KEY=sk-...                # for AI SDK
```

**Setup steps:**
1. Install Supabase integration from [Vercel Marketplace](https://vercel.com/marketplace/supabase) -- this auto-populates most env vars
2. Manually add `OPENAI_API_KEY` and any other secrets in Vercel Project Settings > Environment Variables
3. For preview deployments: add wildcard redirect URL in Supabase Auth settings: `https://*-your-project.vercel.app/auth/callback`
4. Use separate Supabase projects for production vs preview environments

**Recommendation for CourseHub:** Use the Supabase Vercel integration for zero-config setup. Add `OPENAI_API_KEY` manually. Never store `SUPABASE_SERVICE_ROLE_KEY` in `.env.local` that could be committed.

Sources:
- [Supabase for Vercel Marketplace](https://vercel.com/marketplace/supabase)
- [Deploy Next.js Supabase to Vercel (MakerKit)](https://makerkit.dev/docs/next-supabase-turbo/going-to-production/vercel)
- [Production Environment Variables](https://makerkit.dev/docs/next-supabase-turbo/going-to-production/production-environment-variables)

### 3.2 Edge Functions vs Serverless for AI API Calls

**Key finding:** Use **serverless functions** (not Edge) for AI API calls. Edge functions have a hard 30-second timeout and don't support all Node.js APIs. Serverless functions support up to 60s (Pro) or 800s with Fluid Compute.

| Feature | Edge Functions | Serverless Functions |
|---------|---------------|---------------------|
| Timeout | 30s hard limit | 60s (Pro), 800s (Fluid Compute) |
| Cold start | ~0ms | 250ms-1s |
| Node.js APIs | Limited (no `fs`, no `canvas`) | Full support |
| Streaming | 25s to start, then up to 300s | Up to function timeout |
| Best for | Auth middleware, redirects, simple transforms | AI API calls, PDF processing, DB queries |

**For CourseHub's PDF parsing flow:**
- Short AI calls (quiz generation, study tips): Serverless function, 60s timeout is plenty
- Long PDF parsing (100+ page textbook): Use streaming response OR background job with Supabase Edge Functions + webhook callback
- If a single PDF parse takes >60s: Break into chunks, process each chunk in a separate function call, aggregate results

**Recommendation for CourseHub:** Set `maxDuration` in your API routes:

```typescript
// app/api/parse-syllabus/route.ts
export const maxDuration = 60; // seconds (Vercel Pro)

export async function POST(req: Request) {
  // ... AI SDK call here
}
```

For truly long operations, consider Vercel's `waitUntil` or a Supabase Edge Function with a database-backed job queue.

Sources:
- [Vercel Functions Limits](https://vercel.com/docs/functions/limitations)
- [What to do about Vercel Functions timing out](https://vercel.com/kb/guide/what-can-i-do-about-vercel-serverless-functions-timing-out)
- [Edge Functions vs Serverless 2025](https://byteiota.com/edge-functions-vs-serverless-the-2025-performance-battle/)
- [Vercel Edge Explained (Upstash)](https://upstash.com/blog/vercel-edge)

### 3.3 Database Connection Pooling

**Key finding:** Supabase provides two pooling options: Supavisor (shared, free) and PgBouncer (dedicated, paid plans). For Vercel serverless, **always use transaction mode pooling** -- direct connections will exhaust your pool fast.

**Connection setup for CourseHub:**

```typescript
// Use the pooled connection string (port 6543), NOT direct (port 5432)
// In Supabase dashboard: Project Settings > Database > Connection Pooling

// supabase client (browser -- uses REST API, no pooling needed)
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
);

// For server-side direct DB access (e.g., with Drizzle/Prisma):
// Use the transaction-mode pooler URL (port 6543)
// Disable prepared statements (transaction mode doesn't support them)
```

**Key gotchas:**
- Transaction mode does NOT support prepared statements -- disable them in your ORM config
- Vercel does not support IPv6; ensure your Supabase project has IPv4 enabled (paid plans)
- With Vercel Fluid Compute + Supavisor, monitor for connection leaks (known issue where client connections grow without dropping)

**Recommendation for CourseHub:** Use the Supabase JS client (`@supabase/supabase-js`) for all database access -- it goes through the REST API (PostgREST) which handles pooling internally. Only worry about connection pooling if you add a direct ORM like Drizzle or Prisma. On the free tier, the REST API approach avoids pooling headaches entirely.

Sources:
- [Supabase: Connecting to Postgres](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [PgBouncer on Supabase](https://supabase.com/blog/supabase-pgbouncer)
- [Supavisor GitHub](https://github.com/supabase/supavisor)
- [Supavisor + Vercel Fluid Compute issue](https://github.com/orgs/supabase/discussions/40671)

---

## Summary: Recommended Next Actions

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| 1 | Install `ai` + `@ai-sdk/openai`, migrate one API route to GPT-4.1 nano | 2 hours | 90% cost reduction starts |
| 2 | Set up Supabase Vercel integration, configure env vars | 30 min | Production-ready deployment |
| 3 | Migrate remaining API routes from @anthropic-ai/sdk | 1 day | Full cost savings |
| 4 | Create 5 TikTok-ready demo videos of CourseHub | 1 day | User acquisition pipeline |
| 5 | Implement freemium tier with 3-course limit | 3 hours | Monetization foundation |
| 6 | Set `maxDuration` on all AI routes, test PDF parsing timeouts | 1 hour | Production reliability |
