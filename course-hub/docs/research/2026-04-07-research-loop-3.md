# Research Loop 3 — 72-Hour Exam Sprint: Study Science, Quick Wins, Tooltip UX, Daily Reports

**Date**: 2026-04-07
**Context**: Calculus II exam April 10 (3 days away). Phase 5 complete (Exam Scope Filter + Term Cards shipped). Stabilization mode.
**Previous research**: `research-loop-2.md` covered streamObject deprecation, FSRS migration plan, monitoring stack, basic 72-hour strategy.
**Focus**: NEW findings not covered before. 4 topics: (1) last-72-hour study science, (2) quick-win features for exam sprint, (3) term tooltip UX, (4) daily progress report design.
**Searches conducted**: 14

---

## 1. Last 72 Hours Before Exam: What the Science Actually Says

Previous research covered basic cramming-vs-spacing and Pomodoro timing. This section adds **three new dimensions**: sleep neuroscience, interleaving, and the pretesting effect.

### 1.1 Sleep: The Non-Negotiable Multiplier

- **Source**: [Systems Memory Consolidation During Sleep (PMC, 2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12576410/) | [Sleep Deprivation Meta-Analysis (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8893218/) | [Sleep Consistency and Grades (Nature, 2025)](https://www.nature.com/articles/s41598-025-33775-0)
- **Key findings**:
  1. **Triple coupling mechanism**: Memory consolidation during sleep requires the coupling of slow oscillations + sleep spindles + hippocampal sharp-wave ripples. This triple coupling transfers memories from hippocampus to neocortex. Disrupted sleep breaks this chain.
  2. **Same-day consolidation is critical**: If you sleep on the same day as training, long-term memory transfer is significantly better. Studying at 2 AM and sleeping at 3 AM is worse than studying at 9 PM and sleeping at 11 PM -- the brain needs time to begin the consolidation cycle.
  3. **Weekday sleep consistency predicts grades**: A 2025 Nature study found that stable, efficient weekday sleep is the strongest sleep-related predictor of academic outcomes -- not total hours, but **consistency**.
  4. **Naps are real**: 20-30 min afternoon naps produce medium-to-large effects on memory retention vs. active wakefulness. A nap after a morning study session genuinely helps.
  5. **Sleep deprivation before learning is worse than after**: The meta-analysis found that sleep deprivation *before* the exam (reducing encoding capacity) is more damaging than poor sleep after studying.
- **Recommendation for CourseHub user**:
  - Sleep at the **same time** all 3 nights (consistency > duration)
  - Study the hardest material in the morning, review in the evening, sleep by 11 PM
  - Take a 20-min nap after the midday study session on Day 1 and Day 2
  - On exam morning (April 10): wake at normal time, do NOT set an early alarm to cram

### 1.2 Interleaving: Mix Problem Types, Don't Block Them

- **Source**: [Interleaved Practice Improves Mathematics Learning (ERIC/Rohrer)](https://files.eric.ed.gov/fulltext/ED557355.pdf) | [IES: Interleaved Mathematics Practice](https://ies.ed.gov/use-work/awards/interleaved-mathematics-practice) | [How Interleaving Works (2025)](https://richardjamesrogers.com/2025/03/09/how-interleaving-works-universal-strategies-for-secondary-school-classroom-practice/) | [RetrievalPractice.org: Interleaving](https://www.retrievalpractice.org/interleaving)
- **Key findings**:
  1. **Nearly 2x exam performance**: 4th graders doing interleaved math problems scored 77% vs 38% for blocked practice on the same exam. The effect is large and replicated.
  2. **Why it works for math specifically**: Interleaving forces "strategy selection" -- you must identify which technique to use (u-sub vs integration by parts vs trig sub), not just execute a technique you already know is needed. This is exactly what exams test.
  3. **The discrimination hypothesis**: The benefit comes from juxtaposing different problem types, forcing the learner to discriminate between them. Blocked practice never exercises this discrimination skill.
  4. **Spacing is a bonus**: Interleaving naturally spaces out same-type problems, giving a double benefit (interleaving + spacing) in one study design.
- **Recommendation for CourseHub**:
  - **Immediate (for the student)**: When reviewing in CourseHub, don't filter to a single topic. Use the full review queue that mixes convergence tests, integration techniques, and series problems.
  - **Post-exam feature**: Add an "interleaved practice" mode that deliberately shuffles problem types within a review session, even when the user has filtered to a specific chapter. Surface a prompt: "Mix it up? Interleaved practice improves exam scores by ~40%."

### 1.3 The Pretesting Effect: Failing First Helps

- **Source**: [The Pretesting Effect (PMC, 2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12292081/) | [Retrieval Practice in Mathematics (Springer, 2025)](https://link.springer.com/article/10.1007/s10763-025-10607-1) | [Retrieval Practice Evidence from College Sample (ResearchGate)](https://www.researchgate.net/publication/393114908_Enhancing_Final_Exam_Performance_Through_Retrieval_Practice_Evidence_From_a_Diverse_College_Sample)
- **Key findings**:
  1. **Even wrong answers help**: Testing yourself on material you haven't studied yet ("pretesting") improves subsequent learning compared to just studying. The failed retrieval attempt primes the brain to encode the correct answer more deeply.
  2. **Feedback is essential**: The pretesting effect requires corrective feedback. Without feedback, wrong guesses can become entrenched. With feedback, the effect is robust.
  3. **Retrieval practice narrows achievement gaps**: A 2025 Springer study found that retrieval practice particularly benefits students who were initially lower-performing in mathematics.
  4. **Delayed feedback slightly outperforms immediate**: Counter-intuitively, slightly delayed feedback (even 10-30 seconds) produces stronger learning than instant correction.
- **Recommendation for CourseHub**:
  - The existing "show answer after attempt" flow is correct. Consider adding a brief delay (5-10 seconds of thinking time) before showing the correct answer.
  - **Quick win idea**: Add a "Pre-test" mode for exam prep -- show questions from topics not yet studied, let the user attempt them, then show explanations. This primes learning for subsequent study sessions.

### 1.4 Consolidated 72-Hour Protocol (Updated)

This supersedes the Day 1-2-3 plan in `research-loop-2.md` with new interleaving and sleep science.

| Day | Morning (9-12) | Afternoon (1-4) | Evening (7-9:30) | Night |
|-----|----------------|-----------------|-------------------|-------|
| **Apr 7** | Interleaved review: mix all Calc II topics, lowest-retrievability first | 20-min nap, then drill weakest topics identified in morning | Light re-review of morning errors only | Sleep by 11 PM |
| **Apr 8** | Interleaved practice: focus on topics you got wrong yesterday | 20-min nap, then work practice problems from Paul's Online Notes | Timed practice: simulate exam conditions (50 min, no notes) | Sleep by 11 PM |
| **Apr 9** | Light review only (30-45 min). Review personal error notes from Day 1-2 | Logistics prep. Light exercise. NO new material | Relaxation. No studying after 8 PM | Sleep by 10:30 PM |
| **Apr 10** | Breakfast. 10-min formula review if allowed. No cramming | **EXAM** | -- | -- |

---

## 2. Quick-Win Features for Exam Sprint (<2 Hours Each)

Previous research identified exam mode params and coverage dashboard. This section focuses on **small, high-impact features** not yet discussed.

### 2.1 Auto-Generated "Cheat Sheet" / Formula Summary

- **Source**: [MyLens AI Cheatsheet Creator](https://mylens.ai/ai-cheatsheet-creator) | [Inkfluence AI Study Guide Generator](https://www.inkfluenceai.com/ai-study-guide-generator) | [How to Make a Cheat Sheet (MoreExams)](https://moreexams.com/blog/how-to-make-a-cheat-sheet)
- **Key findings**:
  1. AI-generated cheat sheets work by extracting key concepts, definitions, and formulas from source material, then organizing into a scannable format.
  2. Best practice: Let AI generate the initial sheet, then **the student customizes** by removing known items and adding personal mnemonics. The act of customization is itself a learning activity.
  3. Export formats matter: PDF for printing, responsive HTML for phone review during commute.
- **CourseHub implementation** (est. 1.5 hours):
  - Add a "Generate Review Sheet" button on the course page
  - Use existing qwen3.5-plus + `streamText` to generate a condensed summary of all terms + formulas from the exam-scoped outline
  - Output as printable HTML with `@media print` styles
  - Input: the existing outline data + term explanations already in the system
  - This reuses existing AI infrastructure, no new APIs needed

### 2.2 Mistake Pattern Analysis ("Your Weak Spots")

- **Source**: [Automated Identification of Logical Errors (EDM 2025)](https://educationaldatamining.org/EDM2025/proceedings/2025.EDM.long-papers.85/index.html) | [AI in Student Management (Nature, 2025)](https://www.nature.com/articles/s41598-025-19159-4) | [Prediction and Correction of Wrong Learning Strategies (ResearchGate)](https://www.researchgate.net/publication/336932516_Data_Analysis_for_the_prediction_and_correction_of_students'_wrong_learning_strategies)
- **Key findings**:
  1. **Distinguish carelessness from misunderstanding**: Models that track multiple attempts can tell if a student made a one-time slip vs. has a persistent misconception. The pattern (correct -> wrong -> correct) is carelessness; (wrong -> wrong -> wrong) is misunderstanding.
  2. **Temporal features matter**: When a student makes errors (early vs. late in study) is as informative as what errors they make.
  3. **Simple heuristics work**: You don't need ML. Count wrong answers per topic, identify topics with >50% error rate, surface those. A simple bar chart of "% correct by topic" is surprisingly effective.
- **CourseHub implementation** (est. 1 hour):
  - Parse existing localStorage FSRS data to extract per-topic error rates
  - Group questions by outline section/chapter
  - Display a simple "Weak Spots" card on the review page: topic name + error rate + "Review now" link
  - No AI needed -- pure client-side data aggregation from existing review history

### 2.3 Confidence Calibration ("How Well Do You Know This?")

- **Source**: [Metacognitive Monitoring (Structural Learning)](https://www.structural-learning.com/post/metacognitive-monitoring-fixing-student) | [Calibration Discrepancy Predicts Strategy Use (Springer, 2025)](https://link.springer.com/article/10.1007/s40593-025-00514-5) | [Metacognitive Accuracy (Shyam Barr)](https://www.shyambarr.com.au/blog/metacognitive-accuracy-and-the-self-regulated-learner)
- **Key findings**:
  1. **The "illusion of knowing"**: Students routinely overestimate their readiness. Poor calibration leads to studying easy material and neglecting hard material -- the exact opposite of what's needed.
  2. **JOL (Judgment of Learning)**: Have the student rate their confidence (1-5) before answering. Compare with actual correctness. Show the gap. This gap visualization is one of the most powerful metacognitive interventions.
  3. **Feedback improves calibration**: Simply showing students their prediction vs. actual performance over time reduces overconfidence significantly.
  4. **Calibration predicts strategy use**: A 2025 Springer study found that students who see their calibration discrepancy are more likely to adopt effective study strategies.
- **CourseHub implementation** (est. 1.5 hours):
  - Before showing the question, add a "How confident are you?" slider (1-5)
  - After answering, show: "You said 4/5 confident, but got it wrong. This topic needs more review."
  - Aggregate: show a calibration chart (confidence vs. accuracy per topic)
  - This pairs naturally with FSRS -- cards where confidence is high but accuracy is low are the most dangerous blind spots

### 2.4 Priority Ranking of Quick Wins

| Feature | Effort | Impact on Exam | Implementation Complexity | Verdict |
|---------|--------|---------------|--------------------------|---------|
| Mistake Pattern Analysis | 1 hr | **High** -- directly targets weak spots | Low (client-side only) | **Build now** |
| Confidence Calibration | 1.5 hr | **High** -- fixes "illusion of knowing" | Low (UI + localStorage) | **Build now** |
| Auto-Generated Review Sheet | 1.5 hr | **Medium** -- useful but passive | Medium (AI generation + print CSS) | Build if time permits |
| Pre-test Mode | 2 hr | **Medium** -- primes learning | Medium (new question flow) | Post-exam |

---

## 3. Term Tooltip UX Best Practices

CourseHub just shipped inline term explanation tooltips. This section covers what the UX research says about doing them well.

### 3.1 Tooltip vs. Popover: Choose the Right Pattern

- **Source**: [Tooltip vs Popover (Design Encyclopedia)](https://design-encyclopedia.com/?T=Tooltip+Vs+Popover) | [Carbon Design System: Tooltip, ToggleTip, Popover, Disclosure](https://github.com/carbon-design-system/carbon/issues/9901) | [IxDF: Progressive Disclosure (2026)](https://ixdf.org/literature/topics/progressive-disclosure)
- **Key findings**:
  1. **Tooltips** = brief, supplementary, non-essential info. Appear on hover/focus. Disappear when you move away. Max ~150 characters.
  2. **Popovers** = richer content, interactive elements, remain until dismissed. Use for content that users need to read or interact with.
  3. **For term explanations**: A term definition is richer than a tooltip label but simpler than a full modal. The right pattern is a **popover triggered by click/tap** (not hover), with a dismiss button.
  4. **Progressive disclosure**: Show the term inline (highlighted), click to expand explanation, optionally click "Learn more" for full context. Three levels of depth.
- **Recommendation for CourseHub**:
  - Current tooltips should be **click-triggered popovers**, not hover tooltips (hover doesn't work on mobile, and definitions are too long for transient tooltips)
  - Add a visible "X" close button on the popover
  - Include a "Mark as known" action button inside the popover

### 3.2 Mobile UX: Thumb Zone and Positioning

- **Source**: [Mobile-First UX Design 2026 (Trinergi)](https://www.trinergydigital.com/news/mobile-first-ux-design-best-practices-in-2026) | [Tooltips for Mobile Apps (NudgeNow)](https://www.nudgenow.com/blogs/tooltips-mobile-user-experience) | [NN/g: Instructional Overlays for Mobile](https://www.nngroup.com/articles/mobile-instructional-overlay/)
- **Key findings**:
  1. **Hover doesn't exist on touch**: Any tooltip that relies on hover is invisible on mobile. Must use tap/click.
  2. **Position within thumb zone**: On mobile, popovers should appear below the term (if term is in top half of screen) or above (if in bottom half). Never obscure the term itself.
  3. **Full-width on small screens**: On phones (<640px), term popovers should expand to near-full-width at the bottom of the screen (bottom sheet pattern), not a tiny floating card.
  4. **One popover at a time**: If the user taps a second term, close the first popover before opening the second. Stacking popovers creates confusion.
  5. **Backdrop dimming**: Dim the background slightly when a popover is open to focus attention.
- **Recommendation for CourseHub**:
  - Desktop: floating popover positioned with `@floating-ui/react` (already standard in the ecosystem)
  - Mobile: slide-up bottom sheet with term name, definition, and action buttons
  - Implement "one at a time" logic -- close any open popover when a new one opens

### 3.3 Animation and Timing

- **Source**: [Accessible Tooltips & Popovers (Accesify)](https://www.accesify.io/blog/accessible-tooltips-popovers-aria-roles-triggers-timing-control/) | [Tippy.js Documentation](https://atomiks.github.io/tippyjs/) | [HTML Popover API (Frontend Masters)](https://frontendmasters.com/blog/using-the-popover-api-for-html-tooltips/)
- **Key findings**:
  1. **Entry animation**: Fade-in over 150-200ms. Avoid bounce or slide -- they're distracting in an educational context.
  2. **Exit animation**: Fade-out over 100-150ms. Faster exit than entry feels natural.
  3. **Delay on hover (if used)**: 300-500ms delay before showing. Prevents accidental triggers when scanning text.
  4. **No delay on click**: Click-triggered popovers should appear instantly (<100ms). Delay on intentional click feels broken.
  5. **Arrow pointing to trigger**: A small arrow/caret connecting the popover to the term helps the user understand what the explanation refers to.
  6. **Native `popover` API**: The HTML `popover` attribute (2024 baseline) handles dismiss-on-click-outside, stacking context, and top-layer rendering natively. No JS library needed for basic positioning.
- **Recommendation for CourseHub**:
  - Use CSS `transition: opacity 150ms ease-out` for entry, `100ms` for exit
  - Include an arrow/caret pointing to the highlighted term
  - Consider using the native Popover API (`popover` attribute) for automatic light-dismiss behavior
  - Tippy.js or `@floating-ui/react` for smart positioning if the native API doesn't handle edge cases

### 3.4 "Mark as Known" Mechanics

- **Source**: [Appcues: Tooltips UX](https://www.appcues.com/blog/tooltips) | [LogRocket: Designing Better Tooltips](https://blog.logrocket.com/ux-design/designing-better-tooltips-improved-ux/) | [NN/g: Tooltip Guidelines](https://www.nngroup.com/articles/tooltip-guidelines/) | [UserPilot: Tooltip Best Practices](https://userpilot.com/blog/tooltip-best-practices/)
- **Key findings**:
  1. **Don't bombard**: If the user has seen the same tooltip 3+ times and dismissed it, stop showing it automatically. This is the core insight behind "mark as known."
  2. **Two-tier approach**: (a) Auto-hide terms the user has dismissed 3+ times. (b) Let users explicitly "mark as known" to immediately stop highlighting.
  3. **Reversibility**: Always provide a way to un-mark terms (e.g., a "Show all terms" toggle in settings). Users sometimes mark things known prematurely.
  4. **Visual differentiation**: Known terms should lose their highlight styling. Unknown terms keep a subtle dotted underline or background color. This gives a visual progress indicator -- as the lesson text loses its highlights, the student sees progress.
  5. **Integrate with SRS**: A "mark as known" action should feed into the FSRS data. Mark-as-known = a successful recall event (rating: "Easy"). Mark-as-unknown = a failed recall (rating: "Again"). This connects the tooltip system to the spaced repetition engine.
- **Recommendation for CourseHub**:
  - Add "I know this" button inside the term popover
  - Store known/unknown status in localStorage (same store as FSRS data)
  - Known terms: remove dotted underline, show them as plain text. User can re-enable via a "Show all terms" toggle.
  - Integrate with FSRS: "I know this" = `Rating.Easy`, popover dismiss without marking = no FSRS event, looking up a term you marked as known = implicit `Rating.Again`

### 3.5 Accessibility

- **Source**: [Accessibility in UI/UX 2025 (Orbix)](https://www.orbix.studio/blogs/accessibility-uiux-design-best-practices-2025) | [Tooltip Pattern (UX Patterns for Developers)](https://uxpatterns.dev/patterns/content-management/tooltip) | [Accessible Tooltips (Accesify)](https://www.accesify.io/blog/accessible-tooltips-popovers-aria-roles-triggers-timing-control/)
- **Key findings**:
  1. **`role="tooltip"`** on the popover element, `aria-describedby` on the trigger linking to the tooltip ID
  2. **Keyboard accessible**: Tab to the term, Enter/Space to open, Escape to close
  3. **Focus trap**: When popover contains interactive elements ("Mark as known" button), focus should move into the popover and cycle within it
  4. **Sufficient contrast**: Popover background must meet WCAG 2.1 AA contrast ratio (4.5:1 for text)
  5. **Screen reader announcement**: When popover opens, screen reader should announce the term definition
- **Recommendation for CourseHub**:
  - Add `role="tooltip"`, `aria-describedby`, and keyboard handlers
  - Ensure the "Mark as known" button is focusable and has an `aria-label`
  - Test with VoiceOver on macOS

---

## 4. Daily Progress Report Design: "Private Tutor" Briefing

Previous research didn't cover this topic. This is a full analysis.

### 4.1 What Top Platforms Show in Daily Reports

#### Duolingo

- **Source**: [Duolingo Gamified Success (SensorTower)](https://sensortower.com/blog/duolingos-gamified-success-a-language-learning-triumph) | [Duolingo Case Study 2025 (Young Urban Project)](https://www.youngurbanproject.com/duolingo-case-study/) | [Duolingo Gamification (StriveCloud)](https://www.strivecloud.io/blog/gamification-examples-boost-user-retention-duolingo) | [How Duolingo Reignited Growth (Lenny's Newsletter)](https://www.lennysnewsletter.com/p/how-duolingo-reignited-user-growth)
- **Key metrics shown**:
  1. **Streak count** (consecutive days of practice) -- the #1 engagement driver
  2. **XP earned today** vs. daily goal
  3. **League position** (weekly leaderboard, 10 tiers up to Diamond)
  4. **Duolingo Score** (2025 launch) -- a single number representing overall language level, shareable on LinkedIn
  5. **Hearts remaining** (mistake budget)
- **Design insights**:
  - Duolingo's daily engagement comes from **loss aversion** (don't break the streak) + **social comparison** (leaderboard)
  - 32% of 103M MAU engage daily -- proving the model works
  - The redesigned "chest" experience gamifies daily rewards with animation and delight

#### Khan Academy

- **Source**: [Khan Academy Activity Overview Report](https://support.khanacademy.org/hc/en-us/articles/360031052391) | [Khan Academy Self-Assessment Blog](https://blog.khanacademy.org/students-need-better-self-assessment-tools-khan/) | [Khan Academy Learning Dashboard Blog](https://blog.khanacademy.org/introducingthe-learning-dashboard/)
- **Key metrics shown**:
  1. **Mastery level per skill**: Attempted -> Practiced -> Level 1 -> Level 2 -> Mastered (5-tier progression)
  2. **Activity tab**: Time spent, skills practiced, exercises completed (per day/week)
  3. **Skills tab**: Grid of all skills in a course with mastery color coding
  4. **Energy points + badges** earned
- **Design insights**:
  - Khan Academy's 2025 blog explicitly states "students need better self-assessment tools" -- they recognize the metacognitive gap
  - The mastery grid gives a **coverage map** that shows what's been touched and what hasn't
  - Teacher-facing reports are more detailed (scores, completion %) than student-facing ones

#### Anki (SRS-Specific)

- **Source**: [Review Heatmap Plugin (AnkiWeb)](https://ankiweb.net/shared/info/1771074083) | [Review Heatmap Wiki (GitHub)](https://github.com/glutanimate/review-heatmap/wiki/Use) | [Anki Heatmap Guide (WillPeachMD)](https://willpeachmd.com/anki-heatmap)
- **Key metrics shown**:
  1. **Review heatmap**: GitHub-style contribution graph. Green = past reviews, gray = future scheduled reviews. Darker = more reviews.
  2. **Current streak** (consecutive days with reviews)
  3. **Daily average** reviews completed
  4. **Forecast**: Upcoming review load for the next 30 days
  5. **Per-day tooltip**: Hover over any day to see exact card count
- **Design insights**:
  - The heatmap is motivational because it makes consistency **visible**
  - The forecast feature helps students plan study time (seeing a spike of 200 cards due Thursday motivates earlier action)
  - What's mapped is **repetitions**, not time -- rewarding effort over duration

### 4.2 What Metrics Actually Matter (Evidence-Based)

Synthesizing across platforms and learning science:

| Metric | Why It Matters | Source |
|--------|---------------|--------|
| **Streak** | Loss aversion is the strongest engagement driver | Duolingo (32% DAU/MAU ratio) |
| **Coverage %** | "What haven't I reviewed yet?" prevents blind spots | Khan Academy mastery grid |
| **Weakest topics** | Directs attention to highest-impact study areas | Error pattern research |
| **Retrievability forecast** | "Will I remember this on exam day?" | FSRS algorithm |
| **Review volume** | Effort visibility motivates continued practice | Anki heatmap |
| **Calibration gap** | "Am I overconfident?" drives better study strategy | Metacognition research (Springer 2025) |
| **Time to exam** | Urgency framing increases study initiation | General motivation research |

### 4.3 Notification Design: What Not to Do

- **Source**: [Push Notifications and Student Engagement (Springer, 2025)](https://link.springer.com/article/10.1186/s41239-025-00537-x) | [Student Engagement Platform Features](https://www.ofashandfire.com/blog/student-engagement-platform-development-features) | [Push Notifications for Students (uTeach)](https://uteach.io/articles/push-notifications-for-student-engagement)
- **Key findings**:
  1. **2-3 notifications per week maximum** for educational platforms. More causes disable.
  2. **Progressive escalation**: Gentle reminder 3 days before deadline -> stronger reminder 1 day before -> urgent alert on deadline day. Map this to exam countdown.
  3. **Personalize timing**: Send reminders when the student typically uses the app (based on historical login patterns).
  4. **Content matters more than frequency**: A notification saying "You have 15 cards due" is less effective than "Your weakest topic (Series Convergence) has 8 cards due -- review them to boost your exam readiness."
  5. **Avoid vanity metrics**: Don't lead with "You earned 50 XP!" -- lead with actionable information.
- **Anti-patterns**:
  - Daily emails with no actionable content
  - Generic "Don't forget to study!" messages
  - Showing only positive stats (hiding weak spots feels good but hurts outcomes)

### 4.4 Recommended Daily Progress Report Design for CourseHub

Based on all research, here is the recommended "Private Tutor Briefing" design:

```
+--------------------------------------------------+
|  DAILY BRIEFING                    Apr 7 | Day 1  |
|  Calculus II Exam in 3 days                       |
+--------------------------------------------------+
|                                                    |
|  STREAK: 5 days                    [flame icon]    |
|                                                    |
|  TODAY'S PRIORITY                                  |
|  Your 3 weakest topics (by error rate):            |
|  1. Series Convergence Tests -- 42% accuracy       |
|  2. Trig Substitution -- 55% accuracy              |
|  3. Integration by Parts -- 68% accuracy           |
|  [Start Focused Review ->]                         |
|                                                    |
|  EXAM READINESS                                    |
|  [=========--------] 62% of cards at target        |
|  retrievability for April 10                       |
|                                                    |
|  12 cards due today | 8 overdue                    |
|                                                    |
|  YESTERDAY'S SESSION                               |
|  45 cards reviewed | 23 min | 71% accuracy         |
|  Improved: Partial Fractions (+15%)                |
|  Still weak: Series Convergence (no change)        |
|                                                    |
|  CALIBRATION CHECK                                 |
|  Your confidence vs reality:                       |
|  Convergence: rated 4/5, scored 42% -- GAP         |
|  Integration by Parts: rated 3/5, scored 68% -- OK |
|                                                    |
|  TIP: Focus on Convergence Tests today.            |
|  You think you know it better than you do.         |
+--------------------------------------------------+
```

**Design principles**:
1. **Lead with urgency**: Exam countdown is the first thing visible
2. **Action-oriented**: "Start Focused Review" button is the primary CTA
3. **Honest about weaknesses**: Show error rates, not just XP earned
4. **Calibration surfacing**: Explicitly show where confidence exceeds performance
5. **Celebrate progress**: "Improved: Partial Fractions (+15%)" provides positive reinforcement
6. **Concise**: Entire report fits on one screen, no scrolling needed
7. **One daily tip**: Personalized, based on data, not generic advice

### 4.5 Implementation Plan

| Component | Effort | Dependencies |
|-----------|--------|-------------|
| Streak tracking (localStorage) | 30 min | None -- count consecutive days with reviews |
| Exam readiness bar (FSRS retrievability aggregation) | 1 hr | Existing FSRS data in localStorage |
| Weak topics list (error rate per topic) | 1 hr | Parse review history, group by outline section |
| Yesterday's session summary | 30 min | Aggregate last session's review data |
| Calibration display | 1 hr | Requires confidence rating feature (see 2.3) |
| Daily tip (AI-generated or template) | 30 min | Template-based for now, AI post-exam |
| Report page/component | 1 hr | React component, route at `/review/daily` |
| **Total** | **~5.5 hr** | Can ship core (streak + readiness + weak topics) in **2-3 hours** |

**MVP for exam sprint (2-3 hours)**:
- Streak counter
- Exam readiness % bar
- Top 3 weakest topics with error rates
- Cards due today count
- Yesterday's review summary (count, accuracy)

**Post-exam additions**:
- Confidence calibration chart
- AI-generated personalized tip
- Email/push notification delivery
- Review heatmap (Anki-style)

---

## 5. Cross-Cutting Recommendations

### What to Build Before April 10 (Ranked by Impact/Effort)

| Priority | Feature | Effort | Impact |
|----------|---------|--------|--------|
| **P0** | Mistake Pattern Analysis (weak spots card) | 1 hr | Directly targets blind spots |
| **P0** | Daily Progress MVP (streak + readiness + weak topics) | 2-3 hr | "Private tutor" briefing |
| **P1** | Confidence Calibration slider on questions | 1.5 hr | Fixes "illusion of knowing" |
| **P1** | Term tooltip: click-to-popover + "Mark as known" | 1.5 hr | Better tooltip UX |
| **P2** | Auto-generated review sheet (printable) | 1.5 hr | Passive but useful |
| **P2** | Interleaved practice mode toggle | 1 hr | Better review session design |

### What NOT to Build Before April 10

- Email/push notification system (complex, low ROI for 3 days)
- Full review heatmap (cosmetic, not functional for exam prep)
- AI-generated daily tips (template tips are fine for now)
- FSRS Supabase migration (post-exam -- too risky to touch data layer before exam)

### What the Student Should Do Right Now (No Code)

1. **Use interleaved review mode**: Don't filter to one topic. Let the queue mix everything.
2. **Study hardest topics first thing in the morning** when encoding capacity is highest.
3. **Take a 20-min nap after midday study** to consolidate morning learning.
4. **Sleep at the same time tonight, tomorrow, and Wednesday** (consistency > total hours).
5. **Stop studying by 10 PM** each night. The last 2 hours before sleep should be low-stimulus.
6. **On April 9 (night before): NO new material**. Light review only. Sleep by 10:30 PM.

---

## Sources

### Sleep & Memory Consolidation
- [Systems Memory Consolidation During Sleep (PMC 2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12576410/)
- [Sleep Deprivation and Memory Meta-Analysis (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8893218/)
- [Sleep Consistency and Academic Performance (Nature 2025)](https://www.nature.com/articles/s41598-025-33775-0)
- [Memory, Sleep and Dreaming (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3079906/)
- [Overnight Memory Consolidation (ScienceDirect 2025)](https://www.sciencedirect.com/science/article/pii/S0010027725001817)
- [Memory and Learning (UCSB)](https://wellness.ucsb.edu/challenges/sleep-challenge/ucsb-sleep-challenge/memory-and-learning)

### Interleaving & Retrieval Practice
- [Interleaved Practice Improves Mathematics Learning (ERIC/Rohrer)](https://files.eric.ed.gov/fulltext/ED557355.pdf)
- [IES: Interleaved Mathematics Practice](https://ies.ed.gov/use-work/awards/interleaved-mathematics-practice)
- [How Interleaving Works 2025](https://richardjamesrogers.com/2025/03/09/how-interleaving-works-universal-strategies-for-secondary-school-classroom-practice/)
- [RetrievalPractice.org: Interleaving](https://www.retrievalpractice.org/interleaving)
- [The Pretesting Effect (PMC 2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12292081/)
- [Retrieval Practice in Mathematics (Springer 2025)](https://link.springer.com/article/10.1007/s10763-025-10607-1)
- [Retrieval Practice Evidence from College Sample](https://www.researchgate.net/publication/393114908_Enhancing_Final_Exam_Performance_Through_Retrieval_Practice_Evidence_From_a_Diverse_College_Sample)

### Tooltip & Popover UX
- [Tooltip vs Popover (Design Encyclopedia)](https://design-encyclopedia.com/?T=Tooltip+Vs+Popover)
- [Carbon Design: Tooltip, ToggleTip, Popover](https://github.com/carbon-design-system/carbon/issues/9901)
- [Progressive Disclosure (IxDF 2026)](https://ixdf.org/literature/topics/progressive-disclosure)
- [Mobile-First UX 2026 (Trinergi)](https://www.trinergydigital.com/news/mobile-first-ux-design-best-practices-in-2026)
- [NN/g: Instructional Overlays for Mobile](https://www.nngroup.com/articles/mobile-instructional-overlay/)
- [NN/g: Tooltip Guidelines](https://www.nngroup.com/articles/tooltip-guidelines/)
- [Accessible Tooltips & Popovers (Accesify)](https://www.accesify.io/blog/accessible-tooltips-popovers-aria-roles-triggers-timing-control/)
- [Tippy.js Documentation](https://atomiks.github.io/tippyjs/)
- [HTML Popover API (Frontend Masters)](https://frontendmasters.com/blog/using-the-popover-api-for-html-tooltips/)
- [LogRocket: Designing Better Tooltips](https://blog.logrocket.com/ux-design/designing-better-tooltips-improved-ux/)
- [Appcues: Tooltips UX](https://www.appcues.com/blog/tooltips)
- [UserPilot: Tooltip Best Practices](https://userpilot.com/blog/tooltip-best-practices/)

### Daily Progress Reports & Gamification
- [Duolingo Gamified Success (SensorTower)](https://sensortower.com/blog/duolingos-gamified-success-a-language-learning-triumph)
- [Duolingo Case Study 2025](https://www.youngurbanproject.com/duolingo-case-study/)
- [Duolingo Gamification (StriveCloud)](https://www.strivecloud.io/blog/gamification-examples-boost-user-retention-duolingo)
- [How Duolingo Reignited Growth (Lenny's Newsletter)](https://www.lennysnewsletter.com/p/how-duolingo-reignited-user-growth)
- [Khan Academy Activity Reports](https://support.khanacademy.org/hc/en-us/articles/360031052391)
- [Khan Academy Self-Assessment Blog](https://blog.khanacademy.org/students-need-better-self-assessment-tools-khan/)
- [Review Heatmap Plugin (AnkiWeb)](https://ankiweb.net/shared/info/1771074083)
- [Review Heatmap Wiki (GitHub)](https://github.com/glutanimate/review-heatmap/wiki/Use)
- [Push Notifications and Student Engagement (Springer 2025)](https://link.springer.com/article/10.1186/s41239-025-00537-x)

### Mistake Patterns & Confidence Calibration
- [Automated Identification of Logical Errors (EDM 2025)](https://educationaldatamining.org/EDM2025/proceedings/2025.EDM.long-papers.85/index.html)
- [AI in Student Management (Nature 2025)](https://www.nature.com/articles/s41598-025-19159-4)
- [Metacognitive Monitoring (Structural Learning)](https://www.structural-learning.com/post/metacognitive-monitoring-fixing-student)
- [Calibration Discrepancy Predicts Strategy (Springer 2025)](https://link.springer.com/article/10.1007/s40593-025-00514-5)
- [Metacognitive Accuracy (Shyam Barr)](https://www.shyambarr.com.au/blog/metacognitive-accuracy-and-the-self-regulated-learner)

### Quick-Win Features
- [MyLens AI Cheatsheet Creator](https://mylens.ai/ai-cheatsheet-creator)
- [Inkfluence AI Study Guide Generator](https://www.inkfluenceai.com/ai-study-guide-generator)
- [How to Make a Cheat Sheet (MoreExams)](https://moreexams.com/blog/how-to-make-a-cheat-sheet)
- [Student Engagement Platform Features](https://www.ofashandfire.com/blog/student-engagement-platform-development-features)
