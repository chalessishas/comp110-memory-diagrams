"""Folinic S1 "Camouflage" — toggle/permanent (3600s sentinel), ATK+30%.

Tests cover:
  - S1 config (name, sp_cost=72, initial_sp=0, duration=3600s)
  - S1 ATK buff applied on trigger
  - S2 slot regression (name, sp_cost=30, initial_sp=9)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, BuffAxis
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.folivo import (
    make_folivo, _S1_TAG, _S1_ATK_RATIO, _S1_BUFF_TAG, _S1_DURATION,
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


def test_folivo_s1_config():
    op = make_folivo(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Camouflage"
    assert sk.sp_cost == 72
    assert sk.initial_sp == 0
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG


def test_s1_atk_buff_applied():
    w = _world()
    op = make_folivo(slot="S1")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    atk_buffs = [b for b in op.buffs if b.axis == BuffAxis.ATK]
    assert any(b.source_tag == _S1_BUFF_TAG and b.value == _S1_ATK_RATIO for b in atk_buffs)


def test_s2_slot_config():
    op = make_folivo(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Panoramic Camera Overload"
    assert sk.sp_cost == 30 and sk.initial_sp == 9
