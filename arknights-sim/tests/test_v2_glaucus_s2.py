"""Glaucus S2 "Trident Strike" — MANUAL instant, AoE Arts 200% ATK + BIND 3s to all in range.

Tests cover:
  - S2 config (name, sp_cost=25, initial_sp=10, instant, MANUAL, requires_target)
  - AoE arts damage: 200% ATK to all in-range enemies
  - BIND 3s applied to all in-range enemies
  - Out-of-range enemy: not affected
  - S3 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, StatusKind, SkillTrigger, SPGainMode
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.glaucus import (
    make_glaucus, _S2_TAG, _S2_DAMAGE_RATIO, _S2_BIND_DURATION, _S2_BIND_TAG,
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


def _enemy(world: World, x: float, y: float, hp: int = 99999, res: float = 0.0) -> UnitState:
    e = UnitState(name="Enemy", faction=Faction.ENEMY, max_hp=hp, atk=0, defence=0, res=res)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


def test_glaucus_s2_config():
    op = make_glaucus(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Trident Strike"
    assert sk.sp_cost == 25
    assert sk.initial_sp == 10
    assert sk.duration == 0.0
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.behavior_tag == _S2_TAG


def test_s2_arts_damage_to_in_range_enemy():
    w = _world()
    g = make_glaucus(slot="S2")
    g.deployed = True; g.position = (0.0, 1.0); g.atk_cd = 999.0
    w.add_unit(g)
    e = _enemy(w, 2.0, 1.0)
    hp_before = e.hp

    g.skill.sp = float(g.skill.sp_cost)
    manual_trigger(w, g)

    expected = int(g.effective_atk * _S2_DAMAGE_RATIO)
    dmg = hp_before - e.hp
    assert dmg == expected, f"expected {expected}, got {dmg}"


def test_s2_bind_applied_to_in_range():
    w = _world()
    g = make_glaucus(slot="S2")
    g.deployed = True; g.position = (0.0, 1.0); g.atk_cd = 999.0
    w.add_unit(g)
    e = _enemy(w, 2.0, 1.0)

    g.skill.sp = float(g.skill.sp_cost)
    manual_trigger(w, g)

    bind = next((s for s in e.statuses if s.source_tag == _S2_BIND_TAG), None)
    assert bind is not None, "BIND status not applied"
    assert bind.kind == StatusKind.BIND
    assert bind.expires_at > w.global_state.elapsed


def test_s2_out_of_range_enemy_not_affected():
    w = _world()
    g = make_glaucus(slot="S2")
    g.deployed = True; g.position = (0.0, 1.0); g.atk_cd = 999.0
    w.add_unit(g)
    # DECEL_BINDER_RANGE: dx in range(0, 4), dy in range(-1, 2)
    # Enemy at dx=5 is out of range
    e_out = _enemy(w, 5.0, 1.0)
    hp_before = e_out.hp

    g.skill.sp = float(g.skill.sp_cost)
    manual_trigger(w, g)

    assert e_out.hp == hp_before, "out-of-range enemy should not take damage"
    assert not any(s.source_tag == _S2_BIND_TAG for s in e_out.statuses)


def test_s2_bind_duration():
    w = _world()
    g = make_glaucus(slot="S2")
    g.deployed = True; g.position = (0.0, 1.0); g.atk_cd = 999.0
    w.add_unit(g)
    e = _enemy(w, 2.0, 1.0)

    g.skill.sp = float(g.skill.sp_cost)
    manual_trigger(w, g)

    bind = next((s for s in e.statuses if s.source_tag == _S2_BIND_TAG), None)
    assert bind is not None
    expected_expires = w.global_state.elapsed + _S2_BIND_DURATION
    assert abs(bind.expires_at - expected_expires) < 0.2


def test_s3_regression():
    op = make_glaucus(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Tidal Prison"
