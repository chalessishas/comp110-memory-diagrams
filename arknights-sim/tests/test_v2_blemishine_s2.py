"""Blemishine S2 "Iron Aegis" — ATK+40% + DEF+60% for 25s, MANUAL trigger.

Tests cover:
  - S2 config (slot, name, sp_cost, initial_sp, duration, behavior_tag)
  - ATK buff applied on skill activation
  - DEF buff applied on skill activation
  - Both buffs cleared after skill ends
  - S3 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.blemishine import (
    make_blemishine, _S2_TAG, _S2_ATK_RATIO, _S2_DEF_RATIO,
    _S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG, _S2_DURATION,
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


def _activate_s2(w: World, op) -> None:
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)


def test_blemishine_s2_config():
    op = make_blemishine(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Iron Aegis"
    assert sk.sp_cost == 45
    assert sk.initial_sp == 25
    assert sk.duration == _S2_DURATION
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff_applied():
    w = _world()
    op = make_blemishine(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _activate_s2(w, op)

    assert op.effective_atk > base_atk
    assert any(b.source_tag == _S2_ATK_BUFF_TAG for b in op.buffs)
    expected = int(base_atk * (1 + _S2_ATK_RATIO))
    assert op.effective_atk == expected


def test_s2_def_buff_applied():
    w = _world()
    op = make_blemishine(slot="S2")
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _activate_s2(w, op)

    assert op.effective_def > base_def
    assert any(b.source_tag == _S2_DEF_BUFF_TAG for b in op.buffs)
    expected_def = int(base_def * (1 + _S2_DEF_RATIO))
    assert op.effective_def == expected_def


def test_s2_buffs_cleared_on_end():
    w = _world()
    op = make_blemishine(slot="S2")
    base_atk = op.effective_atk
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _activate_s2(w, op)

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag in (_S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG) for b in op.buffs)
    assert op.effective_atk == base_atk
    assert op.effective_def == base_def


def test_s3_regression():
    op = make_blemishine(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Holy Flash"
