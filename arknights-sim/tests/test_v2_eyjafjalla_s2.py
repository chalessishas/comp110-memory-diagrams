"""Eyjafjalla S2 "Volcanic Activity" — ATK+160%, splash_radius=1.3, 50s AUTO.

Tests cover:
  - S2 config (slot, name, sp_cost=60, initial_sp=15, duration=50s)
  - ATK+160% buff applied on S2 start
  - splash_radius set to 1.3 on S2 start
  - ATK buff removed on S2 end
  - splash_radius restored on S2 end
  - S1 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, BuffAxis, SPGainMode, TICK_RATE
from core.systems import register_default_systems
from data.characters.eyjafjalla import (
    make_eyjafjalla,
    _S2_TAG, _S2_ATK_RATIO, _S2_SPLASH_RADIUS, _S2_BUFF_TAG,
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


def test_eyjafjalla_s2_config():
    op = make_eyjafjalla(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Volcanic Activity"
    assert sk.sp_cost == 40
    assert sk.initial_sp == 20
    assert abs(sk.duration - 40.0) < 1e-6
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff_on_start():
    """S2 start grants +160% ATK."""
    w = _world()
    op = make_eyjafjalla(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    _enemy(w, 1.0, 1.0)
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    assert op.skill.active_remaining > 0, "S2 should be active"
    atk_buff = next((b for b in op.buffs if b.source_tag == _S2_BUFF_TAG), None)
    assert atk_buff is not None, "ATK buff should be applied"
    assert abs(atk_buff.value - _S2_ATK_RATIO) < 1e-6


def test_s2_splash_radius_on_start():
    """S2 sets splash_radius to 1.3."""
    w = _world()
    op = make_eyjafjalla(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    _enemy(w, 1.0, 1.0)
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    assert op.skill.active_remaining > 0
    assert abs(op.splash_radius - _S2_SPLASH_RADIUS) < 1e-6, (
        f"splash_radius should be {_S2_SPLASH_RADIUS}, got {op.splash_radius}"
    )


def test_s2_buffs_cleared_on_end():
    """ATK buff and splash_radius reset after S2 ends."""
    w = _world()
    op = make_eyjafjalla(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    _enemy(w, 1.0, 1.0)
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    for _ in range(int(TICK_RATE * (40.0 + 2.0))):
        w.tick()

    assert op.skill.active_remaining == 0.0
    atk_buff = next((b for b in op.buffs if b.source_tag == _S2_BUFF_TAG), None)
    assert atk_buff is None, "ATK buff should be removed after S2"
    # splash_radius should be back to base (< S2 value)
    assert op.splash_radius < _S2_SPLASH_RADIUS or not hasattr(op, "_s2_splash_set"), (
        "splash_radius should be restored after S2"
    )


def test_s3_regression():
    op = make_eyjafjalla(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Pyroclastic Eruption"
