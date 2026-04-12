# TOEFL Automated Scoring Research
**Date:** 2026-04-12  
**Scope:** How e-rater works, published correlations, weaknesses, datasets, score distributions, and heuristic predictors — actionable for the TOEFL practice app custom scoring engine.

---

## 1. Published e-rater vs. Human Rater Correlations

**Bottom line: e-rater meets or beats inter-rater reliability in most conditions.**

- The operational standard ETS uses: QWK ≥ 0.70 and Pearson r ≥ 0.70 between e-rater and human scores. This is the published threshold for deployment.
- Attali, Bridgeman & Trapani (2010): e-rater agreement with a single human rater on TOEFL Independent and GRE Issue tasks **exceeded** the agreement between two independent human raters.
- Attali (2007), construct validity study: "e-rater measures essentially the same construct as human-based essay scores with significantly higher reliability."
- A 2014 monitoring study (Wang) found human/e-rater hybrid scoring was stable within a discrepancy threshold of ±1.5 score points for TOEFL Independent.
- Early e-rater (v99) had a critical flaw: models using **only word count** performed almost as well, accounting for only 0.05 additional variance when length effects were removed. e-rater v2.0+ improved this to 0.14 additional variance after controlling for length — still modest.

**Key implication for the app:** The app's current scoring engine likely operates at ~0.50-0.65 correlation with real human scores (typical for heuristic systems without ML). This is lower than operational e-rater but acceptable for practice/diagnostic purposes if clearly disclosed.

---

## 2. Known Weaknesses of Automated Scoring (warn users)

Documented in ETS's own publications:

1. **Length inflation**: The single strongest correlate of automated scores is word count (r = 0.50–0.70 with human scores in most studies). AES systems are gameable by writing more words even without improving quality. The app's 24% development weight based on word count amplifies this bias.

2. **Content blindness**: AES cannot evaluate factual accuracy, relevance to the specific prompt, or quality of argumentation. A fluent off-topic essay scores high. ETS partially addresses this with topic-specific vocabulary models, which the app lacks.

3. **Homophone/register errors**: e-rater flags homophones (their/there) inconsistently and has known racial/dialect bias — e-rater gave African American test-takers significantly lower scores than human raters on GRE/TOEFL essays (documented in ETS research). This is a mechanics/style measurement artifact.

4. **No syntactic depth**: Automated systems measure syntactic variety via surface regex-style patterns. Deep clause embedding and argument structure are not captured.

5. **Creativity and originality**: AES cannot assess novel ideas, humor, or rhetorical effectiveness — all of which distinguish score-5 essays from score-4 essays per ETS rubrics.

6. **Gaming is feasible**: NYT-documented exploits include padding with tangential but fluent text. ETS mitigates this with human review triggers; the practice app has no such safety net.

**Recommended disclosure to users:** "This score reflects surface-level writing features (length, vocabulary, mechanics). It cannot evaluate argument quality, factual accuracy, or originality. A real TOEFL examiner may score differently."

---

## 3. Open-Source Datasets for Calibration

**TOEFL-specific, free:**
- **TOEFL11 Corpus** — 1,100 essays by non-native English speakers on 8 TOEFL prompts, with L1 (native language) annotations. Available via LDC (Linguistic Data Consortium), free for academic use. No public score labels, but useful for feature distribution calibration. URL: https://catalog.ldc.upenn.edu/LDC2014T06
- **ASAP (Automated Student Assessment Prize) dataset** — Hewlett Foundation / Kaggle 2012. 8 essay sets (~12,000 essays), double-scored by expert human raters, QWK-graded. Not TOEFL-specific (grades 7-10 English), but the most widely used open dataset for AES calibration. URL: https://www.kaggle.com/c/asap-aes

**Not freely available:**
- ETS's own TOEFL scored essay corpus is proprietary. Access requires licensing through LDC or an institutional data agreement.

**Practical recommendation:** Use ASAP sets 1 and 2 (argumentative, closest to TOEFL Independent) to calibrate score-to-band mapping. Correlate your app's raw score output against ASAP human scores to benchmark feature weights.

---

## 4. Typical TOEFL Writing Score Distribution

From ETS data (2021-2023 score summaries) and published research:

- **Scale**: 0–5 in 0.5 increments for each task, converted to 0–30 section score.
- **Mean writing score**: ~3.5–3.6 / 5 for global TOEFL iBT test takers (per ETS 2023 data summary).
- **Score classification**: ETS labels 4.0–5.0 as "Good," 2.5–3.5 as "Fair," 0–2.0 as "Limited."
- **Score 5 is rare**: Fewer than 10% of test-takers score 5/5 on either task.
- **Score 1-2 is also rare**: Most test-takers cluster in 3.0–4.0.
- **Integrated task typically scores 0.2–0.3 points lower** than Independent in the same test-taker — content accuracy requirements are stricter.

**App implication:** The app's scoring output should be calibrated so that the modal output is 3.0–3.5 for typical submissions, not 4.0–4.5. If the app is systematically generous (common with heuristic systems), it erodes trust and fails to help users identify weak areas.

---

## 5. Strong Heuristic Predictors (Validated)

Ranked by evidence strength:

| Feature | r with human score | Evidence |
|---|---|---|
| Word count / essay length | r = 0.50–0.70 | PMC 2020 study; ETS RR-04-04 |
| Discourse connectives / cohesion markers | r ≈ 0.45–0.60 (QWK +4% when added) | Coh-Metrix studies; IJCAI 2024 |
| Vocabulary sophistication (rare word ratio, AWL coverage) | r ≈ 0.40–0.55 | Attali 2007; e-rater v8 feature analysis |
| Grammar/mechanics error rate | r ≈ 0.40–0.50 | e-rater GUMS feature analysis (Chen 2017) |
| Syntactic variety (clause types) | r ≈ 0.30–0.45 | e-rater macrofeature; Attali 2015 trait scores |
| TTR (type-token ratio) | r ≈ 0.25–0.35 | Weaker predictor; easily gamed |

**Three-factor structure confirmed by ETS factor analysis (Chen 2017):**
1. Discourse factor (organization + development + cohesion)
2. Grammar factor (grammar + usage + mechanics)  
3. Word usage factor (vocabulary + lexical complexity)

This is consistent with what the app measures, but the relative importance differs.

---

## 6. Recommended Weight Adjustments

Comparing published e-rater weights (from toeflresources.com analysis, 2010 weights) against the app's current weights:

| Dimension | e-rater weight | App current | Recommendation |
|---|---|---|---|
| Organization | 32% | 30% | Keep — well-calibrated |
| Development (word count + detail) | 29% | 24% | Increase to 28% — length is the single strongest predictor |
| Vocabulary (rare words + word length) | ~14% | 18% | Reduce to 14% — app over-weights this vs. e-rater |
| Mechanics (spellcheck) | 10% | 10% | Keep |
| Grammar | 7% | 7% | Keep |
| Style (TTR, sentence variety) | 3% | 3% | Keep |
| Relevance (topic vocab overlap) | ~3% | 8% | **Reduce to 3–5%** — keyword overlap is a weak signal for an off-the-shelf spellcheck-style approach; only worth 8% if using TF-IDF against the actual prompt, not just keyword count |

**Single highest-ROI addition not currently in the app:** Collocations / idiomatic phrase patterns. e-rater v8 rewards "idiomatic phraseology" as a positive feature alongside vocabulary. This is measurable via a fixed list of academic collocations (AWL collocations) — ~50 pattern checks. Would distinguish 4 from 5 essays better than any other single addition.

---

## Sources

- [Evaluation of e-rater for TOEFL Independent (ERIC EJ1109838)](https://files.eric.ed.gov/fulltext/EJ1109838.pdf)
- [ETS: How the e-rater Scoring Engine Works](https://www.ets.org/erater/how.html)
- [Attali 2015: Automated Trait Scores for TOEFL Writing Tasks (Wiley)](https://onlinelibrary.wiley.com/doi/full/10.1002/ets2.12061)
- [Attali 2007: Construct Validity of e-rater in Scoring TOEFL Essays (Wiley)](https://onlinelibrary.wiley.com/doi/abs/10.1002/j.2333-8504.2007.tb02063.x)
- [Wang 2014: Monitoring e-rater + Human Raters (Wiley)](https://onlinelibrary.wiley.com/doi/full/10.1002/ets2.12005)
- [ETS RR-04-04: Beyond Essay Length — e-rater on TOEFL Essays](https://www.ets.org/Media/Research/pdf/RR-04-04.pdf)
- [PMC 2020: Is a Long Essay Always a Good Essay? Text Length and Writing Assessment](https://pmc.ncbi.nlm.nih.gov/articles/PMC7544919/)
- [Chen 2017: e-rater GUMS Microfeatures (Wiley)](https://onlinelibrary.wiley.com/doi/full/10.1002/ets2.12131)
- [ETS Contrasting Automated and Human Scoring (RD Connections 21)](https://www.ets.org/Media/Research/pdf/RD_Connections_21.pdf)
- [TOEFL Resources: How Does e-rater Work?](https://www.toeflresources.com/how-does-the-toefl-e-rater-work/)
- [ASAP Dataset on Kaggle](https://www.kaggle.com/c/asap-aes)
- [TOEFL11 Corpus via LDC](https://catalog.ldc.upenn.edu/LDC2014T06)
- [ETS TOEFL iBT Score Data Summary 2023](https://www.ets.org/pdfs/toefl/toefl-ibt-test-score-data-summary-2023.pdf)
- [Coh-Metrix Discourse/Cohesion study (bonoi.org)](https://bonoi.org/index.php/sief/article/view/1729)
- [IJCAI 2024: Automated Essay Scoring Using Discourse External Features](https://www.ijcai.org/proceedings/2024/0791.pdf)
