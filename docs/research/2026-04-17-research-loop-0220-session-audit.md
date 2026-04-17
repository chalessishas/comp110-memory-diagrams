# Research Loop 02:20 — Session Audit & Next-Move Analysis

**Trigger**: Automated Research Loop, 2026-04-17 02:20 UTC+8  
**Context**: User asleep. No user questions pending.

---

## 1. Session State Since Last Research Loop (00:04)

| Event | Time | Outcome |
|-------|------|---------|
| Progress Loop: multiple-select bug fix | 00:09 | TOEFL f45c98c ✅ |
| Progress Loop: prose_summary CPH passage | 00:25 | TOEFL 888f996 ✅ |
| Progress Loop: prose_summary m1–m5 | 00:31 | TOEFL dcdec3e ✅ |
| Progress Loop: dataset_v6 audit notice | 00:40 | docs only, no code change |
| ai-text-detector decision gate | ongoing | **BLOCKED** — user must decide product direction |

**Net result**: TOEFL has absorbed all autonomous bandwidth tonight. ai-text-detector blocked on master-gated product decision (DeepSeek-only detector vs multi-family general detector).

---

## 2. TOEFL Reading — Question Type Coverage Audit

Current question type distribution in `pack6.js`:

| Type | Count | ETS Typical per Passage | Status |
|------|-------|------------------------|--------|
| detail (factual) | 27 | 3-4 | ✅ Well covered |
| inference | 17 | 2-3 | ✅ Well covered |
| negative_fact | 7 | 0-1 | ✅ Covered |
| text_insertion | 6 | 1 | ✅ 1 per passage |
| sentence_simplification | 6 | 1 | ✅ 1 per passage |
| prose_summary | 6 | 1 | ✅ Just completed tonight |
| vocab/vocabulary | 6 | 2-3 | ⚠️ Underrepresented; also naming inconsistency |
| purpose | 1 | 1-2 | ⚠️ Only 1 vs 6 passages |

**Missing ETS types**:
- **Fill in a Table** (category chart): Worth 3-4 pts on ETS. Requires drag-and-drop or checkbox-per-row UI. Complex to implement. **However**: ETS replaced "Fill in a Table" with "Prose Summary" on most passages in the 2023 TOEFL iBT redesign. Only ~1 in 3 reading passages now uses Fill-in-Table vs Prose Summary. With 6 prose_summary already, this is lower priority.
- **Reference** (pronoun reference): Already partially present via `type: 'detail'` questions (see commit `2ea4886`). ETS format is identical to detail — no special UI needed. Can add more reference questions as detail-type.

**Key gap: Vocabulary questions are underrepresented (6 vs ETS typical 12-18 for 6 passages).**
ETS places 2-3 vocab questions per passage; we have ~1 per passage average.

**Actionable**: Next autonomous grammar/reading loop should target adding 1-2 vocabulary questions per passage that don't yet have them.

---

## 3. TOEFL Grammar Loop — Next Candidates (Loop 69+)

Grammar.js currently has 115 patterns. High-frequency Chinese L1 errors not yet addressed (based on CLEC/ICNALE research in `docs/research/chinese-l1-transfer.md`):

### Loop 69 Candidates (ranked by error frequency):

1. **Gerund vs infinitive after "avoid/finish/mind/enjoy/consider/practice"** (~8-12% CLEC essays)
   - Error: "avoid to make", "finish to study", "enjoy to read"  
   - Chinese has no gerund/infinitive distinction (动词原形)
   - FP risk: low (these verbs rarely take infinitive in standard use)
   - Source: Celce-Murcia & Larsen-Freeman 1999 §8.3

2. **"discuss about X" → "discuss X"** (~6-9% CLEC)
   - "discuss" is transitive, needs no "about"
   - Chinese 讨论关于 calque adds about
   - FP risk: ~1-2%

3. **"reach to X" → "reach X"** and **"approach to X" → "approach X"**
   - Both are transitive, preposition insertion is L2 calque
   - FP risk: <1%

4. **Stative verb progressive: "I am understanding/knowing/believing"** (~4-7% CLEC)
   - Chinese aspect particles don't prohibit progressive on stative verbs
   - Guard: needs mental-verb list, check preceding "currently/right now" markers
   - FP risk: ~3% (need to guard "I am understanding the problem better now")

**Recommendation**: Loop 69 should target gerund-after-verb (highest frequency, cleanest FP profile) + "discuss about" (near-zero FP).

---

## 4. ai-text-detector — Decision Gate Summary

**Status**: Yellow light. Not proceeding autonomously.

**Facts established today**:
- `dataset_v6.jsonl`: 711,520 samples, binary label, **87% of AI samples are DeepSeek-family**
- `build_dataset_v6.py` line 3-4: "DeepSeek API" — this is **design intent, not a bug**
- `train_runpod_v6.py` confirms single-file load, no multi-source merge

**User decision required**:

| Option | Implication |
|--------|-------------|
| A: DeepSeek-only is correct | Train on RunPod A100, update CLAUDE.md to say "DeepSeek-focused detector". Fast path, ~$8-15 GPU cost. |
| B: Need general detector | Add ~60K samples from GPT-4o/Claude/Gemini/Llama APIs first (~$20-50 API cost). Then retrain. 1-2 day delay. |

**4 CLAUDE.md drift lines awaiting user decision**: Lines 10, 22, 72, 199.

---

## 5. Signal-Map & chronicle — Dormant

- **Signal-Map**: Last commit 5681df6 (Haversine threshold fix). No autonomous work to do — Phase 2 features (event notifications, course scheduling) require user input on specs.
- **chronicle**: Last commit a420b0c (touch support). Phase 2 (node colors, image attachments) is implementable autonomously, but user has not signaled priority.

**Potential autonomous work on chronicle**:
- Node color picker: `<input type="color">` + node.color field already exists in schema. 30-min implementation, no blockers. Could do if Progress Loop finds nothing higher-priority.

---

## 6. Recommended Next Actions

| Priority | Project | Action | Blocker |
|----------|---------|--------|---------|
| 1 | TOEFL | Add vocab questions to passages with <2 (m2, m4, m5) | None — autonomous |
| 2 | TOEFL | Loop 69 grammar: gerund-after-verb + discuss-about | None — autonomous |
| 3 | ai-text-detector | User decision on Option A vs B | **User gate** |
| 4 | chronicle | Node color picker (Phase 2 start) | None — but user hasn't prioritized |
| 5 | TOEFL | purpose question for each remaining passage | None — autonomous |

---

*Research Loop auto-generated at 2026-04-17 02:20 UTC+8*
