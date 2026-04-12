# CourseHub Frontend Design Specification

> Follows methodology v2 design sequence: Practice → Course Detail → Exam Prep → Lesson → Dashboard → Onboarding → Auth → Phase 2

---

## Global Elements

### Navigation Bar (all pages)
| Element | Desktop | Mobile |
|---------|---------|--------|
| Logo | Left — "CourseHub" text, links to dashboard | Same |
| Course selector | Dropdown if inside a course page, shows current course title | Hamburger → slide-out |
| User avatar | Right — click opens dropdown: Settings, Sign Out | Same |
| Theme toggle | Sun/Moon icon next to avatar | Same |

**Dark mode**: Default to system preference. Toggle persists in localStorage.

### Toast System
- Position: bottom-center on mobile, bottom-right on desktop
- AI completion: "Questions generated — tap to view" (actionable)
- Error: red accent, auto-dismiss 5s, retry button inline
- Success: brand accent, auto-dismiss 3s

---

## Page 1: Practice Mode

**Route**: `/courses/[id]/practice`
**Device**: Mobile-first
**Primary action**: Answer the current question
**API**: `GET /api/questions?courseId=`, `POST /api/attempts`, `POST /api/bookmarks`, `POST /api/questions/[id]/feedback`

### Layout (Mobile — single column, full-width)

```
┌─────────────────────────────┐
│ ← Back to Course    3/15  ⋯ │  ← Header: back, progress, menu
├─────────────────────────────┤
│                             │
│  Question stem text here    │  ← Stem: 18px, zinc-900, max 60% viewport
│  (supports LaTeX via        │
│   KaTeX inline rendering)   │
│                             │
├─────────────────────────────┤
│                             │
│  ┌─────────────────────┐    │  ← Options (MCQ): 4 tappable cards
│  │ A. Option text       │    │     48px min height, 8px radius
│  └─────────────────────┘    │     touch target: full width
│  ┌─────────────────────────┐│
│  │ B. Option text         ││
│  └─────────────────────────┘│
│  ┌─────────────────────────┐│
│  │ C. Option text         ││
│  └─────────────────────────┘│
│  ┌─────────────────────────┐│
│  │ D. Option text         ││
│  └─────────────────────────┘│
│                             │
├─────────────────────────────┤
│      [ Check Answer ]       │  ← Primary CTA: brand accent, full-width
│                             │     disabled until selection made
└─────────────────────────────┘
```

### Layout (Desktop — centered, max-w-2xl)
Same structure but centered with whitespace. Question stem gets more vertical space. Options arranged in 2×2 grid for MCQ if options are short.

### Question Type Variants

| Type | Input Element | Submit |
|------|---------------|--------|
| multiple_choice | 4 radio-style cards (A/B/C/D) | "Check Answer" button |
| true_false | 2 large buttons: True / False | Tap = submit (no extra button) |
| fill_blank | Text input field (autofocus on mobile) | "Check Answer" button or Enter key |
| short_answer | Textarea (3 rows, expandable) | "Submit Answer" button |

### Header Elements
| Element | Purpose | Interaction |
|---------|---------|------------|
| ← Back | Return to course detail | Navigate to `/courses/[id]` |
| Progress | "3/15" — current / total | Static text |
| ⋯ Menu | Overflow: Bookmark, Report, Skip | Bottom sheet (mobile), dropdown (desktop) |

### Feedback State (after submission)

```
┌─────────────────────────────┐
│ ← Back to Course    3/15  ⋯ │
├─────────────────────────────┤
│                             │
│  Question stem text here    │
│                             │
├─────────────────────────────┤
│  ✓ Correct!                 │  ← Green banner (or ✗ Incorrect — red)
│                             │
│  Your answer: B             │
│  Correct answer: B          │  ← Only shown if wrong
│                             │
│  Explanation:               │  ← Revealed after attempt
│  The integral of x·eˣ dx   │     AI-generated badge + flag button
│  uses LIATE rule to choose  │
│  u = x...                   │
│                             │
│  📌 Bookmark  🚩 Report     │  ← Action row
├─────────────────────────────┤
│      [ Next Question → ]    │  ← Advance to next
└─────────────────────────────┘
```

**Correct answer animation**: Green flash on selected option (150ms), checkmark icon slides in. Subtle, not distracting.
**Wrong answer animation**: Selected option flashes red (150ms), correct option highlights green. Shake animation (200ms, 3px) on the wrong selection.

### Session Complete State

```
┌─────────────────────────────┐
│        Session Complete      │
├─────────────────────────────┤
│                             │
│     12/15 correct (80%)     │  ← Large, centered
│                             │
│  ██████████░░  80%          │  ← Progress bar, brand accent
│                             │
│  Topics to review:          │  ← Only if any wrong answers
│  • Taylor Series (0/2)      │     Clickable → filtered practice
│  • Power Series (1/3)       │
│                             │
├─────────────────────────────┤
│  [ Practice Weak Topics ]   │  ← Primary CTA
│  [ Back to Course ]         │  ← Secondary
└─────────────────────────────┘
```

### State Mapping

| State | What user sees |
|-------|---------------|
| **Empty** | "No questions yet. Generate questions from your outline?" → CTA links to Course Detail → Generate |
| **Loading** | Skeleton shimmer for question card (one card, not multiple) |
| **Answering** | Question + input + Check Answer button |
| **Feedback** | Answer result + explanation + bookmark/report |
| **Complete** | Session summary + weak topics + next action |
| **Error (network)** | "Couldn't submit answer. Your answer is saved locally." → Retry button |
| **Error (AI)** | Never happens here — questions are pre-generated |

### Keyboard Shortcuts (Desktop)
| Key | Action |
|-----|--------|
| 1/2/3/4 or A/B/C/D | Select MCQ option |
| Enter | Submit answer / Next question |
| B | Bookmark current question |
| S | Skip question |

### Accessibility
- `aria-live="polite"` on feedback region (announces correct/incorrect)
- MCQ options are `role="radiogroup"` with `role="radio"` children
- Focus moves to explanation after submission
- Fill-blank input has `aria-label="Your answer"`

---

## Page 2: Course Detail

**Route**: `/courses/[id]`
**Device**: Laptop-first
**Primary action**: Navigate to practice/lessons/exams
**API**: `GET /api/courses/[id]`, `GET /api/courses/[id]/outline`, `GET /api/courses/[id]/mastery`, `GET /api/questions?courseId=`, `GET /api/courses/[id]/lessons`, `GET /api/courses/[id]/exams`

### Layout (Desktop)

```
┌──────────────────────────────────────────────────────┐
│  ← Dashboard    MATH 232 — Calculus II    ⚙ Share    │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Dr. Joe · Spring 2026 · 30 knowledge points         │
│  ██████████████░░░░  58% mastered                    │
│                                                      │
├──────────────────────────────────────────────────────┤
│  [ Outline ]  [ Practice ]  [ Lessons ]  [ Exams ]   │  ← Tab bar
├──────────────────────────────────────────────────────┤
│                                                      │
│  (Tab content — see below)                           │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Course Header
| Element | Content | Notes |
|---------|---------|-------|
| Title | Course title (h1, 24px) | Editable inline on click |
| Meta | Professor · Semester · KP count | Gray text, 14px |
| Mastery bar | Overall mastery % | Brand accent fill, zinc track |
| Share button | Opens share dialog | Icon button, secondary |

### Tab: Outline

```
┌──────────────────────────────────────┐
│  📂 Week 1: Integration Techniques    │  ← Collapsible sections
│    📄 Integration by Parts      ██▓░  │  ← KP + mastery mini-bar
│    📄 Trig Integrals            ████  │     Green=mastered, yellow=practicing
│    📄 Trig Substitution         ░░░░  │     Gray=untested
│  📂 Week 2: Series               ▼   │
│  📂 Week 3: Power Series         ▼   │
│                                      │
│  [ + Add Section ]                   │  ← Ghost button, bottom
└──────────────────────────────────────┘
```

Each knowledge point row:
| Element | Purpose | Interaction |
|---------|---------|------------|
| Icon | 📄 for KP, 📂 for section | Static |
| Title | Knowledge point name | Click → expand inline: content preview + actions |
| Mastery bar | 4-segment mini bar (unseen/weak/reviewing/mastered) | Tooltip: "Practiced 3 times, 67% correct" |
| Actions (expanded) | Practice / View Lesson / Edit | Shown on expand |

### Tab: Practice

```
┌──────────────────────────────────────┐
│  22 questions · 4 types              │
│                                      │
│  [ Start Practice (all) ]            │  ← Primary CTA
│                                      │
│  Filter by topic:                    │
│  ┌────────────┐ ┌────────────────┐   │
│  │ Integration │ │ Trig Integrals │   │  ← Chip/toggle filters
│  └────────────┘ └────────────────┘   │
│  ┌────────────┐ ┌────────────────┐   │
│  │ Series     │ │ Power Series   │   │
│  └────────────┘ └────────────────┘   │
│                                      │
│  Filter by difficulty:               │
│  [ Easy ] [ Medium ] [ Hard ]        │
│                                      │
│  [ Generate More Questions ]         │  ← Secondary, triggers AI
│                                      │
│  AI-generated · 🚩 2 flagged         │  ← Trust signal
└──────────────────────────────────────┘
```

### Tab: Lessons

```
┌──────────────────────────────────────┐
│  5 lessons available                 │
│                                      │
│  ┌──────────────────────────────┐    │
│  │ Integration by Parts         │    │
│  │ 4 chunks · 12 min · ✓ done  │    │  ← Lesson card
│  └──────────────────────────────┘    │
│  ┌──────────────────────────────┐    │
│  │ Trig Substitution            │    │
│  │ 4 chunks · 15 min · ○ 2/4   │    │  ← In progress
│  └──────────────────────────────┘    │
│  ┌──────────────────────────────┐    │
│  │ Improper Integrals           │    │
│  │ Not generated yet            │    │  ← Ghost card
│  │ [ Generate Lesson ]          │    │
│  └──────────────────────────────┘    │
│                                      │
│  [ Generate All Lessons ]            │  ← Batch generate
└──────────────────────────────────────┘
```

### Tab: Exams

```
┌──────────────────────────────────────┐
│  Upcoming Exams                      │
│                                      │
│  ┌──────────────────────────────┐    │
│  │ 🔴 Midterm 3 · April 10      │    │  ← Red dot = <7 days
│  │    5 days away · 73% covered │    │
│  │    [ Start Exam Prep ]       │    │  ← Links to Exam Prep page
│  └──────────────────────────────┘    │
│                                      │
│  [ + Add Exam Date ]                │  ← Opens inline form
│                                      │
│  Past: Midterm 2 (March 11) ✓       │  ← Collapsed, gray
└──────────────────────────────────────┘
```

### State Mapping

| State | What user sees |
|-------|---------------|
| **Empty (new course)** | "Upload your syllabus to get started" → file upload area + paste text option |
| **Parsing** | Latency Ladder: "Analyzing your syllabus... (12s)" with stage labels |
| **Outline only** | Outline tab active, Practice/Lessons tabs show "Generate" CTAs |
| **Full** | All tabs populated with data |
| **Error** | Per-tab: "Couldn't load questions. [Retry]" inline, not full-page |

### Mobile Layout
- Tabs become scrollable horizontal pills
- Course header collapses: hide professor/semester, show only title + mastery
- Outline tree stays the same (indentation reduced)
- "Start Practice" becomes a floating FAB (bottom-right)

---

## Page 3: Exam Prep

**Route**: `/courses/[id]/exam-prep`
**Device**: Laptop-first
**Primary action**: Paste exam scope → get targeted questions
**API**: `POST /api/courses/[id]/exam-scope`, `POST /api/courses/[id]/exam-prep`, `GET /api/courses/[id]/mistake-patterns`, `GET /api/courses/[id]/export-anki`

### Layout

```
┌──────────────────────────────────────────────────────┐
│  ← Course    Exam Prep: Midterm 3 (April 10)         │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Step 1: Paste your exam scope                       │
│  ┌──────────────────────────────────────────────┐    │
│  │ Our 3rd midterm covers:                      │    │  ← Textarea
│  │ 5.3 Error bounds using improper integral...  │    │     min 4 rows
│  │ 5.5 Alternating Series...                    │    │     placeholder text
│  │ 5.6 Ratio and Root Tests...                  │    │     with example
│  └──────────────────────────────────────────────┘    │
│  [ Match Topics & Generate Questions ]               │  ← Primary CTA
│                                                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Step 2: Matched Topics (13/30 knowledge points)     │
│                                                      │
│  ✓ Improper Integrals                                │  ← Checkbox list
│  ✓ Infinite Series                                   │     User can deselect
│  ✓ Divergence and Integral Tests                     │
│  ✓ Comparison Tests                                  │
│  ✓ Alternating Series                                │
│  ✓ Ratio and Root Tests                              │
│  ✓ Power Series and Functions                        │
│  ...                                                 │
│                                                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Step 3: AI Generating Questions...                  │
│  Analyzing topic 3/6: "Comparison Tests" (18s)       │  ← Latency Ladder
│  ████████░░░░  3 of 6 topics done                    │     Real progress (topics)
│                                                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Step 4: 12 Questions Generated                      │
│  [ Start Exam Practice ]                             │  ← Primary CTA
│  [ Export to Anki ]                                  │  ← Secondary
│                                                      │
│  Your weak areas:                                    │
│  • Taylor Series — 42% mastery (worst)               │
│  • Alternating Series — 65% mastery                  │
│  [ Practice Weak Topics Only ]                       │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Key Design Decisions
1. **Single-page wizard** — all 4 steps on one scrollable page, not separate routes
2. **Real progress for AI** — topic-level progress is trackable (6 topics → bar advances by 1/6 each), unlike token-level inference
3. **Editable matches** — user can deselect incorrectly matched KPs before generation
4. **Weak areas** — shown after generation using mistake-patterns API data
5. **Anki export** — secondary action, downloads .txt file directly

### State Mapping

| State | What user sees |
|-------|---------------|
| **Entry** | Empty textarea + placeholder showing example scope text |
| **Matching** | Latency Ladder 0-10s range (scope matching is fast) |
| **Matched** | Checkbox list of KPs, primary CTA changes to "Generate Questions" |
| **Generating** | Topic-level progress bar (real, not fake) + elapsed time per topic |
| **Complete** | Question count + Start Practice CTA + weak areas + Anki export |
| **Error (AI)** | "Generation failed for 2 topics. 10 questions generated from 4 topics." → partial results + retry failed topics |

---

## Page 4: Lesson Viewer

**Route**: `/courses/[id]/lessons/[lessonId]`
**Device**: Laptop-first (reading), mobile-acceptable
**Primary action**: Read content, answer checkpoints
**API**: `GET /api/courses/[id]/lessons/[lessonId]/chunks`, `POST /api/courses/[id]/lessons/[lessonId]/progress`

### Layout

```
┌──────────────────────────────────────────────────────┐
│  ← Course    Lesson: Integration by Parts    2/4     │
├──────────────────────────────────────────────────────┤
│  ○───●───○───○                                       │  ← Chunk progress dots
├──────────────────────────────────────────────────────┤
│                                                      │
│  ## Concrete Example: Work Done by a Variable Force  │
│                                                      │
│  Imagine you're pushing a box along a surface...     │
│  The work done is $W = \int_0^5 F(x)\,dx$...        │  ← Markdown + KaTeX
│                                                      │
│  **Key terms**:                                      │
│  • **Work integral**: The total energy...            │  ← Expandable glossary
│  • **Variable force**: A force that changes...       │
│                                                      │
├──────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────┐            │
│  │ 📝 Checkpoint                        │            │
│  │                                      │            │
│  │ A spring has force constant k=3 N/m. │            │  ← Inline checkpoint
│  │ The work to stretch it from x=0 to  │            │     Same MCQ/fill-blank
│  │ x=2 is:                             │            │     UI as Practice Mode
│  │                                      │            │
│  │ ○ A. 3 J                            │            │
│  │ ○ B. 6 J                            │            │
│  │ ○ C. 12 J                           │            │
│  │ ○ D. 9 J                            │            │
│  │                                      │            │
│  │ [ Check ]                            │            │
│  └──────────────────────────────────────┘            │
│                                                      │
├──────────────────────────────────────────────────────┤
│              [ ← Prev ]  [ Next → ]                  │
└──────────────────────────────────────────────────────┘
```

### Chunk Navigation
- Progress dots at top: ○ = unvisited, ● = current, ✓ = completed
- Prev/Next buttons at bottom
- Swipe left/right on mobile
- Checkpoint must be answered to proceed (but "Skip" available)

### Chunk Content Elements
| Element | Rendering |
|---------|-----------|
| Markdown headings | h2 = 20px bold, h3 = 18px semibold |
| Math | KaTeX inline ($...$) and display ($$...$$) |
| Code | Syntax-highlighted code blocks (if CS course) |
| Key terms | Collapsible glossary section at bottom of content |
| Checkpoint | Bordered card, same interaction as Practice Mode questions |

### State Mapping

| State | What user sees |
|-------|---------------|
| **Loading** | Skeleton: heading shimmer + 3 paragraph shimmers + checkpoint card shimmer |
| **Generating (SSE)** | Chunks appear one by one as they stream in. Chunk 1 readable while 2-4 generate. |
| **Reading** | Markdown content + key terms + checkpoint |
| **Checkpoint answered** | Feedback inline (same as Practice), Next button enables |
| **Complete** | "Lesson complete! Mastery updated." → Back to Course or Next Lesson |

---

## Page 5: Dashboard

**Route**: `/` (root)
**Device**: Mobile-first
**Primary action**: Resume studying (algorithmic: nearest exam or weakest topic)
**API**: `GET /api/courses`, `GET /api/courses/[id]/exams`, `GET /api/courses/[id]/mastery`

### Layout (Mobile)

```
┌─────────────────────────────┐
│  CourseHub          🌙 👤   │
├─────────────────────────────┤
│                             │
│  Good evening, Sarah 👋     │
│                             │
│  ┌─────────────────────┐    │
│  │ 🔴 Midterm 3 in 5 days│   │  ← Urgent card (exam <7 days)
│  │ MATH 232 · 73% ready │    │     Red accent border
│  │ [ Start Exam Prep ]  │    │     Primary CTA
│  └─────────────────────┘    │
│                             │
│  📋 Review Queue            │
│  15 cards due · ~8 min      │  ← FSRS-driven daily review
│  [ Start Review ]           │
│                             │
├─────────────────────────────┤
│  My Courses                 │
│                             │
│  ┌─────────────────────┐    │
│  │ MATH 232 — Calc II  │    │
│  │ 30 KPs · 58% ██████░│    │  ← Course card
│  │ Midterm 3 in 5 days │    │     Mastery bar + next exam
│  └─────────────────────┘    │
│  ┌─────────────────────┐    │
│  │ CS 201 — Data Struct│    │
│  │ 24 KPs · 41% ████░░│    │
│  │ No upcoming exams   │    │
│  └─────────────────────┘    │
│                             │
│  [ + New Course ]           │  ← Ghost button
│                             │
├─────────────────────────────┤
│  💡 Weak Spots              │
│  Taylor Series (42%)        │  ← One-click to practice
│  Partial Fractions (55%)    │
│                             │
└─────────────────────────────┘
```

### Dashboard Sections (priority order)

| Section | When shown | Content |
|---------|-----------|---------|
| **Urgent exam card** | If exam in <7 days | Course name, days left, coverage %, Start Exam Prep CTA |
| **Review queue** | If FSRS has cards due | Count + estimated time + Start Review CTA |
| **My courses** | Always | Course cards with mastery bar, sorted by last activity |
| **Weak spots** | If any KP <60% mastery with ≥3 attempts | Top 3 weakest KPs, each clickable to filtered practice |
| **New course** | Always | Ghost button at end of course list |

### Course Card Elements
| Element | Content |
|---------|---------|
| Title | Course title, truncated at 40 chars |
| Meta | KP count · mastery % with mini bar |
| Next event | Nearest exam date or "No upcoming exams" |
| Tap action | Navigate to `/courses/[id]` |

### State Mapping

| State | What user sees |
|-------|---------------|
| **Empty (new user)** | Greeting + "Create your first course" card + "Or try a demo" link |
| **1 course, no data** | Course card with "Upload syllabus to get started" |
| **Active studying** | Urgent card (if exam) + review queue + courses + weak spots |
| **All mastered** | "You're on track! Review queue empty." + course list |

### Mobile vs Desktop
- Mobile: Single column, cards stack vertically, full-width
- Desktop: 2-column layout. Left (2/3): urgent + courses. Right (1/3): review queue + weak spots.
- Desktop max width: 1200px, centered

---

## Page 6: Onboarding

**Route**: `/welcome` (redirected to after first signup)
**Device**: Both
**Primary action**: Experience value before setup effort

### Flow

```
Step 1: Welcome
┌─────────────────────────────┐
│                             │
│  Upload your syllabus,      │
│  AI does the rest.          │
│                             │
│  Practice questions,        │
│  lessons, and exam prep     │
│  — generated from YOUR      │
│  course materials.          │
│                             │
│  [ Try a Demo Question ]    │  ← Primary: instant gratification
│  [ Create My Course ]       │  ← Secondary: setup flow
│                             │
└─────────────────────────────┘

Step 2 (if demo): Demo Practice
→ Show 3 pre-loaded demo questions (Calculus)
→ Same Practice Mode UI
→ After 3 questions: "Like it? Create your own course."

Step 3 (if create): Course Setup
→ Enter course title (required)
→ Upload syllabus PDF or paste text (required)
→ AI parses (Latency Ladder)
→ Review outline → Save
→ Redirect to Course Detail
```

### Key Design Decision
No tutorial/tour/walkthrough. The product teaches itself through use. The demo questions ARE the onboarding — they show exactly what the product does.

---

## Page 7: Auth

**Route**: `/login`
**Device**: Both
**Primary action**: Sign in quickly

### Layout

```
┌─────────────────────────────┐
│                             │
│       CourseHub             │
│   Study smarter with AI     │
│                             │
│  ┌─────────────────────┐    │
│  │ 🔵 Continue with     │    │  ← Google OAuth (primary)
│  │    Google            │    │
│  └─────────────────────┘    │
│                             │
│  ────── or ──────           │
│                             │
│  Email: [              ]    │
│  Password: [           ]    │
│  [ Sign In ]                │
│                             │
│  No account? [Sign Up]      │
│                             │
└─────────────────────────────┘
```

- Google SSO is primary (one click)
- Email/password is secondary (collapsed behind "or")
- Sign up is same form with extra "confirm password"
- After auth → redirect to Dashboard (existing user) or Onboarding (new user)

---

## Page 8: Phase 2 Pages

### 8a. AI Chat (`/courses/[id]/chat`)

```
┌──────────────────────────────────────┐
│  ← Course    AI Study Buddy          │
├──────────────────────────────────────┤
│                                      │
│  (message history, scrollable)       │
│                                      │
│  👤 What topics should I focus on    │
│     for the midterm?                 │
│                                      │
│  🤖 Based on your mastery data,      │
│     I'd recommend focusing on:       │
│     1. Taylor Series (42%)           │
│     2. Power Series (55%)            │
│     ...                              │  ← Streaming token-by-token
│                                      │
├──────────────────────────────────────┤
│  [ Type your question...     ] [→]   │  ← Input + send button
└──────────────────────────────────────┘
```

- Streaming display: tokens appear as received via SSE
- Messages support Markdown + LaTeX rendering
- "Stop generating" button appears during streaming
- Context: AI knows course outline + mastery data (shown in system prompt)
- Quick suggestions: "Explain [weak topic]", "Quiz me on [topic]", "What should I study next?"

### 8b. Notes (`/courses/[id]/notes`)

```
┌──────────────────────────────────────┐
│  ← Course    Notes                   │
├──────────────────────────────────────┤
│                                      │
│  [ 🎙 Voice Note ]  [ ✏️ Text Note ] │  ← Two creation modes
│                                      │
│  Recent Notes:                       │
│  ┌──────────────────────────────┐    │
│  │ Integration by Parts Notes   │    │
│  │ 4 key points · Matched: IBP  │    │
│  │ Apr 10 · voice               │    │
│  └──────────────────────────────┘    │
│                                      │
└──────────────────────────────────────┘
```

Voice note flow:
1. Tap 🎙 → browser mic permission → recording indicator
2. Stop → raw transcript shown
3. "Organize with AI" → Latency Ladder → organized note appears
4. Review: title, summary, key points, confusing points
5. Save → stored in DB, linked to matched KP

### 8c. Settings (`/settings`)

Minimal. Three sections:
| Section | Settings |
|---------|---------|
| Profile | Name, email (read-only from Supabase) |
| Preferences | Language (EN/ZH), Theme (system/light/dark) |
| Data | Export all data, Delete account |

No elaborate preference panels. Defaults should just work.

### 8d. Share & Fork

**Share dialog** (from Course Detail → Share button):
```
┌──────────────────────────────┐
│  Share this course           │
│                              │
│  [ Generate Share Link ]     │
│                              │
│  https://coursehub.app/      │
│  share/ab5d5db9a54cc3a9     │
│  [ Copy Link ]  [ Revoke ]  │
└──────────────────────────────┘
```

**Fork page** (`/share/[token]`):
- Shows course title, professor, semester, KP count
- "Fork to my account" button → creates copy
- No signup required to VIEW, but fork requires auth

---

## Component Inventory

### From shadcn/ui (use directly)
- Button (primary, secondary, ghost, destructive)
- Input, Textarea
- Card, CardHeader, CardContent
- Tabs, TabsList, TabsTrigger, TabsContent
- Dialog (for share, confirm delete)
- DropdownMenu (user avatar, overflow menus)
- Progress (mastery bars)
- Badge (question type, AI-generated indicator)
- Skeleton (loading states)
- Toast (notifications)
- Tooltip
- Collapsible (outline tree sections)
- RadioGroup (MCQ options — extended with custom styling)

### Custom Components (truly novel)
| Component | Why custom |
|-----------|-----------|
| QuestionCard | 4 question types with different inputs, feedback animations, bookmark/flag |
| OutlineTree | Recursive tree with mastery bars, drag-to-reorder (future), expand/collapse |
| LatencyIndicator | AI loading with elapsed timer + stage labels + background notification |
| ChunkReader | Markdown + KaTeX + checkpoint integration, swipe navigation |
| ExamCountdown | Red urgency card with days remaining + coverage percentage |
| MasteryBar | 4-color segmented bar (untested/weak/reviewing/mastered) |

---

## Route Map

| Route | Page | Auth Required |
|-------|------|--------------|
| `/` | Dashboard | Yes |
| `/login` | Auth | No |
| `/welcome` | Onboarding | Yes (just signed up) |
| `/demo` | Demo Practice (3 questions) | No |
| `/courses/[id]` | Course Detail | Yes |
| `/courses/[id]/practice` | Practice Mode | Yes |
| `/courses/[id]/lessons/[lessonId]` | Lesson Viewer | Yes |
| `/courses/[id]/exam-prep` | Exam Prep | Yes |
| `/courses/[id]/chat` | AI Chat | Yes |
| `/courses/[id]/notes` | Notes | Yes |
| `/settings` | Settings | Yes |
| `/share/[token]` | Share Preview / Fork | No (view), Yes (fork) |
| `/courses/[id]/history` | Attempt History | Yes |

---

## Appendix A: Accessibility Specification

### A1. Screen Reader Flows

**Practice Mode** (documented above):
- `aria-live="polite"` on feedback region
- `role="radiogroup"` for MCQ options
- Focus moves to explanation after submission

**Dashboard**:
- Course list: `role="list"` with `role="listitem"` for each course card
- Urgent exam card: `role="alert"` (auto-announced)
- Review queue: `aria-label="Review queue: 15 cards due, approximately 8 minutes"`
- Weak spots: `role="list"`, each item `aria-label="Taylor Series, 42% mastery, click to practice"`

**Course Detail**:
- Tab bar: `role="tablist"` with `role="tab"` + `aria-selected` per tab
- Outline tree: `role="tree"` with `role="treeitem"` + `aria-expanded` for collapsible sections
- Mastery bars: `role="progressbar"` with `aria-valuenow` (percentage) + `aria-label="Mastery: 58%"`

**Exam Prep**:
- Wizard steps: `aria-live="polite"` on the step indicator region (announces "Step 2: Matched 13 topics")
- Checkbox list: `role="group"` with `role="checkbox"` per KP
- Generation progress: `aria-live="assertive"` on stage label ("Analyzing topic 3 of 6")

**Lesson Viewer**:
- Chunk progress: `role="progressbar"` with `aria-valuenow` (current chunk index)
- New chunk arrival (SSE): `aria-live="polite"` on chunk content region
- Checkpoint: same ARIA pattern as Practice Mode questions
- Navigation: "Previous chunk" and "Next chunk" buttons with `aria-label`

**AI Chat**:
- Message list: `role="log"` with `aria-live="polite"` (new messages announced)
- Streaming tokens: `aria-live="off"` during streaming, switch to `"polite"` when complete
- Input: `aria-label="Type your question to the AI study assistant"`

**Auth**:
- Form: `role="form"` with `aria-label="Sign in"`
- Error messages: `role="alert"` for validation errors ("Invalid email address")

### A2. Keyboard Navigation

| Page | Key | Action |
|------|-----|--------|
| **All pages** | Tab | Move focus to next interactive element |
| **All pages** | Escape | Close modal/dropdown/sheet |
| **Dashboard** | Enter on course card | Navigate to course |
| **Dashboard** | Enter on "Start Review" | Open practice mode |
| **Course Detail** | Arrow Left/Right | Switch tabs |
| **Course Detail** | Enter on outline node | Expand/collapse |
| **Exam Prep** | Tab through wizard | Textarea → Submit → Checkboxes → Generate → Practice |
| **Lesson Viewer** | Arrow Left/Right | Previous/Next chunk |
| **Lesson Viewer** | Enter on checkpoint option | Select option |
| **AI Chat** | Enter | Send message |
| **AI Chat** | Shift+Enter | Newline in input |

### A3. Reduced Motion

**All animations respect `prefers-reduced-motion: reduce`:**

| Animation | Default | Reduced Motion |
|-----------|---------|---------------|
| Correct answer green flash | 150ms flash + checkmark slide | Instant color change, no slide |
| Wrong answer shake | 200ms shake + red flash | Instant color change, no shake |
| Page transitions | 300ms ease-out slide | Instant swap, no transition |
| Skeleton shimmer | Shimmer animation loop | Static gray blocks (no animation) |
| Toast entrance | Slide up 200ms | Instant appear |
| Tab content switch | Fade 150ms | Instant swap |
| Chunk swipe (Lesson) | Slide left/right 300ms | Instant swap |

Implementation: wrap all motion in `motion-safe:` Tailwind modifier or check `window.matchMedia('(prefers-reduced-motion: reduce)')`.

---

## Appendix B: Performance Budget

### Targets
| Metric | Target | Measurement |
|--------|--------|-------------|
| LCP | <2.5s | Lighthouse on 4G throttle |
| FID / INP | <200ms | Real user monitoring |
| CLS | <0.1 | No layout shift during AI loading |
| Initial bundle (gzipped) | <200KB | `next build` output |
| Per-route chunk | <50KB | Code splitting per route |

### Code Splitting Strategy
| Route | Lazy-loaded deps | Reason |
|-------|-----------------|--------|
| `/courses/[id]/practice` | KaTeX (28KB gzip) | Only needed if questions have LaTeX |
| `/courses/[id]/lessons/[id]` | KaTeX + Markdown renderer | Heavy rendering deps |
| `/courses/[id]/chat` | Streaming parser | Only on chat page |
| `/courses/[id]/notes` | Web Speech API polyfill | Only on notes page |
| All routes | shadcn/ui components | Tree-shaken, only import used components |

### KaTeX Strategy
- Don't import globally. Import dynamically on pages that render math.
- Detect if question/lesson contains `$` or `$$` → conditionally import KaTeX renderer.
- Fallback: show raw LaTeX text with a "loading math..." indicator.

### Image / Font Strategy
- Font: Inter via `next/font/google` (automatic subsetting, no layout shift)
- Icons: Lucide tree-shaken imports (not the full icon pack)
- No images in core UI (no hero images, no illustrations)

---

## Appendix C: Missing States (Gap Fixes)

### Dashboard — Loading State
```
┌─────────────────────────────┐
│  CourseHub          🌙 👤   │
├─────────────────────────────┤
│  Good evening                │  ← Greeting (instant, no API)
│                             │
│  ┌─────────────────────┐    │
│  │ ░░░░░░░░░░░░░░░░░░░ │    │  ← Skeleton cards (3)
│  │ ░░░░░░  ░░░░░░░░░░░ │    │     shimmer animation
│  └─────────────────────┘    │
│  ┌─────────────────────┐    │
│  │ ░░░░░░░░░░░░░░░░░░░ │    │
│  └─────────────────────┘    │
└─────────────────────────────┘
```

### Dashboard — Error State
"Couldn't load your courses. [Retry]" — inline message replacing course list, greeting still visible.

### Auth — Loading State
- OAuth redirect: "Redirecting to Google..." with spinner
- Email submit: Button shows loading spinner, disabled

### Auth — Error States
- Invalid credentials: Red alert below form: "Email or password is incorrect."
- OAuth failure: "Google sign-in failed. Try again or use email."
- Already logged in visiting /login: Auto-redirect to dashboard

### Lesson Viewer — Error State
- Chunk load failure: "Couldn't load this section. [Retry]" inline
- Checkpoint submit failure: "Couldn't check your answer. [Try Again]" inline, answer preserved

### Edge Cases by Page

**Practice Mode**:
- 0 questions after AI generation: "AI couldn't generate questions for this topic. Try adding more detail to the knowledge point, or report this issue." + [Edit Outline] button
- Very long question text (>500 chars): Scrollable stem area with max-height 50vh
- Phone landscape: Same layout (single column), question text gets more horizontal space

**Course Detail**:
- 50+ KPs in outline: Virtual scrolling for outline tree (only render visible nodes)
- 0 questions after generation: Practice tab shows "No questions generated. AI may need more specific knowledge points." + [Regenerate] button

**Exam Prep**:
- 0 KP matches: "Couldn't match any topics. Try being more specific, or manually select from the list below." + show full KP list as checkboxes
- All KPs match: "All 30 topics matched! This looks like a comprehensive exam." + proceed normally
- Very long scope text (>5000 chars): Textarea scrollable, no truncation. API handles the full text.

**Dashboard**:
- 10+ courses: Show first 6, "Show all (12)" expandable link
- No exams at all: Hide urgent card section entirely, don't show empty "No upcoming exams"

---

## Appendix D: Attempt History Page

**Route**: `/courses/[id]/history`
**Device**: Both
**Purpose**: Review past attempts, identify patterns

### Layout

```
┌──────────────────────────────────────┐
│  ← Course    Attempt History         │
├──────────────────────────────────────┤
│                                      │
│  Last 7 days: 45 attempts, 78% avg   │
│                                      │
│  Filter: [All] [Correct] [Wrong]     │
│                                      │
│  ┌──────────────────────────────┐    │
│  │ ✓ "Find the area of the..." │    │  ← Attempt row
│  │   MCQ · Correct · 3s ago     │    │     Tap to expand
│  │   Topic: Area Between Curves │    │     Shows full Q+A+explanation
│  └──────────────────────────────┘    │
│  ┌──────────────────────────────┐    │
│  │ ✗ "The series Σ 1/n² ..."   │    │
│  │   Short answer · Wrong · 1h  │    │
│  │   Your: "diverges"          │    │
│  │   Correct: "converges to π²/6" │  │
│  └──────────────────────────────┘    │
│  ...                                 │
└──────────────────────────────────────┘
```

**Access**: Course Detail → overflow menu → "Attempt History" (3 clicks from dashboard)

---

## Appendix E: Click-by-Click Flow Traces

### Flow 3: Return to Study
1. User opens app → `/` (Dashboard)
2. Sees "Review Queue: 15 cards due, ~8 min" → taps **[Start Review]**
3. → `/courses/[auto-selected]/practice` with FSRS-due questions
4. Answers questions one by one (Practice Mode loop)
5. Session complete → sees score + weak topics
6. Taps **[Back to Course]** → `/courses/[id]` (Course Detail)
7. Sees updated mastery bar

### Flow 4: Exam Cram
1. User opens app → `/` (Dashboard)
2. Sees urgent card "Midterm 3 in 5 days" → taps **[Start Exam Prep]**
3. → `/courses/[id]/exam-prep`
4. Pastes exam scope text in textarea → taps **[Match Topics & Generate Questions]**
5. Waits 5-10s for matching (Latency Ladder: stage labels) → sees 13 matched KPs
6. Reviews checkboxes, deselects 1 irrelevant match → taps **[Generate Questions]**
7. Waits 60-120s (Latency Ladder: topic-level progress, "3/6 topics done") → sees 12 questions generated
8. Taps **[Start Exam Practice]** → `/courses/[id]/practice` (filtered to exam questions)
9. After session → sees weak areas → taps **[Practice Weak Topics Only]**

### Flow 5: Review Progress
1. User opens app → `/` (Dashboard)
2. Sees course card "MATH 232 · 58% mastered" → taps card
3. → `/courses/[id]` (Course Detail, Outline tab default)
4. Sees mastery mini-bars per KP → identifies "Taylor Series ░░░░" as weakest
5. Expands "Taylor Series" → taps **[Practice]**
6. → `/courses/[id]/practice` (filtered to Taylor Series questions)
7. Answers 5 questions → session complete: "4/5 correct"
8. Taps **[Back to Course]** → mastery bar updated: "Taylor Series ██░░" (improved)

---

## Appendix F: Color System

### Light Mode
| Token | Hex | Usage | Contrast on white |
|-------|-----|-------|-------------------|
| `--text-primary` | `#18181b` (zinc-900) | Body text, headings | 16.8:1 ✅ |
| `--text-secondary` | `#71717a` (zinc-500) | Meta text, labels | 4.6:1 ✅ |
| `--text-on-accent` | `#ffffff` | Text on brand accent | depends on accent |
| `--bg-primary` | `#ffffff` | Page background | — |
| `--bg-secondary` | `#f4f4f5` (zinc-100) | Card backgrounds, sections | — |
| `--bg-accent` | `#2563eb` (blue-600) | Primary CTA | 4.7:1 with white text ✅ |
| `--border` | `#e4e4e7` (zinc-200) | Card borders, dividers | — |
| `--success` | `#16a34a` (green-600) | Correct answer | 4.5:1 on white ✅ |
| `--error` | `#dc2626` (red-600) | Wrong answer, errors | 4.6:1 on white ✅ |
| `--warning` | `#ca8a04` (yellow-600) | Reviewing mastery | 3.3:1 ⚠️ (use with zinc-900 text) |
| `--mastery-untested` | `#d4d4d8` (zinc-300) | Untested KP bar segment | — |
| `--mastery-weak` | `#dc2626` (red-600) | Weak KP bar segment | — |
| `--mastery-reviewing` | `#ca8a04` (yellow-600) | Reviewing KP bar segment | — |
| `--mastery-mastered` | `#16a34a` (green-600) | Mastered KP bar segment | — |

### Dark Mode
| Token | Hex | Usage |
|-------|-----|-------|
| `--text-primary` | `#fafafa` (zinc-50) | Body text |
| `--text-secondary` | `#a1a1aa` (zinc-400) | Meta text |
| `--bg-primary` | `#09090b` (zinc-950) | Page background |
| `--bg-secondary` | `#18181b` (zinc-900) | Card backgrounds |
| `--bg-accent` | `#3b82f6` (blue-500) | Primary CTA (brighter for dark bg) |
| `--border` | `#27272a` (zinc-800) | Card borders |

All accent/success/error colors verified ≥4.5:1 contrast against their respective backgrounds.
