"""Tests for Mulberry S3 "Bloom Storm" — ATK+50%, 100% elemental cleanse on heal, 20s MANUAL."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import Faction, TileType, TICK_RATE
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from core.systems.talent_registry import fire_on_attack_hit
import pytest
from data.characters.mulberry import make_mulberry, _S3_TAG, _S3_ATK_RATIO, _S3_DURATION


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def _ally_with_bars(x=1.0):
    a = UnitState(name="Fang", faction=Faction.ALLY, max_hp=3000, atk=600, defence=200, res=0.0)
    a.hp = 2000
    a.deployed = True
    a.position = (x, 1.0)
    a.elemental_bars = {"fire": 80.0, "ice": 50.0}
    return a


def test_s3_config():
    op = make_mulberry(slot="S3")
    assert op.skill is not None
    assert op.skill.slot == "S3"
    assert op.skill.behavior_tag == _S3_TAG
    assert op.skill.sp_cost == 25
    assert op.skill.duration == _S3_DURATION


def test_s3_atk_buff_applied():
    from core.types import BuffAxis, BuffStack
    w = _world()
    op = make_mulberry(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    atk_buffs = [b for b in op.buffs if b.axis == BuffAxis.ATK and b.source_tag == "mulberry_s3_atk"]
    assert len(atk_buffs) == 1
    assert atk_buffs[0].value == pytest.approx(_S3_ATK_RATIO)


def test_s3_full_elemental_cleanse_on_heal():
    w = _world()
    op = make_mulberry(slot="S3")
    ally = _ally_with_bars(x=1.0)
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    w.add_unit(ally)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    # During S3, talent on_attack_hit should clear 100% of elemental bars
    fire_on_attack_hit(w, op, ally, 300)
    assert ally.elemental_bars == {}


def test_s3_partial_cleanse_without_s3():
    w = _world()
    op = make_mulberry(slot="S2")
    ally = _ally_with_bars(x=1.0)
    op.deployed = True
    op.position = (0.0, 1.0)
    w.add_unit(op)
    w.add_unit(ally)
    # Without S3, elemental bars reduced by 50% only
    fire_on_attack_hit(w, op, ally, 300)
    assert ally.elemental_bars  # not fully cleared


def test_s3_buff_cleared_on_end():
    w = _world()
    op = make_mulberry(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    _ticks(w, _S3_DURATION + 0.5)
    assert not any(b.source_tag == "mulberry_s3_atk" for b in op.buffs)
    assert not getattr(op, "_mulberry_s3_active", False)
