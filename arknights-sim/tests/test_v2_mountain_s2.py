"""Mountain S2 "Mountain Spirit" — ATK+160% for 20s, AUTO_ATTACK trigger.

Kill extension: each kill while S2 active extends active_remaining by 1s (max +3s cap).

Tests cover:
  - S2 config (slot, name, sp_cost, duration, behavior_tag)
  - ATK buff applied on skill start
  - effective_atk = base_atk * (1 + 1.60)
  - Kill extension: active_remaining +1s per kill
  - ATK buff cleared after skill ends
  - S3 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, Faction
from core.systems import register_default_systems
from core.systems.talent_registry import fire_on_kill
from core.state.unit_state import UnitState
from data.characters.mountain import (
    make_mountain, _S2_TAG, _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_KILL_EXTENSION,
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


def _enemy(world: World, x: float, y: float) -> UnitState:
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=99999, atk=0, defence=0, res=0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


def test_mountain_s2_config():
    op = make_mountain(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Mountain Spirit"
    assert sk.sp_cost == 2
    assert sk.duration == 20.0
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff_applied():
    w = _world()
    op = make_mountain(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _enemy(w, 1.0, 1.0)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    assert op.effective_atk > base_atk
    assert any(b.source_tag == _S2_BUFF_TAG for b in op.buffs)


def test_s2_atk_amount():
    w = _world()
    op = make_mountain(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _enemy(w, 1.0, 1.0)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    # Talent also adds ATK buff on tick; check S2 buff value directly
    s2_buff = next(b for b in op.buffs if b.source_tag == _S2_BUFF_TAG)
    assert s2_buff.value == _S2_ATK_RATIO


def test_s2_kill_extends_duration():
    w = _world()
    op = make_mountain(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    e = _enemy(w, 1.0, 1.0)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()
    before = op.skill.active_remaining

    fire_on_kill(w, op, e)
    after = op.skill.active_remaining

    assert after == pytest.approx(before + _S2_KILL_EXTENSION, abs=0.05)


def test_s2_buff_cleared_on_end():
    w = _world()
    op = make_mountain(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _enemy(w, 1.0, 1.0)

    op.skill.sp = float(op.skill.sp_cost)
    for _ in range(int(TICK_RATE * 22.0)):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in op.buffs)


def test_s3_regression():
    op = make_mountain(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Blood and Iron"
