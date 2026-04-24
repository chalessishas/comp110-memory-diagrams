"""Zebra S2 "Group Camouflage" — 20s MANUAL, HP+55%, DEF+55%.

Tests cover:
  - S2 config (name, sp_cost=40, initial_sp=25, duration=20s)
  - S2 HP buff applied on trigger
  - S2 DEF buff applied on trigger
  - S2 both buffs cleared after skill ends
  - S1 slot regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.zebra import (
    make_zebra,
    _S1_TAG,
    _S2_TAG, _S2_HP_RATIO, _S2_DEF_RATIO,
    _S2_HP_BUFF_TAG, _S2_DEF_BUFF_TAG, _S2_DURATION,
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


def test_zebra_s2_config():
    op = make_zebra(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Group Camouflage"
    assert sk.sp_cost == 40 and sk.initial_sp == 25
    assert sk.duration == _S2_DURATION
    assert sk.behavior_tag == _S2_TAG


def test_s2_hp_buff_applied():
    w = _world()
    op = make_zebra(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert any(b.source_tag == _S2_HP_BUFF_TAG and b.value == _S2_HP_RATIO
               for b in op.buffs if b.axis == BuffAxis.MAX_HP)


def test_s2_def_buff_applied():
    w = _world()
    op = make_zebra(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert any(b.source_tag == _S2_DEF_BUFF_TAG and b.value == _S2_DEF_RATIO
               for b in op.buffs if b.axis == BuffAxis.DEF)


def test_s2_buffs_cleared_on_end():
    w = _world()
    op = make_zebra(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag in (_S2_HP_BUFF_TAG, _S2_DEF_BUFF_TAG) for b in op.buffs)


def test_s1_slot_config():
    op = make_zebra(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.behavior_tag == _S1_TAG
