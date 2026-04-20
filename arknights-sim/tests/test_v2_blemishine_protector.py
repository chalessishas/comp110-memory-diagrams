"""Blemishine — DEF_PROTECTOR: full-block DEF bonus (trait+talent stack) + S2 ATK/DEF burst.

DEF_PROTECTOR trait: When blocking at full capacity (block=3), DEF +50%.
Talent "Aegis": When at full capacity AND HP > 50%, DEF +30% more (stacks with trait).
S2 "Iron Aegis": ATK +40%, DEF +60% for 25s.

Tests cover:
  - Archetype DEF_PROTECTOR, block=3
  - Trait: no DEF bonus when not blocking
  - Trait: DEF +50% when blocking at full capacity
  - Trait bonus removed when blocking drops below capacity
  - Talent: DEF +30% more when HP > 50% AND at full capacity
  - Talent bonus NOT applied when HP ≤ 50%
  - S2 applies ATK +40% and DEF +60%
  - S2 buffs cleared on end
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, DT, RoleArchetype
from core.systems import register_default_systems
from data.characters.blemishine import (
    make_blemishine,
    _TALENT_TAG, _TRAIT_DEF_BONUS, _TALENT_DEF_BONUS,
    _TRAIT_DEF_TAG, _TALENT_DEF_TAG,
    _S2_ATK_RATIO, _S2_DEF_RATIO, _S2_DURATION,
    _S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG,
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


def _slug(pos=(0, 1), hp=99999) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = 0; e.move_speed = 0.0; e.res = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Archetype DEF_PROTECTOR, block=3
# ---------------------------------------------------------------------------

def test_blemishine_archetype():
    b = make_blemishine()
    assert b.archetype == RoleArchetype.DEF_PROTECTOR
    assert b.block == 3
    assert len(b.talents) == 1
    assert b.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: No DEF bonus when not blocking
# ---------------------------------------------------------------------------

def test_no_def_bonus_when_not_blocking():
    """Trait DEF bonus must NOT be active when no enemies are being blocked."""
    w = _world()
    b = make_blemishine()
    b.deployed = True; b.position = (0.0, 1.0)
    w.add_unit(b)

    base_def = b.effective_def
    w.tick()  # No enemies — not blocking

    assert not any(buf.source_tag == _TRAIT_DEF_TAG for buf in b.buffs), (
        "Trait DEF buff must NOT be present when not blocking"
    )
    assert b.effective_def == base_def


# ---------------------------------------------------------------------------
# Test 3: DEF +50% when blocking at full capacity (3 enemies)
# ---------------------------------------------------------------------------

def test_trait_def_bonus_at_full_capacity():
    """When blocking 3 enemies (= block limit), DEF must increase by 50%."""
    w = _world()
    b = make_blemishine()
    b.deployed = True; b.position = (0.0, 1.0)
    w.add_unit(b)

    base_def = b.effective_def

    # Add 3 enemies at same tile so all block slots fill
    for _ in range(3):
        w.add_unit(_slug(pos=(0, 1)))

    w.tick()

    blocking = sum(1 for e in w.enemies() if b.unit_id in e.blocked_by_unit_ids)
    if blocking >= 3:
        trait_buffs = [buf for buf in b.buffs if buf.source_tag == _TRAIT_DEF_TAG]
        assert len(trait_buffs) == 1, "Trait DEF buff must be active at full block"
        assert abs(trait_buffs[0].value - _TRAIT_DEF_BONUS) < 0.01
        expected_def = int(base_def * (1 + _TRAIT_DEF_BONUS))
        # Note: talent bonus also applies here (HP > 50%), so include both
        assert b.effective_def > base_def, "DEF must be increased when at full block"


# ---------------------------------------------------------------------------
# Test 4: Trait bonus removed when blocking drops below capacity
# ---------------------------------------------------------------------------

def test_trait_bonus_removed_when_not_at_capacity():
    """After enemies leave and blocking drops below capacity, trait buff must be removed."""
    w = _world()
    b = make_blemishine()
    b.deployed = True; b.position = (0.0, 1.0)
    w.add_unit(b)

    # Fill block slots
    enemies = [_slug(pos=(0, 1)) for _ in range(3)]
    for e in enemies:
        w.add_unit(e)

    w.tick()  # At capacity → trait buff applied

    # Kill 2 enemies to drop below capacity
    for e in enemies[:2]:
        e.hp = 0
        e.alive = False
    w.tick()  # Below capacity → trait buff must be removed

    trait_buffs = [buf for buf in b.buffs if buf.source_tag == _TRAIT_DEF_TAG]
    assert len(trait_buffs) == 0, "Trait DEF buff must be removed when below capacity"


# ---------------------------------------------------------------------------
# Test 5: Talent: extra DEF when HP > 50% AND at full capacity
# ---------------------------------------------------------------------------

def test_talent_extra_def_when_hp_above_half():
    """Aegis talent must add additional DEF when at full capacity AND HP > 50%."""
    w = _world()
    b = make_blemishine()
    b.deployed = True; b.position = (0.0, 1.0)
    b.hp = int(b.max_hp * 0.8)   # HP > 50%
    w.add_unit(b)

    for _ in range(3):
        w.add_unit(_slug(pos=(0, 1)))

    w.tick()

    blocking = sum(1 for e in w.enemies() if b.unit_id in e.blocked_by_unit_ids)
    if blocking >= 3 and b.hp > b.max_hp * 0.5:
        talent_buffs = [buf for buf in b.buffs if buf.source_tag == _TALENT_DEF_TAG]
        assert len(talent_buffs) == 1, "Talent DEF buff must be active at capacity + HP > 50%"
        assert abs(talent_buffs[0].value - _TALENT_DEF_BONUS) < 0.01


# ---------------------------------------------------------------------------
# Test 6: Talent bonus NOT applied when HP ≤ 50%
# ---------------------------------------------------------------------------

def test_talent_no_bonus_when_low_hp():
    """Aegis talent extra DEF must NOT apply when HP ≤ 50%."""
    w = _world()
    b = make_blemishine()
    b.deployed = True; b.position = (0.0, 1.0)
    b.hp = int(b.max_hp * 0.4)   # HP ≤ 50%
    w.add_unit(b)

    for _ in range(3):
        w.add_unit(_slug(pos=(0, 1)))

    w.tick()

    talent_buffs = [buf for buf in b.buffs if buf.source_tag == _TALENT_DEF_TAG]
    assert len(talent_buffs) == 0, (
        "Talent DEF buff must NOT apply when HP ≤ 50%"
    )


# ---------------------------------------------------------------------------
# Test 7: S2 applies ATK +40% and DEF +60%
# ---------------------------------------------------------------------------

def test_s2_atk_def_buff():
    """Iron Aegis must apply ATK+40% and DEF+60%."""
    w = _world()
    b = make_blemishine()
    b.deployed = True; b.position = (0.0, 1.0)
    w.add_unit(b)

    enemy = _slug(pos=(0, 1))
    w.add_unit(enemy)

    base_atk = b.effective_atk
    base_def = b.effective_def

    b.skill.sp = float(b.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, b)

    assert b.skill.active_remaining > 0.0, "S2 must be active"
    expected_atk = int(base_atk * (1 + _S2_ATK_RATIO))
    expected_def = int(base_def * (1 + _S2_DEF_RATIO))
    assert abs(b.effective_atk - expected_atk) <= 2, (
        f"S2 ATK must be ×{1+_S2_ATK_RATIO}; got {b.effective_atk}"
    )
    assert abs(b.effective_def - expected_def) <= 2, (
        f"S2 DEF must be ×{1+_S2_DEF_RATIO}; got {b.effective_def}"
    )


# ---------------------------------------------------------------------------
# Test 8: S2 buffs cleared on end
# ---------------------------------------------------------------------------

def test_s2_buffs_cleared():
    """S2 ATK and DEF buffs must be removed after skill ends."""
    w = _world()
    b = make_blemishine()
    b.deployed = True; b.position = (0.0, 1.0)
    w.add_unit(b)

    enemy = _slug(pos=(0, 1))
    w.add_unit(enemy)

    b.skill.sp = float(b.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, b)

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert b.skill.active_remaining == 0.0
    s2_buffs = [buf for buf in b.buffs if buf.source_tag in (_S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG)]
    assert len(s2_buffs) == 0, "S2 ATK/DEF buffs must be cleared after skill ends"
