"""Liskam S1 'Charged Defense' — 8s AUTO, DEF+80%.

Tests cover:
  - S1 config (sp_cost=20, initial_sp=0, duration=8s, AUTO)
  - DEF buff applied when skill fires
  - DEF buff cleared after skill ends
  - S2 config regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis, BuffStack
from core.systems import register_default_systems
from data.characters.liskam import (
    make_liskam, _S1_TAG, _S1_DEF_RATIO, _S1_BUFF_TAG, _S1_DURATION,
    _S2_TAG, _S2_DURATION,
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


def test_liskam_s1_config():
    op = make_liskam(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Charged Defense"
    assert sk.sp_cost == 20
    assert sk.initial_sp == 0
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG
    assert sk.sp == 0.0


def test_s1_def_buff_applied():
    w = _world()
    op = make_liskam(slot="S1")
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    expected = int(base_def * (1 + _S1_DEF_RATIO))
    assert op.effective_def == expected
    assert any(b.source_tag == _S1_BUFF_TAG for b in op.buffs)


def test_s1_def_buff_cleared_on_end():
    w = _world()
    op = make_liskam(slot="S1")
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()
    for _ in range(int(TICK_RATE * (_S1_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S1_BUFF_TAG for b in op.buffs)
    assert op.effective_def == base_def


def test_liskam_s2_config():
    op = make_liskam(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.sp_cost == 55 and sk.initial_sp == 28
    assert sk.duration == _S2_DURATION and sk.behavior_tag == _S2_TAG
    assert sk.sp == 28.0
