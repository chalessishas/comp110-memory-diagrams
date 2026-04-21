"""Saileach S1 "Tactical Deployment I" — 8s AUTO, drip 14 DP over duration (1.75 DP/s).

Tests cover:
  - S1 config (name, sp_cost=22, initial_sp=11, duration=8s, AUTO, requires_target=False)
  - DP gain: approximately 14 DP over 8s
  - DP fractional accumulator resets on skill end
  - S2 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction
from core.systems import register_default_systems
from data.characters.saileach import (
    make_saileach, _S1_TAG, _S1_DP_RATE, _S1_DP_FRAC,
)

_S1_DURATION = 8.0
_S1_DP_TOTAL = _S1_DP_RATE * _S1_DURATION  # 14.0


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def test_saileach_s1_config():
    op = make_saileach(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Tactical Deployment I"
    assert sk.sp_cost == 22
    assert sk.initial_sp == 11
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG


def test_s1_dp_drip_over_duration():
    w = _world()
    op = make_saileach(slot="S1")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    dp_before = w.global_state.dp
    op.skill.sp = float(op.skill.sp_cost)
    for _ in range(int(TICK_RATE * _S1_DURATION)):
        w.tick()

    dp_gained = w.global_state.dp - dp_before
    assert abs(dp_gained - _S1_DP_TOTAL) <= 1.0, f"Expected ~{_S1_DP_TOTAL} DP, got {dp_gained}"


def test_s1_frac_resets_on_end():
    w = _world()
    op = make_saileach(slot="S1")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    for _ in range(int(TICK_RATE * (_S1_DURATION + 1.0))):
        w.tick()

    frac = getattr(op, _S1_DP_FRAC, None)
    assert frac is None or abs(frac) < 0.01


def test_s2_regression():
    op = make_saileach(slot="S2")
    assert op.skill is not None and op.skill.slot == "S2"
    assert op.skill.name == "Flagship Order"
