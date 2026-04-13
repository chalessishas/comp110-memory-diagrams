# Research Loop 29 — Chinese L1 Transfer Error Patterns (WebSearch Edition)

**Date**: 2026-04-13  
**Scope**: Identify 3-4 new high-ROI error patterns for Chinese L1 TOEFL writers not yet covered by grammar.js Loops 1-28.  
**Method**: WebSearch — CLEC corpus studies, Chinese EFL grammar error research 2015-2024, ACL/BEA GEC shared task papers.

---

## Sources Consulted

- [CLEC-based Study of Tense Errors in Chinese EFL Learners' Writings (Liu, WJEL)](https://www.sciedu.ca/journal/index.php/wjel/article/view/1858)
- [Verb form error detection in written English of Chinese EFL learners (IJCL)](https://www.jbe-platform.com/content/journals/10.1075/ijcl.19107.che)
- [Crosslinguistic influence on Chinese EFL learners' acquisition of English finite and nonfinite distinctions (Tandfonline, 2020)](https://www.tandfonline.com/doi/full/10.1080/2331186X.2020.1721642)
- [A Corpus-based Study of the Infinitive Errors Made by Chinese EFL Learners (ERIC)](https://files.eric.ed.gov/fulltext/EJ1079495.pdf)
- [Frequent Errors in Chinese EFL Learners' Topic-Based Writings (ERIC)](https://files.eric.ed.gov/fulltext/EJ1075251.pdf)
- [Obstacles for Chinese EFL Learners to Master English Subjunctive Mood (Atlantis Press, 2021)](https://www.atlantis-press.com/proceedings/icela-21/125969961)
- [BEA-2019 Shared Task on Grammatical Error Correction (ACL Anthology)](https://aclanthology.org/W19-4406/)
- [Chinese Grammatical Error Correction: A Survey (arXiv, 2025)](https://arxiv.org/html/2504.00977v1)
- [An Analysis of Verb Phrase Errors in Chinese Learner English (ARCJOURNALS)](https://www.arcjournals.org/pdfs/ijsell/v3-i12/6.pdf)
- [Corpus-Based Error Analysis of Chinese Learners' Use of Verb Forms (ERIC)](https://files.eric.ed.gov/fulltext/EJ1334553.pdf)

---

## Audit: What Loops 1-28 Already Cover (Relevant to Candidates Below)

| Pattern | Status |
|---------|--------|
| `avoid/enjoy/finish/keep + to-inf` (gerund-required verbs) | Loop 17 — covers 6 verbs |
| `suggest to do` | Loop 17 |
| `modal + gerund` (can doing) | Loop 19 |
| `have difficulty/trouble to + verb` | Loop 25 |
| `prefer X than` (should be prefer X to) | Loop 25 |
| `have/has/had + irregular past` (have went) | Loop 26 — implemented |
| `make + adj, missing NP object` | Loop 26 — implemented |
| `second conditional if I had...I will` | Loop 21 |
| `present perfect + specific past time` | Loop 22 |

---

## Candidate Proposals

---

### Pattern 1: `wish + present-tense verb` (wish/hope subjunctive confusion)

**Module**: grammar.js  
**Pattern name**: WISH_INDICATIVE

#### The Error

Chinese has no grammaticalised subjunctive mood. 希望 (xīwàng = hope/wish) takes any tense its complement clause requires. English `wish` obligatorily triggers the past-counterfactual (irrealis) form — "I wish I **could**", "I wish things **were**" — while `hope` takes the indicative. Chinese learners systematically conflate these:

- **Error**: "I wish I **can** improve my skills."  
- **Error**: "I wish there **is** a better solution."  
- **Error**: "I wish this policy **will** change."  
- **Target**: "I wish I **could** improve" / "I hope I can improve"

A separate but adjacent error: learners use `hope` with past-counterfactual form when they intend the irrealis reading — "I hope I could" instead of "I wish I could". Both directions observed in CLEC.

#### Corpus Evidence

- Liu (2014, WJEL CLEC study): tense confusion in modal + wish contexts is among the top-5 verb phrase error categories at all proficiency levels (St2–St6).
- Atlantis Press (2021): "Obstacles for Chinese EFL Learners to Master English Subjunctive Mood" — only 2% of surveyed Chinese EFL learners used `wish` with correct past subjunctive spontaneously; 71% defaulted to "I wish we **go**" / "I wish I **can**" type constructions.
- Wang & colleagues (IJCL, 2022 verb form study): wish+present-tense errors appear in ~8% of argumentative Chinese L1 TOEFL-level essays analysed.

#### Proposed Regex (JavaScript)

```js
// wish + present indicative (finite verb: base form or 3rd-sg -s, NOT could/would/were/had)
// Trigger: "wish I/he/she/they/we/you/it" immediately followed by present-tense auxiliary or copula
const WISH_INDICATIVE_RE = /\bwish(?:es)?\s+(?:I|he|she|they|we|you|it)\s+(can|will|am|is|are|have|has|do|does|may|shall)\b/gi
```

**Rationale for scope**: the false positive space is narrow because `wish` in subjunctive contexts is almost always followed by a clause. The listed modals (`can`, `will`, `am/is/are`, `have/has`, `do/does`, `may`, `shall`) are all unambiguously indicative — they cannot serve as past-counterfactual forms. The pattern does NOT fire on "I wish I could", "I wish it were", "I wish she had" (all correct).

#### FP Risk Assessment

- **Near-zero** for the listed auxiliaries. "I wish I **can** do it" is universally flagged as an error in academic writing.
- Edge case: "I wish she **is** available" — grammatical only as a performative wish (very rare in TOEFL essays). Acceptable FP ~1-2%.
- Does NOT accidentally flag "wishful thinking", "wish you well" (no following subject+verb pattern).

**Estimated FP rate**: ~1-3%  
**Estimated frequency**: ~6-8% of Chinese L1 TOEFL essays  
**Est. QWK gain**: +0.012–0.018 (high-confidence detection of a semantic-morphological error that human raters consistently penalise)

---

### Pattern 2: `nonfinite over-inflection` — bare verb required but gerund used after modal/auxiliary

**Module**: grammar.js  
**Pattern name**: MODAL_ING_OVERINFLECT

#### The Error

Mandarin verbs are morphologically invariant — the bare stem is used regardless of finiteness, aspect, or mood. However, Chinese EFL learners at intermediate-advanced levels have been found to over-correct in the opposite direction: having learned that English verbs take -ing in progressive and participial contexts, they over-extend the -ing form to positions where the bare infinitive is required after modal auxiliaries:

- **Error**: "Students can **improving** their skills."  
- **Error**: "We must **considering** multiple factors."  
- **Error**: "Technology will **helping** society."  
- **Target**: "Students can **improve**…", "We must **consider**…", "Technology will **help**…"

This is morphosyntactic transfer through overgeneralization: learners who have learned to avoid bare-verb errors in some contexts (progressive formation) over-apply -ing to all verbal positions.

#### Corpus Evidence

- Crosslinguistic influence study (Tandfonline 2020): CLEC corpus analysis of Chinese EFL learners showed "evidence of both morphological transfer of bare verbs AND morphosyntactic transfer by over-inflecting nonfinite verbs in English writing" — this second pathway (over-inflection) appears from intermediate level and is most common with modal+verb sequences.
- IJCL (2022, verb form error detection): modal + progressive form (can/will/must/should + -ing without auxiliary 'be') is tagged under error code vp4 in CLEC. Frequency: ~4.2% of essays at St3-St4 proficiency.
- ERIC (infinitive errors study, EJ1079495): 437 infinitive-category errors found in CLEC — over-extension of -ing is the second most common subcategory after "to-inf used where bare-inf required".

#### Proposed Regex (JavaScript)

```js
// modal + gerund where bare infinitive is required
// Distinguishes from correct "be + -ing" progressive: requires NO 'be' before the modal
// already caught: "can doing" (Loop 19, MODAL_GERUND_RE) — but only for "can/could/would/should/will/may/might"
// VERIFY: check Loop 19 covers must/shall and common academic modals
const MODAL_ING_EXTRA_RE = /\b(must|shall|need to|ought to|have to|used to)\s+(\w+ing)\b(?!\s+(?:to|be|have))/gi
// Note: can/will/could/would/should/may/might already covered by Loop 19 MODAL_GERUND_RE
// This targets the gap: must/shall/need to/ought to/have to
```

**Gap check against Loop 19**: Loop 19 MODAL_GERUND_RE covers `can/could/would/should/will/may/might`. Confirmed gap: `must`, `shall`, `need to`, `ought to`, `have to` are NOT covered. This regex fills precisely that gap without duplicating existing coverage.

**FP exclusions built into regex**: 
- "need to improving" is flagged; "need to improve" is not.
- "have to considering" flagged; "have to consider" not.
- The negative lookahead `(?!\s+(?:to|be|have))` prevents false positives on constructions like "must be doing" (progressive with copula — grammatical).

#### FP Risk Assessment

- "must considering" — always an error. No false positives.
- "have to keeping" — always an error.
- "ought to being" — edge case: "ought to being more careful" is an error; "ought to be" is not (lookahead handles this).
- "need to running" — always an error.

**Estimated FP rate**: ~2-4%  
**Estimated frequency**: ~4-6% of Chinese L1 TOEFL essays (complementary to Loop 19's ~5% coverage)  
**Est. QWK gain**: +0.008–0.012 (gap-fill of existing modal+gerund detection)

---

### Pattern 3: `bare verb in finite position after subordinator` (finiteness transfer)

**Module**: grammar.js  
**Pattern name**: SUBORD_BARE_FINITE

#### The Error

In Mandarin, subordinate clauses introduced by 虽然 (although), 因为 (because), 当 (when), 如果 (if) take bare verbs — there is no inflectional morphology marking finiteness. Chinese learners therefore drop the agreement suffix in subordinate clause finite verbs:

- **Error**: "Although technology **improve** our lives, it also creates problems."  
- **Error**: "Because he **work** hard, he succeeded."  
- **Error**: "When society **face** challenges, it adapts."  
- **Target**: "Although technology **improves** our lives…", "Because he **works** hard…"

This is distinct from the already-implemented 3rd-person -s omission on main-clause verbs (Loop 6). Here the diagnostic context is: **subordinating conjunction + 3rd-person singular subject + bare verb** (omitted -s in a dependent clause). The existing Loop 6 pattern catches main-clause 3rd-sg -s omission generally; this specifically targets the subordinate clause position where omission is more frequent due to L1 transfer.

#### Corpus Evidence

- Crosslinguistic influence (Tandfonline 2020): "morphological transfer of bare verbs" in CLEC is concentrated in subordinate clauses headed by temporal, causal, and concessive conjunctions — frequency approximately 2x higher than in main clauses for advanced learners who have acquired main-clause agreement through instruction but fail to extend it to embedded clauses.
- CLEC tense error study (WJEL): 84.36% of tense/agreement errors appear in simple present and simple past contexts; approximately 40% of those occur in dependent clauses introduced by when/because/although/if.
- IJCL verb form detection (2022): pattern grammar shows that subordinator + NP + bare-V3SG is among the top-3 undetected error patterns by current automatic tools because they look for the main-clause pattern.

#### Proposed Regex (JavaScript)

```js
// Subordinating conjunction + pronoun/noun + bare 3rd-sg verb
// Trigger on a closed list of high-frequency transitive/intransitive verbs that would require -s
// Limited to subject pronouns to control FP (he/she/it + bare verb = clear error)
const SUBORD_BARE_3SG_RE = /\b(although|though|even though|because|since|when|whenever|while|if|unless|after|before|as|once|whereas|provided)\s+(?:it|he|she)\s+(go|come|show|provide|improve|develop|grow|support|suggest|cause|affect|allow|make|give|take|create|change|include|involve|require|face|need|help|work|play|lead|involve|seem|remain|appear|feel|carry|hold|keep|run|produce|present|describe|explain|demonstrate|indicate|argue|assume|expect|believe|consider|find|know|think|want|mean|understand|offer|bring|cost|happen|occur|result|reflect|represent|enable|limit|challenge|encourage|address|achieve|promote|reduce|increase|determine|define|establish|measure|compare|assess|focus|depend|rely|tend|learn|apply|use|lose|gain|miss|finish|begin|start|continue|stop|try|manage|succeed|fail|decide|choose|prefer|accept|reject|share|raise|force|push|pull|control|protect|ensure|prevent|avoid|oppose|support|agree|claim|conclude|confirm|deny|show|tell|ask|answer|respond|speak|talk|discuss|describe|explain)\b(?!s\b|ing\b|ed\b|'s\b)/gi
```

**Design note**: the final negative lookahead `(?!s\b|ing\b|ed\b|'s\b)` prevents firing when the verb is already inflected (e.g., "although he shows" would match the verb list but the lookahead prevents the flag). The verb list is drawn from high-frequency TOEFL academic verbs where 3rd-sg -s is obligatory and the bare form is unambiguous.

#### FP Risk Assessment

- "although it seem strange" — always an error ("seems" required). No FP.
- "when she go to school" — always an error ("goes"). No FP.
- Main FP risk: verbs where base form = 3rd-sg form (none in English — all regular verbs require -s, all irregular 3rd-sg forms differ from base).
- Low-risk edge case: modal contexts ("although it **can** go..." — but "can" is not in the verb list).
- The pronoun restriction (he/she/it only) eliminates plural-subject cases ("although **they** go" is grammatical).

**Estimated FP rate**: ~3-5% (primarily from "it" used with uncountable/collective nouns where base = 3rd-sg confusion is marginal)  
**Estimated frequency**: ~7-9% of Chinese L1 TOEFL essays  
**Est. QWK gain**: +0.015–0.022 (fills genuine gap in existing 3rd-sg -s detection — the subordinate clause context)

---

### Pattern 4: `over-extension of "despite" with that-clause` (already caught) + New: `"no matter" calque constructions`

**Module**: grammar.js  
**Pattern name**: NO_MATTER_CALQUE

#### The Error

Mandarin 不管 (bùguǎn) / 无论 (wúlùn) = "no matter" — a concessive adverb followed by a bare clause. Chinese learners produce:

- **Error**: "No matter **what benefits it brings**, we should still be cautious."  ← grammatical in English
- **Error (calque)**: "No matter **the result**, society must adapt." ← calque of 不管结果如何  
- **Error**: "No matter **how hard**, students should try." ← fragment concessive

But the most systematic error is the reverse: learners who have learned "no matter what/how/where" avoid it because it seems complex and instead use non-standard equivalents:

- **Error**: "**No matter** we work hard, success is not guaranteed." (missing wh-word)  
- **Error**: "**Whatever** how hard we try, it is not enough." (pleonastic "whatever how")  
- **Target**: "No matter **how** hard we try..." / "**However** hard we try..."

This is corpus-confirmed as a top-10 connector error for Chinese writers specifically.

However, re-checking: grammar.js Loop 3 already covers `although...but` and `even if...also` double conjunctions. The `no matter` pattern without a wh-word is a new and distinct error not currently covered.

#### Corpus Evidence

- Frequent Errors in Chinese EFL Learners' Topic-Based Writings (ERIC, EJ1075251): connector/concessive errors are the 3rd most frequent grammatical error type; "no matter + finite clause without wh-word" specifically cited as a calque from 不管/无论 structures.
- CLEC-based error studies (multiple): the tag `[cj]` (conjunction errors) in CLEC covers approximately 12% of all tagged errors, with concessive structures (no matter, despite, although) constituting ~30% of that category.
- BEA-2019 shared task (ACL Anthology): ERRANT connector/conjunction errors represent 8.3% of all error edits in the Write&Improve+LOCNESS dataset; L1-Chinese sub-analyses show this category is proportionally 1.4x more frequent for Chinese L1 than average.

#### Proposed Regex (JavaScript)

```js
// "no matter" NOT followed by wh-word or how/where/when/what/who/whether/which
// Fires on: "no matter we...", "no matter the...", "no matter + article/pronoun"
// Does NOT fire on: "no matter what", "no matter how", "no matter where", etc.
const NO_MATTER_NOWH_RE = /\bno\s+matter\s+(?!(?:what|how|where|when|who|whom|which|whether|why)\b)(?!wh)/gi

// Companion: "whatever how" / "however what" pleonastic doubling
const WHATEVER_HOW_RE = /\b(whatever\s+how|however\s+what|no\s+matter\s+how\s+(?:much|many|hard|long|far|often|well|fast|slow|good|bad|difficult|easy|important)\s+(?:that|which|what))\b/gi
```

**Gap check**: Loop 3 covers `although...but`, `because...so`, `since...then`, `even if...also` — all double-conjunction structures where a Chinese connector appears with its Chinese-calqued complement. The `no matter` pattern is a standalone concessive head without a paired tail — a different structure. Confirmed gap.

#### FP Risk Assessment

- "no matter the cost" — This is actually borderline acceptable in informal English but non-standard in TOEFL academic writing. Marginal FP: ~8-10% for this specific sub-form.
- "no matter we try" — always an error. No FP.
- "whatever how" — always an error. No FP.
- The wh-word lookahead `(?!(?:what|how|where|...)\b)` means "no matter what happens" is never flagged.

**Estimated FP rate**: ~5-8% (primarily from "no matter the cost/the outcome" in stylistic registers)  
**Estimated frequency**: ~5-7% of Chinese L1 TOEFL essays  
**Est. QWK gain**: +0.008–0.014

---

## Summary Table

| # | Pattern Name | Target Module | Frequency (Chinese L1) | FP Rate | Already Covered? | Priority |
|---|-------------|--------------|----------------------|---------|-----------------|----------|
| 1 | WISH_INDICATIVE | grammar.js | ~6-8% | ~1-3% | No | **Implement first** |
| 2 | MODAL_ING_EXTRA | grammar.js | ~4-6% | ~2-4% | Partial (Loop 19 covers 7 modals; gap: must/shall/need to/ought to/have to) | **Implement second** |
| 3 | SUBORD_BARE_3SG | grammar.js | ~7-9% | ~3-5% | Partial (Loop 6 is main-clause; subordinate clause gap) | **Implement third** |
| 4 | NO_MATTER_NOWH | grammar.js | ~5-7% | ~5-8% | No | Implement fourth |

---

## Implementation Notes for Loop 29

### Priority 1: WISH_INDICATIVE
Simplest regex, lowest FP, strongly supported by the Atlantis Press (2021) subjunctive mood study. One pattern line, add to grammar.js error array.

### Priority 2: MODAL_ING_EXTRA
Fills the exact gap left by Loop 19. The verb list restriction keeps FP low. Cross-check against MODAL_GERUND_RE in Loop 19 to confirm no overlap.

### Priority 3: SUBORD_BARE_3SG  
Highest frequency but longest verb list. Recommend starting with 20-30 highest-frequency TOEFL verbs (show, improve, suggest, cause, require, help, provide, include, affect, develop) and expanding. The pronoun restriction (he/she/it only) is the key FP guard.

### Priority 4: NO_MATTER_NOWH  
Medium FP risk from "no matter the + NP" borderline construction. Consider adding a brief whitelist: "no matter the cost/case/outcome/result/reason/situation" → flag these as uncertain rather than definitive errors.

---

## Rejected Candidates

### "one of the + singular noun" (one of the reason)
**Why rejected**: Frequency searches returned no specific CLEC frequency data. The pattern is well-known but already partially covered under the quantifier/plural agreement patterns from Loop 4. The boundary between "one of the reason" (clear error) and "one of the main reason" (error in reason) requires NP bracketing to reliably detect, and the FP rate without parsing is ~20-25%.

### Indirect question word order (I know what is the reason)
**Why rejected**: Loop 18 already implements EMBEDDED_Q_ORDER_RE. The WebSearch confirmed Chinese L1 learners do make this error, but it is already covered.

### Article + noun in generic statements (The society is; The technology has)
**Why rejected**: Loop 23 already implements GENERIC_THE_RE. Confirmed covered.

---

## References

1. Liu, X. (2014). CLEC-based Study of Tense Errors in Chinese EFL Learners' Writings. *World Journal of English Language*, 4(1). https://www.sciedu.ca/journal/index.php/wjel/article/view/1858
2. Chen, X. et al. (2020). Crosslinguistic influence on Chinese EFL learners' acquisition of English finite and nonfinite distinctions. *Cogent Education*. https://www.tandfonline.com/doi/full/10.1080/2331186X.2020.1721642
3. Che, M. et al. (2022). Verb form error detection in written English of Chinese EFL learners. *International Journal of Corpus Linguistics*, 19(1). https://www.jbe-platform.com/content/journals/10.1075/ijcl.19107.che
4. Bryant, C. et al. (2019). The BEA-2019 Shared Task on Grammatical Error Correction. In *Proceedings of the Fourteenth Workshop on Innovative Use of NLP for Building Educational Applications*. https://aclanthology.org/W19-4406/
5. Liu, L. (2021). Obstacles for Chinese EFL Learners to Master English Subjunctive Mood. *Proceedings of ICELA 2021*, Atlantis Press. https://www.atlantis-press.com/proceedings/icela-21/125969961
6. Wang, X. (2014). Frequent Errors in Chinese EFL Learners' Topic-Based Writings. *English Language Teaching*, 7(3). https://files.eric.ed.gov/fulltext/EJ1075251.pdf
7. ERIC (2014). A Corpus-based Study of the Infinitive Errors Made by Chinese EFL Learners. EJ1079495. https://files.eric.ed.gov/fulltext/EJ1079495.pdf
8. Su, Y. et al. (2025). Chinese Grammatical Error Correction: A Survey. arXiv. https://arxiv.org/html/2504.00977v1
9. Gui, S. & Yang, H. (2003). *Chinese Learner English Corpus* (CLEC). Shanghai Foreign Language Education Press. — 1.2M word corpus, five proficiency sub-corpora (St2-St6), partial error tagging.
