"""Zima S3 "March Order" — instantly grants 15 DP + ATK+60% aura to all deployed Vanguards, 25s MANUAL.

Tests cover:
  - S3 config (slot, sp_cost, MANUAL)
  - Instantly grants 15 DP on activation
  - Deployed Vanguard ally receives ATK+60%
  - Non-Vanguard ally does NOT receive ATK buff
  - ATK buff cleared from Vanguards on end
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, Faction, Profession
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from core.state.unit_state import UnitState
from data.characters.zima import (
    make_zima,
    _S3_TAG, _S3_DP_GAIN, _S3_ATK_RATIO, _S3_DURATION, _S3_ATK_BUFF_TAG,
)
from data.characters.saga import make_saga


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    w.global_state.dp = 0
    register_default_systems(w)
    return w


def _ticks(w, seconds):
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


_ZIMA_POS = (0.0, 1.0)


def test_s3_config():
    z = make_zima(slot="S3")
    assert z.skill is not None and z.skill.slot == "S3"
    assert z.skill.name == "March Order"
    assert z.skill.sp_cost == 45
    from core.types import SkillTrigger
    assert z.skill.trigger == SkillTrigger.MANUAL
    assert z.skill.behavior_tag == _S3_TAG


def test_s3_grants_dp():
    w = _world()
    z = make_zima(slot="S3")
    z.deployed = True; z.position = _ZIMA_POS; z.atk_cd = 999.0
    w.add_unit(z)
    w.global_state.dp = 5
    z.skill.sp = float(z.skill.sp_cost)
    manual_trigger(w, z)
    assert w.global_state.dp == 5 + _S3_DP_GAIN


def test_s3_vanguard_gets_atk_buff():
    w = _world()
    z = make_zima(slot="S3")
    z.deployed = True; z.position = _ZIMA_POS; z.atk_cd = 999.0
    w.add_unit(z)
    saga = make_saga(slot="S2")
    saga.deployed = True; saga.position = (1.0, 1.0)
    w.add_unit(saga)
    base_atk = saga.effective_atk
    z.skill.sp = float(z.skill.sp_cost)
    manual_trigger(w, z)
    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(saga.effective_atk - expected) <= 2


def test_s3_non_vanguard_no_atk_buff():
    w = _world()
    z = make_zima(slot="S3")
    z.deployed = True; z.position = _ZIMA_POS; z.atk_cd = 999.0
    w.add_unit(z)
    from data.characters.liskarm import make_liskarm
    defender = make_liskarm(slot="S2")
    defender.deployed = True; defender.position = (1.0, 1.0)
    w.add_unit(defender)
    base_atk = defender.effective_atk
    z.skill.sp = float(z.skill.sp_cost)
    manual_trigger(w, z)
    assert defender.effective_atk == base_atk
    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in defender.buffs)


def test_s3_atk_buff_cleared_on_end():
    w = _world()
    z = make_zima(slot="S3")
    z.deployed = True; z.position = _ZIMA_POS; z.atk_cd = 999.0
    w.add_unit(z)
    saga = make_saga(slot="S2")
    saga.deployed = True; saga.position = (1.0, 1.0)
    w.add_unit(saga)
    base_atk = saga.effective_atk
    z.skill.sp = float(z.skill.sp_cost)
    manual_trigger(w, z)
    _ticks(w, _S3_DURATION + 1)
    assert z.skill.active_remaining == 0.0
    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in saga.buffs)
    assert abs(saga.effective_atk - base_atk) <= 2


def test_s2_regression():
    z = make_zima(slot="S2")
    assert z.skill is not None and z.skill.slot == "S2"
    assert z.skill.name == "Battle Cry"
