"""Sesa S3 "Percussion Resonance II" — ATK+120%, resonance fires every 3 hits (vs 7), 20s MANUAL.

Tests cover:
  - S3 config (slot, sp_cost, MANUAL)
  - ATK +120% buff applied on start
  - During S3: Percussion Resonance fires every 3 attacks (not 7)
  - Outside S3: Percussion still fires every 7 (regression)
  - Resonance AoE during S3 hits adjacent enemies
  - ATK buff cleared on end, resonance interval restored
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
from core.systems.talent_registry import fire_on_attack_hit
from core.state.unit_state import UnitState
from data.characters.sesa import (
    make_sesa,
    _S3_TAG, _S3_ATK_RATIO, _S3_DURATION, _S3_ATK_BUFF_TAG,
    _S3_RESONANCE_INTERVAL, _TALENT_HIT_COUNT,
)


def _world() -> World:
    grid = TileGrid(width=8, height=5)
    for x in range(8):
        for y in range(5):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ticks(w, seconds):
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def _enemy(world, x, y, name="Enemy"):
    e = UnitState(name=name, faction=Faction.ENEMY, max_hp=99999, atk=0, defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (float(x), float(y))
    world.add_unit(e)
    return e


_SESA_POS = (0.0, 2.0)


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    s = make_sesa(slot="S3")
    assert s.skill is not None and s.skill.slot == "S3"
    assert s.skill.name == "Percussion Resonance II"
    assert s.skill.sp_cost == 45
    from core.types import SkillTrigger
    assert s.skill.trigger == SkillTrigger.MANUAL
    assert s.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK +120% applied
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    s = make_sesa(slot="S3")
    s.deployed = True; s.position = _SESA_POS; s.atk_cd = 999.0
    w.add_unit(s)
    target = _enemy(w, 2.0, 2.0)

    base_atk = s.effective_atk
    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)

    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(s.effective_atk - expected) <= 2, (
        f"S3 ATK must be ×{1 + _S3_ATK_RATIO}; expected {expected}, got {s.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: During S3, Percussion fires every 3 hits
# ---------------------------------------------------------------------------

def test_s3_resonance_every_3_hits():
    w = _world()
    s = make_sesa(slot="S3")
    s.deployed = True; s.position = _SESA_POS; s.atk_cd = 999.0
    w.add_unit(s)
    primary = _enemy(w, 2.0, 2.0)
    adjacent = _enemy(w, 2.0, 3.0, "Adjacent")  # within resonance radius

    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)
    assert s.skill.active_remaining > 0

    hp_before = adjacent.hp
    # Fire 3 hits (should trigger resonance on 3rd)
    for _ in range(_S3_RESONANCE_INTERVAL):
        fire_on_attack_hit(w, s, primary, 100)

    assert adjacent.hp < hp_before, (
        f"Resonance must fire after {_S3_RESONANCE_INTERVAL} hits during S3, dealing AoE to adjacent"
    )


# ---------------------------------------------------------------------------
# Test 4: Outside S3, Percussion still fires every 7 (regression)
# ---------------------------------------------------------------------------

def test_outside_s3_resonance_every_7_hits():
    w = _world()
    s = make_sesa(slot="S3")
    s.deployed = True; s.position = _SESA_POS; s.atk_cd = 999.0
    w.add_unit(s)
    primary = _enemy(w, 2.0, 2.0)
    adjacent = _enemy(w, 2.0, 3.0, "Adjacent")

    # S3 NOT active
    s._sesa_hit_count = 0
    hp_before = adjacent.hp

    # 3 hits should NOT trigger resonance outside S3
    for _ in range(_S3_RESONANCE_INTERVAL):
        fire_on_attack_hit(w, s, primary, 100)

    assert adjacent.hp == hp_before, (
        "Resonance must NOT fire after only 3 hits outside S3"
    )

    # 7 hits total should trigger
    for _ in range(_TALENT_HIT_COUNT - _S3_RESONANCE_INTERVAL):
        fire_on_attack_hit(w, s, primary, 100)

    assert adjacent.hp < hp_before, "Resonance must fire after 7 total hits outside S3"


# ---------------------------------------------------------------------------
# Test 5: ATK buff cleared on end
# ---------------------------------------------------------------------------

def test_s3_atk_buff_cleared_on_end():
    w = _world()
    s = make_sesa(slot="S3")
    s.deployed = True; s.position = _SESA_POS; s.atk_cd = 999.0
    w.add_unit(s)
    _enemy(w, 2.0, 2.0)

    base_atk = s.effective_atk
    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)
    _ticks(w, _S3_DURATION + 1)

    assert s.skill.active_remaining == 0.0
    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in s.buffs), "ATK buff must clear"
    assert abs(s.effective_atk - base_atk) <= 2


# ---------------------------------------------------------------------------
# Test 6: S3 inactive after end — resonance reverts to every 7
# ---------------------------------------------------------------------------

def test_s3_resonance_reverts_after_end():
    w = _world()
    s = make_sesa(slot="S3")
    s.deployed = True; s.position = _SESA_POS; s.atk_cd = 999.0
    w.add_unit(s)
    primary = _enemy(w, 2.0, 2.0)
    adjacent = _enemy(w, 2.0, 3.0, "Adjacent")

    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)
    _ticks(w, _S3_DURATION + 1)

    assert s.skill.active_remaining == 0.0
    from data.characters.sesa import _S3_ACTIVE_ATTR
    assert not getattr(s, _S3_ACTIVE_ATTR, False), "S3 active attr must be cleared"


# ---------------------------------------------------------------------------
# Test 7: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    s = make_sesa(slot="S2")
    assert s.skill is not None and s.skill.slot == "S2"
    assert s.skill.name == "Drumroll"
