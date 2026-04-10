# CourseHub Next Priorities — 2026-04-10 09:45:56

## Current State (post i18n sprint)

- i18n migration: **complete** — 460 keys per locale, 0 duplicates, t() interpolation added
- TS build: **clean**
- Fetch guards: **fixed** (practice, library, review initial loads + library refresh)
- Product test: **dashboard passes**, auth-gated pages verified via static analysis

## Highest-ROI Next Steps

### 1. Server Component i18n (notes/page.tsx "Back to Dashboard")
`notes/page.tsx` is an RSC — `useI18n()` not available. The `"Back to Dashboard"` text is hardcoded EN.
**Options:**
- A) Add a `locale` cookie read server-side (simple, no new infra)
- B) Extract the back-link into a small `"use client"` wrapper component
- **Recommendation:** Option B — `<BackToDashboard />` client component, 5 lines, reusable across RSC pages

### 2. Vercel auto-deploy (currently manual `npx vercel deploy --prod`)
Git integration not set up. Every push requires manual deploy command.
**Fix:** Connect Vercel project to GitHub repo via Vercel dashboard (UI action, 2 min). Cannot be done via code.

### 3. Question exam-prep result is missing `examScope` KP scope persistence
When exam-prep generates questions, the scope is not persisted to `exam_scope` in localStorage via `setExamScope()` — so the "Exam Scope" badge in learn/review pages doesn't reflect the newly generated scope.
**Check needed:** Does `exam-prep` API set scope KP IDs? Or does user have to manually set scope via review page?

### 4. Missing `misc.delete`, `misc.rename`, `misc.addChild` in practice page loading state
`practice/page.tsx` loading state uses `t("misc.backToDashboard")` — this was just fixed. Verify all misc keys referenced exist.

### 5. Error boundary for course pages
No React error boundary on course pages. If a component throws (e.g., malformed Supabase data), the whole page white-screens. `app/course/[id]/error.tsx` may not exist.

**Check:**
