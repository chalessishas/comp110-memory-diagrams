"""Saga S3 "Zangetsu" — ATK+180%, 20s MANUAL, on-kill restores 15% sp_cost SP.

Tests cover:
  - S3 config (slot, sp_cost, MANUAL, AUTO_ATTACK sp gain)
  - ATK +180% buff applied on start
  - On kill during S3: SP restored by 15% of sp_cost
  - On kill outside S3: no SP restore
  - SP capped at sp_cost after kill
  - ATK buff cleared on end
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
from core.systems.talent_registry import fire_on_kill
from core.state.unit_state import UnitState
from data.characters.saga import (
    make_saga,
    _S3_TAG, _S3_ATK_RATIO, _S3_DURATION, _S3_SP_RESTORE_RATIO, _S3_ATK_BUFF_TAG,
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


def _dummy_enemy():
    e = UnitState(name="Enemy", faction=Faction.ENEMY, max_hp=1, atk=0, defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (1.0, 1.0)
    return e


_SAGA_POS = (0.0, 1.0)


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    s = make_saga(slot="S3")
    assert s.skill is not None and s.skill.slot == "S3"
    assert s.skill.name == "Zangetsu"
    assert s.skill.sp_cost == 45
    from core.types import SkillTrigger, SPGainMode
    assert s.skill.trigger == SkillTrigger.MANUAL
    assert s.skill.sp_gain_mode == SPGainMode.AUTO_ATTACK
    assert s.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK +180% applied
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    s = make_saga(slot="S3")
    s.deployed = True; s.position = _SAGA_POS; s.atk_cd = 999.0
    w.add_unit(s)

    enemy = _dummy_enemy()
    w.add_unit(enemy)

    base_atk = s.effective_atk
    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)

    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(s.effective_atk - expected) <= 2, (
        f"S3 ATK must be ×{1 + _S3_ATK_RATIO}; expected {expected}, got {s.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: On kill during S3, SP restored
# ---------------------------------------------------------------------------

def test_s3_on_kill_restores_sp():
    w = _world()
    s = make_saga(slot="S3")
    s.deployed = True; s.position = _SAGA_POS; s.atk_cd = 999.0
    w.add_unit(s)

    enemy = _dummy_enemy()
    w.add_unit(enemy)

    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)
    assert s.skill.active_remaining > 0.0

    # Drain SP to 0 (simulates skill still active with empty SP)
    s.skill.sp = 0.0
    sp_before = s.skill.sp

    fire_on_kill(w, s, enemy)

    expected_gain = s.skill.sp_cost * _S3_SP_RESTORE_RATIO
    assert abs(s.skill.sp - (sp_before + expected_gain)) <= 0.01, (
        f"Kill during S3 must restore {_S3_SP_RESTORE_RATIO:.0%} sp_cost; "
        f"expected {sp_before + expected_gain:.2f}, got {s.skill.sp:.2f}"
    )


# ---------------------------------------------------------------------------
# Test 4: On kill OUTSIDE S3, no SP restore
# ---------------------------------------------------------------------------

def test_s3_no_sp_restore_outside_s3():
    w = _world()
    s = make_saga(slot="S3")
    s.deployed = True; s.position = _SAGA_POS; s.atk_cd = 999.0
    w.add_unit(s)

    enemy = _dummy_enemy()
    w.add_unit(enemy)

    s.skill.sp = 5.0   # some SP but S3 NOT active
    sp_before = s.skill.sp
    fire_on_kill(w, s, enemy)

    assert s.skill.sp == sp_before, "Kill outside S3 must not restore SP"


# ---------------------------------------------------------------------------
# Test 5: SP capped at sp_cost after kill
# ---------------------------------------------------------------------------

def test_s3_sp_restore_capped():
    w = _world()
    s = make_saga(slot="S3")
    s.deployed = True; s.position = _SAGA_POS; s.atk_cd = 999.0
    w.add_unit(s)

    enemy = _dummy_enemy()
    w.add_unit(enemy)

    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)

    # SP already at max (active means sp drains, but we force it to max for test)
    s.skill.sp = float(s.skill.sp_cost)
    fire_on_kill(w, s, enemy)

    assert s.skill.sp <= float(s.skill.sp_cost), "SP must not exceed sp_cost after kill restore"


# ---------------------------------------------------------------------------
# Test 6: ATK buff cleared on end
# ---------------------------------------------------------------------------

def test_s3_atk_buff_cleared_on_end():
    w = _world()
    s = make_saga(slot="S3")
    s.deployed = True; s.position = _SAGA_POS; s.atk_cd = 999.0
    w.add_unit(s)

    enemy = _dummy_enemy()
    w.add_unit(enemy)

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
    s = make_saga(slot="S2")
    assert s.skill is not None and s.skill.slot == "S2"
    assert s.skill.name == "Tsurugi"
