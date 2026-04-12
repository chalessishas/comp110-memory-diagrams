# TOEFL App — Next Improvements Research
**Date:** 2026-04-12  
**Scope:** Pure-frontend improvements not yet implemented, no new npm packages

---

## Scorer State (as of today)

7 dimensions wired: grammar / mechanics / vocabulary / organization / development / style / relevance.  
`relevance.js` is already live at 8% weight — Gap 1 from `toefl-scorer-improvements.md` is closed.

The two remaining scorer gaps from that doc (peer engagement, syntactic variety) are still open.  
The improvements below are ranked independently for net impact.

---

## Improvement #1 — Peer Engagement Detection in Discussion Scorer

**Rank:** 1 (highest impact)  
**Complexity:** S (~25 lines)  
**File:** `src/writing/scorer/organization.js`

### Why

ETS Academic Discussion rubric explicitly scores whether the writer "meaningfully engages with peer responses." The current `taskSpecific` branch awards full credit for first-person opinion phrases alone (`I agree`, `I think`) — these require zero peer reference. A student who ignores both classmates entirely still scores high on this dimension.

WebSearch confirmed: the ETS rubric for score 5 requires "building on a peer's contribution or supporting/challenging a claim made by a peer."

### What to add

In `organization.js`, inside the `taskType === 'discussion'` block, replace the binary `taskSpecific` check with a 4-level signal:

```js
function peerEngagementScore(text, prompt) {
  // Extract capitalized names from prompt (classmate names like Kelly, Andrew)
  const names = (prompt.match(/\b[A-Z][a-z]{2,}\b/g) || [])
    .filter(n => !['The','This','These','However','While'].includes(n))

  const lower = text.toLowerCase()
  const nameRef = names.some(n => lower.includes(n.toLowerCase()))
  const buildOn = /\b(building on|adding to|while .{0,20} (said|mentioned|argues?|points? out)|unlike .{0,20},|as .{0,20} (noted|mentioned))\b/i.test(text)
  const opinionOnly = /\b(i agree|i disagree|in my opinion|i believe|i think)\b/i.test(lower)

  if (nameRef && buildOn) return 1.0   // explicit engagement + elaboration
  if (nameRef)            return 0.65  // name-drop without elaboration
  if (opinionOnly)        return 0.3   // current behavior ceiling
  return 0.1
}
```

Pass `promptText` down from `organization.score(text, taskType, promptText)` — update caller in `index.js` accordingly (it already receives `promptText`).

**Integration point:** `index.js` line 37 already calls `organization.score(text, taskType)` — add third arg `promptText`.

---

## Improvement #2 — SM-2 Spaced Repetition for Writing Prompts

**Rank:** 2 (high practice value)  
**Complexity:** M (~80 lines across 2 files)  
**Files:** `src/writing/AcademicDiscussion.jsx`, `src/writing/WriteEmail.jsx`, new `src/writing/srs.js`

### Why

BuildSentence already has spaced repetition for sentence items, but the 10 email and 10 discussion prompts rotate naively (random or sequential). Students benefit most from re-attempting prompts where their score was lowest. ETS research shows deliberate practice on weak areas is more effective than random exposure.

SM-2 is the correct algorithm here: it requires only `interval`, `efactor`, and `repetitions` per item — no npm package needed, ~30 lines of pure JS.

### What to add

**`src/writing/srs.js`** — self-contained SM-2 implementation:

```js
// Returns { interval, efactor, repetitions } after a review
// quality: 0-5 (map TOEFL score: 0→0, 1→1, 2→2, 3→3, 4→4, 5→5)
export function sm2(quality, { interval = 0, efactor = 2.5, repetitions = 0 }) {
  if (quality < 3) {
    return { interval: 1, efactor, repetitions: 0 }
  }
  const newEF = Math.max(1.3, efactor + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
  const newInterval = repetitions === 0 ? 1 : repetitions === 1 ? 6 : Math.round(interval * newEF)
  return { interval: newInterval, efactor: newEF, repetitions: repetitions + 1 }
}

// Pick the next prompt index: due first, then lowest interval
export function nextDuePrompt(srsState, totalPrompts) {
  const today = Date.now()
  const dueItems = []
  for (let i = 0; i < totalPrompts; i++) {
    const s = srsState[i] || { interval: 0, dueDate: 0 }
    if (s.dueDate <= today) dueItems.push({ i, interval: s.interval || 0 })
  }
  if (dueItems.length === 0) return 0
  dueItems.sort((a, b) => a.interval - b.interval)  // lowest interval = least practiced
  return dueItems[0].i
}
```

**In `WriteEmail.jsx` and `AcademicDiscussion.jsx`:**

```js
// On submit, after scoring:
const srsKey = `toefl-srs-${taskType}`  // 'email' | 'discussion'
const srsState = JSON.parse(localStorage.getItem(srsKey) || '{}')
const prev = srsState[promptIndex] || {}
const quality = Math.round(result.overall)  // 0-5 TOEFL score
const updated = sm2(quality, prev)
srsState[promptIndex] = { ...updated, dueDate: Date.now() + updated.interval * 86400000 }
localStorage.setItem(srsKey, JSON.stringify(srsState))

// On next prompt selection:
const nextIdx = nextDuePrompt(srsState, prompts.length)
```

No UI change required — the prompt just loads smarter. Optionally add a badge "Due for review" on the prompt selector.

---

## Improvement #3 — Syntactic Variety Sub-Score in Style Module

**Rank:** 3 (medium impact, completes ETS language facility coverage)  
**Complexity:** S (~20 lines)  
**File:** `src/writing/scorer/style.js`

### Why

ETS score-5 descriptor for both email and discussion tasks requires "variety of syntactic structures." The current `style.js` measures only TTR (lexical diversity) and sentence length variance. A writer using 10 simple SVO sentences with rare vocabulary would score high on style — ETS would not award 5.

### What to add

In `style.js`, add a `syntacticVariety` sub-score and blend it in at 30% weight:

```js
const SYNTAX_PATTERNS = [
  /\b(who|which|that)\s+\w+/,            // relative clauses
  /\b(if|unless|were\s+to)\b/,           // conditionals
  /\b(is|are|was|were)\s+\w+ed\b/,       // passives
  /\b(although|despite|while|even\s+though)\b/,  // concessive
  /\bto\s+[a-z]+\s+[a-z]+/,             // infinitive phrases
]

function syntacticVarietyScore(text) {
  const matched = SYNTAX_PATTERNS.filter(p => p.test(text)).length
  return matched / SYNTAX_PATTERNS.length  // 0.0 – 1.0
}

// In score(): change weight blend from TTR×0.5 + sentLenVar×0.5
// to: TTR×0.4 + sentLenVar×0.3 + syntacticVariety×0.3
```

Add a suggest tip: "Use a variety of sentence structures: relative clauses (which/who), conditionals (if/unless), and passive voice to demonstrate syntactic range."

---

## Implementation Order

| Order | Item | File(s) | Effort |
|-------|------|---------|--------|
| 1st | Syntactic variety (S) | `style.js` | ~20 min |
| 2nd | Peer engagement (S) | `organization.js`, `index.js` | ~30 min |
| 3rd | Writing prompt SRS (M) | new `srs.js`, 2 task files | ~2 hrs |

Start with #3 last — it requires plumbing `srsState` into component lifecycle and verifying the due-date math doesn't break existing localStorage keys.

---

## Sources

- [ETS TOEFL Writing Rubrics (official PDF)](https://www.ets.org/pdfs/toefl/writing-rubrics.pdf)
- [ETS Academic Discussion Task Transcript](https://www.ets.org/toefl/transcript/writing-for-an-academic-discussion-task.html)
- [SM-2 Algorithm — Fresh Cards](https://www.freshcardsapp.com/srs/write-your-own-algorithm.html)
- [SM-2 ES6 Implementation — cnnrhill/sm-2](https://github.com/cnnrhill/sm-2)
- [TOEFL Writing Scoring 2026 — Writing30](https://www.writing30.com/blog/toefl-writing-scoring)
- [TOEFL Resources: Academic Discussion Guide](https://www.toeflresources.com/new-toefl-writing-task-description-and-guide/)
