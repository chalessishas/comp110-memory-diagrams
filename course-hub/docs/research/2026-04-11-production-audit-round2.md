# Production Audit Round 2 — 2026-04-11

## What Was Done This Session

### Security (HIGH impact, all fixed)
- 18 API routes had IDOR vulnerabilities (no user_id ownership check)
- Most critical: `chat` route could leak any user's course content via AI
- Most severe: `outline/PUT` had no `getUser()` call at all — pure RLS reliance
- `teach-back` and `chunks` discarded the course `id` param entirely (dead code + security bug)
- `extract` allowed downloading arbitrary storage paths

### UX (MEDIUM impact, all fixed)
- 7 `window.confirm()` → in-app `ConfirmDialog` with promise-based hook
- 2 `alert()` → inline error state in settings
- 2 `window.location.reload()` → `router.refresh()`
- `ConfirmDialog` Escape key dismissal via window keydown listener

## Remaining Known Gaps

### Low-priority / user-action required
- Vercel env vars: `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`, `SUPABASE_SERVICE_ROLE_KEY`
- `mastery-summary` leaks KP UUIDs for any course_id — accepted (no content, just UUIDs)
- `ConfirmDialog` has no focus trap (Tab can escape modal) — a11y gap, non-critical

### Hardcoded strings (not blocking)
- `course/[id]/page.tsx` `buildTodayTasks`: raw `title`/`description` fields have hardcoded English but are dead code (never rendered — `titleKey`/`descKey` take priority)
- `global-error.tsx`: hardcoded English, accepted limitation (no i18n context at root error boundary)

## Next High-Value Work

### Option 1: FSRS desired retention slider (MEDIUM impact)
Research finding from prior session: FSRS supports a `desired_retention` parameter (0.7-0.97). Currently hardcoded at 0.9 in `mastery-v2.ts`. Adding a user-configurable slider in settings would directly improve learning outcomes for users who want either aggressive review or lighter load.
- 1 Supabase column in user_profiles or settings table
- 1 settings UI component
- Pass retention value to `getFSRS(params)` call in mastery-v2.ts

### Option 2: Remove dead `title`/`description` raw fields from buildTodayTasks
Minor cleanup — remove the hardcoded English fallback strings since titleKey/descKey always exist. Reduces confusion.

### Option 3: Optimize mastery-summary route ownership check
Currently reads KP IDs from `outline_nodes` without verifying course ownership. Add `.eq("user_id", user.id)` via course join. Low priority (only leaks UUIDs).

### Option 4: Error boundary for course sub-pages
Currently only `error.tsx` exists at `course/[id]/`. Individual sub-pages (review, learn, practice) don't have local error boundaries. If a sub-page throws after hydration, the entire course route catches it. Could add granular `error.tsx` per sub-page.

## Recommendation
Option 1 (FSRS retention slider) has the highest learning-science impact. Option 2 is trivial cleanup.
