"""Manticore S1 "Scorpion's Art" — 8s AUTO, self REGEN 150 HP/s for duration.

Tests cover:
  - S1 config (name, sp_cost=10, initial_sp=5, duration=8s, AUTO, requires_target=False)
  - REGEN status applied on skill start (hps=150, 8s duration)
  - HP increases during REGEN ticks
  - REGEN status expires after 8s
  - S2 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, StatusKind
from core.systems import register_default_systems
from data.characters.manticore import (
    make_manticore, _S1_TAG, _S1_REGEN_HPS, _S1_REGEN_DURATION, _S1_REGEN_TAG,
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


def test_manticore_s1_config():
    op = make_manticore(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Scorpion's Art"
    assert sk.sp_cost == 10
    assert sk.initial_sp == 5
    assert sk.duration == _S1_REGEN_DURATION
    assert sk.behavior_tag == _S1_TAG


def test_s1_regen_status_applied():
    w = _world()
    op = make_manticore(slot="S1")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    regen = next((s for s in op.statuses if s.source_tag == _S1_REGEN_TAG), None)
    assert regen is not None, "REGEN status not applied"
    assert regen.kind == StatusKind.REGEN
    assert regen.params.get("hps") == _S1_REGEN_HPS


def test_s1_hp_increases_during_regen():
    w = _world()
    op = make_manticore(slot="S1")
    op.hp = op.max_hp // 2  # injured
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    hp_before = op.hp
    op.skill.sp = float(op.skill.sp_cost)
    for _ in range(int(TICK_RATE * 3.0)):
        w.tick()

    assert op.hp > hp_before, "HP should increase during REGEN"


def test_s1_regen_status_expires():
    w = _world()
    op = make_manticore(slot="S1")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    for _ in range(int(TICK_RATE * (_S1_REGEN_DURATION + 1.0))):
        w.tick()

    assert not any(s.source_tag == _S1_REGEN_TAG for s in op.statuses)


def test_s2_regression():
    op = make_manticore(slot="S2")
    assert op.skill is not None and op.skill.slot == "S2"
    assert op.skill.name == "Predator's Claws"
