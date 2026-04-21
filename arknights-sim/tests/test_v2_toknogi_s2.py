"""Toknogi S2 "Grove Shade" — ATK+30%/DEF+35% for 20s, AUTO trigger.

Tests: config, atk buff applied, def buff applied, buffs cleared, s3 regression.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.toknogi import (
    make_toknogi, _S2_ATK_BUFF_TAG, _S2_ATK_RATIO, _S2_DEF_BUFF_TAG, _S2_DEF_RATIO,
    _S2_DURATION, _S2_TAG,
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


def test_toknogi_s2_config():
    op = make_toknogi(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Grove Shade"
    assert sk.sp_cost == 30
    assert sk.initial_sp == 15
    assert sk.duration == _S2_DURATION
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff_applied():
    w = _world()
    op = make_toknogi(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert op.effective_atk > base_atk
    assert any(b.source_tag == _S2_ATK_BUFF_TAG for b in op.buffs)


def test_s2_def_buff_applied_to_ally():
    from core.state.unit_state import UnitState
    from core.types import Faction
    w = _world()
    op = make_toknogi(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    # Add an ally within S2 range
    ally = UnitState(name="Ally", faction=Faction.ALLY, max_hp=1000, atk=100, defence=100, res=0)
    ally.alive = True; ally.deployed = True; ally.position = (2.0, 1.0)
    w.add_unit(ally)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert any(b.source_tag == _S2_DEF_BUFF_TAG for b in ally.buffs)


def test_s2_buffs_cleared_on_end():
    from core.state.unit_state import UnitState
    from core.types import Faction
    w = _world()
    op = make_toknogi(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    ally = UnitState(name="Ally", faction=Faction.ALLY, max_hp=1000, atk=100, defence=100, res=0)
    ally.alive = True; ally.deployed = True; ally.position = (2.0, 1.0)
    w.add_unit(ally)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()
    assert not any(b.source_tag in (_S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG) for b in op.buffs)
    assert not any(b.source_tag == _S2_DEF_BUFF_TAG for b in ally.buffs)
    assert op.effective_atk == base_atk


def test_s3_regression():
    op = make_toknogi(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Ancient Forest"
