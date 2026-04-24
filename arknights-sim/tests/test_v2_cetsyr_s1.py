"""Czerny (cetsyr) S1 "Fingerfertigkeit" — 29s MANUAL, ATK+50%+RES+80.

Tests cover:
  - Config: archetype DEF_ARTS_PROTECTOR, profession DEFENDER
  - S1 config (name, sp_cost=42, initial_sp=12, duration=29s)
  - S1 ATK+RES buffs applied on trigger
  - S1 buffs cleared after skill ends
  - S2 slot regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, AttackType, Profession, RoleArchetype, BuffAxis, BuffStack
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.cetsyr import (
    make_cetsyr, _S1_TAG, _S1_ATK_RATIO, _S1_RES_FLAT,
    _S1_ATK_BUFF_TAG, _S1_RES_BUFF_TAG, _S1_DURATION, _S2_TAG,
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


def test_cetsyr_config():
    op = make_cetsyr()
    assert op.name == "Czerny"
    assert op.profession == Profession.DEFENDER
    assert op.archetype == RoleArchetype.DEF_ARTS_PROTECTOR
    assert op.attack_type == AttackType.ARTS


def test_cetsyr_s1_config():
    op = make_cetsyr(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Fingerfertigkeit"
    assert sk.sp_cost == 42 and sk.initial_sp == 12
    assert sk.duration == _S1_DURATION and sk.behavior_tag == _S1_TAG


def test_s1_buffs_applied():
    w = _world()
    op = make_cetsyr(slot="S1")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert op.effective_atk == int(base_atk * (1 + _S1_ATK_RATIO))
    assert any(b.source_tag == _S1_ATK_BUFF_TAG for b in op.buffs)
    res_buffs = [b for b in op.buffs if b.axis == BuffAxis.RES and b.stack == BuffStack.FLAT]
    assert any(b.value == _S1_RES_FLAT for b in res_buffs)
    assert any(b.source_tag == _S1_RES_BUFF_TAG for b in op.buffs)


def test_s1_buffs_cleared_on_end():
    w = _world()
    op = make_cetsyr(slot="S1")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S1_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag in (_S1_ATK_BUFF_TAG, _S1_RES_BUFF_TAG) for b in op.buffs)
    assert op.effective_atk == base_atk


def test_s2_slot_config():
    op = make_cetsyr(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2" and sk.behavior_tag == _S2_TAG
