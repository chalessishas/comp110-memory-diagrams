# AbortSignal Re-enable Analysis
**Date:** 2026-04-09  
**Loop:** Research Loop (Turn 60)  
**Status:** IMPLEMENTED

## Background

AbortSignal was disabled on 2026-04-06 in commit `f7838d4` with message:
> "Investigating generate pipeline failures — AbortSignal.timeout might be interfering with DashScope API. Disabled to isolate."

7 calls in `src/lib/ai.ts` had their `abortSignal` parameter commented out.

## Root Cause Analysis

The generate failures were **not** caused by AbortSignal. The actual bug was fixed in `7594fc5`:
> "fix: balanced-brace JSON extractor for AI output — Replace greedy regex with a proper balanced-brace parser that tracks depth, string boundaries, and escape sequences."

The greedy `/{[\s\S]*}/` regex was including trailing text when AI appended notes after JSON output. AbortSignal was a red herring.

## Why It's Safe to Re-enable Now

1. **Original bug fixed independently** — JSON parsing now handles AI output noise robustly
2. **Faster model** — `qwen3.5-plus` is 19x faster than `qwen-plus-latest` (the model used when AbortSignal was disabled). Legitimate timeouts are much less likely
3. **55s headroom** — `AI_TIMEOUT_MS = 55_000` gives a 5-second buffer before Vercel's 60s hard kill
4. **Cost protection** — Without AbortSignal, a hung DashScope call occupies a full Vercel function slot for 60s. With AbortSignal, it errors cleanly at 55s, freeing resources sooner

## Risk of Keeping It Disabled

- Vercel kills the function at exactly 60s with no cleanup → user sees a generic 504 rather than a meaningful error
- Hung SSE streaming connections linger until forced kill, consuming serverless concurrency
- Extremely slow DashScope responses (>55s) would still fail either way; only the error message differs

## Action Taken

Re-enabled all 7 `abortSignal: AbortSignal.timeout(AI_TIMEOUT_MS)` calls in `src/lib/ai.ts`.
TypeScript check: **0 errors**.

## Next Pending Items

The following require **user action** before production deploy:

| Item | Priority | Action Required |
|------|----------|----------------|
| Upstash Redis env vars | P0 | Register at upstash.com → get `UPSTASH_REDIS_REST_URL` + `UPSTASH_REDIS_REST_TOKEN` |
| Add env vars to Vercel | P0 | Vercel dashboard → Project Settings → Environment Variables |
| Redeploy | P0 | `vercel --prod` or trigger via GitHub push |
| DashScope API key region | P1 | Confirm key works from Japan (hnd1) region, not GFW-blocked |
| experience.md improvements | P2 | 3 proposals from Turn 7 research — user to confirm |
| AI detector v6 training | P2 | Confirm Colab training status (may have stopped) |
