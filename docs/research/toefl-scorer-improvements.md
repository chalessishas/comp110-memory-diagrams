# TOEFL Scorer Improvement Research
**Date:** 2026-04-12  
**Scope:** `src/writing/scorer/` vs real ETS scoring criteria for Academic Discussion + Write Email tasks

---

## What the Current Scorer Does

6 dimensions with e-rater-inspired weights:

| Dimension | Weight | Method |
|-----------|--------|--------|
| Organization | 32% | Discourse marker count + paragraph count + task-specific cues |
| Development | 30% | Word count + detail markers + sentence count |
| Vocabulary | 14% | Word length + rare word ratio |
| Mechanics | 10% | 275k-word spellcheck |
| Grammar | 7% | Fragment/run-on/comma-splice regex |
| Style | 7% | TTR + sentence length variance + repetition |

---

## What ETS Actually Evaluates

Based on official ETS rubrics for the two active TOEFL Essentials tasks (Write an Email, Academic Discussion):

### Three Core Rubric Dimensions (ETS Official)

1. **Communicative Goals / Task Completion**  
   Score 5: "successfully accomplishes all three communicative goals"  
   Score 3: partial completion, unclear purpose  
   Score 1-2: goals not met or irrelevant content  
   → *This is the dominant differentiator between score levels.*

2. **Language Facility** (vocabulary precision + syntactic variety)  
   Score 5: "precise, idiomatic word choice" + "variety of syntactic structures"  
   Score 3: "limited range" of vocabulary and structures  
   Score 1-2: "accumulation of errors"

3. **Grammatical Control**  
   Score 5: "almost no lexical or grammatical errors other than those expected of a competent writer"  
   Score 3: errors "obscure" connections  
   → Errors penalized in proportion to frequency AND whether they impede meaning.

### Academic Discussion Task: Additional Dimension

4. **Peer Engagement** — unique to discussion task  
   The rubric explicitly requires "meaningful engagement with peer responses" — not just stating your own view.  
   A response that ignores classmate posts scores lower even if otherwise well-written.

---

## Gap Analysis: Current vs. ETS

### What the scorer does well
- Mechanics (spellcheck) and grammar (structural errors) cover part of ETS's "grammatical control"
- Organization marker density partially captures "language facility" (cohesion)
- Development word count partially tracks "task completion" breadth
- Task-specific bonuses for email greeting/closing are correct

### Critical gaps

**Gap 1 — Task completion is not scored at all**  
The current scorer has no concept of whether the response actually addresses the prompt. A 150-word off-topic essay scores higher than a 100-word on-topic one. ETS's #1 criterion is relevance and goal completion. The scorer has zero coverage here.

**Gap 2 — Peer engagement is not detected (discussion task)**  
ETS explicitly requires referencing classmate posts in the Academic Discussion task. The current `taskSpecific` check only looks for "I agree / I disagree / I think" — phrases that can appear without any peer reference. There is no check that the student actually mentioned or paraphrased what a classmate said.

**Gap 3 — Syntactic variety is absent**  
ETS rewards "variety of syntactic structures" (relative clauses, conditionals, passives, complex NPs). The current `style.js` measures TTR (lexical) and sentence length variance, but has nothing on syntactic structure diversity. A student writing 10 simple Subject-Verb-Object sentences with varied vocabulary would score well, when ETS would penalize the monotony.

---

## Three Improvements, Ranked by Impact

---

### #1 — Prompt-Relevance Scorer (Impact: HIGH | Complexity: M)

**What to change:**  
Add a `relevance.js` module that takes both `text` and `prompt` as inputs (already available in the component — the prompt string is passed but never forwarded to the scorer). Score is based on keyword overlap between the user's response and key terms extracted from the prompt question.

Simple implementation: extract noun phrases from the prompt (split on stop words, keep 3+ char tokens), count how many appear in the response. Normalize by prompt token count. Weight 0-1.

**Integration:**  
- `scoreWriting(text, taskType, prompt)` — add `prompt` param
- Add `relevance` to `WEIGHTS` at ~15%, redistributing from `development` (30%→20%) and `style` (7%→5%)
- Show "Relevance" as a 7th bar in `WritingResult.jsx`

**Why it matters:**  
This is ETS's #1 criterion. A student who writes fluent but off-topic prose should not score 4/5. Currently they do. This is the most significant accuracy gap.

---

### #2 — Peer Engagement Detection for Discussion Task (Impact: HIGH | Complexity: S)

**What to change:**  
In `organization.js`, the `taskType === 'discussion'` branch currently awards `taskSpecific = 1.0` if the text contains "I agree", "I believe", etc. This is too easy to game and misses the actual criterion.

Replace with two-signal check:
1. Does the text reference a name from the discussion prompt classmates (e.g., "Kelly", "Andrew")? — extract expected names from the prompt and pass them down, OR use a generic pattern: `/(name|[A-Z][a-z]+) (makes|said|mentioned|points? out|argues?|suggests?)/i`
2. Does the text build on or contrast a stated idea? — look for "while [Name]", "unlike [Name]", "building on", "adding to"

Score:  
- Both signals: 1.0 (genuine engagement)  
- Name mention only: 0.6  
- Opinion phrase only (current behavior): 0.3  
- Neither: 0.1

**Why it matters:**  
Peer engagement is a hard ETS requirement specific to this task. Students need to be trained to address classmates explicitly — the current scorer rewards omitting this entirely.

**Complexity: S** — ~20 lines in `organization.js`, no new module needed.

---

### #3 — Syntactic Variety Score in Style Module (Impact: MEDIUM | Complexity: S)

**What to change:**  
Add a `syntacticVariety` sub-score in `style.js` alongside existing TTR + sentence length variance. Check presence of:

```js
const COMPLEX_PATTERNS = [
  /\bwho\b|\bwhich\b|\bthat\b/,       // relative clauses
  /\bif\b|\bunless\b|\bwere to\b/,    // conditionals
  /\bis\s+\w+ed\b|\bare\s+\w+ed\b/,  // passives
  /\bto\s+\w+\s+\w+\b/,              // infinitive phrases
  /\balthough\b|\bdespite\b|\bwhile\b/, // concessive clauses
]
```

Count how many of the 5 pattern types appear (0–5), normalize to 0–1. Blend into style score at 30% weight (currently style = TTR×0.5 + sentLenVariance×0.5 → new: TTR×0.4 + sentLenVariance×0.3 + syntacticVariety×0.3).

**Why it matters:**  
ETS explicitly values "variety of syntactic structures" as part of language facility. Students aiming for 4-5 need to use complex grammar, not just difficult vocabulary. This adds a trainable signal they can act on.

**Complexity: S** — ~15 lines in `style.js`.

---

## Implementation Order

```
#2 (peer engagement) → deploy  [~30 min, immediate accuracy improvement for discussion task]
#3 (syntactic variety) → deploy [~30 min, no new dependencies]
#1 (relevance scorer) → deploy  [~2 hrs, requires plumbing prompt through scorer API]
```

All three are pure JS regex/heuristics — no new npm deps, no backend, no breaking changes to the score schema (only additive).

---

## Sources

- [ETS TOEFL Writing Rubrics (iBT)](https://www.ets.org/pdfs/toefl/toefl-ibt-writing-rubrics.pdf)
- [ETS Writing for Academic Discussion Rubrics](https://www.toefl-ibt.jp/dcms_media/other/toeflibt_writing_for_an_academic_discussion_rubrics.pdf)
- [TOEFL Writing Rubrics 2026 — Writing30](https://www.writing30.com/blog/toefl-writing-rubrics)
- [TOEFL Resources: Academic Discussion Guide](https://www.toeflresources.com/new-toefl-writing-task-description-and-guide/)
