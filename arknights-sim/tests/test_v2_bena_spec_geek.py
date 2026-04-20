"""Bena — SPEC_GEEK: Bloodlust ATK bonus when HP < 50% + S2 Overdrive HP drain.

SPEC_GEEK: High-risk high-reward Specialist. Trades HP for damage.

Talent "Bloodlust": When HP < 50% of max, ATK +35%.

S2 "Overdrive": ATK +80% for 15s, but loses 3% max HP per second.
  HP can never drop below 1 from the drain.

Tests cover:
  - Archetype SPEC_GEEK
  - Talent: no ATK bonus when HP ≥ 50%
  - Talent: ATK +35% when HP < 50%
  - Talent ATK bonus removed when HP recovers above 50%
  - S2 applies ATK +80%
  - S2 drains HP every tick (HP decreases over time)
  - S2 HP drain never reduces HP below 1
  - S2 ATK buff removed on end
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, DT, RoleArchetype
from core.systems import register_default_systems
from data.characters.bena import (
    make_bena,
    _TALENT_TAG, _TALENT_ATK_BONUS, _TALENT_ATK_TAG, _HP_LOW_THRESHOLD,
    _S2_ATK_RATIO, _S2_HP_DRAIN_RATIO, _S2_DURATION, _S2_ATK_BUFF_TAG,
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


def _slug(pos=(1, 1), hp=99999) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = 0; e.move_speed = 0.0; e.res = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Archetype SPEC_GEEK
# ---------------------------------------------------------------------------

def test_bena_archetype():
    b = make_bena()
    assert b.archetype == RoleArchetype.SPEC_GEEK
    assert b.block == 2
    assert len(b.talents) == 1
    assert b.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: Talent: no ATK bonus when HP ≥ 50%
# ---------------------------------------------------------------------------

def test_talent_no_bonus_at_full_hp():
    """No Bloodlust bonus when HP is at or above 50% threshold."""
    w = _world()
    b = make_bena()
    b.deployed = True; b.position = (0.0, 1.0)
    b.hp = b.max_hp  # full HP
    w.add_unit(b)

    base_atk = b.effective_atk
    w.tick()

    bloodlust_buffs = [buf for buf in b.buffs if buf.source_tag == _TALENT_ATK_TAG]
    assert len(bloodlust_buffs) == 0, "Bloodlust must NOT be active at full HP"
    assert b.effective_atk == base_atk


# ---------------------------------------------------------------------------
# Test 3: Talent: ATK +35% when HP < 50%
# ---------------------------------------------------------------------------

def test_talent_atk_bonus_at_low_hp():
    """Bloodlust must activate and add +35% ATK when HP drops below 50%."""
    w = _world()
    b = make_bena()
    b.deployed = True; b.position = (0.0, 1.0)
    b.hp = int(b.max_hp * 0.3)   # HP = 30%, below threshold
    w.add_unit(b)

    base_atk_no_buff = b.atk  # raw base (before any buffs)
    w.tick()

    bloodlust_buffs = [buf for buf in b.buffs if buf.source_tag == _TALENT_ATK_TAG]
    assert len(bloodlust_buffs) == 1, "Bloodlust must be active when HP < 50%"
    assert abs(bloodlust_buffs[0].value - _TALENT_ATK_BONUS) < 0.01
    expected_atk = int(base_atk_no_buff * (1 + _TALENT_ATK_BONUS))
    assert abs(b.effective_atk - expected_atk) <= 2


# ---------------------------------------------------------------------------
# Test 4: Talent bonus removed when HP recovers above 50%
# ---------------------------------------------------------------------------

def test_talent_bonus_removed_when_hp_recovers():
    """Bloodlust buff must be removed when HP recovers above threshold."""
    w = _world()
    b = make_bena()
    b.deployed = True; b.position = (0.0, 1.0)
    b.hp = int(b.max_hp * 0.3)   # Start below threshold
    w.add_unit(b)

    w.tick()  # Bloodlust activates
    assert any(buf.source_tag == _TALENT_ATK_TAG for buf in b.buffs)

    # Heal to above threshold
    b.hp = b.max_hp
    w.tick()  # Bloodlust must deactivate

    bloodlust_buffs = [buf for buf in b.buffs if buf.source_tag == _TALENT_ATK_TAG]
    assert len(bloodlust_buffs) == 0, "Bloodlust must be removed when HP recovers"


# ---------------------------------------------------------------------------
# Test 5: S2 applies ATK +80%
# ---------------------------------------------------------------------------

def test_s2_atk_buff():
    """Overdrive must increase ATK by _S2_ATK_RATIO."""
    w = _world()
    b = make_bena()
    b.deployed = True; b.position = (0.0, 1.0)
    w.add_unit(b)

    enemy = _slug(pos=(1, 1))
    w.add_unit(enemy)

    base_atk = b.effective_atk
    b.skill.sp = float(b.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, b)

    assert b.skill.active_remaining > 0.0, "S2 must be active"
    expected_atk = int(base_atk * (1 + _S2_ATK_RATIO))
    assert abs(b.effective_atk - expected_atk) <= 2, (
        f"S2 ATK must be ×{1+_S2_ATK_RATIO}; expected={expected_atk}, got={b.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 6: S2 drains HP over time
# ---------------------------------------------------------------------------

def test_s2_drains_hp():
    """During S2, Bena must lose HP each tick from the drain."""
    w = _world()
    b = make_bena()
    b.deployed = True; b.position = (0.0, 1.0)
    w.add_unit(b)

    enemy = _slug(pos=(1, 1))
    w.add_unit(enemy)

    initial_hp = b.hp
    b.skill.sp = float(b.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, b)

    # Tick a few times to let drain accumulate
    ticks = 10
    for _ in range(ticks):
        w.tick()

    assert b.hp < initial_hp, (
        f"S2 drain must reduce Bena's HP; was {initial_hp}, now {b.hp}"
    )
    # Per-tick drain uses int() truncation: actual = ticks × int(max_hp × ratio × DT)
    expected_drain = ticks * int(b.max_hp * _S2_HP_DRAIN_RATIO * DT)
    assert (initial_hp - b.hp) >= expected_drain, (
        f"Must have drained at least {expected_drain} HP; actual drain={initial_hp - b.hp}"
    )


# ---------------------------------------------------------------------------
# Test 7: S2 HP drain never reduces HP below 1
# ---------------------------------------------------------------------------

def test_s2_hp_drain_floor_is_one():
    """HP drain must never reduce Bena's HP to 0 or below — floor is 1."""
    w = _world()
    b = make_bena()
    b.deployed = True; b.position = (0.0, 1.0)
    b.hp = 5  # Almost dead — drain should floor to 1
    w.add_unit(b)

    enemy = _slug(pos=(1, 1))
    w.add_unit(enemy)

    b.skill.sp = float(b.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, b)

    for _ in range(int(TICK_RATE * 5)):
        w.tick()

    assert b.hp >= 1, f"HP drain must not kill Bena; hp={b.hp}"
    assert b.alive, "Bena must survive HP drain (floor at 1)"


# ---------------------------------------------------------------------------
# Test 8: S2 ATK buff removed on end
# ---------------------------------------------------------------------------

def test_s2_buff_removed_on_end():
    """After S2 ends, ATK must return to base."""
    w = _world()
    b = make_bena()
    b.deployed = True; b.position = (0.0, 1.0)
    w.add_unit(b)

    enemy = _slug(pos=(1, 1))
    w.add_unit(enemy)

    base_atk = b.effective_atk
    b.skill.sp = float(b.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, b)

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert b.skill.active_remaining == 0.0, "S2 must have ended"
    s2_buffs = [buf for buf in b.buffs if buf.source_tag == _S2_ATK_BUFF_TAG]
    assert len(s2_buffs) == 0, "S2 ATK buff must be cleared"
