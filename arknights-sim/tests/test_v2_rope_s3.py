"""Tests for Rope S3 "Binding Tempest" — AoE Arts 250%+BIND 2.5s+pull 4 tiles."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import Faction, TileType, TICK_RATE, SkillTrigger, StatusKind
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.rope import make_rope, _S3_ATK_MULT, _S3_BIND_DURATION, _S3_PULL_DIST
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=10, height=3)
    for x in range(10):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def _enemy(name: str, x: float = 1.0, y: float = 0.0) -> UnitState:
    e = UnitState(
        name=name, faction=Faction.ENEMY,
        max_hp=3000, atk=0, defence=0, res=0.0,
        atk_interval=1.0, attack_range_melee=True,
    )
    e.position = (x, y)
    return e


def test_s3_config():
    op = make_rope(slot="S3")
    assert op.skill.slot == "S3"
    assert op.skill.sp_cost == 40
    assert op.skill.initial_sp == 15
    assert op.skill.duration == 0.0   # instant
    assert op.skill.trigger == SkillTrigger.MANUAL


def test_s3_damages_multiple_enemies():
    w = _world()
    op = make_rope(slot="S3")
    op.deployed = True
    op.position = (0.0, 0.0)
    op.atk_cd = 999.0
    w.add_unit(op)

    e1 = _enemy("e1", x=1.0)
    e2 = _enemy("e2", x=2.0)
    w.add_unit(e1)
    w.add_unit(e2)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert e1.hp < e1.max_hp
    assert e2.hp < e2.max_hp


def test_s3_deals_arts_damage():
    w = _world()
    op = make_rope(slot="S3")
    op.deployed = True
    op.position = (0.0, 0.0)
    op.atk_cd = 999.0
    w.add_unit(op)

    # High RES enemy takes less damage
    e_tank = UnitState(
        name="tank", faction=Faction.ENEMY,
        max_hp=5000, atk=0, defence=0, res=0.80,
        atk_interval=1.0, attack_range_melee=True,
    )
    e_tank.position = (1.0, 0.0)
    e_weak = _enemy("weak", x=2.0)
    w.add_unit(e_tank)
    w.add_unit(e_weak)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert (e_tank.max_hp - e_tank.hp) < (e_weak.max_hp - e_weak.hp)


def test_s3_applies_bind():
    w = _world()
    op = make_rope(slot="S3")
    op.deployed = True
    op.position = (0.0, 0.0)
    op.atk_cd = 999.0
    w.add_unit(op)

    e = _enemy("e", x=1.0)
    w.add_unit(e)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    bind_statuses = [s for s in e.statuses if s.kind == StatusKind.BIND]
    assert len(bind_statuses) == 1
    # expires_at should be roughly elapsed + BIND_DURATION
    assert bind_statuses[0].expires_at >= w.global_state.elapsed + _S3_BIND_DURATION - 0.1


def test_s3_pulls_enemy():
    w = _world()
    op = make_rope(slot="S3")
    op.deployed = True
    op.position = (0.0, 0.0)
    op.atk_cd = 999.0
    w.add_unit(op)

    # Use a slug with enough HP to survive the hit so pull can apply
    slug = make_originium_slug(path=[(x, 0) for x in range(10)])
    slug.deployed = True
    slug.path_progress = 5.0
    slug.move_speed = 0.0
    slug.max_hp = 50000
    slug.hp = 50000
    w.add_unit(slug)

    progress_before = slug.path_progress
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert slug.path_progress < progress_before


def test_s3_s2_regression():
    op = make_rope(slot="S2")
    assert op.skill.slot == "S2"
    assert op.skill.sp_cost == 25
    assert op.skill.duration == 0.0
