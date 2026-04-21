"""Lava the Purgatory S3 "Volcanic Surge" — MANUAL, 30s, ATK+100%, splash=2.0, burn DOT on start.

Tests cover:
  - S3 configured correctly (slot, sp_cost=50, initial_sp=20, MANUAL, 30s)
  - ATK+100% buff applied on activation
  - Splash radius expanded to 2.0 tiles during S3
  - Enemies in range receive burn DOT (200 DPS / 5s) on activation
  - Splash radius restored to 0.8 on S3 end
  - ATK buff cleared on S3 end
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, SkillTrigger, StatusKind, SPGainMode
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.lava2 import (
    make_lava2,
    _S3_TAG, _S3_ATK_RATIO, _S3_ATK_BUFF_TAG, _S3_DURATION,
    _S3_SPLASH_RADIUS, _S3_BURN_DPS, _S3_BURN_DURATION, _S3_BURN_TAG,
    _TRAIT_SPLASH_RADIUS,
)


def _world() -> World:
    grid = TileGrid(width=8, height=3)
    for x in range(8):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def _enemy(world: World, x: float, y: float, hp: int = 99999) -> UnitState:
    e = UnitState(name="Enemy", faction=Faction.ENEMY, max_hp=hp, atk=0, defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


# ---------------------------------------------------------------------------
def test_s3_config():
    lv = make_lava2(slot="S3")
    sk = lv.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "Volcanic Surge"
    assert sk.sp_cost == 50
    assert sk.initial_sp == 20
    assert sk.duration == _S3_DURATION
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
def test_s3_atk_buff():
    w = _world()
    lv = make_lava2(slot="S3")
    lv.deployed = True; lv.position = (0.0, 1.0); lv.atk_cd = 999.0
    w.add_unit(lv)
    _enemy(w, 2.0, 1.0)
    base_atk = lv.effective_atk

    lv.skill.sp = float(lv.skill.sp_cost)
    manual_trigger(w, lv)

    buff = next((b for b in lv.buffs if b.source_tag == _S3_ATK_BUFF_TAG), None)
    assert buff is not None, "ATK buff must be applied on S3 activation"
    assert abs(buff.value - _S3_ATK_RATIO) <= 0.001

    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(lv.effective_atk - expected) <= 2


# ---------------------------------------------------------------------------
def test_s3_splash_radius_expanded():
    w = _world()
    lv = make_lava2(slot="S3")
    lv.deployed = True; lv.position = (0.0, 1.0); lv.atk_cd = 999.0
    w.add_unit(lv)
    _enemy(w, 2.0, 1.0)

    lv.skill.sp = float(lv.skill.sp_cost)
    manual_trigger(w, lv)

    assert abs(lv.splash_radius - _S3_SPLASH_RADIUS) < 0.001, (
        f"Splash radius must be {_S3_SPLASH_RADIUS} during S3, got {lv.splash_radius}"
    )


# ---------------------------------------------------------------------------
def test_s3_burn_applied_to_enemies_in_range():
    w = _world()
    lv = make_lava2(slot="S3")
    lv.deployed = True; lv.position = (0.0, 1.0); lv.atk_cd = 999.0
    w.add_unit(lv)
    e = _enemy(w, 2.0, 1.0)  # in range_shape

    lv.skill.sp = float(lv.skill.sp_cost)
    manual_trigger(w, lv)

    burn = [s for s in e.statuses if s.kind == StatusKind.DOT and s.source_tag == _S3_BURN_TAG]
    assert len(burn) == 1, "Enemy in range must receive burn DOT on S3 activation"
    assert abs(burn[0].params["dps"] - _S3_BURN_DPS) < 1.0


# ---------------------------------------------------------------------------
def test_s3_burn_not_applied_out_of_range():
    w = _world()
    lv = make_lava2(slot="S3")
    lv.deployed = True; lv.position = (0.0, 1.0); lv.atk_cd = 999.0
    w.add_unit(lv)
    e = _enemy(w, 7.0, 1.0)  # out of range (range_shape goes 0..4 dx)

    lv.skill.sp = float(lv.skill.sp_cost)
    manual_trigger(w, lv)

    burn = [s for s in e.statuses if s.kind == StatusKind.DOT and s.source_tag == _S3_BURN_TAG]
    assert len(burn) == 0, "Enemy out of range must NOT receive burn DOT"


# ---------------------------------------------------------------------------
def test_s3_splash_and_buff_restored_on_end():
    w = _world()
    lv = make_lava2(slot="S3")
    lv.deployed = True; lv.position = (0.0, 1.0); lv.atk_cd = 999.0
    w.add_unit(lv)
    _enemy(w, 2.0, 1.0)

    lv.skill.sp = float(lv.skill.sp_cost)
    manual_trigger(w, lv)
    assert lv.skill.active_remaining > 0.0

    _ticks(w, _S3_DURATION + 1.0)

    assert abs(lv.splash_radius - _TRAIT_SPLASH_RADIUS) < 0.001, (
        f"Splash must revert to {_TRAIT_SPLASH_RADIUS} after S3 ends"
    )
    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in lv.buffs), (
        "ATK buff must be cleared after S3 ends"
    )


# ---------------------------------------------------------------------------
def test_s2_regression():
    lv = make_lava2(slot="S2")
    assert lv.skill is not None and lv.skill.slot == "S2"
    assert lv.skill.name == "Scorched Earth"
    assert lv.skill.sp_cost == 35
    assert lv.skill.trigger == SkillTrigger.AUTO
