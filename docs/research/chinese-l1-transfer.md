# Chinese L1 Transfer Errors in TOEFL Writing
## Research for Rule-Based Scoring Engine

**Date:** 2026-04-12
**Scope:** Pattern-matchable grammar errors caused by Mandarin → English negative transfer in TOEFL/academic writing contexts. Excludes lexical/vocabulary errors; excludes errors requiring full parse tree.

---

## Q1: Error Categories (Frequency Ranking)

Sources: CLEC (Chinese Learner English Corpus), LANCAWE, SSLA corpus studies, EJ1075251 (Frequent Errors in Chinese EFL Learners' Topic-Based Writings), tense studies via sciedu.ca/wjel article view/1858.

### Rank 1 — Tense / Verb Morphology Omission
**Chinese source:** Chinese verbs do not inflect for tense; time is expressed via adverbs (yesterday, tomorrow). Learners default to bare/present-tense forms and mark time lexically.

Core sub-errors:
- **Past tense omission:** "Yesterday I go to school" / "Last year the company decide to expand"
  - Simple present/past confusion accounts for ~84% of all tense errors in CLEC data (sciedu.ca study)
- **Third-person -s omission:** "He go", "She want", "It seem"
  - ~50% omission rate in obligatory contexts (LANCAWE 2014 empirical study, Lancaster University)
  - Fossilization documented: no improvement after grammar instruction
- **Perfect aspect confusion:** Present perfect treated as simple past ("I have went", "she has finish")
  - Chinese lacks present-perfect; learners conceptualize it as belonging to the past sphere, not present

### Rank 2 — Article Omission / Misuse
**Chinese source:** Chinese has no article system whatsoever.

- Omission of definite article: "university is important" (for "the university")
- Omission of indefinite article: "She is teacher" (for "a teacher")
- Overuse of "the" with generics: "The dogs are loyal animals"
- Most frequent grammatical error in determiner category in Chinese ESL corpora

> NOTE: grammar.js already handles the `a` → `an` direction. The omission direction (no article at all) requires positional heuristics and is harder to pattern-match without a parse tree.

### Rank 3 — Subject-Verb Agreement (3P Singular)
**Chinese source:** Same as tense — Chinese verbs are uninflected, so the -s morpheme carries zero information in the source language.

- "He go", "She want", "This show that", "The government argue"
- Well-studied: "fossilized" in intermediate learners
- Already partially covered by grammar.js SVA_PATTERNS; 3P singular omission is the high-frequency gap

### Rank 4 — Preposition Errors (Transitive Verb + Spurious Preposition)
**Chinese source:** Chinese has fewer prepositions; many English transitive verbs require no preposition but learners calque from Chinese verb-complement structure.

Documented redundant-preposition patterns (City University HK ELSS corpus):
- `emphasise on` → `emphasise`
- `discuss about` → `discuss` (**already in grammar.js**)
- `stress on` → `stress`
- `demand for` → `demand`
- `request for` → `request`
- `lack of` (as verb) → `lack`
- `enter into` → `enter`
- `marry with` → `marry`
- `reach to` → `reach`
- `approach to` → `approach`

### Rank 5 — Topic-Comment Structure (Double Subject / Resumptive Pronoun)
**Chinese source:** Chinese is topic-prominent; the topic is fronted and then resumed with a pronoun or re-stated subject. Structure: "这个问题，我们应该解决它" → *"This problem, we should solve it."

Patterns:
- Fronted NP + comma + pronoun resumption: "This problem, it is very serious."
- Fronted NP + comma + subject restart: "As for education, we should invest more."
- Double subject: "The student, she works hard." / "My friend he told me"
- Lower-proficiency learners produce ~46% double-subject sentences; reduces to ~19% at higher proficiency

### Rank 6 — Aspect Marker Errors (Perfect / Progressive Confusion)
**Chinese source:** Mandarin uses aspect particles (了 le, 着 zhe, 过 guo) that map imperfectly onto English have+V-en and be+V-ing. No morphological tense marking means learners must learn both tense AND aspect simultaneously.

Patterns:
- `have been` + bare verb: "have been finish" / "have been complete"
- `be` + past participle (passive confusion): "is finished" used where "has finished" is needed
- Stative progressive overuse: "I am knowing the answer" / "She is having a car"
- Bare infinitive after auxiliary: "have finish", "has decide", "had went"

### Rank 7 — Passive Voice: Missing `be` Auxiliary
**Chinese source:** Mandarin passive uses 被 (bèi) directly before the verb — no auxiliary equivalent of "be". Pattern: "The building built in 1990" (omitting "was").

- `was/were/is/are` omitted before past participle
- Under-passivization is the dominant Chinese learner passive error (IGI Global study)
- Five most common passive errors: tense, participle form, word choice, by-transposition, be-omission

### Rank 8 — Pronoun Gender Confusion (he/she swap)
**Chinese source:** Mandarin pronoun 他/她/它 (tā) are homophonic in speech; learners internalized the same phonological form for all genders.

- "My mother, he works as a nurse"
- "The professor, she published his research"
- High frequency in narrative/descriptive writing, lower in abstract academic argumentation

---

## Q2: Detectable Patterns (Regex + False-Positive Risk)

### Pattern A: Third-Person Singular -s Omission
```js
// Detect: pronoun/singular-NP + present-tense bare verb (high-frequency head verbs)
// Target: "he go", "she want", "it seem", "the government argue"
// ⚠ Cannot detect NP subjects without NLP — restrict to pronouns only for safety

const THIRD_PERSON_S_RE = /\b(he|she|it)\s+(go|come|want|need|seem|appear|think|know|say|tell|show|mean|include|suggest|argue|believe|become|remain|work|help|make|take|give|find|use|provide|support|cause|allow|require|enable|affect|involve|represent|reflect|describe|indicate|demonstrate|explain|prove|confirm|reveal)\b/gi
// False-positive risk: LOW — bare infinitive after he/she/it is prohibited in standard English
// Edge case: imperative "She come here!" — rare in TOEFL academic writing
```

### Pattern B: Redundant Preposition after Transitive Verb
```js
// Extends existing grammar.js PREP_ERRORS array
const NEW_PREP_ERRORS = [
  { re: /\bemphasise\s+on\b/i,      msg: 'Preposition error: "emphasise on" → "emphasise" (transitive, no preposition)' },
  { re: /\bemphasize\s+on\b/i,      msg: 'Preposition error: "emphasize on" → "emphasize" (transitive, no preposition)' },
  { re: /\bstress\s+on\b/i,         msg: 'Preposition error: "stress on" → "stress" (when used as verb meaning to emphasize)' },
  { re: /\bdemand\s+for\b/i,        msg: 'Preposition error: "demand for" (as verb) → "demand" + direct object' },
  { re: /\brequest\s+for\b/i,       msg: 'Preposition error: "request for" (as verb) → "request" + direct object' },
  { re: /\benter\s+into\s+(?!an\s+agreement|a\s+contract|negotiations)/i,
    msg: 'Preposition error: "enter into [place/topic]" → "enter" (into is only idiomatic for abstract agreements)' },
  { re: /\bmarry\s+with\b/i,        msg: 'Preposition error: "marry with" → "marry" (no preposition needed)' },
  { re: /\bapproach\s+to\s+(?!the\s+problem|this\s+issue|the\s+topic|the\s+question)/i,
    msg: 'Preposition error: "approach to [noun]" (as verb) → "approach" + direct object' },
]
// False-positive risk: LOW-MEDIUM
// "demand for" has medium risk: "There is a demand for X" is correct; match on verb form only
// "stress on" has medium risk: "stress on the bone" is correct; context filtering helps
```

### Pattern C: Topic-Comment / Double Subject (Resumptive Pronoun)
```js
// Detect: "NP, it/he/she/they [verb]" — fronted topic with pronoun resumption
// This problem, it is serious. / The environment, it needs protection.
const TOPIC_COMMENT_RE = /\b(\w+(?:\s+\w+){0,3}),\s+(it|he|she|they|this|that)\s+(is|are|was|were|has|have|needs|requires|should|must|can)\b/gi
// False-positive risk: MEDIUM
// "Yesterday, it rained." is valid — temporal fronting is correct
// "In Paris, it is cold." is valid — locative fronting is correct
// Mitigation: exclude sentence-initial time/place adverbials as first capture group
```

### Pattern D: `have been` + Bare Verb (Aspect Confusion)
```js
// Detect: "have/has/had been" + bare infinitive (non-progressive form)
// "have been finish" / "has been complete" / "had been decide"
const HAVE_BEEN_BARE_RE = /\b(have|has|had)\s+been\s+(finish|complete|decide|make|take|give|find|do|go|come|write|read|build|create|develop|establish|achieve|solve|resolve|improve|increase|reduce|change|implement|introduce|produce|publish|submit|receive|accept|reject|discuss|consider|examine|analyze|include|exclude|require|provide|support|cause|affect|involve|describe|explain|demonstrate|prove|confirm)\b/gi
// False-positive risk: VERY LOW
// "have been finishing" is correct (progressive) — the bare form after "been" is always wrong
// Only exception: "have been able to" — exclude from list
```

### Pattern E: Stative Progressive Overuse
```js
// Detect: "is/are/was/were" + "-ing" form of stative verbs
// "I am knowing", "she is having", "they are believing"
const STATIVE_PROG_RE = /\b(am|is|are|was|were)\s+(knowing|understanding|believing|thinking(?=\s+that)|supposing|assuming|recognizing|realizing|meaning|wanting|needing|owning|having(?=\s+a\b|\s+the\b|\s+no\b)|preferring|liking|loving|hating|resembling|containing|consisting|belonging)\b/gi
// False-positive risk: LOW-MEDIUM
// "is having a party" is correct (dynamic use of "have")
// "is thinking about" is ambiguous — restrict "thinking" to "thinking that" form
// "is meaning to" is correct in some registers
```

### Pattern F: Passive `be` Omission (Before Past Participle)
```js
// Detect: subject + bare past participle where passive auxiliary expected
// "The building built in 1990" / "The law passed in 2001"
// Hardest of all patterns without NLP — restrict to known high-frequency passive verbs
// after definite NP subject indicator
const PASSIVE_BE_OMIT_RE = /\b(the\s+\w+(?:\s+\w+)?)\s+(built|constructed|established|founded|created|published|written|designed|developed|introduced|implemented|passed|signed|approved|rejected|elected|appointed|named|called|known|considered|regarded|seen|found|given|taken|made|done|used|needed|required|provided|supported)\s+(?:in|by|for|at|on|to|with|during|after|before|from)\b/gi
// False-positive risk: HIGH for this pattern — "The building built in 1990 is now a museum" is valid
// as a reduced relative clause. RECOMMENDATION: Use as a P3 "hint" only, not a hard penalty.
```

### Pattern G: Pronoun Gender Swap
```js
// Detect: gender-inconsistent pronoun reference in same sentence
// "My mother, he works" / "The professor, she published his paper"
// Simplified approach: flag when a clearly feminine noun is followed by "he"
const GENDER_SWAP_PATTERNS = [
  { re: /\b(mother|grandmother|aunt|sister|daughter|wife|girlfriend|woman|girl|lady|queen|princess|nun|bride)\b[^.!?]{0,40}\b(he\s+(?:is|was|has|works|said|told|went|comes|lives|does|makes|takes|gives|finds|needs|wants|helps|plays|runs|studies|teaches|manages|leads|supports))\b/gi,
    msg: 'Pronoun gender mismatch: feminine noun followed by "he"' },
  { re: /\b(father|grandfather|uncle|brother|son|husband|boyfriend|man|boy|gentleman|king|prince|monk|groom)\b[^.!?]{0,40}\b(she\s+(?:is|was|has|works|said|told|went|comes|lives|does|makes|takes|gives|finds|needs|wants|helps|plays|runs|studies|teaches|manages|leads|supports))\b/gi,
    msg: 'Pronoun gender mismatch: masculine noun followed by "she"' },
]
// False-positive risk: LOW-MEDIUM
// "The man who married the woman he loved, she later left him" — garden path, but unusual
// Restriction: max 40-char gap prevents cross-sentence false positives
```

---

## Priority Table

| Priority | Error Type | Chinese Source | Frequency in Corpus | Detectability | False-Positive Risk | Recommended Action |
|----------|-----------|----------------|--------------------|-----------|--------------------|-------------------|
| **P1** | 3P singular -s omission (`he go`) | No verb inflection in Mandarin | ~50% omission rate (LANCAWE) | HIGH: pronoun-restricted regex | LOW | Add to grammar.js |
| **P1** | `have been` + bare verb | 了/着 aspect ≠ English perfect | Very frequent (aspect system gap) | HIGH: lexically closed regex | VERY LOW | Add to grammar.js |
| **P1** | Redundant prep: `emphasize on`, `stress on`, `demand for`, `request for`, `marry with` | Fewer prepositions in Chinese; calquing | High in Chinese learner text | HIGH: anchored verb+prep patterns | LOW | Extend PREP_ERRORS |
| **P2** | Topic-comment / double subject (`This problem, it is`) | Topic-prominent language | 27-46% at lower/mid proficiency | MEDIUM: fronted NP + pronoun | MEDIUM: temporal fronting | Add with exclusion list |
| **P2** | Stative progressive (`is knowing`, `am having a car`) | Mandarin 着 maps loosely to progressive | Moderate; more spoken than written | MEDIUM: stative verb whitelist | LOW for closed stative list | Add to grammar.js |
| **P2** | Gender pronoun swap (`mother, he works`) | Mandarin 他/她 homophonic (tā) | Common in narrative writing | MEDIUM: gendered noun + wrong pronoun | LOW-MEDIUM within sentence | Add gendered-noun check |
| **P3** | Passive `be` omission (`building built in 1990`) | 被 bèi needs no auxiliary | Common but hard to isolate | LOW: high reduced-relative ambiguity | HIGH | Flag as hint only |
| **P3** | Past tense omission (`Yesterday I go`) | No tense morphology in Mandarin | Very high but hard without NLP | LOW: lexical time-marker + present verb | HIGH | Defer; needs NLP |
| **P3** | Article omission (`She is teacher`) | Chinese has no articles | #1 or #2 error by volume | LOW: no clean pattern | VERY HIGH | Defer; needs NLP |

---

## Already Covered in grammar.js (Cross-Reference)

| Error | Status |
|-------|--------|
| Double conjunction (although...but, because...so) | ✅ Implemented |
| Missing copula (he very good) | ✅ Implemented (he/she + adverb) |
| Plural omission after quantifiers (many student) | ✅ Implemented |
| Count quantifier + uncountable noun (many research) | ✅ Implemented |
| Subject-verb agreement (he are, everyone have) | ✅ Implemented |
| Article a → an (before vowel) | ✅ Implemented |
| Preposition: discuss about, depend of, interested on, etc. | ✅ Implemented (8 patterns) |

---

## Implementation Notes

### Adding P1 Patterns to grammar.js

**3P singular -s omission** — extend SVA_PATTERNS with pronoun-anchored bare-verb list. Keep the verb list to ~30 highest-frequency academic verbs to control false positives. Edge case: "Let it go", "Help her come" — imperative structures; exclude if preceded by `let/help/make/have`.

**`have been` + bare verb** — standalone regex loop (same structure as existing copulaRe loop). The pattern is morphologically unique; near-zero false positive rate.

**Redundant prepositions** — extend PREP_ERRORS array directly. `demand for` needs a negative lookahead excluding `demand for change/justice/rights` (collocations where "demand for" as a nominalized phrase is valid).

### P2 Patterns Require Tighter Scoping

**Topic-comment** — the fronted-NP trigger is too broad without POS tagging. Restrict to: NP must be ≤4 words, must start sentence, must not be a time expression (yesterday, last year, in 2010, etc.). Start with a known-topic-noun whitelist (this problem, this issue, this approach, the government, the environment, education, technology).

**Stative progressive** — use a closed whitelist of ~15 core stative verbs. Exclude "have" except when followed by indefinite article + concrete noun ("I am having a meeting" is acceptable in BrE).

---

## Source URLs

1. **CLEC tense error study** — [CLEC-Based Study of Tense Errors in Chinese EFL Learners' Writings, sciedu.ca](https://www.sciedu.ca/journal/index.php/wjel/article/view/1858) — 16 tense-error categories; simple present/past confusion = 84.36% of all tense errors.

2. **3P singular -s omission (LANCAWE corpus)** — [An Empirical Study on the Omission of Third-Person Singular -s in Writing, ccsenet.org](https://ccsenet.org/journal/index.php/ijel/article/view/0/46837) — ~50% omission rate in obligatory contexts; fossilization documented post-instruction.

3. **Topic-comment and redundancy errors** — [Frequent Errors in Chinese EFL Learners' Topic-Based Writings, ERIC EJ1075251](https://files.eric.ed.gov/fulltext/EJ1075251.pdf) — double-subject frequency by proficiency level; topic-comment taxonomy.

4. **Verb + preposition errors (City University HK ELSS)** — [Common Hong Kong Errors: Verbs and Prepositions, lc.cityu.edu.hk](https://www.lc.cityu.edu.hk/ELSS/Resource/chke/index.htm) — empirical list of transitive verbs that Chinese learners incorrectly follow with prepositions.

5. **Passive voice errors (be-omission)** — [An Error Analysis of Students' Use of Passive Voice, ideasspread.org](https://j.ideasspread.org/ilr/article/download/1612/1520) — five passive error types; under-passivization as dominant Chinese learner pattern.

6. **Tense/aspect shifts (Tsai 2023)** — [An Error Analysis on Tense and Aspect Shifts, SAGE Journals](https://journals.sagepub.com/doi/10.1177/21582440231158263) — aspect confusion in Chinese→English translation; perfect/progressive conflation.

7. **Negative syntactic transfer overview** — [The Negative Transfer of Chinese Syntax in English Writing, Atlantis Press](https://www.atlantis-press.com/article/125983026.pdf) — topic-comment structure, multi-predicate sentences, parataxis as main syntactic error categories.
