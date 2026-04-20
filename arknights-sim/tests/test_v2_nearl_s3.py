"""Nearl S3 "The Champion's Path" — self ATK+150%/DEF+55% + dual-axis aura to in-range allies.

Tests cover:
  - S3 config (slot, sp_cost, MANUAL trigger)
  - Self ATK +150% applied on start
  - Self DEF +55% applied on start
  - Self buffs cleared on skill end
  - In-range ally gains ATK +20% aura
  - In-range ally gains DEF +20% aura
  - Out-of-range ally gets no aura
  - Aura cleared on skill end
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from core.state.unit_state import UnitState
from core.types import Faction, AttackType, Profession, RoleArchetype
from data.characters.nearl import (
    make_nearl,
    _S3_TAG, _S3_DURATION,
    _S3_SELF_ATK_RATIO, _S3_SELF_DEF_RATIO,
    _S3_ALLY_ATK_RATIO, _S3_ALLY_DEF_RATIO,
    _S3_SELF_ATK_TAG, _S3_SELF_DEF_TAG,
    _S3_ALLY_ATK_TAG, _S3_ALLY_DEF_TAG,
    DEFENDER_RANGE,
)


def _world() -> World:
    grid = TileGrid(width=6, height=5)
    for x in range(6):
        for y in range(5):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ally(world: World, x: float, y: float, name: str = "Ally") -> UnitState:
    a = UnitState(name=name, faction=Faction.ALLY, max_hp=5000, hp=5000,
                  atk=500, defence=300, res=0.0, atk_interval=1.0)
    a.alive = True; a.deployed = True; a.position = (x, y)
    a.attack_type = AttackType.PHYSICAL
    world.add_unit(a)
    return a


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


_NEARL_POS = (0.0, 2.0)
# DEFENDER_RANGE: (0,0) and (1,0) — tile 1 forward
_ALLY_IN_RANGE = (1.0, 2.0)    # dx=1, in range
_ALLY_OUT_RANGE = (3.0, 2.0)   # dx=3, outside


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    n = make_nearl(slot="S3")
    assert n.skill is not None
    assert n.skill.slot == "S3"
    assert n.skill.name == "The Champion's Path"
    assert n.skill.sp_cost == 55
    from core.types import SkillTrigger
    assert n.skill.trigger == SkillTrigger.MANUAL
    assert n.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: Self ATK +150%
# ---------------------------------------------------------------------------

def test_s3_self_atk_buff():
    w = _world()
    n = make_nearl(slot="S3")
    n.deployed = True; n.position = _NEARL_POS; n.atk_cd = 999.0
    w.add_unit(n)

    base_atk = n.effective_atk
    n.skill.sp = float(n.skill.sp_cost)
    manual_trigger(w, n)

    assert n.skill.active_remaining > 0.0
    expected = int(base_atk * (1 + _S3_SELF_ATK_RATIO))
    assert abs(n.effective_atk - expected) <= 2, (
        f"Self ATK must be ×{1 + _S3_SELF_ATK_RATIO}; expected {expected}, got {n.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: Self DEF +55%
# ---------------------------------------------------------------------------

def test_s3_self_def_buff():
    w = _world()
    n = make_nearl(slot="S3")
    n.deployed = True; n.position = _NEARL_POS; n.atk_cd = 999.0
    w.add_unit(n)

    base_def = n.effective_def
    n.skill.sp = float(n.skill.sp_cost)
    manual_trigger(w, n)

    assert n.skill.active_remaining > 0.0
    expected = int(base_def * (1 + _S3_SELF_DEF_RATIO))
    assert abs(n.effective_def - expected) <= 2, (
        f"Self DEF must be ×{1 + _S3_SELF_DEF_RATIO}; expected {expected}, got {n.effective_def}"
    )


# ---------------------------------------------------------------------------
# Test 4: Self buffs cleared on skill end
# ---------------------------------------------------------------------------

def test_s3_self_buffs_cleared_on_end():
    w = _world()
    n = make_nearl(slot="S3")
    n.deployed = True; n.position = _NEARL_POS; n.atk_cd = 999.0
    w.add_unit(n)

    base_atk = n.effective_atk
    base_def = n.effective_def

    n.skill.sp = float(n.skill.sp_cost)
    manual_trigger(w, n)
    _ticks(w, _S3_DURATION + 1)

    assert n.skill.active_remaining == 0.0
    assert not any(b.source_tag == _S3_SELF_ATK_TAG for b in n.buffs)
    assert not any(b.source_tag == _S3_SELF_DEF_TAG for b in n.buffs)
    assert abs(n.effective_atk - base_atk) <= 2
    assert abs(n.effective_def - base_def) <= 2


# ---------------------------------------------------------------------------
# Test 5: In-range ally gains ATK +20% aura
# ---------------------------------------------------------------------------

def test_s3_ally_atk_aura_in_range():
    w = _world()
    n = make_nearl(slot="S3")
    n.deployed = True; n.position = _NEARL_POS; n.atk_cd = 999.0
    w.add_unit(n)

    ally = _ally(w, *_ALLY_IN_RANGE)
    base_atk = ally.effective_atk

    n.skill.sp = float(n.skill.sp_cost)
    manual_trigger(w, n)
    w.tick()   # one tick so TTL-stamp takes effect

    expected = int(base_atk * (1 + _S3_ALLY_ATK_RATIO))
    assert abs(ally.effective_atk - expected) <= 2, (
        f"In-range ally ATK must be ×{1 + _S3_ALLY_ATK_RATIO}; expected {expected}, got {ally.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 6: In-range ally gains DEF +20% aura
# ---------------------------------------------------------------------------

def test_s3_ally_def_aura_in_range():
    w = _world()
    n = make_nearl(slot="S3")
    n.deployed = True; n.position = _NEARL_POS; n.atk_cd = 999.0
    w.add_unit(n)

    ally = _ally(w, *_ALLY_IN_RANGE)
    base_def = ally.effective_def

    n.skill.sp = float(n.skill.sp_cost)
    manual_trigger(w, n)
    w.tick()

    expected = int(base_def * (1 + _S3_ALLY_DEF_RATIO))
    assert abs(ally.effective_def - expected) <= 2, (
        f"In-range ally DEF must be ×{1 + _S3_ALLY_DEF_RATIO}; expected {expected}, got {ally.effective_def}"
    )


# ---------------------------------------------------------------------------
# Test 7: Out-of-range ally gets no aura
# ---------------------------------------------------------------------------

def test_s3_no_aura_out_of_range():
    w = _world()
    n = make_nearl(slot="S3")
    n.deployed = True; n.position = _NEARL_POS; n.atk_cd = 999.0
    w.add_unit(n)

    ally = _ally(w, *_ALLY_OUT_RANGE)
    base_atk = ally.effective_atk
    base_def = ally.effective_def

    n.skill.sp = float(n.skill.sp_cost)
    manual_trigger(w, n)
    w.tick()

    assert not any(b.source_tag == _S3_ALLY_ATK_TAG for b in ally.buffs), "Out-of-range ally must not get ATK aura"
    assert not any(b.source_tag == _S3_ALLY_DEF_TAG for b in ally.buffs), "Out-of-range ally must not get DEF aura"
    assert abs(ally.effective_atk - base_atk) <= 1
    assert abs(ally.effective_def - base_def) <= 1


# ---------------------------------------------------------------------------
# Test 8: Aura cleared on skill end
# ---------------------------------------------------------------------------

def test_s3_aura_cleared_on_end():
    w = _world()
    n = make_nearl(slot="S3")
    n.deployed = True; n.position = _NEARL_POS; n.atk_cd = 999.0
    w.add_unit(n)

    ally = _ally(w, *_ALLY_IN_RANGE)
    base_atk = ally.effective_atk
    base_def = ally.effective_def

    n.skill.sp = float(n.skill.sp_cost)
    manual_trigger(w, n)
    _ticks(w, _S3_DURATION + 1)

    assert n.skill.active_remaining == 0.0
    assert not any(b.source_tag == _S3_ALLY_ATK_TAG for b in ally.buffs), "ATK aura must clear on S3 end"
    assert not any(b.source_tag == _S3_ALLY_DEF_TAG for b in ally.buffs), "DEF aura must clear on S3 end"
    assert abs(ally.effective_atk - base_atk) <= 2
    assert abs(ally.effective_def - base_def) <= 2


# ---------------------------------------------------------------------------
# Test 9: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    n = make_nearl(slot="S2")
    assert n.skill is not None and n.skill.slot == "S2"
    assert n.skill.name == "Justice"
