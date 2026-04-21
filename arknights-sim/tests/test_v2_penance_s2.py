"""Penance S2 "Verdict" — ATK+60% for 35s, AUTO trigger, sp_cost=25.

Tests cover:
  - S2 config (slot, name, sp_cost=25, initial_sp=10, duration=35s, AUTO)
  - ATK+60% buff applied on S2 start
  - Buff removed on S2 end
  - S3 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, BuffAxis, SPGainMode, SkillTrigger, TICK_RATE
from core.systems import register_default_systems
from data.characters.penance import (
    make_penance,
    _S2_TAG, _S2_ATK_RATIO, _S2_BUFF_TAG,
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


def _enemy(world: World, x: float, y: float):
    from core.types import Faction
    from core.state.unit_state import UnitState
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=99999, atk=0, defence=0, res=0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


def test_penance_s2_config():
    op = make_penance(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Verdict"
    assert sk.sp_cost == 25
    assert sk.initial_sp == 10
    assert abs(sk.duration - 35.0) < 1e-6
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff_on_start():
    """S2 start grants ATK+60%."""
    w = _world()
    op = make_penance(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    _enemy(w, 1.0, 1.0)
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    assert op.skill.active_remaining > 0, "S2 should be active"
    buff = next((b for b in op.buffs if b.source_tag == _S2_BUFF_TAG), None)
    assert buff is not None, "ATK+60% buff should be present"
    assert abs(buff.value - _S2_ATK_RATIO) < 1e-6


def test_s2_buff_cleared_on_end():
    """ATK buff removed when S2 expires."""
    w = _world()
    op = make_penance(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    _enemy(w, 1.0, 1.0)
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    for _ in range(int(TICK_RATE * (35.0 + 2.0))):
        w.tick()

    assert op.skill.active_remaining == 0.0
    buff = next((b for b in op.buffs if b.source_tag == _S2_BUFF_TAG), None)
    assert buff is None, "ATK buff should be removed after S2"


def test_s3_regression():
    op = make_penance(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Purgation"
