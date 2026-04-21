"""Rope S2 "Binding Arts" — instant, AUTO_ATTACK, Arts 200% ATK + 1.5s BIND + pull 3 tiles.

Tests cover:
  - S2 config (name, sp_cost=25, initial_sp=10, instant, AUTO_ATTACK)
  - Arts damage: 200% ATK to nearest target
  - BIND status applied to target (1.5s duration)
  - pull: path_progress reduced by 3
  - Dead target: no BIND applied
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
from data.characters.rope import (
    make_rope, _S2_TAG, _S2_ATK_MULT, _S2_BIND_DURATION, _S2_BIND_TAG, _S2_PULL_DIST,
)


def _world() -> World:
    grid = TileGrid(width=8, height=4)
    for x in range(8):
        for y in range(4):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _enemy(world: World, x: float, y: float, hp: int = 99999) -> UnitState:
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=hp, atk=0, defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    e.path = [(i, 1) for i in range(8)]
    e.path_progress = float(int(x))
    world.add_unit(e)
    return e


def test_rope_s2_config():
    op = make_rope(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Binding Arts"
    assert sk.sp_cost == 25
    assert sk.initial_sp == 10
    assert sk.duration == 0.0
    assert sk.sp_gain_mode == SPGainMode.AUTO_ATTACK
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.behavior_tag == _S2_TAG


def test_s2_arts_damage():
    w = _world()
    op = make_rope(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    e = _enemy(w, 2.0, 1.0)
    hp_before = e.hp

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    expected = int(op.effective_atk * _S2_ATK_MULT)
    actual_dmg = hp_before - e.hp
    # Arts damage with 0 RES: dealt = max(1, raw - 0) = raw
    assert actual_dmg == expected, f"expected {expected}, got {actual_dmg}"


def test_s2_bind_applied():
    w = _world()
    op = make_rope(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    e = _enemy(w, 2.0, 1.0)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    bind = next((s for s in e.statuses if s.source_tag == _S2_BIND_TAG), None)
    assert bind is not None, "BIND status not applied"
    assert bind.kind == StatusKind.BIND
    assert abs(bind.expires_at - (w.global_state.elapsed + _S2_BIND_DURATION - (1.0 / TICK_RATE))) < 0.5


def test_s2_pull_reduces_path_progress():
    w = _world()
    op = make_rope(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    # Enemy at (3, 1): dx=3 is within HOOKMASTER_RANGE (-1..3)
    e = _enemy(w, 3.0, 1.0)
    progress_before = e.path_progress  # 3.0

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    # After pull 3 tiles: progress = max(0, 3.0 - 3.0) = 0.0, then enemy moves ~0.1
    assert e.path_progress < 1.0, f"pull should reduce progress from 3.0, got {e.path_progress}"


def test_s2_no_bind_on_dead_target():
    w = _world()
    op = make_rope(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    # Enemy with 1 HP — S2 200% ATK will kill it
    e = _enemy(w, 2.0, 1.0, hp=1)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    assert not e.alive
    assert not any(s.source_tag == _S2_BIND_TAG for s in e.statuses)


def test_s3_regression():
    op = make_rope(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Binding Tempest"


# pytest.approx needed
import pytest
