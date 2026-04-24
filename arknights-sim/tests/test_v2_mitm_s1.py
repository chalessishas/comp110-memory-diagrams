"""Matterhorn S1 'Stamina Enhancement' (MaxHP+40%) / S2 'Cold Resistance' (MaxHP+DEF+RES)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis, BuffStack
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.mitm import (
    make_mitm,
    _S1_TAG, _S1_DURATION, _S1_MAXHP_RATIO, _S1_MAXHP_BUFF_TAG,
    _S2_TAG, _S2_DURATION,
    _S2_MAXHP_RATIO, _S2_DEF_RATIO, _S2_RES_FLAT,
    _S2_MAXHP_BUFF_TAG, _S2_DEF_BUFF_TAG, _S2_RES_BUFF_TAG,
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


def test_mitm_s1_config():
    op = make_mitm(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Stamina Enhancement"
    assert sk.sp_cost == 39 and sk.initial_sp == 5
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG
    assert sk.sp == 5.0


def test_s1_maxhp_buff_applied():
    w = _world()
    op = make_mitm(slot="S1")
    base_hp = op.max_hp
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    expected = int(base_hp * (1 + _S1_MAXHP_RATIO))
    assert int(op.effective_stat(BuffAxis.MAX_HP)) == expected
    assert any(b.source_tag == _S1_MAXHP_BUFF_TAG for b in op.buffs)


def test_s1_buff_cleared_on_end():
    w = _world()
    op = make_mitm(slot="S1")
    base_hp = op.max_hp
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S1_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S1_MAXHP_BUFF_TAG for b in op.buffs)
    assert int(op.effective_stat(BuffAxis.MAX_HP)) == base_hp


def test_mitm_s2_config():
    op = make_mitm(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Cold Resistance"
    assert sk.sp_cost == 44 and sk.initial_sp == 5
    assert sk.duration == _S2_DURATION and sk.behavior_tag == _S2_TAG
    assert sk.sp == 5.0


def test_s2_triple_buff_applied():
    w = _world()
    op = make_mitm(slot="S2")
    base_hp = op.max_hp
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert int(op.effective_stat(BuffAxis.MAX_HP)) == int(base_hp * (1 + _S2_MAXHP_RATIO))
    assert op.effective_def == int(base_def * (1 + _S2_DEF_RATIO))
    res_buffs = [b for b in op.buffs if b.axis == BuffAxis.RES and b.stack == BuffStack.FLAT]
    assert any(b.value == _S2_RES_FLAT for b in res_buffs)
    assert any(b.source_tag == _S2_MAXHP_BUFF_TAG for b in op.buffs)
    assert any(b.source_tag == _S2_DEF_BUFF_TAG for b in op.buffs)
    assert any(b.source_tag == _S2_RES_BUFF_TAG for b in op.buffs)


def test_s2_triple_buff_cleared_on_end():
    w = _world()
    op = make_mitm(slot="S2")
    base_hp = op.max_hp
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag in (_S2_MAXHP_BUFF_TAG, _S2_DEF_BUFF_TAG, _S2_RES_BUFF_TAG)
                   for b in op.buffs)
    assert int(op.effective_stat(BuffAxis.MAX_HP)) == base_hp
    assert op.effective_def == base_def
