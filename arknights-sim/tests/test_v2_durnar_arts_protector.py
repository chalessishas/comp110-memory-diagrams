"""Dur-nar — DEF_ARTS_PROTECTOR: Arts damage to blocked enemies; DEF-class operator.

DEF_ARTS_PROTECTOR trait:
  - Deals Arts damage (reduced by RES, NOT by DEF) to blocked enemies
  - Block=3, melee range only

Talent "Thunder Strike": ATK+20% when 2+ enemies are currently blocked.
  - Applied each tick the condition holds; removed when count drops below 2.

S2 "Iron Defense": 25s duration.
  - DEF+50% (ratio buff on effective_def)
  - Block increases from 3 to 4
  - Reverts both on skill end

Tests cover:
  - Archetype is DEF_ARTS_PROTECTOR, attack_type=ARTS, block=3
  - Attack damage is reduced by RES (not physical DEF)
  - High physical DEF on enemy does NOT reduce Arts damage
  - Talent: no buff with only 1 blocked enemy
  - Talent: ATK+20% when 2+ blocked
  - Talent buff removed when blocked count drops below 2
  - S2 applies DEF+50% ratio buff
  - S2 increases block to 4; reverts to 3 on end
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, DT, Faction, RoleArchetype, AttackType
from core.systems import register_default_systems
from data.characters.durnar import (
    make_durnar,
    _TALENT_BUFF_TAG, _TALENT_ATK_RATIO, _TALENT_THRESHOLD,
    _S2_DEF_BUFF_TAG, _S2_DEF_RATIO, _S2_BASE_BLOCK, _S2_BLOCK_BONUS, _S2_DURATION,
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


def _slug(pos=(0, 1), hp=99999, defence=0, res=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = int(defence); e.res = float(res)
    e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Archetype, attack_type, and base block
# ---------------------------------------------------------------------------

def test_durnar_archetype_and_stats():
    d = make_durnar()
    assert d.archetype == RoleArchetype.DEF_ARTS_PROTECTOR
    assert d.attack_type == AttackType.ARTS, "Dur-nar must deal Arts damage"
    assert d.block == 3, f"Base block must be 3; got {d.block}"


# ---------------------------------------------------------------------------
# Test 2: Arts damage is reduced by RES, not physical DEF
# ---------------------------------------------------------------------------

def test_arts_damage_reduced_by_res():
    """Enemy with RES=50 must take less damage than same enemy with RES=0."""
    w = _world()
    d = make_durnar()
    d.deployed = True; d.position = (0.0, 1.0)
    d.atk_cd = 0.0
    w.add_unit(d)

    low_res = _slug(pos=(0, 1), hp=99999, defence=0, res=0)
    w.add_unit(low_res)

    # Measure damage against RES=0
    for _ in range(3):
        w.tick()
    dmg_no_res = 99999 - low_res.hp

    # Separate world for RES=50 test
    w2 = _world()
    d2 = make_durnar()
    d2.deployed = True; d2.position = (0.0, 1.0)
    d2.atk_cd = 0.0
    w2.add_unit(d2)

    high_res = _slug(pos=(0, 1), hp=99999, defence=0, res=50)
    w2.add_unit(high_res)

    for _ in range(3):
        w2.tick()
    dmg_high_res = 99999 - high_res.hp

    assert dmg_no_res > 0, "Must have dealt damage"
    assert dmg_no_res > dmg_high_res, (
        f"Arts damage must be reduced by RES; RES=0 dealt {dmg_no_res}, RES=50 dealt {dmg_high_res}"
    )


# ---------------------------------------------------------------------------
# Test 3: Physical DEF does NOT reduce Arts damage
# ---------------------------------------------------------------------------

def test_arts_damage_not_reduced_by_physical_def():
    """Enemy physical DEF must not affect Arts damage output."""
    w1 = _world()
    d1 = make_durnar()
    d1.deployed = True; d1.position = (0.0, 1.0)
    d1.atk_cd = 0.0
    w1.add_unit(d1)

    e_no_def = _slug(pos=(0, 1), hp=99999, defence=0, res=0)
    w1.add_unit(e_no_def)
    for _ in range(3):
        w1.tick()
    dmg_no_def = 99999 - e_no_def.hp

    w2 = _world()
    d2 = make_durnar()
    d2.deployed = True; d2.position = (0.0, 1.0)
    d2.atk_cd = 0.0
    w2.add_unit(d2)

    e_high_def = _slug(pos=(0, 1), hp=99999, defence=2000, res=0)
    w2.add_unit(e_high_def)
    for _ in range(3):
        w2.tick()
    dmg_high_def = 99999 - e_high_def.hp

    assert dmg_no_def > 0, "Must have dealt damage"
    assert dmg_no_def == dmg_high_def, (
        f"Physical DEF must NOT reduce Arts damage; "
        f"DEF=0: {dmg_no_def}, DEF=2000: {dmg_high_def}"
    )


# ---------------------------------------------------------------------------
# Test 4: Talent — no buff with only 1 blocked enemy
# ---------------------------------------------------------------------------

def test_talent_no_buff_single_blocked():
    """Thunder Strike must NOT activate with fewer than 2 blocked enemies."""
    w = _world()
    d = make_durnar()
    d.deployed = True; d.position = (0.0, 1.0)
    w.add_unit(d)

    # Only 1 enemy at same tile
    e1 = _slug(pos=(0, 1))
    w.add_unit(e1)

    for _ in range(3):
        w.tick()

    talent_buffs = [b for b in d.buffs if b.source_tag == _TALENT_BUFF_TAG]
    blocked = sum(1 for e in [e1] if d.unit_id in e.blocked_by_unit_ids)

    if blocked < _TALENT_THRESHOLD:
        assert len(talent_buffs) == 0, (
            f"Thunder Strike must NOT fire with {blocked} blocked enemies; "
            f"buffs={[b.source_tag for b in d.buffs]}"
        )


# ---------------------------------------------------------------------------
# Test 5: Talent — ATK+20% when 2+ blocked
# ---------------------------------------------------------------------------

def test_talent_atk_buff_two_blocked():
    """Thunder Strike: ATK+20% when 2+ enemies are blocked."""
    w = _world()
    d = make_durnar()
    d.deployed = True; d.position = (0.0, 1.0)
    base_atk = d.effective_atk
    w.add_unit(d)

    e1 = _slug(pos=(0, 1))
    e2 = _slug(pos=(0, 1))
    w.add_unit(e1); w.add_unit(e2)

    for _ in range(3):
        w.tick()

    talent_buffs = [b for b in d.buffs if b.source_tag == _TALENT_BUFF_TAG]
    blocked = sum(1 for e in [e1, e2] if d.unit_id in e.blocked_by_unit_ids)

    assert blocked >= _TALENT_THRESHOLD, (
        f"Must have {_TALENT_THRESHOLD}+ blocked enemies; got {blocked}"
    )
    assert len(talent_buffs) == 1, (
        f"Thunder Strike buff must be active; buffs={[b.source_tag for b in d.buffs]}"
    )
    expected_atk = int(base_atk * (1 + _TALENT_ATK_RATIO))
    assert abs(d.effective_atk - expected_atk) <= 2, (
        f"ATK must be base×{1+_TALENT_ATK_RATIO}; base={base_atk}, "
        f"expected={expected_atk}, got={d.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 6: Talent buff removed when blocked count drops below threshold
# ---------------------------------------------------------------------------

def test_talent_buff_removed_below_threshold():
    """Thunder Strike buff is removed when fewer than 2 enemies are blocked."""
    w = _world()
    d = make_durnar()
    d.deployed = True; d.position = (0.0, 1.0)
    w.add_unit(d)

    e1 = _slug(pos=(0, 1))
    e2 = _slug(pos=(0, 1))
    w.add_unit(e1); w.add_unit(e2)

    for _ in range(3):
        w.tick()

    assert any(b.source_tag == _TALENT_BUFF_TAG for b in d.buffs), (
        "Thunder Strike buff must be active before removal test"
    )

    # Kill both enemies so blocking count drops to 0
    e1.alive = False
    e2.alive = False

    for _ in range(3):
        w.tick()

    assert not any(b.source_tag == _TALENT_BUFF_TAG for b in d.buffs), (
        "Thunder Strike buff must be removed when enemies leave"
    )


# ---------------------------------------------------------------------------
# Test 7: S2 applies DEF+50% ratio buff
# ---------------------------------------------------------------------------

def test_s2_applies_def_buff():
    """During S2, effective_def must increase by 50%."""
    w = _world()
    d = make_durnar()
    d.deployed = True; d.position = (0.0, 1.0)
    w.add_unit(d)

    e = _slug(pos=(0, 1))
    w.add_unit(e)

    base_def = d.effective_def

    d.skill.sp = float(d.skill.sp_cost)
    w.tick()

    assert d.skill.active_remaining > 0.0, "S2 must be active"

    expected_def = int(base_def * (1 + _S2_DEF_RATIO))
    assert abs(d.effective_def - expected_def) <= 2, (
        f"DEF during S2 must be base×{1+_S2_DEF_RATIO}; "
        f"base={base_def}, expected={expected_def}, got={d.effective_def}"
    )


# ---------------------------------------------------------------------------
# Test 8: S2 increases block to 4, reverts to 3 after skill ends
# ---------------------------------------------------------------------------

def test_s2_block_increases_and_reverts():
    """S2 must raise block from 3 to 4, returning to 3 when skill ends."""
    w = _world()
    d = make_durnar()
    d.deployed = True; d.position = (0.0, 1.0)
    w.add_unit(d)

    e = _slug(pos=(0, 1))
    w.add_unit(e)

    assert d.block == _S2_BASE_BLOCK, f"Must start at block={_S2_BASE_BLOCK}"

    d.skill.sp = float(d.skill.sp_cost)
    w.tick()

    assert d.skill.active_remaining > 0.0, "S2 must be active"
    assert d.block == _S2_BASE_BLOCK + _S2_BLOCK_BONUS, (
        f"Block must be {_S2_BASE_BLOCK + _S2_BLOCK_BONUS} during S2; got {d.block}"
    )

    # Wait for S2 to end
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert d.skill.active_remaining == 0.0, "S2 must have ended"
    assert d.block == _S2_BASE_BLOCK, (
        f"Block must return to {_S2_BASE_BLOCK} after S2; got {d.block}"
    )
    assert not any(b.source_tag == _S2_DEF_BUFF_TAG for b in d.buffs), (
        "S2 DEF buff must be removed after skill ends"
    )
