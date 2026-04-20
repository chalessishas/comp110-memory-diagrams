"""Liskarm S3 "Energies Converging" — ATK+100%, DEF+60%, 30s MANUAL.
During S3 Lightning Discharge gives SP to ALL nearby allies (not random one).

Tests cover:
  - S3 config (slot, sp_cost, MANUAL)
  - ATK +100% buff applied on start
  - DEF +60% buff applied on start
  - During S3: on hit → ALL nearby allies receive +1 SP
  - Outside S3: on hit → only random one ally receives SP (regression)
  - Buffs cleared on end
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, Faction
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from core.systems.talent_registry import fire_on_hit_received
from core.state.unit_state import UnitState
from data.characters.liskarm import (
    make_liskarm,
    _S3_TAG, _S3_ATK_RATIO, _S3_DEF_RATIO, _S3_DURATION,
    _S3_ATK_BUFF_TAG, _S3_DEF_BUFF_TAG,
)


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ticks(w, seconds):
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def _dummy_attacker():
    a = UnitState(name="Attacker", faction=Faction.ENEMY, max_hp=9999, atk=100, defence=0, res=0.0)
    a.alive = True; a.deployed = True; a.position = (1.0, 1.0)
    return a


def _dummy_ally(name, pos, sp=0.0, sp_cost=30):
    from core.state.unit_state import SkillComponent
    from core.types import SPGainMode, SkillTrigger
    a = UnitState(name=name, faction=Faction.ALLY, max_hp=1000, atk=100, defence=0, res=0.0)
    a.alive = True; a.deployed = True; a.position = pos
    a.skill = SkillComponent(
        name="Dummy", slot="S1", sp_cost=sp_cost, initial_sp=0,
        duration=10.0, sp_gain_mode=SPGainMode.AUTO_TIME,
        trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag="dummy",
    )
    a.skill.sp = sp
    return a


_LISK_POS = (0.0, 1.0)


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    l = make_liskarm(slot="S3")
    assert l.skill is not None and l.skill.slot == "S3"
    assert l.skill.name == "Energies Converging"
    assert l.skill.sp_cost == 50
    from core.types import SkillTrigger
    assert l.skill.trigger == SkillTrigger.MANUAL
    assert l.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK +100% applied
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    l = make_liskarm(slot="S3")
    l.deployed = True; l.position = _LISK_POS; l.atk_cd = 999.0
    w.add_unit(l)

    base_atk = l.effective_atk
    l.skill.sp = float(l.skill.sp_cost)
    manual_trigger(w, l)

    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(l.effective_atk - expected) <= 2, (
        f"S3 ATK must be ×{1 + _S3_ATK_RATIO}; expected {expected}, got {l.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: DEF +60% applied
# ---------------------------------------------------------------------------

def test_s3_def_buff():
    w = _world()
    l = make_liskarm(slot="S3")
    l.deployed = True; l.position = _LISK_POS; l.atk_cd = 999.0
    w.add_unit(l)

    base_def = l.effective_def
    l.skill.sp = float(l.skill.sp_cost)
    manual_trigger(w, l)

    expected = int(base_def * (1 + _S3_DEF_RATIO))
    assert abs(l.effective_def - expected) <= 2, (
        f"S3 DEF must be ×{1 + _S3_DEF_RATIO}; expected {expected}, got {l.effective_def}"
    )


# ---------------------------------------------------------------------------
# Test 4: During S3, all nearby allies receive +1 SP on hit
# ---------------------------------------------------------------------------

def test_s3_all_allies_get_sp_on_hit():
    w = _world()
    l = make_liskarm(slot="S3")
    l.deployed = True; l.position = _LISK_POS; l.atk_cd = 999.0
    w.add_unit(l)

    ally1 = _dummy_ally("Ally1", (0.0, 0.0), sp=0.0)
    ally2 = _dummy_ally("Ally2", (1.0, 1.0), sp=0.0)
    w.add_unit(ally1)
    w.add_unit(ally2)

    attacker = _dummy_attacker()
    w.add_unit(attacker)

    l.skill.sp = float(l.skill.sp_cost)
    manual_trigger(w, l)
    assert l.skill.active_remaining > 0

    fire_on_hit_received(w, l, attacker, 10)

    assert ally1.skill.sp > 0, "Ally1 must receive +1 SP during S3"
    assert ally2.skill.sp > 0, "Ally2 must receive +1 SP during S3"


# ---------------------------------------------------------------------------
# Test 5: Outside S3 (regression), only one random ally gets SP
# ---------------------------------------------------------------------------

def test_outside_s3_random_ally_sp():
    w = _world()
    l = make_liskarm(slot="S3")
    l.deployed = True; l.position = _LISK_POS; l.atk_cd = 999.0
    w.add_unit(l)

    ally1 = _dummy_ally("Ally1", (0.0, 0.0), sp=0.0)
    ally2 = _dummy_ally("Ally2", (1.0, 1.0), sp=0.0)
    w.add_unit(ally1)
    w.add_unit(ally2)

    attacker = _dummy_attacker()
    w.add_unit(attacker)

    # S3 NOT active
    fire_on_hit_received(w, l, attacker, 10)

    total_sp = ally1.skill.sp + ally2.skill.sp
    assert total_sp == 1.0, (
        f"Outside S3 only one ally should receive SP; got ally1={ally1.skill.sp}, ally2={ally2.skill.sp}"
    )


# ---------------------------------------------------------------------------
# Test 6: Buffs cleared on end
# ---------------------------------------------------------------------------

def test_s3_buffs_cleared_on_end():
    w = _world()
    l = make_liskarm(slot="S3")
    l.deployed = True; l.position = _LISK_POS; l.atk_cd = 999.0
    w.add_unit(l)

    base_atk = l.effective_atk
    base_def = l.effective_def
    l.skill.sp = float(l.skill.sp_cost)
    manual_trigger(w, l)
    _ticks(w, _S3_DURATION + 1)

    assert l.skill.active_remaining == 0.0
    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in l.buffs), "ATK buff must clear"
    assert not any(b.source_tag == _S3_DEF_BUFF_TAG for b in l.buffs), "DEF buff must clear"
    assert abs(l.effective_atk - base_atk) <= 2
    assert abs(l.effective_def - base_def) <= 2


# ---------------------------------------------------------------------------
# Test 7: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    l = make_liskarm(slot="S2")
    assert l.skill is not None and l.skill.slot == "S2"
    assert l.skill.name == "Voltaic Shield"
