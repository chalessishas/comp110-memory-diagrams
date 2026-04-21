"""Hoshiguma S2 "Unshakeable" — DEF +300 for 20s, AUTO trigger.

Tests cover:
  - S2 config (slot, name, sp_cost, initial_sp, duration, behavior_tag)
  - DEF buff applied on skill start
  - effective_def = base_def + 300
  - DEF buff cleared after skill ends
  - S3 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis, Faction
from core.systems import register_default_systems
from core.state.unit_state import UnitState
from data.characters.hoshiguma import (
    make_hoshiguma, _S2_TAG, _S2_DEF_TAG, _S2_DEF_FLAT,
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


def test_hoshiguma_s2_config():
    op = make_hoshiguma(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Unshakeable"
    assert sk.sp_cost == 40
    assert sk.initial_sp == 0
    assert sk.duration == 20.0
    assert sk.behavior_tag == _S2_TAG


def test_s2_def_buff_applied():
    w = _world()
    op = make_hoshiguma(slot="S2")
    base_def = op.defence
    op.deployed = True; op.position = (0.0, 1.0)
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    assert any(b.source_tag == _S2_DEF_TAG for b in op.buffs)
    assert op.effective_def > base_def


def test_s2_def_amount():
    w = _world()
    op = make_hoshiguma(slot="S2")
    base_def = op.defence
    op.deployed = True; op.position = (0.0, 1.0)
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    assert op.effective_def == base_def + _S2_DEF_FLAT


def test_s2_def_cleared_on_end():
    w = _world()
    op = make_hoshiguma(slot="S2")
    base_def = op.defence
    op.deployed = True; op.position = (0.0, 1.0)
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    for _ in range(int(TICK_RATE * (20.0 + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S2_DEF_TAG for b in op.buffs)
    assert op.effective_def == base_def


def test_s3_regression():
    op = make_hoshiguma(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Shield Bash"
