"""Grani S1 'DEF Up γ' / S2 'Press the Attack!' — DEF+60% / ATK+DEF+60%."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis, BuffStack
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.grani import (
    make_grani, _S1_TAG, _S1_DURATION, _S2_TAG,
    _S1_DEF_RATIO, _S1_BUFF_TAG,
    _S2_ATK_RATIO, _S2_DEF_RATIO, _S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG, _S2_DURATION,
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


def test_grani_s1_config():
    op = make_grani(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "DEF Up γ"
    assert sk.sp_cost == 40 and sk.initial_sp == 10
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG


def test_s1_def_buff_applied():
    w = _world()
    op = make_grani(slot="S1")
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    expected = int(base_def * (1 + _S1_DEF_RATIO))
    assert op.effective_def == expected
    assert any(b.source_tag == _S1_BUFF_TAG for b in op.buffs)


def test_s1_buff_cleared_on_end():
    w = _world()
    op = make_grani(slot="S1")
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S1_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S1_BUFF_TAG for b in op.buffs)
    assert op.effective_def == base_def


def test_s2_slot_config():
    op = make_grani(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Press the Attack!"
    assert sk.sp_cost == 74 and sk.initial_sp == 50
    assert sk.behavior_tag == _S2_TAG


def test_s2_dual_buff_applied():
    w = _world()
    op = make_grani(slot="S2")
    base_atk = op.effective_atk
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert op.effective_atk == int(base_atk * (1 + _S2_ATK_RATIO))
    assert op.effective_def == int(base_def * (1 + _S2_DEF_RATIO))
    assert any(b.source_tag == _S2_ATK_BUFF_TAG for b in op.buffs)
    assert any(b.source_tag == _S2_DEF_BUFF_TAG for b in op.buffs)


def test_s2_buffs_cleared_on_end():
    w = _world()
    op = make_grani(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag in (_S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG) for b in op.buffs)
    assert op.effective_atk == base_atk
