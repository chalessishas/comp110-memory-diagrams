"""Midnight S1 "Weapon Enchantment α" — 40s MANUAL, ATK+35%.

Tests cover:
  - S1 config (sp_cost=70, initial_sp=30, duration=40s)
  - S1 ATK buff applied on trigger
  - S1 ATK buff cleared after skill ends
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.midn import (
    make_midn,
    _S1_TAG, _S1_ATK_RATIO, _S1_ATK_BUFF_TAG, _S1_DURATION,
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


def test_midn_s1_config():
    op = make_midn(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Weapon Enchantment α"
    assert sk.sp_cost == 70 and sk.initial_sp == 30
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG
    assert sk.sp == 30.0


def test_s1_atk_buff_applied():
    w = _world()
    op = make_midn(slot="S1")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert any(b.source_tag == _S1_ATK_BUFF_TAG and b.value == _S1_ATK_RATIO
               for b in op.buffs if b.axis == BuffAxis.ATK)


def test_s1_atk_buff_cleared_on_end():
    w = _world()
    op = make_midn(slot="S1")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S1_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S1_ATK_BUFF_TAG for b in op.buffs)
