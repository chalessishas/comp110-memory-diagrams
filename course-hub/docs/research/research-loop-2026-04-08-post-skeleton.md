# Research Loop 4 — Post-Skeleton Strip: Design System, Accessibility, Performance, Competitors

**Date**: 2026-04-08 02:03 UTC-7
**Context**: All decorative CSS stripped to bare functional skeleton (black/white/gray only). Features ~95% complete. Two bugs fixed (auth ordering, error handling). Now deciding what to rebuild and how.
**Previous research**: Loop 2 covered FSRS migration, streamObject deprecation. Loop 3 covered sleep science, interleaving, tooltip UX. Competitor analysis covered Chinese-market products (Metaso, Zhihu, etc.)
**Focus**: 4 new dimensions — (1) educational platform design systems, (2) accessible color restoration, (3) SSE streaming + FSRS storage performance, (4) English-market AI study tool competitors.
**Searches conducted**: 10

---

## 1. Educational Platform Design Systems

### 1.1 Minimalist Mobile-First Design

- **Source**: [MorHover — Education App Design 2025](https://morhover.com/blog/education-app-design-in-2025/) | [Lollypop — Top 11 Trends](https://lollypop.design/blog/2025/august/top-education-app-design-trends-2025/)
- **Core insight**: The best learning apps use whitespace aggressively, large CTAs, and consistent navigation. Minimalism is not about removing visual identity — it is about removing visual noise that competes with content. Mobile-first is non-negotiable since learners study on the go.
- **CourseHub application**: The skeleton strip was correct directionally. The next step is NOT to add decoration back, but to add **purposeful visual hierarchy**: larger type for headings, consistent spacing scale, and clear primary action buttons. Keep the monochrome base, add color only for functional meaning.
- **Priority**: HIGH — this defines the entire rebuild direction

### 1.2 Bite-Sized Content + Progress Visibility

- **Source**: [Shakuro — E-Learning App Design](https://shakuro.com/blog/e-learning-app-design-and-how-to-make-it-better) | [RiseApps — LMS UI/UX 2025](https://riseapps.co/lms-ui-ux-design/)
- **Core insight**: Learners respond to visible progress (progress bars, streak counters, completion percentages). Bite-sized lessons (5-15 min) outperform long-form content for engagement. The design should show WHERE the learner is in the course at all times.
- **CourseHub application**: CourseHub already generates lessons and has FSRS cards. What is missing: a clear progress indicator per course (X of Y lessons complete), a session-level progress bar during lesson study, and visual completion states on the course overview. These are high-ROI, low-effort additions.
- **Priority**: HIGH — directly impacts retention

### 1.3 Tailwind v4 Design Token Architecture

- **Source**: [Tailwind CSS v4 Theme Variables](https://tailwindcss.com/docs/theme) | [Mavik Labs — Design Tokens 2026](https://www.maviklabs.com/blog/design-tokens-tailwind-v4-2026) | [DEV.to — Typesafe Tokens in Tailwind 4](https://dev.to/wearethreebears/exploring-typesafe-design-tokens-in-tailwind-4-372d)
- **Core insight**: Tailwind v4 exposes all design tokens as native CSS variables through a three-layer system: base tokens (raw values like `--color-blue-500`), semantic tokens (purpose-driven like `--color-primary`), and component tokens (specific like `--btn-bg`). This CSS-first approach means you define your entire design language in one `@theme` block and the whole app speaks the same visual language.
- **CourseHub application**: Instead of sprinkling colors inline, define a minimal token set:
  - `--color-surface` / `--color-surface-elevated` (backgrounds)
  - `--color-text` / `--color-text-muted` (typography)
  - `--color-border` (dividers)
  - `--color-accent` (primary action — one color only)
  - `--color-success` / `--color-error` / `--color-warning` (functional states)

  This gives you dark mode for free (swap the token values) and keeps the skeleton's simplicity while adding functional color.
- **Priority**: HIGH — foundational for all visual work that follows

---

## 2. Accessible Color Restoration

### 2.1 WCAG 1.4.1 — Color Must Not Be the Only Indicator

- **Source**: [W3C — Understanding SC 1.4.1](https://www.w3.org/TR/UNDERSTANDING-WCAG20/visual-audio-contrast-without-color.html) | [W3C — WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- **Core insight**: Color alone cannot convey information. Every color-coded state (success=green, error=red) must have a secondary indicator: an icon, text label, border pattern, or shape change. Required form fields marked only by red are a WCAG violation. The fix is pairing color with icons (checkmark for success, X for error) and text ("Saved successfully", "Error: field required").
- **CourseHub application**: When restoring functional colors, always pair them:
  - Success: green + checkmark icon + "Saved" text
  - Error: red + X icon + descriptive error message
  - Warning: amber + triangle icon + explanation
  - In-progress: blue + spinner + "Generating..."

  This is better UX for ALL users, not just those with color vision deficiency.
- **Priority**: HIGH — accessibility is not optional, and this shapes how we add color back

### 2.2 Contrast Ratios and the Magic Number System

- **Source**: [USWDS — Using Color](https://designsystem.digital.gov/design-tokens/color/overview/) | [AllAccessible — WCAG 2025 Guide](https://www.allaccessible.org/blog/color-contrast-accessibility-wcag-guide-2025) | [InclusiveColors](https://www.inclusivecolors.com/)
- **Core insight**: The US Web Design System uses a "magic number" approach: each color gets a numeric grade (0-100), and the difference between two colors' grades determines contrast compliance. Grade difference of 40+ = AA Large Text, 50+ = AA Normal Text, 70+ = AAA. This is much faster than checking every pair with a contrast checker. For educational apps, WCAG 2.1 requires at least 3:1 contrast for non-text elements (buttons, icons, charts) and 4.5:1 for normal text.
- **CourseHub application**: Use InclusiveColors to generate a minimal WCAG-compliant palette. Since we are starting from black/white/gray, we only need to add:
  - 1 accent color (for primary actions)
  - 3 functional colors (success, error, warning)
  - Each must pass 4.5:1 against the background it appears on

  Tools: Use [InclusiveColors](https://www.inclusivecolors.com/) to generate, [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/) to verify.
- **Priority**: HIGH — must be done correctly before any color is added

### 2.3 Educational Context: Keep Color Logic Simple

- **Source**: [Material UI — Accessible Color Palettes for Inclusive Learning](https://materialui.co/blog/accessible-color-palettes-for-inclusive-learning)
- **Core insight**: In educational apps, avoid using more than 5-6 distinct functional colors. Every color must have a clear, consistent meaning throughout the app. Include a visible legend when using color-coding. Overcomplicating a system with many similar shades makes it harder to decode — the opposite of helpful.
- **CourseHub application**: The skeleton approach (almost no color) is a better starting point than most apps. Add color back surgically:
  1. ONE accent color for "do this next" (primary buttons, links)
  2. Green for correct/success (with checkmark)
  3. Red for wrong/error (with X)
  4. Amber for caution/incomplete (with warning triangle)
  5. Gray for disabled/inactive (already have this)

  That is 5 colors total. Do not add more.
- **Priority**: MEDIUM — conceptual guide, implement via the token system from 1.3

---

## 3. Performance: SSE Streaming + FSRS Storage

### 3.1 Next.js Streaming — Critical Configuration

- **Source**: [Next.js Docs — Streaming](https://nextjs.org/docs/app/guides/streaming) | [HackerNoon — Streaming in Next.js 15](https://hackernoon.com/streaming-in-nextjs-15-websockets-vs-server-sent-events) | [DEV.to — Streaming with ReadableStream](https://dev.to/arfatapp/tutorial-streaming-responses-in-nextjs-with-function-yield-and-readablestream-3bna)
- **Core insight**: Three things commonly break SSE in Next.js and cause buffering or silent failures:
  1. Missing `export const dynamic = 'force-dynamic'` — Next.js caches the route and SSE never streams
  2. Missing `'X-Accel-Buffering': 'no'` header — Nginx/reverse proxies buffer the entire response
  3. Missing cleanup on `request.signal.aborted` — server keeps sending after client disconnects, wasting resources

  The correct pattern: use `ReadableStream` with `controller.enqueue()`, send data as `data: ${JSON.stringify(chunk)}\n\n`, listen for abort signal in the stream's `start` or `pull` method.
- **CourseHub application**: Audit the current SSE lesson generation endpoint for these three issues. If any are missing, fix them. This is a 10-minute fix with major reliability impact. Also: consider using the Vercel AI SDK's `streamText` which handles all of this correctly out of the box (returns a proper ReadableStream, handles backpressure, suppresses errors gracefully).
- **Priority**: HIGH — broken streaming = broken core feature

### 3.2 AI SDK streamText as Replacement for Raw SSE

- **Source**: [AI SDK — Generating Text](https://ai-sdk.dev/docs/ai-sdk-core/generating-text) | [AI SDK — Stream Text Next.js](https://ai-sdk.dev/cookbook/next/stream-text) | [LogRocket — Real-time AI in Next.js](https://blog.logrocket.com/nextjs-vercel-ai-sdk-streaming/)
- **Core insight**: The Vercel AI SDK provides `streamText()` which returns a result whose `textStream` is both a `ReadableStream` and an `AsyncIterable`. It handles token-by-token streaming, backpressure, error suppression (prevents server crashes), and integrates with React via `useChat` or `useCompletion` hooks. Using it eliminates the need to manually implement SSE protocol framing.
- **CourseHub application**: CourseHub uses Qwen (likely via OpenAI-compatible API). The AI SDK supports custom providers, so it could be adapted. However, if the current SSE implementation works and is correct (per 3.1 audit), switching to the AI SDK is a nice-to-have, not a must-have. The SDK adds value if you plan multiple streaming endpoints.
- **Priority**: LOW — only if current SSE has problems or you plan more streaming features

### 3.3 FSRS Storage: IndexedDB over localStorage

- **Source**: [RxDB — localStorage vs IndexedDB vs OPFS](https://rxdb.info/articles/localstorage-indexeddb-cookies-opfs-sqlite-wasm.html) | [DEV.to — 9 Differences](https://dev.to/armstrong2035/9-differences-between-indexeddb-and-localstorage-30ai) | [ts-fsrs on GitHub](https://github.com/open-spaced-repetition/ts-fsrs)
- **Core insight**: localStorage is synchronous, blocks the main thread, limited to ~5-10 MB, and only stores strings (requiring JSON.parse/stringify on every read/write). IndexedDB is asynchronous, supports complex objects natively, has ~1 GB capacity, and can run in Web Workers. For a spaced repetition system that stores cards with scheduling metadata and review history, localStorage becomes a bottleneck at ~500-1000 cards. Individual write latency is lower for localStorage (0.017ms vs 0.17ms), but IndexedDB wins on bulk operations and does not block the UI.
- **CourseHub application**: Current localStorage approach works fine for small card sets (<200 cards per course). Migration to IndexedDB becomes worthwhile when:
  - A user accumulates 500+ cards across courses
  - Review history needs to be stored (for FSRS optimization)
  - You want offline support (IndexedDB + Service Worker)

  Use `localforage` as a drop-in replacement — same API as localStorage but uses IndexedDB under the hood. Migration path: check if data exists in localStorage on app load, copy to IndexedDB, delete from localStorage.
- **Priority**: MEDIUM — current approach works, but plan the migration for when card counts grow

### 3.4 fsrs-browser for Client-Side Optimization

- **Source**: [awesome-fsrs — Curated List](https://github.com/open-spaced-repetition/awesome-fsrs) | [Open Spaced Repetition GitHub](https://github.com/open-spaced-repetition)
- **Core insight**: The FSRS ecosystem has two JS flavors: `ts-fsrs` (pure TypeScript, no optimization) and `fsrs-browser` (WASM-compiled, with parameter optimization). The difference: ts-fsrs calculates the next review interval given preset parameters, while fsrs-browser can also optimize those parameters based on the user's actual review history — making the algorithm personalize to each learner over time.
- **CourseHub application**: Start with `ts-fsrs` (simpler, already sufficient). Once users have 100+ reviews, run `fsrs-browser` optimization to personalize their scheduling parameters. This is a strong differentiator: "the app learns how YOU learn." But it requires storing review history (reinforces the IndexedDB migration from 3.3).
- **Priority**: LOW for now, HIGH for v2 — this is a killer feature but needs the storage foundation first

---

## 4. Competitive Analysis: English-Market AI Study Tools

### 4.1 Coursebox — AI Course Creator + LMS

- **Source**: [Coursebox](https://www.coursebox.ai/) | [Coursebox Pricing](https://www.coursebox.ai/pricing) | [Futurepedia Review](https://www.futurepedia.io/tool/coursebox)
- **What it does**: Upload documents/slides/videos/URLs, AI generates a structured course with lessons, quizzes, interactions, and visuals in minutes. Includes LMS features (learner management, analytics, SCORM export), AI chatbot tutor per course, and AI avatar video generation. 100+ language support.
- **Pricing**: Free tier (limited) / $29.99/mo Creator / $99.99/mo Plus / $499.99/mo Enterprise
- **What CourseHub can learn**: Coursebox targets course creators and training providers (B2B), not individual learners. CourseHub targets individual learners (B2C). This is a different market, but the "upload content, get course" flow is table stakes. Coursebox is noted as "5-10x faster to launch" but "limited when customizing design." CourseHub's edge: deeper learning science (FSRS, spaced repetition) vs. Coursebox's surface-level quiz generation.
- **Priority**: MEDIUM — understand the market but do not pivot toward B2B

### 4.2 Mindgrasp — AI Note-Taker + Study Tool

- **Source**: [Mindgrasp](https://mindgrasp.ai/)
- **What it does**: Upload any file or record live lectures. AI generates notes, summaries, flashcards, quizzes, and provides a 24/7 AI tutor. Positions itself as the "#1 AI Study Tool."
- **Key differentiator**: Live lecture recording + real-time transcription. Turns passive listening into active study material automatically.
- **What CourseHub can learn**: Mindgrasp focuses on TRANSFORMING existing content (lectures, textbooks) into study tools. CourseHub GENERATES new learning content from topics. These are complementary approaches. Consider adding "import your notes/materials" as a future feature to complement AI generation.
- **Priority**: LOW — different approach, but note the content-import pattern

### 4.3 StudyFetch — AI-Powered Study Platform

- **Source**: [StudyFetch](https://www.studyfetch.com/)
- **What it does**: Transforms PowerPoints, lectures, class notes, and study guides into AI study tools (flashcards, quizzes, tests) with an AI tutor. Emphasizes being a "complete study platform."
- **What CourseHub can learn**: StudyFetch and Mindgrasp occupy the same niche (content-to-study-tools). Both rely on user-uploaded content. CourseHub's unique angle is AI-GENERATED content from scratch — you do not need existing materials. This is a stronger value proposition for self-learners who do not have course materials.
- **Priority**: LOW — confirms CourseHub's differentiation

### 4.4 Penseum — Free AI Study Tool

- **Source**: [Penseum](https://www.penseum.com/)
- **What it does**: AI-generated flashcards, detailed problem solutions, personalized summaries, and practice questions. Free tier available. Targets students preparing for exams.
- **What CourseHub can learn**: Penseum is the closest competitor in spirit — it generates study content rather than just transforming uploads. However, it focuses on individual study artifacts (flashcards, Q&A) rather than structured courses. CourseHub's advantage: full course structure with lesson progression + spaced repetition scheduling.
- **Priority**: MEDIUM — this is the competitor to watch most closely

### 4.5 Market Positioning Summary

| Product | Input | Output | Target | Differentiator |
|---------|-------|--------|--------|----------------|
| **CourseHub** | Topic/prompt | Structured course + FSRS cards | Individual learners | AI generation + spaced repetition |
| Coursebox | Documents/URLs | LMS course + quizzes | Training providers (B2B) | Speed, SCORM export |
| Mindgrasp | Lectures/files | Notes + flashcards + tutor | Students | Live lecture capture |
| StudyFetch | Class materials | Flashcards + quizzes + tutor | Students | Content transformation |
| Penseum | Topics/questions | Flashcards + solutions | Exam preppers | Free, problem-focused |

**CourseHub's unique position**: The only tool that GENERATES full course structures from scratch AND applies evidence-based spaced repetition scheduling. No competitor combines both.

---

## 5. Recommended Action Plan (Priority-Ordered)

### Immediate (This Week)
1. **Define design tokens** (Section 1.3) — Create a `@theme` block with 10-12 CSS variables. This unblocks all visual work.
2. **Audit SSE streaming** (Section 3.1) — Check for the three critical configurations. 10-minute fix, major reliability impact.
3. **Add non-color indicators** (Section 2.1) — Icons + text labels for every success/error/warning state. Do this BEFORE adding color.

### Short-Term (Next 2 Weeks)
4. **Add functional colors via tokens** (Section 2.2, 2.3) — 5 colors maximum, all WCAG AA compliant.
5. **Add progress indicators** (Section 1.2) — Course completion %, lesson progress bar, session summary.
6. **Migrate to localforage** (Section 3.3) — Drop-in replacement for localStorage, uses IndexedDB under the hood.

### Future (v2)
7. **FSRS parameter optimization** (Section 3.4) — Personalized scheduling using fsrs-browser.
8. **Content import feature** (Section 4.2) — Let users upload their own materials alongside AI generation.
9. **AI SDK migration** (Section 3.2) — Only if adding more streaming endpoints.

---

*Research conducted: 2026-04-08 02:03 UTC-7*
*Searches: 10 queries across educational UX, accessibility, streaming performance, FSRS storage, and competitor products*
