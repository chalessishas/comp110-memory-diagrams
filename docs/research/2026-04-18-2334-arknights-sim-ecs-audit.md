# Research Report — arknights-sim ECS + Mechanics Audit
**Generated:** 2026-04-18 23:34 | Agent: sonnet-0418r (background WebSearch)

---

## 1. ECS Performance Patterns in Python

The SanderMertens ECS FAQ identifies two core trade-offs: archetype-based ECS wins on bulk iteration (cache locality), sparse-set ECS wins on add/remove frequency. The current implementation iterates `world.units` as a plain Python list — correct but no cache locality. In CPython, loop overhead dominates over cache misses anyway, so NumPy-vectorized stat computation is the highest-leverage optimization if performance becomes an issue. `esper` (benmoran56/esper, v3.x) is the most-used Python ECS, but at 62 tests (sub-100ms) performance is not yet a bottleneck.

**Key anti-pattern flagged:** `getattr(u, "__target__", None)` in `combat_system.py` — implicit relationship stored on entity, invisible to type system.

---

## 2. Arknights Mechanics Gaps

### 2a. ASPD Formula — Correct but missing hard caps
Formula `atk_interval * 100.0 / max(1.0, aspd)` is equivalent to `b * 100/(100+x)` — matches wiki. **Missing:** ASPD hard caps [20, 600] not enforced in `effective_aspd`.

### 2b. FRAGILE — Stacking is wrong ⚠️ CORRECTNESS BUG
Current code multiplies all FRAGILE stacks: `fragile_mult *= 1.0 + amount`.
Wiki says: **highest value per same-type wins; different-type sources multiply.** Fix: group by `source_tag`, take `max` per group, multiply groups. ~5 lines.
**File:** `core/state/unit_state.py:254–267`

### 2c. SP Lockout — Defined but never enforced
`SkillComponent.locked_out: bool = False` exists but is never set/checked in `skill_system.py`. Wiki: auto skills hold SP at full and block SP recovery when no valid target. Without this, SP ticks freely even when unit has no target — causes wrong skill timing. Critical for Exusiai/SilverAsh/Angelina.
**File:** `core/systems/skill_system.py`

### 2d. Arts lethal edge case
Wiki: Arts damage only kills if strictly greater than current HP — unit can survive at exactly 0 HP from Arts. Current `take_damage()` sets `alive=False` when `hp==0`, which is wrong for Arts sources.

---

## 3. Open-Source Reference

No Python combat simulator with comparable talent hooks found. The `talent_registry.py` hook pattern (registry dict of callbacks keyed by behavior_tag) is more sophisticated than any public reference. Main gap in all public simulators: SP lockout state machine is universally skipped, causing 1–2s timing errors.

---

## 3 Actionable Improvements (Ranked)

**#1 — Fix FRAGILE stacking** (HIGH, ~30 min) — correctness bug affecting all FRAGILE interactions
- `core/state/unit_state.py` lines 254–267
- Change multiply-all to: group by source_tag → max per group → multiply groups

**#2 — Enforce SP lockout in skill_system** (HIGH, ~1 hour) — wrong skill timing without this
- `core/systems/skill_system.py`
- Set `sk.locked_out = True` when SP full but no valid target; skip SP gain while locked

**#3 — Clamp ASPD [20, 600] + handle flat interval modifier** (MEDIUM, ~30 min)
- Add `aspd = max(20.0, min(600.0, aspd))` in `current_atk_interval`
- Exusiai S2 may need `BuffAxis.ATK_INTERVAL_FLAT` axis rather than ASPD buff

---

**Lower priority:** Arts lethal 0-HP edge case, `__target__` → TargetComponent refactor.
