"""Greyy the Lightchaser S2 'Swift Strike' — 35s MANUAL, ATK+34% ASPD+35.

Tests cover:
  - S2 config (sp_cost=39, initial_sp=10, duration=35s, MANUAL)
  - ATK buff applied on trigger
  - ASPD buff applied on trigger
  - Both buffs cleared after skill ends
  - S3 config regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis, BuffStack
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.greyy2 import (
    make_greyy2, _S2_TAG, _S2_ATK_RATIO, _S2_ASPD_FLAT,
    _S2_ATK_BUFF_TAG, _S2_ASPD_BUFF_TAG, _S2_DURATION,
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


def test_greyy2_s2_config():
    op = make_greyy2(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Swift Strike"
    assert sk.sp_cost == 39
    assert sk.initial_sp == 10
    assert sk.duration == _S2_DURATION
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff_applied():
    w = _world()
    op = make_greyy2(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    expected = int(base_atk * (1 + _S2_ATK_RATIO))
    assert op.effective_atk == expected
    assert any(b.source_tag == _S2_ATK_BUFF_TAG for b in op.buffs)


def test_s2_aspd_buff_applied():
    w = _world()
    op = make_greyy2(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    aspd_buffs = [b for b in op.buffs
                  if b.axis == BuffAxis.ASPD and b.stack == BuffStack.FLAT]
    assert len(aspd_buffs) == 1
    assert aspd_buffs[0].value == _S2_ASPD_FLAT


def test_s2_both_buffs_cleared_on_end():
    w = _world()
    op = make_greyy2(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag in (_S2_ATK_BUFF_TAG, _S2_ASPD_BUFF_TAG) for b in op.buffs)
    assert op.effective_atk == base_atk


def test_s3_slot_config():
    op = make_greyy2(slot="S3")
    sk = op.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.sp_cost == 60 and sk.initial_sp == 30
