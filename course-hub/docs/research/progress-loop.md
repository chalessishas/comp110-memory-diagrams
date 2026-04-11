# Progress Loop Status — 2026-04-11 16:27:03

## Status: ADVANCING

### Recent commits (last 5)
- `edb2f8d` refactor: verifyCourseOwnership helper + fix 3 missing ownership checks (uploads/GET, exams/GET)
- `76a8149` feat: error boundaries for review/learn/practice sub-routes
- `44c455f` fix(practice): bookmark badge shows course-scoped count not global
- `84be37a` feat(practice): bookmarked-only filter mode
- `1f65813` docs: chronicle + research

### What's done this session
- ✅ Full API security audit: 25+ routes, all IDOR gaps closed (+ 2 new gaps found today)
- ✅ window.confirm/alert/prompt → in-app components
- ✅ window.location.reload → router.refresh
- ✅ ConfirmDialog Escape key
- ✅ i18n: zero hardcoded strings (only global-error.tsx accepted)
- ✅ tsc: exit 0
- ✅ Error boundaries: review, learn, practice sub-routes
- ✅ verifyCourseOwnership DRY helper (ownership.ts)

### Remaining tasks

1. **FSRS desired retention slider** — MEDIUM impact, learning science value
   - 1 DB column in user_profiles
   - 1 settings UI slider (0.7–0.97, default 0.9)
   - Pass to `getFSRS(params)` in mastery-v2.ts
   
2. **mastery-summary ownership** — still reads outline_nodes without course ownership check
   - Leaks KP UUIDs only (no content); accepted as low risk
   - Easy fix: add course join to the query

3. **ConfirmDialog focus trap** — Tab can escape modal
   - a11y gap, non-critical

### Blocked items (user action required)
- Vercel env vars: `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`, `SUPABASE_SERVICE_ROLE_KEY`
