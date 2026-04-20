"""Silence S3 "Curative Panacea" — ATK+60%, heal ALL deployed allies per tick, 25s MANUAL.

Tests cover:
  - S3 config (slot, sp_cost, MANUAL)
  - ATK +60% buff applied on start
  - All deployed allies (below max HP) healed per tick
  - Healing proportional to ATK (0.70 ATK/s)
  - Full-HP ally not overhealed
  - ATK buff cleared on end
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
from core.types import Faction
from data.characters.silence import (
    make_silence,
    _S3_TAG, _S3_ATK_RATIO, _S3_DURATION, _S3_ATK_BUFF_TAG, _S3_HEAL_PER_SECOND,
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


def _injured_ally(name, pos, hp_frac=0.5, max_hp=1000):
    a = UnitState(name=name, faction=Faction.ALLY, max_hp=max_hp, atk=100, defence=0, res=0.0)
    a.alive = True; a.deployed = True; a.position = pos
    a.hp = int(max_hp * hp_frac)
    return a


_SILENCE_POS = (0.0, 1.0)


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    s = make_silence(slot="S3")
    assert s.skill is not None and s.skill.slot == "S3"
    assert s.skill.name == "Curative Panacea"
    assert s.skill.sp_cost == 45
    assert abs(s.skill.duration - _S3_DURATION) < 0.01
    from core.types import SkillTrigger
    assert s.skill.trigger == SkillTrigger.MANUAL
    assert s.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK +60% buff applied
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    s = make_silence(slot="S3")
    s.deployed = True; s.position = _SILENCE_POS; s.atk_cd = 999.0
    w.add_unit(s)

    base_atk = s.effective_atk
    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)

    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(s.effective_atk - expected) <= 2, (
        f"S3 ATK must be ×{1 + _S3_ATK_RATIO}; expected {expected}, got {s.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: All deployed allies healed per tick
# ---------------------------------------------------------------------------

def test_s3_heals_all_allies():
    w = _world()
    s = make_silence(slot="S3")
    s.deployed = True; s.position = _SILENCE_POS; s.atk_cd = 999.0
    w.add_unit(s)

    ally1 = _injured_ally("Ally1", (1.0, 1.0))
    ally2 = _injured_ally("Ally2", (2.0, 1.0))
    w.add_unit(ally1)
    w.add_unit(ally2)

    hp1_before = ally1.hp
    hp2_before = ally2.hp

    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)
    _ticks(w, 2.0)

    assert ally1.hp > hp1_before, "Ally1 must be healed during S3"
    assert ally2.hp > hp2_before, "Ally2 must be healed during S3"


# ---------------------------------------------------------------------------
# Test 4: Healing amount matches 0.70 ATK/s
# ---------------------------------------------------------------------------

def test_s3_heal_amount():
    w = _world()
    s = make_silence(slot="S3")
    s.deployed = True; s.position = _SILENCE_POS; s.atk_cd = 999.0
    w.add_unit(s)

    ally = _injured_ally("Ally", (1.0, 1.0), hp_frac=0.1, max_hp=99999)
    w.add_unit(ally)
    hp_before = ally.hp

    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)
    _ticks(w, 3.0)

    expected_heal = int(s.effective_atk * _S3_HEAL_PER_SECOND * 3.0)
    actual_heal = ally.hp - hp_before
    assert abs(actual_heal - expected_heal) <= s.effective_atk * _S3_HEAL_PER_SECOND + 2, (
        f"Heal after 3s must be ~{expected_heal}; got {actual_heal}"
    )


# ---------------------------------------------------------------------------
# Test 5: Full-HP ally not overhealed
# ---------------------------------------------------------------------------

def test_s3_no_overheal():
    w = _world()
    s = make_silence(slot="S3")
    s.deployed = True; s.position = _SILENCE_POS; s.atk_cd = 999.0
    w.add_unit(s)

    ally = _injured_ally("Ally", (1.0, 1.0), hp_frac=1.0)  # already full HP
    w.add_unit(ally)

    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)
    _ticks(w, 2.0)

    assert ally.hp == ally.max_hp, "Full-HP ally must not be overhealed"


# ---------------------------------------------------------------------------
# Test 6: ATK buff cleared on end
# ---------------------------------------------------------------------------

def test_s3_atk_buff_cleared_on_end():
    w = _world()
    s = make_silence(slot="S3")
    s.deployed = True; s.position = _SILENCE_POS; s.atk_cd = 999.0
    w.add_unit(s)

    base_atk = s.effective_atk
    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)
    _ticks(w, _S3_DURATION + 1)

    assert s.skill.active_remaining == 0.0
    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in s.buffs), "ATK buff must clear"
    assert abs(s.effective_atk - base_atk) <= 2


# ---------------------------------------------------------------------------
# Test 7: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    s = make_silence(slot="S2")
    assert s.skill is not None and s.skill.slot == "S2"
    assert s.skill.name == "Medical Protocol"
