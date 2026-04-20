"""Shamare — SUP_HEXER: Rancor talent ATK/DEF debuff on hit + S2 AoE FRAGILE.

SUP_HEXER trait:
  - Normal attacks apply ATK_DOWN (−25%) and DEF_DOWN (−25%) for 10s
  - Debuffs refresh on repeated hits (expires_at resets)
  - S2 "Puppetmaster": instant AoE applies FRAGILE (+65% dmg taken) for 20s

Tests cover:
  - Archetype is SUP_HEXER
  - ATK_DOWN applied after hitting enemy
  - DEF_DOWN applied after hitting enemy
  - Rancor debuffs refresh expires_at on re-hit
  - Rancor debuffs expire after 10s
  - S2 applies FRAGILE to all enemies in range
  - S2 FRAGILE expires after 20s
  - FRAGILE actually amplifies damage taken
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, DT, Faction, RoleArchetype, StatusKind
from core.systems import register_default_systems
from data.characters.shamare import (
    make_shamare,
    _RANCOR_ATK_TAG, _RANCOR_DEF_TAG,
    _RANCOR_DURATION,
    _S2_FRAGILE_TAG, _S2_FRAGILE_AMOUNT, _S2_FRAGILE_DURATION,
)
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(pos=(1, 1), hp=99999, defence=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = defence; e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Archetype is SUP_HEXER
# ---------------------------------------------------------------------------

def test_shamare_archetype():
    s = make_shamare()
    assert s.archetype == RoleArchetype.SUP_HEXER


# ---------------------------------------------------------------------------
# Test 2: ATK_DOWN applied after Shamare hits enemy
# ---------------------------------------------------------------------------

def test_rancor_atk_down_applied():
    """After Shamare hits an enemy, ATK_DOWN status appears on that enemy."""
    w = _world()
    s = make_shamare()
    s.deployed = True; s.position = (0.0, 1.0)
    s.atk_cd = 0.0   # force immediate first attack
    w.add_unit(s)

    enemy = _slug(pos=(1, 1))
    enemy.atk = 200   # non-zero so -25% ratio is measurable
    base_atk = enemy.effective_atk
    w.add_unit(enemy)

    for _ in range(3):
        w.tick()

    atk_statuses = [st for st in enemy.statuses if st.kind == StatusKind.ATK_DOWN]
    assert len(atk_statuses) >= 1, (
        f"ATK_DOWN must be applied after Shamare hits; statuses={[st.kind for st in enemy.statuses]}"
    )
    assert enemy.effective_atk < base_atk, (
        f"enemy ATK must decrease; was {base_atk}, now {enemy.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: DEF_DOWN applied after Shamare hits enemy
# ---------------------------------------------------------------------------

def test_rancor_def_down_applied():
    """After Shamare hits an enemy, DEF_DOWN status and reduced effective_def appear."""
    w = _world()
    s = make_shamare()
    s.deployed = True; s.position = (0.0, 1.0)
    s.atk_cd = 0.0
    w.add_unit(s)

    enemy = _slug(pos=(1, 1), defence=200)
    base_def = enemy.effective_def
    w.add_unit(enemy)

    for _ in range(3):
        w.tick()

    def_statuses = [st for st in enemy.statuses if st.kind == StatusKind.DEF_DOWN]
    assert len(def_statuses) >= 1, (
        f"DEF_DOWN must be applied after Shamare hits; statuses={[s.kind for s in enemy.statuses]}"
    )
    assert enemy.effective_def < base_def, (
        f"enemy DEF must decrease; was {base_def}, now {enemy.effective_def}"
    )


# ---------------------------------------------------------------------------
# Test 4: Rancor debuffs refresh expires_at on re-hit
# ---------------------------------------------------------------------------

def test_rancor_debuffs_refresh():
    """Each hit resets expires_at — the debuff doesn't fall off while Shamare attacks."""
    w = _world()
    s = make_shamare()
    s.deployed = True; s.position = (0.0, 1.0)
    s.atk_cd = 0.0
    w.add_unit(s)

    enemy = _slug(pos=(1, 1))
    w.add_unit(enemy)

    # First hit
    for _ in range(3):
        w.tick()

    atk_st = next((st for st in enemy.statuses if st.source_tag == _RANCOR_ATK_TAG), None)
    assert atk_st is not None, "ATK_DOWN must be present after first hit"
    first_expires = atk_st.expires_at

    # Wait half the duration then force another hit
    for _ in range(int(TICK_RATE * (_RANCOR_DURATION / 2))):
        w.tick()
    s.atk_cd = 0.0   # force another attack
    w.tick()

    atk_st2 = next((st for st in enemy.statuses if st.source_tag == _RANCOR_ATK_TAG), None)
    assert atk_st2 is not None, "ATK_DOWN must persist after re-hit"
    assert atk_st2.expires_at > first_expires, (
        f"Re-hit must push expires_at forward; first={first_expires:.3f}, now={atk_st2.expires_at:.3f}"
    )


# ---------------------------------------------------------------------------
# Test 5: Rancor debuffs expire after 10s
# ---------------------------------------------------------------------------

def test_rancor_debuffs_expire():
    """ATK_DOWN and DEF_DOWN must be gone after _RANCOR_DURATION seconds without re-hit."""
    w = _world()
    s = make_shamare()
    s.deployed = True; s.position = (0.0, 1.0)
    s.atk_cd = 0.0
    w.add_unit(s)

    enemy = _slug(pos=(1, 1))
    w.add_unit(enemy)

    # Trigger one hit
    for _ in range(3):
        w.tick()

    assert any(st.source_tag == _RANCOR_ATK_TAG for st in enemy.statuses), \
        "ATK_DOWN must be present right after hit"

    # Freeze Shamare so she can't refresh the debuff
    s.atk_cd = 9999.0

    # Advance past the debuff duration
    for _ in range(int(TICK_RATE * (_RANCOR_DURATION + 1))):
        w.tick()

    atk_remaining = [st for st in enemy.statuses if st.source_tag == _RANCOR_ATK_TAG]
    def_remaining = [st for st in enemy.statuses if st.source_tag == _RANCOR_DEF_TAG]
    assert len(atk_remaining) == 0, f"ATK_DOWN must have expired; remaining={atk_remaining}"
    assert len(def_remaining) == 0, f"DEF_DOWN must have expired; remaining={def_remaining}"


# ---------------------------------------------------------------------------
# Test 6: S2 applies FRAGILE to all enemies in range
# ---------------------------------------------------------------------------

def test_s2_fragile_applied_to_enemies_in_range():
    """Shamare S2 fires and applies FRAGILE to every enemy within attack range."""
    w = _world()
    s = make_shamare()
    s.deployed = True; s.position = (0.0, 1.0)
    w.add_unit(s)

    # Two enemies in range (dx=1, dy=0 and dx=2, dy=0)
    e1 = _slug(pos=(1, 1))
    e2 = _slug(pos=(2, 1))
    # One enemy out of range
    e_out = _slug(pos=(5, 1))
    w.add_unit(e1); w.add_unit(e2); w.add_unit(e_out)

    # Fire skill manually by setting SP to max
    s.skill.sp = float(s.skill.sp_cost)
    w.tick()

    fragile_e1 = [st for st in e1.statuses if st.source_tag == _S2_FRAGILE_TAG]
    fragile_e2 = [st for st in e2.statuses if st.source_tag == _S2_FRAGILE_TAG]
    fragile_out = [st for st in e_out.statuses if st.source_tag == _S2_FRAGILE_TAG]

    assert len(fragile_e1) == 1, f"e1 in range must be FRAGILE; statuses={[s.kind for s in e1.statuses]}"
    assert len(fragile_e2) == 1, f"e2 in range must be FRAGILE; statuses={[s.kind for s in e2.statuses]}"
    assert len(fragile_out) == 0, f"e_out of range must NOT be FRAGILE"
    assert abs(fragile_e1[0].params["amount"] - _S2_FRAGILE_AMOUNT) < 0.01


# ---------------------------------------------------------------------------
# Test 7: S2 FRAGILE expires after 20s
# ---------------------------------------------------------------------------

def test_s2_fragile_expires():
    """FRAGILE applied by S2 must expire after _S2_FRAGILE_DURATION seconds."""
    w = _world()
    s = make_shamare()
    s.deployed = True; s.position = (0.0, 1.0)
    w.add_unit(s)

    enemy = _slug(pos=(1, 1))
    w.add_unit(enemy)

    s.skill.sp = float(s.skill.sp_cost)
    w.tick()

    assert any(st.source_tag == _S2_FRAGILE_TAG for st in enemy.statuses), \
        "FRAGILE must be applied by S2"

    # Advance past FRAGILE duration
    for _ in range(int(TICK_RATE * (_S2_FRAGILE_DURATION + 1))):
        w.tick()

    remaining = [st for st in enemy.statuses if st.source_tag == _S2_FRAGILE_TAG]
    assert len(remaining) == 0, f"FRAGILE must have expired; remaining={remaining}"


# ---------------------------------------------------------------------------
# Test 8: FRAGILE amplifies damage taken
# ---------------------------------------------------------------------------

def test_fragile_amplifies_damage():
    """An enemy under FRAGILE takes more damage than without FRAGILE."""
    w = _world()
    s = make_shamare()
    s.deployed = True; s.position = (0.0, 1.0)
    w.add_unit(s)

    # Two identical enemies — one will be given FRAGILE manually
    e_normal = _slug(pos=(1, 1), hp=50000, defence=0)
    e_fragile = _slug(pos=(2, 1), hp=50000, defence=0)
    w.add_unit(e_normal); w.add_unit(e_fragile)

    # Apply FRAGILE to e_fragile manually (bypass S2 firing complexity)
    from core.state.unit_state import StatusEffect
    e_fragile.statuses.append(StatusEffect(
        kind=StatusKind.FRAGILE,
        source_tag=_S2_FRAGILE_TAG,
        expires_at=float("inf"),
        params={"amount": _S2_FRAGILE_AMOUNT},
    ))

    # Hit both with 1000 raw physical damage
    raw = 1000
    e_normal.take_physical(raw)
    e_fragile.take_physical(raw)

    dmg_normal = 50000 - e_normal.hp
    dmg_fragile = 50000 - e_fragile.hp

    assert dmg_fragile > dmg_normal, (
        f"FRAGILE target must take more damage; normal={dmg_normal}, fragile={dmg_fragile}"
    )
    expected_ratio = 1.0 + _S2_FRAGILE_AMOUNT
    actual_ratio = dmg_fragile / dmg_normal
    assert abs(actual_ratio - expected_ratio) < 0.05, (
        f"Damage ratio must be ~{expected_ratio:.2f}; got {actual_ratio:.3f}"
    )
