"""Beanstalk S1 "Sentinel Command" — instant AUTO, refund 8 DP on activation.

Tests cover:
  - S1 config (name, sp_cost=34, initial_sp=11, instant, AUTO, requires_target=False)
  - DP refunded on skill activation (+8 DP)
  - DP gain fires only once (instant skill — no drip)
  - S2 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, SkillTrigger, SPGainMode
from core.systems import register_default_systems
from data.characters.beanstalk import make_beanstalk, _S1_TAG, _S1_DP


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def test_beanstalk_s1_config():
    op = make_beanstalk(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Sentinel Command"
    assert sk.sp_cost == 34
    assert sk.initial_sp == 11
    assert sk.duration == 0.0
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.behavior_tag == _S1_TAG


def test_s1_refunds_dp():
    w = _world()
    op = make_beanstalk(slot="S1")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    dp_before = w.global_state.dp
    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    assert w.global_state.dp == dp_before + _S1_DP


def test_s1_fires_once():
    w = _world()
    op = make_beanstalk(slot="S1")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()
    dp_after_skill = w.global_state.dp

    # Run a few more ticks — DP should not keep accumulating from S1
    for _ in range(int(TICK_RATE * 2.0)):
        w.tick()

    assert w.global_state.dp == dp_after_skill


def test_s2_regression():
    op = make_beanstalk(slot="S2")
    assert op.skill is not None and op.skill.slot == "S2"
    assert op.skill.name == "Everyone Together!"
