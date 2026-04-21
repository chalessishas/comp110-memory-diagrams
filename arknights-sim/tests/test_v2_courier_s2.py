"""Courier S2 "Support Order" — 15s AUTO, ~12 DP drip over duration (0.8 DP/s).

Tests cover:
  - S2 config (name, sp_cost=35, initial_sp=15, duration=15s, behavior_tag)
  - DP gain: approximately 12 DP over 15s (0.8 DP/s rate)
  - DP fractional accumulator resets on skill end
  - S3 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction
from core.systems import register_default_systems
from data.characters.courier import (
    make_courier, _S2_TAG, _S2_DP_RATE, _S2_DP_FRAC_ATTR,
)


_S2_DURATION = 15.0
_S2_DP_TOTAL = _S2_DP_RATE * _S2_DURATION  # 12.0


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
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=99999, atk=0, defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


def test_courier_s2_config():
    op = make_courier(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Support Order"
    assert sk.sp_cost == 35
    assert sk.initial_sp == 15
    assert abs(sk.duration - _S2_DURATION) < 0.01
    assert sk.behavior_tag == _S2_TAG


def test_s2_dp_drip_over_duration():
    w = _world()
    op = make_courier(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _enemy(w, 1.0, 1.0)

    dp_before = w.global_state.dp
    op.skill.sp = float(op.skill.sp_cost)
    for _ in range(int(TICK_RATE * _S2_DURATION)):
        w.tick()

    dp_gained = w.global_state.dp - dp_before
    assert abs(dp_gained - _S2_DP_TOTAL) <= 1.0, f"Expected ~{_S2_DP_TOTAL} DP, got {dp_gained}"


def test_s2_frac_accumulator_resets_on_end():
    w = _world()
    op = make_courier(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _enemy(w, 1.0, 1.0)

    op.skill.sp = float(op.skill.sp_cost)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    frac = getattr(op, _S2_DP_FRAC_ATTR, None)
    assert frac is None or abs(frac) < 0.01


def test_s2_no_dp_before_activation():
    w = _world()
    op = make_courier(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _enemy(w, 1.0, 1.0)

    dp_before = w.global_state.dp
    # Skill not yet activated (SP not full)
    for _ in range(int(TICK_RATE * 2.0)):
        w.tick()

    dp_gained = w.global_state.dp - dp_before
    assert dp_gained < 0.5, f"DP should not accumulate before skill fires, got {dp_gained}"


def test_s3_regression():
    op = make_courier(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Combat Deployment"
