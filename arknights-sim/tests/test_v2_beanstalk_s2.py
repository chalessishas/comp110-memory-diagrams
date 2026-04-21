"""Beanstalk S2 "Everyone Together!" — 15s AUTO, 12 DP drip over duration, block=0 while active.

Tests cover:
  - S2 config (name, sp_cost=44, initial_sp=15, duration=15s, behavior_tag)
  - block drops to 0 on skill start
  - DP gain: approximately 12 DP over 15s
  - block restored to 1 on skill end
  - S3 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction
from core.systems import register_default_systems
from data.characters.beanstalk import (
    make_beanstalk, _S2_TAG, _S2_DP_TOTAL, _S2_DURATION,
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


def _enemy(world: World, x: float, y: float) -> UnitState:
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=99999, atk=0, defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


def test_beanstalk_s2_config():
    op = make_beanstalk(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Everyone Together!"
    assert sk.sp_cost == 44
    assert sk.initial_sp == 15
    assert sk.duration == _S2_DURATION
    assert sk.behavior_tag == _S2_TAG


def test_s2_block_drops_to_0():
    w = _world()
    op = make_beanstalk(slot="S2")
    assert op.block == 1
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _enemy(w, 1.0, 1.0)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    assert op.block == 0


def test_s2_dp_drip_over_duration():
    w = _world()
    op = make_beanstalk(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _enemy(w, 1.0, 1.0)

    dp_before = w.global_state.dp
    op.skill.sp = float(op.skill.sp_cost)
    for _ in range(int(TICK_RATE * _S2_DURATION)):
        w.tick()

    dp_gained = w.global_state.dp - dp_before
    assert abs(dp_gained - _S2_DP_TOTAL) <= 1.0, f"Expected ~{_S2_DP_TOTAL} DP, got {dp_gained}"


def test_s2_block_restored_on_end():
    w = _world()
    op = make_beanstalk(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _enemy(w, 1.0, 1.0)

    op.skill.sp = float(op.skill.sp_cost)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert op.block == 1


def test_s3_regression():
    op = make_beanstalk(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Grand Rally"
