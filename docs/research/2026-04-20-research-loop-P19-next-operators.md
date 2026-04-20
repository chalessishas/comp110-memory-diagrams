# P19 Loop: Next Operators for Implementation
**Date:** 2026-04-20 (P18 Texas S2 complete, 1206 tests passing)  
**Scope:** Operators lacking **skills** vs. those with talents only  
**Basis:** Prior research (P18, P13 gaps) + current state survey  

---

## Current State Summary

**With Talents/Archetype Only** (no skill mechanics):
- Ashlock (Fortress Defender) — identical to Horn; range/archetype only
- Erato (Besieger Sniper) — identical to Typhon; range/archetype only
- Fang (Charger Vanguard) — has trait (DP-on-kill), no S1/S2/S3
- Gravel (Fast Redeploy Specialist) — has talent (deploy shield), no S1/S2/S3
- Horn (Fortress Defender) — archetype switching, no S1/S2/S3
- **Liskarm (Sentinel Defender)** — has talent (SP battery), no S1/S2/S3
- **Nearl (Knight Guardian)** — has talent (passive healing), no S1/S2/S3
- Perfumer (Ring-healer Medic) — has talent (passive HoT), no S1/S2
- Typhon (Besieger Sniper) — archetype only, no S1/S2

**Skills Recently Completed (P16–P18):**
- Bard Inspiration stacking (P16 Inspiration mechanic)
- Shamare Rancor (P17 unique stacking mode)
- Texas S2 Sword Rain (P18 ranged AoE skill)

---

## Priority-Ranked Implementation List

### P19a: Liskarm S1 "Phalanx Dash" — **Medium Effort**
**Why first:** Liskarm has talent, so S1 is additive (not a base mechanic). Highest-impact skill on this list.

**Mechanics:**
- Self buff: +25% DEF for 10s (no stacking cost)
- Can activate while existing buff is active (refreshes duration, does NOT consume SP to extend)
- SP cost: 25 (SL1) → 18 (M3)
- Initial SP: 10 → 15

**ECS Requirements:**
- `BuffStack.FLAT` ATK/DEF ratio boost (existing)
- Time-based buff expiry + refresh pattern
- No new systems; reuses existing buff framework

**Test Scope:** Buff timing, refresh behavior, DEF calculation with stacking

---

### P19b: Nearl S2 "Justice" (or S3 "Holy Knight Verdict") — **Medium Effort**
**Why next:** Nearl has talent; S2 is focused support buff, lower complexity than S3.

**Mechanics (S2):**
- Self buff: +20–40% ATK (scales with SL/M3)
- All adjacent allies: +15–30% ATK (same skill level)
- Duration: 8s
- SP cost: 18 (SL1) → 13 (M3)
- Activation: manual or automatic on timer

**ECS Requirements:**
- `BuffStack.FLAT` ATK boost (existing)
- Aura-emit pattern (one operator buffs adjacent allies)
- No new systems

**Test Scope:** Aura range, multi-target buff application, duration tracking

---

### P19c: Gravel S1 "Smoke Bomb" — **Low Effort**
**Why now:** Gravel has talent; S1 is simple utility (invisibility/evasion).

**Mechanics:**
- Grants Gravel: 60% reduced damage taken for 10s (cumulative with talent shield for first 10s post-deploy)
- Creates a smoke tile (visual obstruction; affects enemy targeting?)
- SP cost: 30 (SL1) → 20 (M3)
- Initial SP: 15

**ECS Requirements:**
- Status effect: `StatusKind.EVASION` or damage reduction (distinct from talent)
- Interaction: talent shield (80% reduction) + skill evasion (60% reduction) stack, or higher wins?
- Optional: smoke tile (targeting obstruction) — defer if not critical

**Test Scope:** Buff stacking mode verification, target interaction

---

### P19d: Fang S1 "Cleave" — **Low Effort**
**Why included:** Fang has trait; S1 is basic ATK boost (no archetype integration needed).

**Mechanics:**
- Self buff: +30% ATK for 10s (E1 baseline)
- Attacks during buff deal 50% splash damage to adjacent enemies (small AoE)
- SP cost: 25 (SL1) → 16 (M3)
- Initial SP: 5

**ECS Requirements:**
- `BuffStack.FLAT` ATK (existing)
- Conditional AoE on attack (attack event triggers secondary AoE to adjacent)
- Per-attack RNG/evaluation: NOT per-tick, but per-hit

**Pattern Gap:** This is the **first operator using per-attack triggering** (not per-tick, not on-skill-activation). Sets precedent for "on_attack_hit" hook + chance evaluation.

**Test Scope:** Buff timing, splash AoE adjacency, per-attack event firing

---

### P19e: Typhon S2 "Explosive Fire" (or S1) — **Medium Effort**
**Why later:** Typhon is data-only (no skill yet), but Besieger archetype + "heaviest target" is already handled by archetype tests.

**Mechanics (S2 candidate):**
- Skill activation: next attack deals 2× ATK Arts damage
- Also guarantees hit (no miss, even on low-ACC enemies)
- Duration: 6s (can overlap with subsequent attacks if ATK interval short)
- SP cost: 30 (SL1) → 18 (M3)
- Initial SP: 10

**ECS Requirements:**
- `attack_modifier` pattern (2× multiplier + Arts forced conversion)
- Guarantee hit flag (bypass MISS chance)
- Time-gated skill mode (expires after 6s)

**Test Scope:** Damage multiplication, Arts type conversion, no-miss verification

---

### P19f: Perfumer S2 "Aroma Therapy" — **Low Effort**
**Why last:** Perfumer has talent; S2 is a focused (targeted) heal, complements passive aura.

**Mechanics:**
- Activate: heal one ally (highest priority: lowest HP% first) for 80–150% ATK value (scales SL/M3)
- Can activate while healing is occurring (no gating)
- SP cost: 20 (SL1) → 12 (M3)
- Initial SP: 8
- Cooldown: 15s (time between activations)

**ECS Requirements:**
- Single-target heal with priority selector (lowest HP%)
- Cooldown tracking (distinct from SP)
- Stat-based heal: `heal = int(perfumer.effective_atk * ratio)`

**Test Scope:** Target selection, heal amount calculation, cooldown reset

---

## Notable ECS Pattern Gaps (Post P19)

| Gap | Current State | P19 Operator | Impact |
|-----|---|---|---|
| **Per-attack RNG triggering** | No operator uses `on_attack_hit` + chance | Fang S1 splash | Medium — first of archetype |
| **Cooldown timer (distinct SP)** | Cooldowns tracked, but not heavily tested | Perfumer S2 | Low — framework exists |
| **Guaranteed-hit flag** | Miss RNG exists, but bypass untested | Typhon S2 | Medium — combat system |
| **Aura multi-target buff (non-healing)** | Healing auras exist (Nearl passive, Perfumer passive) | Nearl S2 | Low — buff pattern reused |
| **Skill overrides blocking-mode range** | Fortress Defenders switch, but skill-gated range not done | (Deferred P20+) | High — complex merge |

---

## Recommended P19 Roadmap

**Cohort 1 (3–4 days):**
1. Liskarm S1 — quick win, existing buff framework
2. Nearl S2 — aura pattern precedent
3. Gravel S1 — simple damage-reduction stacking

**Cohort 2 (2–3 days):**
4. Fang S1 — introduces per-attack event (new pattern, light cost)
5. Perfumer S2 — cooldown + target priority

**Cohort 3 (deferred P20):**
- Typhon S2 — Arts conversion + guaranteed-hit (verify hit RNG system first)
- Erato S1/S2 — follow Typhon once precedent set
- Horn S1/S2 — range override (complex; consider P21+)

---

## Mechanics Requiring Follow-Up Infrastructure

**Per-Attack Triggering Hook:**
- Fang S1 splash needs `on_attack_hit(attacker, defender, damage)` event
- Currently only `on_tick`, `on_kill`, `on_death`, `on_hit_received` exist
- Add slot to `TalentRegistry` + `fire_on_attack_hit` in `combat_system.py`
- **Cost:** 2–3 hours + tests

**Cooldown vs. SP Separation:**
- Perfumer S2 has both: SP charges the skill, cooldown gates re-activation
- Skill components need `cooldown: float` field (or reuse `active_remaining`)
- **Cost:** 1–2 hours (low friction if `active_remaining` reusable)

---

## Sources & Verification

- Liskarm S1: arknights.wiki.gg/wiki/Liskarm
- Nearl S2: arknights.wiki.gg/wiki/Nearl
- Gravel S1: arknights.wiki.gg/wiki/Gravel
- Fang S1: arknights.wiki.gg/wiki/Fang
- Perfumer S2: arknights.wiki.gg/wiki/Perfumer
- Typhon S2: arknights.wiki.gg/wiki/Typhon

---

## Test Coverage Estimate

- **Liskarm S1:** 4–5 tests (buff timing, refresh, stacking)
- **Nearl S2:** 5–6 tests (aura range, ally target, buff calc)
- **Gravel S1:** 3–4 tests (evasion + talent shield interaction)
- **Fang S1:** 4–5 tests (splash AoE, per-attack trigger)
- **Perfumer S2:** 3–4 tests (target priority, cooldown, heal calc)

**Total new tests:** ~20–25 (brings total to ~1230–1235 by P19 end)

