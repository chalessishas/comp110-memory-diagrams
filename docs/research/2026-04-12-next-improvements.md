# Research Loop — 2026-04-12 Next Improvement Proposals

## Current State (as of 01:13)

All originally-scoped autonomous tasks are complete:
- Dark mode (100%), Settings toggles (100%), Content expansion (10 prompts each)
- Reading.jsx refactor (4 components), english-words lazy-load
- Score history + Progress panel wired, Home dashboard live stats
- Study Plan + Areas to Improve now dynamic

## Remaining 0% Items (require user input)
1. Notebook/vocabulary backend persistence — needs Supabase/auth decision
2. User authentication — platform decision needed
3. Deployment — hosting platform decision needed

## Autonomous Improvements Still Possible

### High Value, Low Risk

**1. Adaptive Review Mode (BuildSentence)**
- Track which items the user got wrong across sessions (wrong answers saved to history)
- Add "Review Mode" that only shows previously-missed items
- Effort: ~2h | Risk: low (additive, uses existing sessionItems pattern)

**2. WritingResult — comparison to previous attempt**
- Each result page shows only current score; no "you improved" feedback
- Add delta indicator: compare current score to last attempt of same type
- Effort: 1h | Risk: low

**3. Reading Pack completion unlock flow**
- Currently all 6 Pack 6 modules are available at once
- Could show "Recommended next" based on history (next incomplete module)
- Effort: 30min | Risk: low

**4. Home page "Resume" deep links**
- Home.jsx already has `hasResume` logic from commit 0c24fd1
- Check if BuildSentence/Email/Discussion localStorage keys exist → show direct resume button
- Effort: 1h | Risk: low

### Medium Value

**5. Score trend sparkline in Progress panel**
- Currently shows only last 6 sessions as a list
- Mini line chart (pure SVG, no library) of writing scores over time
- Effort: 2h | Risk: low (SVG math is deterministic)

**6. Vocabulary list editable in Notebook**
- Currently `vocabPlaceholder` is hardcoded
- Add localStorage-backed vocab list with add/delete buttons
- Effort: 2h | Risk: low

## Not Recommended Without User Input
- PWA offline support — need deployment decision first
- AI-powered essay feedback — needs ANTHROPIC_API_KEY wired into frontend (currently Express-proxy only)
- Multiplayer / leaderboard — needs auth + backend

## Recommended Priority Order
1. Writing score delta (quick, high UX value)
2. Vocab list editable (clears last major placeholder)
3. Adaptive BuildSentence review mode (learning value)
4. Score trend chart (polish)
