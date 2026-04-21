"""Tests for Toknogi S3 "Ancient Forest" — ATK+80%, DEF+60% to ALL allies, 25s MANUAL."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import Faction, TileType, TICK_RATE, BuffAxis
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
import pytest
from data.characters.toknogi import make_toknogi, _S3_TAG, _S3_ATK_RATIO, _S3_DEF_RATIO, _S3_DURATION


def _world() -> World:
    grid = TileGrid(width=8, height=5)
    for x in range(8):
        for y in range(5):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def _ally(x=6.0):
    a = UnitState(name="Fang", faction=Faction.ALLY, max_hp=3000, atk=600, defence=200, res=0.0)
    a.deployed = True
    a.position = (x, 2.0)
    return a


def test_s3_config():
    op = make_toknogi(slot="S3")
    assert op.skill is not None
    assert op.skill.slot == "S3"
    assert op.skill.behavior_tag == _S3_TAG
    assert op.skill.sp_cost == 40
    assert op.skill.duration == _S3_DURATION


def test_s3_atk_buff_applied():
    from core.types import BuffStack
    w = _world()
    op = make_toknogi(slot="S3")
    op.deployed = True
    op.position = (0.0, 2.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    atk_buffs = [b for b in op.buffs if b.axis == BuffAxis.ATK and b.source_tag == "toknogi_s3_atk"]
    assert len(atk_buffs) == 1
    assert atk_buffs[0].value == pytest.approx(_S3_ATK_RATIO)


def test_s3_def_buff_applied_to_far_allies():
    """S3 applies DEF buff to ALL allies, even those out of S2 range."""
    w = _world()
    op = make_toknogi(slot="S3")
    ally = _ally(x=6.0)  # far away — beyond S2 range of 3 tiles
    op.deployed = True
    op.position = (0.0, 2.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    w.add_unit(ally)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    def_buffs = [b for b in ally.buffs if b.axis == BuffAxis.DEF and b.source_tag == "toknogi_s3_def"]
    assert len(def_buffs) == 1
    assert def_buffs[0].value == pytest.approx(_S3_DEF_RATIO)


def test_s3_def_buff_cleared_on_end():
    w = _world()
    op = make_toknogi(slot="S3")
    ally = _ally(x=6.0)
    op.deployed = True
    op.position = (0.0, 2.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    w.add_unit(ally)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert any(b.source_tag == "toknogi_s3_def" for b in ally.buffs)
    _ticks(w, _S3_DURATION + 0.5)
    assert not any(b.source_tag == "toknogi_s3_def" for b in ally.buffs)


def test_s3_stronger_def_than_s2():
    from data.characters.toknogi import _S2_DEF_RATIO
    assert _S3_DEF_RATIO > _S2_DEF_RATIO


def test_s3_atk_cleared_on_end():
    w = _world()
    op = make_toknogi(slot="S3")
    op.deployed = True
    op.position = (0.0, 2.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    _ticks(w, _S3_DURATION + 0.5)
    assert not any(b.source_tag == "toknogi_s3_atk" for b in op.buffs)
