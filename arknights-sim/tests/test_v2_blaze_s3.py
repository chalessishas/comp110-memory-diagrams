"""Blaze S3 "Blazing Sun" — ATK+220% for 40s, AUTO trigger.

Tests cover:
  - S3 configured correctly (sp_cost=35, AUTO trigger, 40s duration)
  - ATK+220% buff applied when skill fires
  - ATK buff cleared on S3 end
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, BuffAxis, SPGainMode
from core.systems import register_default_systems
from data.characters.blaze import (
    make_blaze,
    _S3_TAG, _S3_ATK_RATIO, _S3_BUFF_TAG,
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


def _enemy(world: World, x: float, y: float) -> UnitState:
    e = UnitState(name="Enemy", faction=Faction.ENEMY, max_hp=99999, atk=0,
                  defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


def _activate(w: World, b) -> None:
    b.skill.sp = float(b.skill.sp_cost)
    w.tick()  # targeting system assigns target, then AUTO skill fires


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    b = make_blaze(slot="S3")
    assert b.skill is not None
    assert b.skill.slot == "S3"
    assert b.skill.name == "Blazing Sun"
    assert b.skill.sp_cost == 35
    assert b.skill.initial_sp == 15
    assert b.skill.duration == 40.0
    from core.types import SkillTrigger
    assert b.skill.trigger == SkillTrigger.AUTO
    assert b.skill.sp_gain_mode == SPGainMode.AUTO_TIME
    assert b.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK+220% buff applied when skill fires
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    b = make_blaze(slot="S3")
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 999.0
    w.add_unit(b)
    _enemy(w, 1.0, 1.0)   # enemy in range so AUTO trigger can fire
    base_atk = b.effective_atk

    _activate(w, b)

    buff = next((bf for bf in b.buffs if bf.source_tag == _S3_BUFF_TAG), None)
    assert buff is not None, "ATK buff must be applied when S3 fires"
    assert buff.axis == BuffAxis.ATK
    assert abs(buff.value - _S3_ATK_RATIO) <= 0.001

    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(b.effective_atk - expected) <= 2, (
        f"Blaze ATK must be ×{1 + _S3_ATK_RATIO}; expected ~{expected}, got {b.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: ATK buff cleared on S3 end
# ---------------------------------------------------------------------------

def test_s3_cleanup_on_end():
    w = _world()
    b = make_blaze(slot="S3")
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 999.0
    w.add_unit(b)
    _enemy(w, 1.0, 1.0)
    base_atk = b.effective_atk

    _activate(w, b)
    _ticks(w, 41.0)

    assert b.skill.active_remaining == 0.0, "S3 must have ended"
    assert not any(bf.source_tag == _S3_BUFF_TAG for bf in b.buffs), "ATK buff must clear"
    assert abs(b.effective_atk - base_atk) <= 2, "ATK must revert to base"


# ---------------------------------------------------------------------------
# Test 4: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    b = make_blaze(slot="S2")
    assert b.skill is not None and b.skill.slot == "S2"
    assert b.skill.name == "Carnage"
    assert b.skill.sp_cost == 25
