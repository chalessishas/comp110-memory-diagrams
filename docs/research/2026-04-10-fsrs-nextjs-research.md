# FSRS Improvements + Next.js 16 PPR Research
Generated: 2026-04-10 10:11:36

## Note on Stale Loop Context
Loop prompt cited pending items (recentAccuracy last-5, migrations 015/016/018) — all resolved. Current project status: fully operational, i18n sprint near-complete.

---

## FSRS-6 Algorithm Improvements

### What Changed
- **FSRS-6** added `w20`: an optimizable parameter for the forgetting curve (range 0.1–0.8), making it personalizable per user rather than using a universal power function.
- Power function (v4+) fits user data better than the exponential curves used in SM-2 and earlier FSRS. 15–20% fewer reviews for the same retention rate.
- Default desired retention = 90%. Lower (e.g., 70%) dramatically reduces review volume while still memorizing more cards per unit time.

### Actionable for CourseHub
`ts-fsrs` already used in project. Two applicable improvements:

**1. Expose desired retention slider (low cost)**
Add a per-course or global preference: "Target retention: 70% / 80% / 90%". Pass as `w` parameter to FSRS scheduler. Currently hardcoded at default (90%). Research shows 70–80% retention with half the review load is often optimal for exam prep (users care about breadth, not perfect recall).

```ts
// In spaced-repetition.ts, expose:
export function updateCard(id: string, rating: Rating, desiredRetention = 0.90) {
  // pass desiredRetention to fsrs.repeat()
}
```

**2. LECTOR pattern: concept-aware scheduling (medium cost)**
arxiv 2508.03275 (2025): LLM-Enhanced Concept-based Test-Oriented Repetition — groups cards by concept cluster, prioritizes clusters with lowest predicted exam performance. CourseHub already has KP-level mastery; could bias FSRS review order toward lowest-mastery KP clusters before an exam. Already partially implemented via exam scope + FSRS exam-mode priority sort.

---

## Next.js 16 — Partial Prerendering (PPR)

### What It Is
PPR (stable in Next.js 16, Oct 2025) lets a single page serve a static HTML shell from CDN edge + dynamic content streamed from origin in parallel. No route-level SSG/SSR choice — per-component within the same page.

### How It Works
- Wrap dynamic components in `<Suspense>`. Next.js precomputes the static shell.
- On request: shell served immediately from CDN, dynamic parts stream in.
- Single HTTP response (no extra roundtrip).
- Replaces experimental `ppr` flag with `cacheComponents` config in `next.config.ts`.

### Actionable for CourseHub
Most course pages are currently full SSR (wait for all Supabase queries). With PPR:

**Dashboard page** — static header + nav from CDN, course cards stream in from Supabase.
**Course overview** — static CourseTabs shell, dynamic content (outline, progress) streams.

```ts
// next.config.ts
const config = {
  experimental: {
    cacheComponents: true, // enables PPR in Next.js 16
  },
};
```

**Implementation cost**: Medium — need to audit which components are safe to mark static. Auth-dependent pages require care (user-specific data must not be cached in static shell).

**Verdict**: Worth evaluating for dashboard but low priority — current RSC parallel queries already give good perf. PPR would mainly help time-to-first-byte for the static shell.

---

## Priority Assessment

| Improvement | Research basis | Cost | Priority |
|-------------|----------------|------|----------|
| Desired retention slider (70/80/90%) | FSRS-6 optimal forgetting index | Low | Medium |
| KP-cluster exam priority sort | LECTOR 2025 | Medium | Low (partially done) |
| PPR for dashboard/course pages | Next.js 16 stable | Medium | Low (perf already ok) |

---

## Sources
- [FSRS Algorithm Overview DeepWiki](https://deepwiki.com/open-spaced-repetition/rs-fsrs/3.1-fsrs-algorithm-overview)
- [Anki FSRS 2026 Explanation](https://studycardsai.com/blog/anki-fsrs-algorithm)
- [LECTOR LLM-Enhanced SRS arXiv 2025](https://arxiv.org/html/2508.03275v1)
- [Next.js 16 Release Blog](https://nextjs.org/blog/next-16)
- [PPR Deep Dive DEV Community](https://dev.to/pockit_tools/nextjs-partial-prerendering-ppr-deep-dive-how-it-works-when-to-use-it-and-why-it-changes-48dk)
- [Next.js 16 PPR Practical Guide](https://www.ashishgogula.in/blogs/a-practical-guide-to-partial-prerendering-in-next-js-16)
