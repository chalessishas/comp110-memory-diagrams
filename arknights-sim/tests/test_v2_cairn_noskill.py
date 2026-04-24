"""Cairn S1 "Overlay Restoration" — 30s MANUAL, MAX_HP+100%.

Tests cover:
  - Config: archetype DEF_PROTECTOR, no skill with default slot
  - S1 config (name, sp_cost=35, initial_sp=16, duration=30s)
  - S1 MAX_HP buff applied on trigger
  - S1 MAX_HP buff cleared after skill ends
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, AttackType, Profession, RoleArchetype, BuffAxis
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.cairn import (
    make_cairn, _S1_TAG, _S1_MAXHP_RATIO, _S1_MAXHP_BUFF_TAG, _S1_DURATION,
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


def test_cairn_config():
    op = make_cairn()
    assert op.name == "Cairn"
    assert op.profession == Profession.DEFENDER
    assert op.archetype == RoleArchetype.DEF_PROTECTOR
    assert op.attack_type == AttackType.PHYSICAL
    assert op.skill is None


def test_cairn_s1_config():
    op = make_cairn(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Overlay Restoration"
    assert sk.sp_cost == 35 and sk.initial_sp == 16
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG


def test_s1_maxhp_buff_applied():
    w = _world()
    op = make_cairn(slot="S1")
    base_hp = op.max_hp
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    expected = int(base_hp * (1 + _S1_MAXHP_RATIO))
    assert int(op.effective_stat(BuffAxis.MAX_HP)) == expected
    assert any(b.source_tag == _S1_MAXHP_BUFF_TAG for b in op.buffs)


def test_s1_maxhp_buff_cleared_on_end():
    w = _world()
    op = make_cairn(slot="S1")
    base_hp = op.max_hp
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S1_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S1_MAXHP_BUFF_TAG for b in op.buffs)
    assert int(op.effective_stat(BuffAxis.MAX_HP)) == base_hp
