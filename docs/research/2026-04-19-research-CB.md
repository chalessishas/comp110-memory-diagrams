# Research Loop — 2026-04-19 — Improvement Proposals

**Current State:** 610 tests green, P8 complete (Shaw SPEC_PUSHER), 10 status types, chain/crit/push mechanics.

---

## 1. Path Distance Calculation Safe for Single Routes Only

**Issue:** `targeting_system.py:60–62` computes `path_distance_remaining = path_len - path_progress` for all units. This assumes one canonical path per enemy.

**Evidence:**
- Line 62: `path_len = len(e.path) - 1 if e.path else 0`
- Arknights maps with multiple entry routes (e.g., late-chapter challenge maps) have enemies that choose routes dynamically
- YAML stage loader (`stages/loader.py:152`) reads only a single `wave.path` per enemy wave
- No multi-route branching logic exists in spawn or movement systems

**Impact:** Any future multi-route map will target incorrectly; enemies taking alternate routes will still be prioritized by a path they're not on.

**Proposal:** 
- Add `route_id: int` field to `UnitState` 
- Extend YAML to declare branch points: `routes: [{id: 0, path: [...]}, {id: 1, path: [...]}]`
- Update distance calc to use the unit's actual route: `remaining = len(current_route) - 1 - progress`

---

## 2. Missing Archetype Special Handling (6/27 Archetypes Unimplemented)

**Evidence:**
- `types.py:111–169` defines 27 archetypes; currently only 4 have targeting/combat hooks:
  - `SNIPER_DEADEYE` — lowest DEF priority (targeting_system.py:70)
  - `SNIPER_SIEGE` — highest weight priority + 1.5× ATK bonus (both files)
  - `DEF_FORTRESS` — ranged AoE toggle (targeting_system.py:110)
  - `GUARD_CENTURION` — multi-target block (targeting_system.py:132)

- Entirely missing: `CASTER_BLAST`, `CASTER_PHALANX`, `SPEC_HOOKMASTER`, `SUP_SUMMONER`, `SUP_BARD`, all Vanguard archetypes except trait DP tags

**Impact:** These archetypes fall to generic single-target behavior, losing unique mechanics (Phalanx tile-lock, Blast stun radius, Hook extended reach, Summoners spawning units).

**Proposal:**
- Create `archetype_traits.py` registry mapping archetype → (targeting override, combat override, range override)
- Implement `CASTER_PHALANX` phalanx formation check (line 78–79 fallback)
- Add `SPEC_HOOKMASTER` extended range bonus in `targeting_system._enemy_in_range()`
- Flag `SUP_SUMMONER`, `CASTER_BLAST` as requiring new mechanics; create stub TODOs

---

## 3. Rope Missing Archetype Assignment

**Issue:** `/data/characters/generated/rope.py` (E2 max, trust 100) has no `archetype` field.

**Evidence:**
- Lines 10–26: only `profession`, `name`, `stats`, `block=2`, `cost=12`
- Rope is Specialist (line 21) but lacks RoleArchetype enum value
- All other generated operators have archetype set

**Impact:** Rope cannot benefit from Specialist-specific mechanics or be referenced in tests needing archetype checks.

**Proposal:**
- Determine Rope's archetype from game data (likely `SPEC_HOOKMASTER` given melee+2-block pattern)
- Regenerate: `python tools/gen_characters.py char_236_rope --archetype spec_hookmaster`
- Or manually append `op.archetype = RoleArchetype.SPEC_HOOKMASTER` to `make_rope()`

---

## 4. Deferred Vigil Summon Mechanic Creates Tech Debt

**Evidence:**
- `/data/characters/vigil.py` comment: "Wolf shadow summon mechanic deferred — DP drip modeled faithfully"
- No summon spawning in combat_system or spawn_system
- No child unit lifecycle management in World

**Impact:** Vigil is partially implemented; stat modeling works but core fantasy (shadow summons) is absent. Increases future refactor risk when summons are implemented.

**Proposal:**
- Create `/core/mechanics/summon_system.py` to handle summon spawn/despawn/lifecycle
- Add `summons: List[UnitState]` field to operators that call summons
- Implement Vigil's S2 in talent_registry with summon spawning hook
- Mark as P9 feature to unblock Vigil full release

---

## 5. Targeting System Structure Opportunity

**Observation:** `targeting_system.py` mixes three concerns:
1. Range checking (`_enemy_in_range`)
2. Blocking logic (`_update_block_assignments`)
3. Archetype-specific selection (`_targeting_for_operator` lines 70–75)

**Proposal (low priority):**
- Extract range/blocking into `block_system.py` (separate system)
- Rename `_targeting_for_operator` → `select_target` with archetype dispatch table
- This unblocks easier addition of new archetypes and simplifies combat_system refactoring

---

**Next Steps:** Prioritize by impact:
1. **Fix Rope archetype** (5 min, unblocks tests)
2. **Implement path multi-route support** (design doc + 2–3 test cases)
3. **Add 2–3 missing archetypes** (e.g., PHALANX targeting, HOOKMASTER range) as P9
4. **Resolve Vigil deferred summons** (P9, depends on summon_system)
