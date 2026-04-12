# AI Frontend Design Methodology v2

> v1 reviewed by Product Critic (27 weaknesses) + UX Researcher (10 actionable changes).
> v2 incorporates all critical feedback. See docs/research/ for full review transcripts.

---

## Unique Value Proposition (every design decision reinforces this)

**"AI generates practice content from YOUR course materials — not generic flashcards."**

Competitors make you type flashcards (Quizlet) or import pre-made decks (Anki). CourseHub takes your syllabus PDF, understands it, and generates questions, lessons, and study plans. Every UI surface must make this visible and trustworthy.

---

## Phase 1: User Model

| Question | Answer |
|----------|--------|
| Primary user | College student preparing for exams |
| Emotional state | Stressed, time-pressured, wants efficiency |
| Device: creation | Laptop (upload syllabus, read lessons, set exam scope) |
| Device: review | Phone (practice questions, check progress, quick review) |
| Study pattern | Bursty — nothing for weeks, then intense before exam |
| Alternative | Quizlet, Anki, ChatGPT, paper notes, doing nothing |

### Gate 1: User Model
- [ ] Every page serves a real user moment (stressed student studying)
- [ ] Creation flows are laptop-optimized; review flows are mobile-first
- [ ] Nothing requires daily engagement (no streak punishment)

---

## Phase 2: Information Architecture

### Design Sequence (value-out, not shell-in)

```
1. Practice Mode ← core value, design this FIRST
2. Course Detail ← context for practice
3. Exam Prep ← highest differentiator
4. Lesson Viewer ← interactive learning
5. Dashboard ← navigation to the above
6. Onboarding ← first-time experience
7. Auth ← simple, defer to Supabase
8. Phase 2: Chat, Notes, Settings, Share/Fork
```

Rationale: Design the destination before the roads. Dashboard is a navigation surface TO practice — you can't design it without knowing what practice delivers.

### Core Pages

| Page | Primary Action | Device |
|------|---------------|--------|
| Dashboard | Resume studying (algorithmic: nearest exam or weakest topic) | Mobile-first |
| Course Detail | Navigate to practice/lessons/exams via tabs | Laptop-first |
| Practice Mode | Answer question, see feedback | Mobile-first |
| Lesson Viewer | Read chunk, answer checkpoint | Laptop-first |
| Exam Prep | Paste scope → get targeted questions | Laptop-first |
| Onboarding | Try demo course before creating own | Both |
| Auth | Sign in (Google SSO + email) | Both |

### Gate 2: IA Check
- [ ] New user can practice a demo question in under 60 seconds (no signup required)
- [ ] New user can create course + see first AI question in under 10 minutes (including AI wait)
- [ ] Core actions (practice, resume, create) reachable in ≤2 clicks from dashboard
- [ ] Supporting pages (settings, attempt review, share) reachable in ≤4 clicks
- [ ] Navigation makes current location obvious (breadcrumb or tab highlight)

---

## Phase 3: Page-Level Design

### 3a. Content Priority (per page)
1. What's the ONE thing the user needs to see first?
2. What's the ONE action they most likely want to take?
3. What can be hidden behind expand/click?

### 3b. State Mapping (design ALL states)
| State | Requirement |
|-------|-------------|
| **Empty** | Show demo/sample content to demonstrate value. Never just "No data yet." |
| **Loading (AI)** | Use Latency Ladder (see below). Show what's happening + let user do other things. |
| **Loaded** | Normal state with data. |
| **Error** | Explain what failed + offer specific recovery (retry, simplify, fallback). |
| **Edge** | 0 questions generated, exam tomorrow, 50+ courses, phone landscape. |

### 3c. AI Latency Ladder (mandatory for all AI operations)

| Duration | UI Pattern |
|----------|-----------|
| 0-3s | Inline skeleton/shimmer |
| 3-10s | "Generating questions..." label + elapsed timer |
| 10-30s | Stage labels ("Analyzing syllabus... Matching topics...") + suggestion to review existing content |
| 30-60s | Move to background, notification when ready, let user navigate away |
| 60s+ | Warn "taking longer than usual", offer cancel + retry |
| Failure | Specific recovery: retry, simplify input, or fall back to cached content |

**Never show fake progress bars.** LLM inference is unpredictable. Show elapsed time, not estimated remaining.

### 3d. AI Trust Signals (mandatory for all AI-generated content)
- Visual indicator that content is AI-generated (subtle badge, not obtrusive)
- One-click flag/report on every AI-generated element (question, lesson, task)
- Inline editing — user can modify AI content and take ownership
- Quality score visible on Course Detail (aggregate of user feedback)

### 3e. Competitive Benchmark (per page)
| Page | Study these products |
|------|---------------------|
| Dashboard | Duolingo (daily goal), Quizlet (recently studied), Linear (task list) |
| Course Detail | Knowt (split-pane: source ↔ generated), RemNote (tabs: notes/cards/review) |
| Practice | Quizlet Learn (one-at-a-time, immediate feedback), Anki (flip + self-rate) |
| Lesson Viewer | Khan Academy (video + inline questions), RemNote (note + flashcard) |
| Exam Prep | No direct competitor — CourseHub's strongest differentiator |

### Gate 3: Page Design Check
- [ ] Every element has a reason to exist (no decorative components)
- [ ] Primary action is visually dominant (size, color, position)
- [ ] Empty states show demo content or guided first-action
- [ ] AI loading uses Latency Ladder, not generic spinners
- [ ] AI content has trust signals (badge, flag, edit)
- [ ] Mobile layout reprioritizes (not just shrinks)

---

## Phase 4: Visual Language & Components

### 4a. Design System Direction

**"Focused Productivity"** — Linear meets Vercel.
- Clean, high-contrast, minimal chrome
- Content-dense without clutter
- Subtle micro-animations (answer feedback, page transitions)
- Dark mode is mandatory (students study at night)

**NOT**: Duolingo-playful (patronizing for college), Anki-brutalist (uninspiring), Notion-infinitely-customizable (too complex).

### 4b. Design Tokens

| Token | Value |
|-------|-------|
| Font | Inter (system fallback), 16px body minimum |
| Color | Neutral base (zinc/slate), ONE brand accent for CTAs + progress |
| Spacing | 4px base grid |
| Radius | 8px cards, 6px inputs, 4px badges |
| Breakpoints | Mobile: <640px, Tablet: 640-1024px, Desktop: >1024px |
| Motion | 150ms ease-out for interactions, 300ms for page transitions |

### 4c. Component Strategy
1. shadcn/ui has it? → Use it directly
2. Variant of existing? → Extend, don't create
3. Truly novel? → Design from scratch, document why

### 4d. Interaction Patterns (every interactive element)
- Click/tap action
- Hover state (desktop)
- Keyboard shortcut (accessibility)
- Loading state
- Error state
- Touch target ≥44px on mobile

### Gate 4: Component Check
- [ ] No custom component duplicates shadcn/ui
- [ ] Color contrast ≥4.5:1 (WCAG AA)
- [ ] Screen reader walkthrough of every critical flow
- [ ] Keyboard-only completion test for critical flows
- [ ] ARIA live regions for dynamic AI content updates
- [ ] prefers-reduced-motion respected
- [ ] Performance: LCP <2.5s, initial bundle <200KB gzipped

---

## Phase 5: Flow Validation

### 5a. Critical User Flows
1. **Try Before Signup**: Land → Try demo question → See value → Sign up
2. **New Course**: Sign up → Create course → Upload syllabus → AI parse (30-60s) → Review outline → Save → Generate questions → Practice
3. **Return to Study**: Login → Dashboard shows "15 cards due, ~8min" → Start practice → See mastery
4. **Exam Cram**: Login → Select course → Create exam → Paste scope → AI generates targeted questions → Practice weak areas
5. **Review Progress**: Dashboard → Course → See mastery per topic → Focus on weakest → See improvement

### 5b. Edge Case Flows
6. AI generates 0 questions for a topic → Show explanation + retry or manual create
7. AI takes 60+ seconds → Background notification, user can navigate away
8. Network drops mid-practice → Preserve in-progress answers locally
9. User has 10 courses → Dashboard still scannable, sorted by urgency
10. Phone in portrait → Practice works full-width, no horizontal scroll

### Gate 5: Flow Check
- [ ] Every critical flow walked through click-by-click
- [ ] No flow requires user to "just know" something
- [ ] Error recovery doesn't require going back to dashboard
- [ ] AI wait times use Latency Ladder (not spinners)
- [ ] Phone flows tested separately (not just "it's responsive")

---

## Phase 6: Retention & Re-engagement

### Retention Hooks (design these, not just mention them)
1. **Review Queue**: Daily landing: "15 cards due across 3 courses, ~8 minutes" (FSRS-driven)
2. **Exam Countdown**: "Midterm 3 in 5 days — you've covered 73% of scope" on dashboard
3. **Exam-anchored Reminders**: Notifications at 7 days, 3 days, 1 day before exam (not daily nagging)
4. **Progress Milestones**: Per-topic mastery badges when reaching "mastered" status
5. **Weak Spot Nudge**: "Your weakest topic is Taylor Series (42% mastery)" → one-click to practice

### NOT doing (overkill for college students):
- Daily streaks with punishment
- XP / leaderboards / leagues
- Cartoon mascots
- Social competition

### Gate 6: Retention Check
- [ ] User has a reason to return within 48 hours of first use
- [ ] Dashboard shows actionable next-step, not just stats
- [ ] Exam proximity drives urgency naturally (no artificial gamification)

---

## Anti-Patterns (things to explicitly avoid)

1. **Dashboard Overload**: Charts, stats, lists competing. Students want "what next?", not analytics.
2. **Premature Abstraction**: Generic "card" for everything. Courses, questions, lessons need different layouts.
3. **Hiding the Core Action**: "Start Practice" buried under 3 navigation levels.
4. **Empty State Neglect**: Designing for "full data" screenshot. First-time UX IS empty states.
5. **Over-designing Settings**: Elaborate preferences when defaults should just work.
6. **Modal Hell**: Modals interrupt flow. Use inline expansion.
7. **Fake Complexity**: Tabs, filters, sort for <10 items.
8. **AI as Authority**: Presenting AI content without flag/edit/report escape hatches.
9. **Progress Theater**: Mastery percentages that don't correlate with exam readiness.
10. **Feature Parity Anxiety**: Trying to match Quizlet + Anki + Notion instead of being best at one thing.
11. **Loading State Amnesia**: Beautiful loaded state, forgotten 30-second loading state (which IS the primary experience for AI pages).
12. **AI-washing**: Making everything AI-powered when simple CRUD is better (e.g., AI course titles).

---

## Definition of Done (when can implementation start?)

Design phase is complete when:
1. All 6 gates pass for every core page
2. Wireframes exist for every page × every state (empty, loading, loaded, error)
3. Mobile wireframes exist for Practice Mode and Dashboard
4. One end-to-end clickable prototype for Flow 1 (try demo) and Flow 2 (new course)
5. Competitive benchmark documented per page (what we do differently and WHY)
