# Arknights-Sim ECS v2 — Next Implementation Priorities
**Date:** 2026-04-19 23:30  
**State at time of research:** 961 tests passing, 51/51 archetypes, 199 main-line stages, 7 multi-operator synergy scenarios  
**Researcher:** sonnet-0419b (Claude Sonnet 4.6)

---

## Research Basis

### Web Findings on Commonly Mis-Simulated Mechanics

**Attack interval frame-rounding** (arknights.wiki.gg, fandom.com/wiki/Attribute/Attack_interval):  
The game runs at 30 FPS. Attack intervals are discretized: `effective_interval = round(interval_secs * 30) / 30`. A 1.6s interval is actually 1.6333…s (49 frames). Simulators that use float seconds directly and compare `atk_cd <= 0` accumulate sub-frame drift over a long fight. The existing ECS uses DT=1/30 ticks so this is well-handled, but the rounding of the computed interval itself must match.

**Deployment search cycle** (wiki.gg/Operator + GamePress attack speed guide):  
Operators search for valid targets every 3 frames (0.1s). The targeting system fires per-tick (every 1/30s) here, which is over-granular but not incorrect — it's conservative in favor of speed.

**Stun/Freeze stops SP accrual** (wiki.gg/Stun, wiki.gg/Freeze):  
A Stunned or Frozen unit cannot attack, move, use skills, or block. Critically, AUTO_TIME SP does not accrue while Stunned. The current `status_system.py` strips `can_act()` but there is no check blocking `AUTO_TIME` SP accrual in `skill_system.py` during status effects. This is a confirmed gap.

**Mudrock S3 "Bloodline of Desecrated Earth" — two-phase mechanic** (wiki.gg/Mudrock, sanitygone.help/mudrock):  
Phase 1 (10s): invulnerability barrier, stops attacking and blocking, 60% MSPD slow to nearby enemies.  
Phase 2 (30s): resumes attacking with reduced ATK interval, +ATK/+DEF buffs, and cleave equal to block count (identical to GUARD_CENTURION trait).  
The transition between phases is a scheduled event at `now + 10.0s` — not a standard skill duration + passive. This two-phase behavior is the textbook use case for `EventQueue.schedule()`.

**SilverAsh S3 — current implementation is synchronous** (`data/characters/silverash.py` `_s3_on_start`):  
The 3 strikes are fired in a tight for-loop inside `on_start`, all in the same tick. The in-game behavior fires them with a small inter-strike delay (~0.15s each based on animation). This matters for: (a) enemies dying before all 3 strikes register, and (b) any on-hit talent firing 3 times in the same tick potentially causing double-application of timed buffs. The current synchronous approach is approximately correct but misses inter-strike timing entirely.

**Pushback** (`combat_system.py` `_apply_push`):  
The current implementation reduces `path_progress` by `distance` tiles and snaps position. The wiki confirms force-weight subtraction determines actual displacement. Current code uses a flat integer distance with no weight check, which is correct for SPEC_PUSHER operators (Shaw, etc.) at their default force level, but will break for enemies with high weight (weight ≥ force → no push). Weight data is in `akgd` enemy JSON but not currently imported.

### Community Assessment of "Complex" Mechanics

From GamePress mastery guides, sanity;gone, and wiki overview pages, the operators consistently flagged as hardest to simulate correctly:

1. **Mudrock S3** — two-phase state machine, invulnerability interruption, transition-scheduled cleave
2. **Thorns** — perpetual passive (never deactivates), deals Arts true damage on melee attacks to all enemies in splash while his archetype is melee — requires per-tick passive not a skill
3. **Mountain** — talent grants extra attack when blocking exactly 1 enemy; edge case fires on the exact tick blocking count changes
4. **W** — delayed bomb placement: S3 plants a bomb at a tile, bomb detonates at `now + delay`; quintessential EventQueue use case
5. **Specter** — near-death auto-revive; HP floor interaction with shield

### Python ECS EventQueue Pattern (Discrete Event Simulation)

The existing `EventQueue` is a min-heap (heapq) keyed by `fire_at` with `dispatch_due(world, now)` called each tick. This is the textbook pattern for discrete-event simulation (DES). The `spawn_system.py` already uses it for wave spawning.

The pattern to reuse for multi-hit skills:

```python
# In on_start of a multi-phase skill:
world.event_queue.schedule(now + 0.15, "silverash_s3_strike2",
    attacker_id=carrier.unit_id, hit_index=1)
world.event_queue.schedule(now + 0.30, "silverash_s3_strike3",
    attacker_id=carrier.unit_id, hit_index=2)

# Registered handler:
def _sa_strike_handler(world, ev):
    carrier = world.unit_by_id(ev.payload["attacker_id"])
    if carrier is None or not carrier.alive or not carrier.deployed:
        return
    for t in _get_targets_in_range(world, carrier):
        dmg = t.take_physical(carrier.effective_atk)
        world.global_state.total_damage_dealt += dmg

world.event_queue.register("silverash_s3_strike2", _sa_strike_handler)
world.event_queue.register("silverash_s3_strike3", _sa_strike_handler)
```

The `schedule_repeating` helper already exists on `EventQueue` for N identical events at fixed intervals.

---

## TOP 3 Concrete Next Implementation Tasks

---

### TASK 1: EventQueue-Driven Multi-Strike for SilverAsh S3 + W S3 Delayed Bomb

**Rationale:**  
The current SilverAsh S3 fires all 3 strikes in one tick. This is the highest-visibility correctness gap with an existing P4 demo. W's S3 (bomb planting) is listed as the canonical EventQueue use case by the community; implementing it proves the pattern works for skills, not just spawns. Together they validate the `EventQueue`-as-skill-effect primitive for all future multi-phase operators (Mudrock S3 phase transition, Archetto multi-hit).

**Existing patterns to reuse:**  
- `EventQueue.schedule()` / `schedule_repeating()` — already in `core/events/event_queue.py`  
- `world.event_queue.register("spawn", ...)` in `spawn_system.py` — identical pattern  
- `silverash.py` `_s3_on_start` / `on_end` hooks — refactor in-place, no new files needed  
- `world.unit_by_id()` — safe deref pattern already on `World`

**Implementation plan:**

*SilverAsh S3 (refactor ~30 LOC):*
1. In `_s3_on_start`, keep strike 1 synchronous (fires immediately with boosted ATK).
2. Schedule strike 2 at `now + 0.133s` and strike 3 at `now + 0.267s` via `event_queue.schedule`.
3. Register a handler `"sa_s3_extra_strike"` that resolves `attacker_id`, checks alive+deployed, finds in-range targets, fires `take_physical(carrier.effective_atk)`.
4. Update test `test_s3_burst_hits_3_times_on_activation` to run `w.tick()` × 9 (≈0.3s) before asserting total damage.

*W S3 "Delayed Blast" (new file `data/characters/w.py`, ~80 LOC):*
1. `on_start`: place bomb at targeted tile, schedule `"w_bomb_detonate"` at `now + 5.0s`.
2. Handler: AoE Arts damage to all enemies within radius 1.5 at stored tile position.
3. 2 tests: (a) bomb detonates at correct time, (b) out-of-range enemies unaffected.

**Estimated LOC:** 30 (SA refactor) + 80 (W S3) + 40 (tests) = ~150 LOC  
**Estimated effort:** 2h  
**Risk:** `carrier.effective_atk` in the deferred handler uses the ATK buff applied in `on_start`; buff must still be active at strike 2/3 time (15s duration >> 0.267s delay, so fine). If carrier dies before `fire_at`, the null-guard in the handler prevents a crash.

---

### TASK 2: Mudrock S3 Two-Phase Implementation (EventQueue Phase Transition)

**Rationale:**  
Mudrock is the most-cited complex operator. Her S3 is a two-phase state machine — phase 1 is an invulnerability + no-attack window, phase 2 restores combat with a cleave buff. The phase transition is inherently a scheduled event (`now + 10.0s`). This cannot be represented cleanly with the current `active_remaining` countdown model (which only has on_start / on_tick / on_end). Implementing Mudrock validates the EventQueue for phase-gated mechanics and creates a reusable pattern for any operator with mid-duration state changes (Specter revival, Surtr passive expiration, etc.).

**Existing patterns to reuse:**  
- `_apply_centurion_cleave` in `combat_system.py` — identical to Mudrock S3 phase 2 cleave; can call directly or mirror logic  
- `Buff(axis=BuffAxis.DEF, ...)` with `expires_at` — already used for status proc debuffs  
- `_s3_on_end` in `silverash.py` — cleanup pattern for removing buffs by `source_tag`  
- `can_act()` on `UnitState` — already blocks movement/attack during Stun; need to reuse for invulnerability window

**Implementation plan (~120 LOC in `data/characters/mudrock.py`):**

```
Phase 1 on_start (t=0):
  - Set carrier.invulnerable = True  (new bool flag on UnitState, default False)
  - Set carrier.block = 0            (cannot block during phase 1)
  - Apply MSPD slow aura to nearby enemies (2-tile radius)
  - Schedule "mudrock_s3_phase2" at now + 10.0s (carrier.unit_id in payload)

Phase 2 handler (t=10s):
  - carrier.invulnerable = False
  - carrier.block = 3                (restore block)
  - Apply ATK + DEF ratio buffs with expires_at = now + 30.0s
  - Apply atk_interval reduction buff with expires_at = now + 30.0s
  - Set carrier.cleave_active = True (new bool, checked in combat_system)

on_end (t=40s):
  - Remove ATK/DEF/interval buffs by source_tag
  - carrier.cleave_active = False
```

New UnitState fields needed: `invulnerable: bool = False`, `cleave_active: bool = False`.  
In `combat_system.py`: skip damage application when `target.invulnerable` (1 line); if `u.cleave_active`, call `_apply_centurion_cleave` (1 line, already exists).

**Tests to add (~50 LOC in `tests/test_v2_mudrock_crusher.py` extension):**
- Phase 1: Mudrock takes 0 damage during invulnerability window
- Phase 1 → Phase 2 transition fires at t≈10s (tolerance ±1 tick)
- Phase 2: Mudrock deals cleave damage to multiple blocked enemies
- Phase 2 buffs expire at t≈40s

**Estimated LOC:** 120 (mudrock.py) + 15 (unit_state.py new fields) + 10 (combat_system.py hooks) + 50 (tests) = ~195 LOC  
**Estimated effort:** 3h  
**Risk:** The MSPD slow aura in phase 1 requires either a per-tick passive scan (like Myrtle's Glistening HoT) or a scheduled event to remove it. The on_tick approach is simpler; add `on_tick` to the skill registry entry that applies MSPD debuff to enemies within 2 tiles.

---

### TASK 3: Stage Integration Test Coverage — Parametrized Clear Verification Across main_01–main_03

**Rationale:**  
There are 199 stages loaded and the bulk test (`test_v2_stage_bulk.py`) confirms they parse and build worlds. But only main_00 stages (11 stages) have actual clearance tests with operators placed. The remaining 188 stages have zero "does it win?" coverage. Bugs in wave timing, route edge cases, or tile mapping for higher-chapter stages would be invisible until a user actually runs a high-chapter stage. One parametrized test that runs a fixed operator squad against a sample of main_01–main_13 stages catches route data bugs (wrong tile, misrouted enemy) that parse tests cannot.

**Existing patterns to reuse:**  
- `test_v2_stage_main00.py` `load_and_build` + `_place` + `world.run(max_seconds=180.0)` — copy exactly  
- `test_v2_stage_bulk.py` `_main_stages()` glob — reuse for parametrize list  
- `make_silverash()` + `make_liskarm()` — already proven to clear main_00; use as canonical strong squad

**Implementation plan (~80 LOC in `tests/test_v2_stage_integration.py`):**

```python
SAMPLE_STAGES = [
    "main_01-01", "main_01-06",
    "main_02-01", "main_02-06",
    "main_03-01", "main_03-06",
    "main_04-01",
    "main_05-01",
    "main_06-01",
    "main_07-01",
]

@pytest.mark.parametrize("stage_name", SAMPLE_STAGES)
def test_stage_clears_with_default_squad(stage_name):
    stage, world = load_and_build(_stage_path(stage_name))
    sa = make_silverash()
    lk = make_liskarm()
    # Place at path midpoints derived from stage tile data
    _place_at_chokepoint(world, stage, sa)
    _place_at_chokepoint(world, stage, lk, offset=1)
    result = world.run(max_seconds=300.0)
    assert result in ("win", "loss"), f"{stage_name}: unexpected {result!r}"
    # Weak assertion: at least test completes without exception or timeout
    # Strict assertion only where stage is known-clearable:
    if stage_name in KNOWN_CLEARABLE:
        assert result == "win"
```

The `_place_at_chokepoint` helper inspects the stage's first tile marked `buildable_melee=True` adjacent to the primary enemy route — a heuristic that works for most main-line stages.

**Why "win or loss" not strict "win":**  
Higher chapters have stronger enemies than main_00. The goal is not to guarantee the sim always wins, but to guarantee the sim does not crash, timeout, or produce undefined behavior. Any `result == "timeout"` (world.run returns `"timeout"`) indicates a broken state (no enemies dying, infinite stall) and is a test failure.

**Estimated LOC:** 80 (new test file) + 20 (chokepoint heuristic helper)  = ~100 LOC  
**Estimated effort:** 1.5h  
**Risk:** Higher-chapter stages may use enemy types not yet in the enemy roster, causing `KeyError` at spawn time. This is a real bug surface; the test will expose it, which is exactly the value. Enemy roster completeness is a separate concern tracked by `test_v2_enemy_roster.py`.

---

## Summary Table

| Task | Type | Impact | Effort | LOC | Reuses |
|------|------|--------|--------|-----|--------|
| **T1: EventQueue multi-strike (SA S3 + W S3)** | Correctness + feature | HIGH — fixes P4 burst timing, proves EventQueue for skills | 2h | ~150 | EventQueue, spawn pattern, existing silverash.py |
| **T2: Mudrock S3 two-phase** | Feature + correctness | HIGH — most-cited hard mechanic, proves phase-gated EventQueue | 3h | ~195 | centurion_cleave, Buff/expires_at, on_end pattern |
| **T3: Stage integration parametrized test** | Test coverage | MEDIUM-HIGH — 188 untested stages, catches route/tile/wave bugs | 1.5h | ~100 | load_and_build, existing stage patterns |

**Recommended sequence:** T1 → T3 → T2.  
T1 is lowest-risk (isolated refactor with existing tests as guard rails).  
T3 unlocks regression detection for all future stage work.  
T2 is highest-complexity but has clear implementation path once T1 proves EventQueue for skills.

---

## Critical Mechanics Gaps Not Yet In Top 3

These were identified but deferred for next cycle:

**SP lockout during Stun/Freeze** (confirmed gap, ~20 LOC):  
`skill_system.py` does not check `u.can_act()` before `AUTO_TIME` SP accrual. Fix: add `if not u.can_act(): continue` before SP accumulation block. Very small fix, worth doing inline during any `skill_system` touch.

**Enemy weight vs. push force** (data gap, ~40 LOC):  
`_apply_push` uses flat integer tile displacement with no weight check. Need to import `weight` from akgd enemy data and gate push on `force > weight`. Without this, Shaw pushes unkillable bosses off-path incorrectly.

**Texas DP talent bug** (confirmed correctness bug from previous research):  
`texas_dp_on_kill` should be `texas_dp_at_deploy`. 30-min fix, well-documented in prior research (2026-04-19-1914). No new investigation needed — just execute.

---

## References

- [Attack interval — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Attribute/Attack_interval)
- [Shift — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Shift)
- [Stun — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Stun)
- [Mudrock — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Mudrock)
- [Mudrock Overview — Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Mudrock/Overview)
- [Mudrock Guide — Sanity;Gone](https://old.sanitygone.help/operators/mudrock)
- [SilverAsh — Arknights Wiki Fandom](https://arknights.fandom.com/wiki/SilverAsh)
- [GamePress: Arknights Mechanics — Attack Speed](https://ak.gamepress.gg/core-gameplay/arknights-mechanics-behind-numbers-attack-speed)
- [Python heapq — discrete event simulation](https://phillipmfeldman.org/Python/discrete_event_simulation/index.html)
- [ECS pattern for Python games](https://github.com/ikvk/ecs_pattern)
