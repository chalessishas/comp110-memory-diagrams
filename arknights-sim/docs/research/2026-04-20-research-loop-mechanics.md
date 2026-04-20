# Research: Unimplemented Arknights Mechanics — 2026-04-20

## Already Implemented (skip these)

- **Shield (StatusKind.SHIELD)** — damage-absorbing HP layer; Shining Illuminate talent, Gravel Tactical Concealment deploy-shield, Bubble Abjurer trait shield
- **Global SP aura (Ptilopsis Unisonant)** — +0.3 SP/s to all allies via `on_tick` talent
- **Operator-buffs-operator ATK aura** — Eyjafjalla/Pallas inspiration (`BuffStack.INSPIRATION`), Sora Bard flat ATK/DEF buffs
- **Conditional ATK buff (HP-threshold)** — Mudrock Rocksteady `on_tick` adds/removes flat DEF buff based on `hp / max_hp`
- **Summon with linked aura** — Ling Dragon's Blood: ally ATK aura conditional on summon being alive (`_has_summon` flag)
- **Summon despawn on retreat/death** — Mayer mech-otters, Ling Long Xian both use `on_death`/`on_retreat` hooks
- **Liberator ATK ramp** — Mlynar `_liberator_ramp` accumulates +5% ATK/s when skill is off, resets on skill activation
- **Fast-redeploy + deploy-shield** — Gravel: 18s CD, 80% damage reduction for 10s after each deploy via `on_deploy`
- **Kill → DP gain** — Fang/Charger archetype `on_kill` talent
- **Kill → SP gain** — Texas2, multiple others via `on_kill`
- **Periodic AoE from EventQueue** — Mudrock S3 five rock-strikes scheduled via `event_queue.schedule()`
- **HP-drain self DoT** — Surtr S3 (approximated at constant rate; ramp unimplemented per previous report)

---

## Top 5 Unimplemented Mechanics (ranked by ECS value)

### 1. Ammunition Mechanic (skill ends on charge depletion, not duration)
- **Operator examples:** Typhon S2 "Eternal Hunt" (4–5 arrows per activation), Lemuen "Salvē Etiam" (5–6 bullets), W S1/S2 grenades
- **Description:** Skill activates with N charges; each attack consumes one charge; skill terminates when charges hit 0 (or manual cancel) rather than after a fixed time window.
- **New ECS primitive needed:** `SkillComponent.ammo_count: int` field + combat system check: when `ammo_count > 0`, decrement on attack-hit; trigger `on_end` when count reaches 0. Duration-based `active_remaining` is bypassed entirely for ammo skills.
- **Estimated LOC:** 30 (SkillComponent field + combat_system decrement + skill_system ammo-end branch) + 15 (tests: ammo consumed per hit, skill ends at 0, manual-cancel resets)
- **Why high value:** Ammunition is used by a large and growing set of operators (W, Typhon, Ch'en alter, Lemuen, Sankta Miksaparato). It is architecturally orthogonal to duration — without it, ammo-based operators must use fake fixed durations that misrepresent burst window timing.

### 2. Barrier (separate damage-absorbing HP pool, scaled from ATK or % max_hp, increments on kill)
- **Operator examples:** Penance "Guardian of the Law" (kill → +15% max_hp barrier, stacks to 300%), Gravel S1 (barrier = 50% max_hp on deploy), Allerdale aura (1000-HP-cap barrier to nearby allies), Papyrus (barrier = portion of her ATK to healed targets)
- **Description:** Unlike `StatusKind.SHIELD` (absorbs exactly one hit), Barrier is a numerical HP-value pool that absorbs any amount of damage until depleted. Multiple sources can increment the same pool up to a cap. Penance's talent grants barrier on every kill and triggers a retaliatory Arts hit when the barrier is struck.
- **New ECS primitive needed:** `StatusKind.BARRIER` (already in wiki taxonomy but NOT in `core/types.py`) with `params["amount"]` and `params["cap"]`. Damage system must route `pre-hp-reduction` damage through Barrier pool first. Talent `on_kill` callback increments `params["amount"]` up to cap. Distinct from SHIELD (multi-value vs one-shot).
- **Estimated LOC:** 25 (new StatusKind + damage routing in combat_system) + 20 (Penance operator: kill-barrier talent + Wreathed in Thorns counter-Arts hit) + 20 (tests: barrier absorbs, kill increments, counter fires, cap respected)
- **Why high value:** Penance is one of the most played 6★ Defenders in the current meta. Her Juggernaut kit is unimplementable without Barrier — Shield is semantically wrong (one-hit vs cumulative pool). Also unlocks Allerdale, Gravel S1 barrier variant, Papyrus.

### 3. On-Kill Barrier Accumulation + Counter-Damage (Penance Wreathed in Thorns)
- **Operator example:** Penance talent 2: while Barrier > 0, any enemy that attacks Penance receives Arts damage = 50% Penance ATK
- **Description:** Reactive counter-damage tied to Barrier presence; fires from `on_hit_received` talent hook. Requires Barrier primitive (item 2 above) to exist first, then 1 extra callback.
- **New ECS primitive needed:** None beyond Barrier — uses existing `on_hit_received` hook + `fire_arts_damage()` helper already in combat_system.
- **Estimated LOC:** 15 (talent callback checking Barrier status, dealing Arts damage to attacker) + 10 (tests: counter fires with barrier, does not fire without)
- **Why high value:** Listed separately from #2 because it is a distinct design pattern (reactive counter-damage conditional on buff presence) that generalises to Mudrock "Unshakeable" trait and other counter-hit operators.

### 4. Summon Count Limit per Deployment (Mayer/Ling deploy-budget, not just alive count)
- **Operator examples:** Mayer (3 Robotters per deployment at E0, +1 at E1, +1 at E2), Ling (same budget model for Long Xian)
- **Description:** Summoner operators have a per-deployment budget of summons they can ever produce in one deployment (not a live-count). Once the budget is exhausted, skill use no longer spawns new tokens even if previous ones are dead. Current Mayer implementation has no budget cap — skills can summon unlimited tokens as long as SP is available.
- **New ECS primitive needed:** `UnitState.summon_budget: int` (set on deploy, decremented on each summon spawn). `world.add_unit()` for summoned tokens must check `carrier.summon_budget > 0` and refuse if exhausted. E1/E2 promotion sets higher budgets.
- **Estimated LOC:** 20 (UnitState field + spawn guard in skill on_start for Mayer/Ling) + 15 (tests: budget depletes, no over-spawn after budget exhausted, redeploy resets budget)
- **Why high value:** Without this, Mayer and Ling simulators overestimate sustained damage and fail long-run scenarios. The budget model is also needed for any future summoner (Deepcolor, toknogi, etc.).

### 5. Nervous Impairment / Skill-Lock Debuff (enemy cannot use skills for N seconds)
- **Operator examples:** Tragodia (new 2025): lures enemies, inflicts Nervous Impairment preventing skill usage for up to 5s; some existing Supporter Hexer operators
- **Description:** A StatusEffect applied to enemies that blocks their skill activation for its duration. Distinct from `SILENCE` (which affects operators) — this is a debuff applied to enemy units, requiring an enemy-side skill system.
- **New ECS primitive needed:** `StatusKind.NERVOUS_IMPAIRMENT` for enemies (enemy skill suppression). Requires enemy units to have `skill_active: bool` / `skill_cd: float` fields and a suppression check during enemy combat tick. Currently the enemy state model has no skill fields.
- **Estimated LOC:** 40 (enemy UnitState skill fields + suppression check in enemy combat + new StatusKind) + 20 (tests: enemy skill fires normally, suppressed with debuff, recovers after)
- **Why medium-high value:** Elite enemies and bosses in Arknights use skills that are core to their threat level. Without enemy skill modeling, any operator whose value comes from denying enemy skills (Tragodia, Gnosis, Manticore) cannot be tested meaningfully.

---

## Immediate Recommendation

**Implement Barrier (StatusKind.BARRIER + damage routing) — approximately 65 LOC total.**

Rationale:
1. Penance is a top-tier Defender missing entirely from the hand-crafted roster despite being mechanically well-documented.
2. Barrier generalises to Gravel's S1 variant, Allerdale's team aura, and Papyrus — one primitive unlocks 4+ operators.
3. The existing SHIELD pattern in `combat_system.py` provides a near-identical routing hook; Barrier is a numerical extension of the same pre-HP damage intercept. Copy the SHIELD intercept, change "consume on first hit" to "subtract from params['amount'], remove when depleted".
4. Penance's `on_kill` barrier increment uses the already-wired `on_kill` talent hook — zero new infrastructure needed there.
5. Ammunition (#1) requires touching `SkillComponent` and `combat_system` simultaneously; higher blast radius for a first pass. Barrier is more contained.

**Specific next step:** Add `BARRIER = "barrier"` to `StatusKind` in `core/types.py`, add Barrier intercept in `combat_system` immediately before the SHIELD check, implement `penance.py` with `on_kill` barrier-stack talent and `on_hit_received` counter-Arts talent, write 8–10 tests covering: deploy gives barrier, kill adds to pool, cap respected, counter fires, barrier absorbs across multiple hits.
