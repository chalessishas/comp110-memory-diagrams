# Missing maxDuration & Timeout Audit
**Date:** 2026-04-09 (written 2026-04-10 00:34)
**Loop:** Research Loop + Progress Loop (Turn 63)
**Status:** FIXED

## Problem Found

Three AI routes were missing `export const maxDuration = 60`, meaning on Vercel Pro
they'd silently timeout at the **default 30s** — half the budget for AI calls that
routinely take 20-50s.

Five inline `generateText` calls in routes that bypass `src/lib/ai.ts` had no
`timeout` parameter, leaving them unprotected if DashScope hangs.

## Routes Fixed

| Route | Fix Applied |
|-------|-------------|
| `exam-scope/route.ts` | Added `export const maxDuration = 60` + `timeout: 55_000` |
| `extract/route.ts` | Added `export const maxDuration = 60` + `timeout: 55_000` |
| `regenerate/route.ts` | Added `export const maxDuration = 60` |
| `exam-prep/route.ts` | Added `timeout: 55_000` to both `generateText` calls |
| `regenerate/route.ts` | Added `timeout: 55_000` to inline `generateText` |

## Why These Were Missed

Routes that call centralized `ai.ts` functions got the timeout fix automatically.
Routes with inline `createOpenAI` (exam-scope, exam-prep, extract, regenerate, chat)
were added later as features and never went through the same hardening pass.

## Pattern to Watch

Any new route that calls `generateText` or `streamText` directly (not via `ai.ts`)
needs:
1. `export const maxDuration = 60` at the top
2. `timeout: 55_000` on each `generateText` call
3. `checkRateLimit` before the AI call

`streamText` routes only need (1) and (3) — streaming handles timeout via `maxDuration`.

## Remaining Architecture Debt (not fixed, for user awareness)

Five routes duplicate the DashScope `createOpenAI` config:
- `chat`, `exam-prep`, `exam-scope`, `extract`, `regenerate`

Consider exporting `textModel` and `visionModel` from `src/lib/ai.ts` so routes
import models rather than re-creating the client. This is P3 cleanup — no
correctness impact, just DRY maintenance.
