"""Ashlock S3 "Fortress Barrage" — MANUAL, 30s, ATK+150%, forced ranged mode, FRAGILE(×1.2) on start.

Tests cover:
  - S3 configured correctly (slot, sp_cost=40, initial_sp=15, MANUAL, 30s)
  - ATK+150% buff applied on activation
  - Forced ranged mode set on activation
  - FRAGILE (×1.2) applied to enemies in range on activation
  - ATK buff and ranged mode cleared on S3 end
  - Enemies out of range do not receive FRAGILE
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
from data.characters.ashlock import (
    make_ashlock,
    _S3_TAG, _S3_ATK_RATIO, _S3_SOURCE_TAG, _S3_DURATION,
    _S3_FRAGILE_TAG, _S3_FRAGILE_MULTIPLIER, _S3_FRAGILE_DURATION,
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
    a = make_ashlock(slot="S3")
    sk = a.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "Fortress Barrage"
    assert sk.sp_cost == 40
    assert sk.initial_sp == 15
    assert sk.duration == _S3_DURATION
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
def test_s3_atk_buff():
    w = _world()
    a = make_ashlock(slot="S3")
    a.deployed = True; a.position = (0.0, 1.0); a.atk_cd = 999.0
    w.add_unit(a)
    base_atk = a.effective_atk

    a.skill.sp = float(a.skill.sp_cost)
    manual_trigger(w, a)

    buff = next((b for b in a.buffs if b.source_tag == _S3_SOURCE_TAG), None)
    assert buff is not None, "ATK buff must be applied on S3 activation"
    assert abs(buff.value - _S3_ATK_RATIO) <= 0.001

    # effective_atk includes talent +8% and S3 +150%, stacking additively
    assert a.effective_atk > base_atk


# ---------------------------------------------------------------------------
def test_s3_forced_ranged_mode():
    w = _world()
    a = make_ashlock(slot="S3")
    a.deployed = True; a.position = (0.0, 1.0); a.atk_cd = 999.0
    w.add_unit(a)

    a.skill.sp = float(a.skill.sp_cost)
    manual_trigger(w, a)

    assert getattr(a, "_force_ranged_mode", False), "S3 must set _force_ranged_mode=True"


# ---------------------------------------------------------------------------
def test_s3_fragile_applied_in_range():
    w = _world()
    a = make_ashlock(slot="S3")
    a.deployed = True; a.position = (0.0, 1.0); a.atk_cd = 999.0
    w.add_unit(a)
    # _RANGED_RANGE includes (1,0),(2,0),(3,0),(1,-1),(1,1)
    e = _enemy(w, 1.0, 1.0)  # dx=1, dy=0 → in range

    a.skill.sp = float(a.skill.sp_cost)
    manual_trigger(w, a)

    fragile = [s for s in e.statuses if s.kind == StatusKind.FRAGILE and s.source_tag == _S3_FRAGILE_TAG]
    assert len(fragile) == 1, "Enemy in range must receive FRAGILE on S3 activation"
    assert abs(fragile[0].params["multiplier"] - _S3_FRAGILE_MULTIPLIER) < 0.01


# ---------------------------------------------------------------------------
def test_s3_no_fragile_out_of_range():
    w = _world()
    a = make_ashlock(slot="S3")
    a.deployed = True; a.position = (0.0, 1.0); a.atk_cd = 999.0
    w.add_unit(a)
    e = _enemy(w, 5.0, 1.0)  # dx=5, dy=0 → outside ranged range

    a.skill.sp = float(a.skill.sp_cost)
    manual_trigger(w, a)

    fragile = [s for s in e.statuses if s.kind == StatusKind.FRAGILE and s.source_tag == _S3_FRAGILE_TAG]
    assert len(fragile) == 0, "Enemy out of range must NOT receive FRAGILE"


# ---------------------------------------------------------------------------
def test_s3_buff_and_ranged_mode_cleared_on_end():
    w = _world()
    a = make_ashlock(slot="S3")
    a.deployed = True; a.position = (0.0, 1.0); a.atk_cd = 999.0
    w.add_unit(a)

    a.skill.sp = float(a.skill.sp_cost)
    manual_trigger(w, a)
    assert a.skill.active_remaining > 0.0

    _ticks(w, _S3_DURATION + 1.0)

    assert not any(b.source_tag == _S3_SOURCE_TAG for b in a.buffs), (
        "ATK buff must be cleared after S3 ends"
    )
    assert not getattr(a, "_force_ranged_mode", False), (
        "_force_ranged_mode must be False after S3 ends"
    )


# ---------------------------------------------------------------------------
def test_s2_regression():
    a = make_ashlock(slot="S2")
    assert a.skill is not None and a.skill.slot == "S2"
    assert a.skill.name == "Torrent"
    assert a.skill.sp_cost == 25
    assert a.skill.trigger == SkillTrigger.AUTO
