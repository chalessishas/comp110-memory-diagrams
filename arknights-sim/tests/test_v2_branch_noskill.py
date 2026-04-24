"""Branch (Foldartol) S1 "Desperate Resistance" (DEF+90%) / S2 "Set on Survival" (ATK+120%+DEF+40%).

Tests cover:
  - Config: archetype DEF_JUGGERNAUT, no skill with default slot
  - S1 config (name, sp_cost=20, initial_sp=6, duration=12s)
  - S1 DEF buff applied/cleared
  - S2 config (name, sp_cost=22, initial_sp=3, duration=15s)
  - S2 dual ATK+DEF buffs applied/cleared
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, AttackType, Profession, RoleArchetype
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.branch import (
    make_branch,
    _S1_TAG, _S1_DEF_RATIO, _S1_BUFF_TAG, _S1_DURATION,
    _S2_TAG, _S2_ATK_RATIO, _S2_DEF_RATIO, _S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG, _S2_DURATION,
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


def test_branch_config():
    op = make_branch()
    assert op.name == "Branch"
    assert op.profession == Profession.DEFENDER
    assert op.archetype == RoleArchetype.DEF_JUGGERNAUT
    assert op.attack_type == AttackType.PHYSICAL
    assert op.skill is None


def test_branch_s1_config():
    op = make_branch(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Desperate Resistance"
    assert sk.sp_cost == 20 and sk.initial_sp == 6
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG


def test_s1_def_buff_applied():
    w = _world()
    op = make_branch(slot="S1")
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    expected = int(base_def * (1 + _S1_DEF_RATIO))
    assert op.effective_def == expected
    assert any(b.source_tag == _S1_BUFF_TAG for b in op.buffs)


def test_s1_def_buff_cleared_on_end():
    w = _world()
    op = make_branch(slot="S1")
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S1_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S1_BUFF_TAG for b in op.buffs)
    assert op.effective_def == base_def


def test_branch_s2_config():
    op = make_branch(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Set on Survival"
    assert sk.sp_cost == 22 and sk.initial_sp == 3
    assert sk.duration == _S2_DURATION
    assert sk.behavior_tag == _S2_TAG


def test_s2_dual_buffs_applied():
    w = _world()
    op = make_branch(slot="S2")
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


def test_s2_dual_buffs_cleared_on_end():
    w = _world()
    op = make_branch(slot="S2")
    base_atk = op.effective_atk
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag in (_S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG) for b in op.buffs)
    assert op.effective_atk == base_atk
    assert op.effective_def == base_def
