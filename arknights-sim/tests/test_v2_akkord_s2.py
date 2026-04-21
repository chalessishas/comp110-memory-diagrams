"""Akkord S2 "Harmonic Blast" — instant AUTO_ATTACK, 150% ATK Arts blast-pierce + SLOW on all hit.

Tests cover:
  - S2 config (name, sp_cost=25, initial_sp=10, instant, AUTO_ATTACK, requires_target)
  - Arts damage to primary target: 150% ATK
  - SLOW applied to primary target
  - SLOW applied to pierce targets in blast ray
  - S3 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, StatusKind, SPGainMode, SkillTrigger
from core.systems import register_default_systems
from data.characters.akkord import (
    make_akkord, _S2_TAG, _S2_ATK_MULT, _S2_SLOW_TAG, _S2_SLOW_DURATION,
)


def _world() -> World:
    grid = TileGrid(width=10, height=5)
    for x in range(10):
        for y in range(5):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _enemy(world: World, x: float, y: float, hp: int = 99999, res: float = 0.0) -> UnitState:
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=hp, atk=0, defence=0, res=res)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


def test_akkord_s2_config():
    op = make_akkord(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Harmonic Blast"
    assert sk.sp_cost == 25
    assert sk.initial_sp == 10
    assert sk.duration == 0.0
    assert sk.sp_gain_mode == SPGainMode.AUTO_ATTACK
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.behavior_tag == _S2_TAG


def test_s2_arts_damage_primary_target():
    w = _world()
    op = make_akkord(slot="S2")
    # No talent ally needed for the basic damage test
    op.deployed = True; op.position = (0.0, 2.0); op.atk_cd = 999.0
    w.add_unit(op)
    target = _enemy(w, 2.0, 2.0)
    hp_before = target.hp

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    expected = int(op.effective_atk * _S2_ATK_MULT)
    dmg = hp_before - target.hp
    assert dmg == expected, f"expected {expected}, got {dmg}"


def test_s2_slow_applied_to_primary():
    w = _world()
    op = make_akkord(slot="S2")
    op.deployed = True; op.position = (0.0, 2.0); op.atk_cd = 999.0
    w.add_unit(op)
    target = _enemy(w, 2.0, 2.0)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    slow = next((s for s in target.statuses if s.source_tag == _S2_SLOW_TAG), None)
    assert slow is not None, "SLOW not applied to primary target"
    assert slow.kind == StatusKind.SLOW


def test_s2_slow_applied_to_pierce_target():
    w = _world()
    op = make_akkord(slot="S2")
    op.deployed = True; op.position = (0.0, 2.0); op.atk_cd = 999.0
    w.add_unit(op)
    # Primary target at dx=2; behind it along the ray at dx=4
    primary = _enemy(w, 2.0, 2.0)
    behind = _enemy(w, 4.0, 2.0)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    slow_primary = next((s for s in primary.statuses if s.source_tag == _S2_SLOW_TAG), None)
    slow_behind = next((s for s in behind.statuses if s.source_tag == _S2_SLOW_TAG), None)
    assert slow_primary is not None, "SLOW not on primary"
    assert slow_behind is not None, "SLOW not on pierce target"


def test_s3_regression():
    op = make_akkord(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Grand Harmonic"
