# Pre-Implementation Research: Frontend Stack

Date: 2026-04-12 | Stack: Next.js 16 + shadcn/ui + Tailwind v4 + Zustand + Motion

---

## 1. Next.js 16 App Router + shadcn/ui Integration

- Run `npx shadcn@latest init` — auto-detects Next.js 16, App Router, Tailwind v4, sets `rsc: true`
- CLI auto-adds `"use client"` to interactive components; display-only (Card, Badge) stay as Server Components
- **Pattern**: thin Client Component wrappers around interactive shadcn; pass server-fetched data as props
- `tailwindcss-animate` is deprecated for v4 — use `tw-animate-css` instead
- Components are vendored (copied into source), not npm packages — version control them
- No conflicts with existing API routes (`src/app/api/`) — frontend goes in `src/app/(routes)/`
- **Sources**: [shadcn/ui install](https://ui.shadcn.com/docs/installation/next), [cheat sheet 2026](https://dev.to/codedthemes/shadcnui-cheat-sheet-2026-2f5k)

---

## 2. Typed API Client Strategy

### Decision: Zod-inferred fetch wrapper (NOT tRPC, NOT Server Actions)

- **Why not tRPC**: 34 existing REST routes with Zod validation. Retrofitting = rewriting every handler. Not justified.
- **Why not Server Actions**: Our routes serve double duty (E2E tests, potential mobile clients). Server Actions are POST-only, uncacheable, not externally callable.
- **Pattern**: thin `typedFetch<T>(url, zodSchema, init)` that calls `schema.parse(await res.json())`
- **Request types**: reuse `courseCreateSchema` etc. from `src/lib/schemas.ts` via `z.infer<>`
- **Response types**: already in `src/types.ts` (Course, Question, Attempt) — use directly
- No codegen needed. Schemas = single source of truth.
- **Sources**: [Zod inference](https://zod.dev/?id=type-inference), [Type-safe API calls](https://www.michaelouroumis.com/en/blog/posts/type-safe-api-calls-typescript-zod), [SA vs API Routes](https://makerkit.dev/blog/tutorials/server-actions-vs-route-handlers)

---

## 3. Zustand v5 Store Organization

### v5 Breaking Changes

1. **Requires React 18+** — we have React 19, OK
2. **`create()` drops custom equality** — use `createWithEqualityFn` from `zustand/traditional` if needed
3. **`useShallow` is mandatory** for object/array selectors — without it, infinite re-renders in v5
4. **Persist middleware** no longer stores initial state on creation — handle hydration explicitly

### Recommended: Separate Stores (not slices)

| Store | Responsibility | Persist? |
|-------|---------------|----------|
| `useCourseStore` | Active course, outline tree, selected node | No (fetched on mount) |
| `usePracticeStore` | Current question queue, answer state, streak | Session only |
| `useUIStore` | Sidebar open, theme, mobile nav, toast queue | Yes (localStorage) |
| `useStudyStore` | Today's tasks, mastery cache, exam dates | No (API-driven) |

**Why separate**: each store subscribes independently. Toast in `useUIStore` never re-renders practice screen.

### Selector Rule: always `useShallow` for multi-field, bare selector for single primitive

- **Sources**: [v5 migration](https://zustand.docs.pmnd.rs/reference/migrations/migrating-to-v5), [useShallow](https://zustand.docs.pmnd.rs/reference/hooks/use-shallow), [stores discussion](https://github.com/pmndrs/zustand/discussions/2496)

---

## 4. Tailwind v4 Dark Mode

### What Changed from v3

| Aspect | Tailwind v3 | Tailwind v4 |
|--------|------------|------------|
| Config | `tailwind.config.js` | `@theme` directive in CSS |
| Colors | HSL | **OKLCH** (perceptually uniform) |
| Dark mode | `darkMode: 'class'` in config | `.dark` selector overrides in CSS |
| Animation | `tailwindcss-animate` plugin | **`tw-animate-css`** (new package) |
| Color format | `hsl(var(--primary))` | `oklch(var(--primary))` |

### Theme Structure (globals.css)

- `:root { --background: oklch(1 0 0); ... }` with `.dark { --background: oklch(0.145 0 0); ... }` overrides
- `@theme inline { --color-background: var(--background); }` exposes vars to Tailwind utilities
- Dark mode toggle: set/remove `.dark` on `<html>` (same as v3)

### Migration Warnings

- **Remove** `tailwindcss-animate`, add `tw-animate-css`
- **No `tailwind.config.js`** in v4 — all config in CSS via `@theme`
- OKLCH and HSL are incompatible — do not mix
- **Sources**: [shadcn v4 guide](https://ui.shadcn.com/docs/tailwind-v4), [theming](https://ui.shadcn.com/docs/theming), [migration](https://zippystarter.com/blog/guides/migrating-tailwind3-to-tailwind4-with-shadcn)

---

## 5. Mobile-First Practice Mode UX

### Card-Based Quiz Interface

- **Swipe right** = correct/next, **swipe left** = wrong/skip — matches Tinder/Anki mental model
- Use Motion's `drag="x"` with `dragConstraints` and threshold detection (dismiss at >100px offset)
- Always provide **visible button fallback** — not all users discover swipe gestures
- Progressive disclosure: start with buttons, introduce swipe shortcut after 3-5 cards

### Haptic Feedback

- `navigator.vibrate(10)` on correct answer, `navigator.vibrate([50, 30, 50])` on wrong
- Pair every gesture completion with haptic confirmation
- Only available on Android Chrome and some PWA contexts — gracefully degrade

### Thumb-Zone Navigation

- Primary actions (answer buttons, next) in **bottom 40%** of screen
- Question stem in center, options below it
- Progress indicator at top (thin bar, not intrusive)
- Bottom sheet pattern for explanations/hints (swipe up to reveal)

### Offline-First Strategy

- **Serwist** (modern Workbox wrapper) for service worker management in Next.js 16
- **Cache-first** for static assets + lesson content markdown
- **Network-first** for API responses (questions, mastery data)
- **IndexedDB** for offline answer queue — sync when back online
- Estimated effort: medium (2-3 days for basic offline, 1 week for full sync)

### Sources

- [Motion swipe actions tutorial](https://motion.dev/tutorials/react-swipe-actions)
- [Swipe actions with React + Motion](https://sinja.io/blog/swipe-actions-react-framer-motion)
- [Next.js 16 PWA guide](https://blog.logrocket.com/nextjs-16-pwa-offline-support/)
- [Mobile UX patterns 2026](https://muz.li/blog/whats-changing-in-mobile-app-design-ui-patterns-that-matter-in-2026/)
- [Gesture-driven UI design](https://fireart.studio/blog/how-to-design-gesture-driven-ui/)

---

## Implementation Priority Matrix

| Item | Effort | Impact | Do When |
|------|--------|--------|---------|
| shadcn/ui init + theme | 30 min | High | Sprint 0 (now) |
| `typedFetch` API client | 2 hrs | High | Sprint 0 (now) |
| Zustand stores (4 separate) | 3 hrs | High | Sprint 0 (now) |
| Dark mode toggle | 1 hr | Medium | Sprint 1 |
| Swipe gesture practice mode | 1 day | High | Sprint 2 |
| Haptic feedback | 2 hrs | Low | Sprint 2 |
| PWA offline support | 3-5 days | Medium | Sprint 3+ |

## Key Decisions Made

1. **Zod fetch wrapper over tRPC** — 34 routes already exist, no rewrite needed
2. **Separate Zustand stores over slice pattern** — better subscription isolation for practice vs UI state
3. **OKLCH color system** — shadcn/ui v4 default, superior perceptual uniformity
4. **`tw-animate-css` over `tailwindcss-animate`** — required for Tailwind v4 compatibility
5. **Serwist over next-pwa** — modern, maintained, better App Router support
6. **Buttons-first, swipe-later** — progressive disclosure for practice mode gestures
