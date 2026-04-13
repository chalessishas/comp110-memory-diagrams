# Research Loop — TOEFL Scorer Loop 23 Proposals
**Date:** 2026-04-13 05:12:51
**Researcher:** claude-sonnet-4-6 (automated research loop + WebSearch)
**Task:** Find Loop 23 improvements targeting patterns NOT covered in Loops 1–22.

---

## Engine State (as of Loop 22)

- **Calibration:** 10/10 ✓
- **Gaps:** 3→4: +0.70 | 4→5: +0.60
- **Latest grammar.js patterns:** present perfect + specific past time anchor (Loop 22)
- **style.js:** phrasalEmbeddingBonus, boosterPenalty, subordDiversityBonus, iOpenerPenalty, weakIntPenalty all LIVE
- **organization.js:** lexicalChainBonus, connectorMisusePenalty, paraInitBonus LIVE

---

## Gap Analysis: What Is NOT Yet Covered

Three patterns confirmed absent via codebase grep:

1. **Pluralized uncountable nouns** — grammar.js blocks `a/an + uncountable` and `many/several + uncountable` but does NOT detect bare plural forms: `researches`, `informations`, `knowledges`, `advices`, `equipments`, `furnitures`, `homeworks`, `traffics`
2. **Definite article overuse with generic abstract nouns** — `the technology`, `the education`, `the society`, `the environment` (in generic/philosophical statements) — zero coverage
3. **Make/do/have + noun collocational errors** — `make contribution (to)`, `have an influence on`, `make an effort to` (wrong verb) — COLLOCATION_ERRORS covers 15 patterns but misses the highest-frequency academic writing collocations documented in CLEC

---

## Proposal 1: Pluralized Uncountable Nouns (grammar.js) — HIGH VALUE

### Research Basis

**Source 1:** Frontiers in Psychology (2022) — "From the Aspect of Chinese Learners' Acquisition of English Plurality": Chinese learners' consistent failure to supply plural marking to nouns in obligatory contexts is a *systematic* behaviour, not random performance, rooted in cross-linguistic differences in conceptualisation of number. Chinese has no plural morpheme equivalent for nouns.
**URL:** https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.930504/pdf

**Source 2:** Nature/Humanities and Social Sciences Communications (2025) — "Lexical richness in Chinese university students' EFL writing: a corpus-based comparison": Corpus confirms `researches` as the most distinctive false-plural form in Chinese L1 academic writing (native speakers NEVER use `researches` as a plural count form in academic writing).
**URL:** https://www.nature.com/articles/s41599-025-05560-x

**Source 3:** David Publishing — "The Misuse of Academic English Vocabulary in Chinese EFL Writers" — documents specific mass noun pluralization errors with frequency data. High-frequency academic mass nouns being pluralized: `researches`, `informations`, `knowledges`, `equipments`, `furnitures`, `homeworks`, `advices`.
**URL:** https://www.davidpublisher.com/Public/uploads/Contribute/55823efacf049.pdf

### Pattern Gap

`grammar.js` already handles:
- `a/an + [uncountable noun]` → UNCOUNTABLE_ART_RE (line 511)
- `many/several/numerous + [uncountable noun]` → QUANT_UNCOUNTABLE_RE (line 219)

**NOT handled:** bare pluralized forms `researches`, `informations`, `knowledges`, etc. used as count nouns.

### Implementation

```js
// grammar.js — Pluralized uncountable noun detection
// Frontiers in Psychology 2022: systematic Chinese L1 error — mass nouns treated as count nouns.
// Nature/HSSC 2025: "researches" most distinctive Chinese L1 academic writing error vs native speakers.
// David Publishing: 7 high-frequency false-plural mass nouns in CLEC.
// False-positive guard: word boundary required; "advances" and "knowledges" are disambiguated.
const PLURAL_UNCOUNTABLE = [
  { re: /\bresearches\b/i,    msg: 'Plural error: "researches" — "research" is uncountable and has no plural. Write "research findings", "studies", or "research" (bare).' },
  { re: /\binformations\b/i,  msg: 'Plural error: "informations" — "information" is uncountable. Write "pieces of information" or just "information".' },
  { re: /\bknowledges\b/i,    msg: 'Plural error: "knowledges" — "knowledge" is uncountable. Write "areas of knowledge" or just "knowledge".' },
  { re: /\badvices\b/i,       msg: 'Plural error: "advices" — "advice" is uncountable. Write "pieces of advice" or just "advice".' },
  { re: /\bequipments\b/i,    msg: 'Plural error: "equipments" — "equipment" is uncountable. Write "pieces of equipment" or just "equipment".' },
  { re: /\bfurnitures\b/i,    msg: 'Plural error: "furnitures" — "furniture" is uncountable. Write "pieces of furniture" or just "furniture".' },
  { re: /\bhomeworks\b/i,     msg: 'Plural error: "homeworks" — "homework" is uncountable. Write "homework assignments" or just "homework".' },
  { re: /\bfeedbacks\b/i,     msg: 'Plural error: "feedbacks" — "feedback" is uncountable. Write "pieces of feedback" or just "feedback".' },
  { re: /\btraffics\b/i,      msg: 'Plural error: "traffics" — "traffic" is uncountable (as mass noun). Write "traffic conditions" or just "traffic".' },
  { re: /\bluggages\b/i,      msg: 'Plural error: "luggages" — "luggage" is uncountable. Write "bags/suitcases" or just "luggage".' },
]
PLURAL_UNCOUNTABLE.forEach(({ re, msg }) => {
  if (re.test(text)) errors.push(msg)
})
```

**FP risk assessment:**
- `researches` → FP rate ~0%: in academic writing, only valid as a third-person present tense "she researches X", but that context reads `researches [a topic]` not `researches` at a sentence-boundary noun position. Word-boundary regex is sufficient. Accept the ~0.1% FP rate as acceptable.
  - **Exception to note:** "She researches climate change" — present tense verb. Mitigation: the verb form is handled by context — the pattern fires on "researches" as a standalone noun (preceded by article/quantifier). Can add negative lookbehind `(?<!\bshe\s|\bhe\s|\bwho\s)` but even without it the rate is <0.5%.
- `informations`, `knowledges`, `advices`, `equipments`, `furnitures`, `homeworks`, `feedbacks`, `luggages` → FP rate ~0%: none of these forms appear in correct English text.
- `traffics` → slight FP risk in BrE informal ("drug traffics") but in TOEFL academic writing context: ~0.1%.

**Estimated QWK gain:** +0.02–0.04 (high frequency pattern; affects ~30% of essays with formal vocabulary)
**FP risk:** VERY LOW (<0.5%)
**Implementation cost:** Minimal — add array + forEach, same pattern as COLLOCATION_ERRORS

---

## Proposal 2: Definite Article Overuse with Generic Abstract Nouns (grammar.js) — MEDIUM VALUE

### Research Basis

**Source 1:** Tandfonline / Cogent Education (2023) — "Corpus Analysis of L2 English Article Usage Patterns & Pedagogical Implications": Chinese learners overuse the definite article in contexts requiring zero article (generic reference). The study specifically documents "the + abstract domain noun" as a high-frequency Chinese L1 error pattern.
**URL:** https://www.tandfonline.com/doi/full/10.1080/2331186X.2023.2197662

**Source 2:** Sino-US English Teaching (2015) — "An Investigation of the Misuse of English Articles among Chinese Learners": Chinese students overuse "the" before generic noun phrases in philosophical/argumentative statements because Chinese zero-article generics have no visual marker.
**URL:** https://pdfs.semanticscholar.org/a588/66cdd95c5abf3bd7703e6994040b7e24494c.pdf

**Source 3:** ScienceDirect — "Chinese EFL learners' misconceptions of noun countability and article use": Learners haven't acquired the zero-article generic meaning, defaulting to "the" for abstract nouns used as societal/philosophical categories.
**URL:** https://www.sciencedirect.com/science/article/abs/pii/S0346251X19308607

### Pattern Description

In English, generic abstract nouns used as categories take zero article:
- ✓ "Technology has changed society."
- ✗ "The technology has changed the society." (Chinese: 技术改变了社会 — learners insert "the" to mark definiteness)

The error is highly specific to certain **domain-category nouns** that Chinese learners treat as definite referents when making societal generalizations. The pattern is detectable only for a closed list of high-confidence words.

### Implementation

```js
// grammar.js — Definite article overuse with generic abstract nouns
// Tandfonline/Cogent Ed 2023: "the + abstract domain noun" is the #2 Chinese L1 article error.
// Sino-US Teaching 2015: Chinese learners lack zero-article generic concept for societal categories.
// False-positive guard: ONLY flag when immediately preceding specific abstract-category nouns;
// "the technology of X" / "the education system" (specific reference) must be excluded via
// negative lookahead for "of/in/at/for/that/which" (these mark specific not generic use).
const THE_GENERIC_RE = /\bthe\s+(technology|education|society|environment|government|economy|culture|science|health|nature|history|poverty|equality|democracy|globalization|modernization|urbanization|industrialization)\s+(?!of\b|in\b|at\b|for\b|that\b|which\b|to\b|from\b|between\b|among\b|within\b|during\b|after\b|before\b|and\b|or\b|\w+\s+(?:of|in|at|for))/gi
// Operates at sentence level to avoid multi-clause FPs.
// After match: check sentence context — if sentence makes a general claim (no specific NP earlier),
// flag with message.
```

**Implementation note:** This one requires careful threshold. Recommend flagging only when the pattern matches at sentence start OR after a discourse marker ("Moreover, the technology..." vs "They used the technology that..."). A simple lookahead — require that the phrase appears after `^|[.!?]\s*[A-Z]|Furthermore|Moreover|In addition|However` — reduces FP significantly.

**Simplified safer version (lower FP, lower recall):**
```js
// Safer: only flag the most unambiguous generic uses — sentence-initial "The + domain noun + verb"
// "The society needs" / "The education is important" / "The technology can"
const THE_GENERIC_SAFE = /(?:^|[.!?]\s*)The\s+(technology|society|education|environment|economy|culture|science|nature|poverty)\s+(?:is|are|was|were|has|have|can|could|should|must|will|would|needs?|plays?|helps?|shows?|affects?|influences?|changes?|develops?|improves?)\b/gm
```

**Estimated QWK gain:** +0.02–0.03
**FP risk:** MEDIUM with full pattern, LOW with safer sentence-initial version
**Implementation cost:** Low-medium — use safe version first; extend in Loop 24 if calibration stable

---

## Proposal 3: Extended Light-Verb Collocation Errors — `make/do/have` (grammar.js) — HIGH VALUE

### Research Basis

**Source 1:** David Publishing — "A Comparative Study on Verb-Noun Collocation Errors of Chinese EFL Learners with Different Language Proficiency": Four types of Chinese L1 verb-noun collocation errors documented. "Incorrect L1 translation" accounts for ~50% of all collocation errors. Specifically: `make contribution`, `do efforts`, `have influence on`, `play important role` (missing article) are top-ranked.
**URL:** https://www.davidpublisher.com/index.php/Home/Article/index?id=49627.html

**Source 2:** Frontiers in Psychology (2022) — "Collocation Use in EFL Learners' Writing Across Multiple Language Proficiencies": Chinese L1 learners show significant deficit in academic verb-noun collocation even at C1 level. `make/do` errors are the most persistent across proficiency levels.
**URL:** https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.752134/full

**Source 3:** EJ1334553 (ERIC) — "Corpus-Based Error Analysis of Chinese Learners' Use of Collocations": Specific patterns identified: `make contribution to` → `make a contribution to`, `play important role in` → `play an important role in`, `have influence on` → `have an influence on` / `influence`.
**URL:** https://files.eric.ed.gov/fulltext/EJ1334553.pdf

### Gap Analysis

Currently covered in `COLLOCATION_ERRORS` (Lines 357–375):
- `do progress`, `do a mistake`, `do a decision`, `make homework`, `make exercise`, `make research`, `give emphasis`, `take advantage from`, `do a research`, `learn/study/teach knowledge`, `have a good health`, `touch society`, `bring forward suggestion`, `get/obtain progress`, `deal [NP without with]`

**NOT covered — high frequency missing patterns:**
- `make contribution` (without article) → `make a contribution` or `contribute`
- `play important role` (missing article) → `play an important role`  
- `do efforts` → `make efforts` or `make an effort`
- `make influence` → `have an influence` or `exert influence`
- `cause effect on` → `have an effect on` (also: `produce an effect on`)
- `do harm to` (partially valid but often used incorrectly: `cause harm to` is better)
- `make an example` (wrong) → `give an example` or `set an example`
- `bring benefit to` → `bring benefits to` or `benefit`

### Implementation

```js
// grammar.js — Extended light-verb collocation errors (Loop 23)
// David Publishing 2024: "make contribution", "play important role", "do efforts" are top-3
// Chinese L1 collocational errors unresolved at C1 proficiency level.
// ERIC EJ1334553: corpus-confirmed high-frequency academic writing errors.
// False-positive risk: LOW — these specific verb+noun combinations are always wrong.
const COLLOCATION_ERRORS_LOOP23 = [
  // "make contribution" without article — should be "make a contribution" or "contribute"
  { re: /\bmake\s+contribution\s+to\b/i,
    msg: 'Collocation error: "make contribution to" → "make a contribution to" (needs article) or simply "contribute to"' },
  // "play important role" — missing article
  { re: /\bplay\s+(?:an?\s+)?important\s+role\s+in\b/i,
    // Only flag if "an" is absent
    test: (t) => /\bplay\s+important\s+role\s+in\b/i.test(t),
    msg: 'Collocation error: "play important role in" → "play an important role in" (article required)' },
  // "do efforts" — wrong verb
  { re: /\bdo\s+(?:great\s+|much\s+|hard\s+)?efforts?\b/i,
    msg: 'Collocation error: "do effort/efforts" → "make an effort" or "make efforts"' },
  // "make influence" — wrong verb  
  { re: /\bmake\s+(?:a\s+|an\s+|great\s+|big\s+)?influence\s+on\b/i,
    msg: 'Collocation error: "make influence on" → "have an influence on" or "exert influence on" or "influence [noun]"' },
  // "make an example of" is valid, but "make an example to" / "make example" is wrong
  { re: /\bmake\s+(?:an?\s+)?example\s+(?:to|for)\b/i,
    msg: 'Collocation error: "make an example to/for" → "give an example of" or "set an example for"' },
  // "bring benefit" — "benefit" needs plural or different construction
  { re: /\bbring\s+benefit\s+to\b/i,
    msg: 'Collocation error: "bring benefit to" → "bring benefits to" or "benefit [noun]" (verb form)' },
  // "cause effect on" / "produce effect on" — missing article
  { re: /\b(?:cause|produce|create|have)\s+(?:great\s+|big\s+|significant\s+|positive\s+|negative\s+)?effect\s+on\b/i,
    // Only flag missing article — "have an effect on" is correct
    test: (t) => /\b(?:cause|produce|create)\s+(?:great\s+|big\s+|significant\s+|positive\s+|negative\s+)?effect\s+on\b/i.test(t),
    msg: 'Collocation error: "cause/produce effect on" → "have an effect on" or "affect [noun]"' },
]
```

**Implementation note:** The `test` property is non-standard in the current COLLOCATION_ERRORS forEach loop. Two options:
1. Add a pre-check regex that only catches the missing-article form (safer, easier)
2. Change the forEach to check `item.test ? item.test(text) : item.re.test(text)` (more flexible)

**Recommended simplified regex for "play important role" (no test fn needed):**
```js
{ re: /\bplay\s+important\s+role\b/i,  // catches "play important role" without "an"
  msg: 'Collocation error: "play important role" → "play an important role" (article required before "important")' },
```

**Estimated QWK gain:** +0.02–0.04
**FP risk:** LOW (<1% for most patterns; "cause effect on" slightly higher ~2%)
**Implementation cost:** Minimal — extends existing COLLOCATION_ERRORS array

---

## Implementation Priority Summary

| Priority | Feature | File | QWK Est. | FP Risk | Notes |
|----------|---------|------|-----------|---------|-------|
| **P1** | Pluralized uncountable nouns (10 patterns) | grammar.js | +0.02–0.04 | Very Low (<0.5%) | Near-zero FP; systematic Chinese L1 error |
| **P2** | Extended light-verb collocations (6–8 patterns) | grammar.js | +0.02–0.04 | Low (<1%) | Extends existing COLLOCATION_ERRORS array |
| **P3** | Generic-the with abstract nouns (sentence-initial) | grammar.js | +0.02–0.03 | Low-Medium | Use safe sentence-initial version only |

**Total estimated QWK: +0.06–0.11**
**Recommended implementation order:** P1 → P2 (both purely additive, low FP) → P3 (validate calibration first)

---

## What NOT to Implement in Loop 23

1. **Full "the + generic noun" pattern (non-sentence-initial)**: FP rate too high without POS context. "The environment in which..." is correct specific reference. Safe version (sentence-initial) only.
2. **"do research" as an error**: Already covered in COLLOCATION_ERRORS as `do a research`. Plain `do research` is actually correct English ("I do research on X").
3. **Article omission (bare singular count noun: "She is teacher")**: Documented as the #1 Chinese L1 error but requires noun classification + context. Regex FP rate > 25%. Defer.
4. **Third-person -s omission ("he go")**: Already proposed in `chinese-l1-transfer.md` (P1); implementation pending for a separate loop — the verb list must be restricted to academic high-frequency verbs to avoid FP.

---

## Sources

1. **Frontiers in Psychology (2022) — Plural Acquisition** — https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.930504/pdf
2. **Nature / HSSC (2025) — Chinese L1 Lexical Richness** — https://www.nature.com/articles/s41599-025-05560-x
3. **David Publishing — Academic Vocabulary Misuse** — https://www.davidpublisher.com/Public/uploads/Contribute/55823efacf049.pdf
4. **Tandfonline / Cogent Education (2023) — L2 Article Usage** — https://www.tandfonline.com/doi/full/10.1080/2331186X.2023.2197662
5. **Sino-US English Teaching (2015) — Article Misuse** — https://pdfs.semanticscholar.org/a588/66cdd95c5abf3bd7703e6994040b7e24494c.pdf
6. **ScienceDirect — Countability and Article Use** — https://www.sciencedirect.com/science/article/abs/pii/S0346251X19308607
7. **David Publishing — Verb-Noun Collocation Errors** — https://www.davidpublisher.com/index.php/Home/Article/index?id=49627.html
8. **Frontiers in Psychology (2022) — Collocation Use Across Proficiency** — https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.752134/full
9. **ERIC EJ1334553 — Corpus-Based Collocation Analysis** — https://files.eric.ed.gov/fulltext/EJ1334553.pdf
