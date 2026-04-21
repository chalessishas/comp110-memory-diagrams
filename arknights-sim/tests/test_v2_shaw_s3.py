"""Tests for Shaw S3 "Raging Flood" — ATK +150%, push_distance→5, 20s MANUAL."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, SkillTrigger
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.shaw import make_shaw, _S3_ATK_RATIO, _S3_DURATION, _S3_PUSH_BOOST, _GALE_PUSH


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


def test_s3_config():
    op = make_shaw(slot="S3")
    assert op.skill.slot == "S3"
    assert op.skill.sp_cost == 30
    assert op.skill.initial_sp == 10
    assert op.skill.duration == _S3_DURATION
    assert op.skill.trigger == SkillTrigger.MANUAL


def test_s3_atk_buff_applied():
    w = _world()
    op = make_shaw(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    base_atk = op.effective_atk

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert op.effective_atk == int(base_atk * (1 + _S3_ATK_RATIO))


def test_s3_push_distance_boosted():
    w = _world()
    op = make_shaw(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    # After battle_start, Gale talent sets push_distance=2
    push_before = op.push_distance

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert op.push_distance == _S3_PUSH_BOOST
    assert op.push_distance > push_before


def test_s3_push_restored_on_end():
    w = _world()
    op = make_shaw(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    push_before = op.push_distance

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    _ticks(w, _S3_DURATION + 0.1)
    assert op.push_distance == push_before


def test_s3_atk_cleared_on_end():
    w = _world()
    op = make_shaw(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    base_atk = op.effective_atk

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    _ticks(w, _S3_DURATION + 0.1)
    assert op.effective_atk == base_atk


def test_s3_s2_regression():
    op = make_shaw(slot="S2")
    assert op.skill.slot == "S2"
    assert op.skill.sp_cost == 15
    assert op.skill.duration == 0.0
