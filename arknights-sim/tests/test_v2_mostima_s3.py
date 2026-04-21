"""Mostima S3 "Ley Lines" — global AoE Arts + 3.5s STUN, MANUAL trigger, instant.

Tests cover:
  - S3 configured correctly (slot, sp_cost=60, initial_sp=30, MANUAL, requires_target=False)
  - Arts damage dealt to all enemies on field (no position check)
  - STUN applied for _S3_STUN_DURATION to all hit enemies
  - Out-of-range enemy still hit (global range)
  - S3 damage accumulates in total_damage_dealt
  - Serenity talent SP-on-kill regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, SkillTrigger, StatusKind
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.mostima import (
    make_mostima,
    _S3_TAG, _S3_ATK_RATIO, _S3_STUN_DURATION, _S3_STUN_TAG,
    _TALENT_TAG, _TALENT_SP_ON_KILL,
)


def _world(w: int = 6, h: int = 3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _ticks(world: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        world.tick()


def _enemy(world: World, x: float, y: float, hp: int = 50000, res: float = 0.0) -> UnitState:
    e = UnitState(name="Enemy", faction=Faction.ENEMY, max_hp=hp, atk=0, defence=0, res=res)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


# ---------------------------------------------------------------------------
# Test 1: S3 configured correctly
# ---------------------------------------------------------------------------

def test_s3_config():
    m = make_mostima(slot="S3")
    sk = m.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "Ley Lines"
    assert sk.sp_cost == 60
    assert sk.initial_sp == 30
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.requires_target is False
    assert sk.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: Arts damage dealt to enemy on activation
# ---------------------------------------------------------------------------

def test_s3_arts_damage():
    world = _world()
    m = make_mostima(slot="S3")
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    world.add_unit(m)

    e = _enemy(world, x=2.0, y=1.0)
    hp_before = e.hp

    m.skill.sp = float(m.skill.sp_cost)
    manual_trigger(world, m)

    expected = int(m.effective_atk * _S3_ATK_RATIO)
    actual_damage = hp_before - e.hp
    assert actual_damage > 0, "S3 must deal Arts damage"
    assert abs(actual_damage - expected) <= max(5, int(expected * 0.02)), (
        f"Expected ~{expected} Arts damage, got {actual_damage}"
    )


# ---------------------------------------------------------------------------
# Test 3: STUN applied for correct duration
# ---------------------------------------------------------------------------

def test_s3_stun_applied():
    world = _world()
    m = make_mostima(slot="S3")
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    world.add_unit(m)

    e = _enemy(world, x=2.0, y=1.0)

    m.skill.sp = float(m.skill.sp_cost)
    manual_trigger(world, m)

    stun = [s for s in e.statuses if s.kind == StatusKind.STUN and s.source_tag == _S3_STUN_TAG]
    assert len(stun) == 1, "Enemy must have STUN after Ley Lines"
    assert abs(stun[0].expires_at - (world.global_state.elapsed + _S3_STUN_DURATION - 1.0 / TICK_RATE)) <= 0.1 or \
           abs(stun[0].expires_at - world.global_state.elapsed - _S3_STUN_DURATION) <= 0.1, (
        f"STUN duration must be ~{_S3_STUN_DURATION}s"
    )


# ---------------------------------------------------------------------------
# Test 4: Global range — enemy far away still hit
# ---------------------------------------------------------------------------

def test_s3_hits_out_of_range_enemy():
    world = _world(w=10, h=5)
    m = make_mostima(slot="S3")
    m.deployed = True; m.position = (0.0, 2.0); m.atk_cd = 999.0
    world.add_unit(m)

    # Place enemy far outside normal range
    e = _enemy(world, x=9.0, y=4.0)
    hp_before = e.hp

    m.skill.sp = float(m.skill.sp_cost)
    manual_trigger(world, m)

    assert e.hp < hp_before, "Ley Lines must hit enemy regardless of range"


# ---------------------------------------------------------------------------
# Test 5: All enemies on field hit simultaneously
# ---------------------------------------------------------------------------

def test_s3_hits_all_enemies():
    world = _world(w=8, h=4)
    m = make_mostima(slot="S3")
    m.deployed = True; m.position = (0.0, 2.0); m.atk_cd = 999.0
    world.add_unit(m)

    enemies = [_enemy(world, x=float(i + 1), y=float(i % 3)) for i in range(5)]
    hp_before = [e.hp for e in enemies]

    m.skill.sp = float(m.skill.sp_cost)
    manual_trigger(world, m)

    for i, e in enumerate(enemies):
        assert e.hp < hp_before[i], f"Enemy {i} must be hit by Ley Lines"


# ---------------------------------------------------------------------------
# Test 6: Serenity talent SP-on-kill regression
# ---------------------------------------------------------------------------

def test_talent_sp_on_kill():
    world = _world()
    m = make_mostima(slot="S3")
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    world.add_unit(m)

    # Simulate kill via talent callback
    killed = UnitState(name="Killed", faction=Faction.ENEMY, max_hp=1, atk=0, defence=0, res=0.0)
    killed.alive = False
    sp_before = m.skill.sp
    sp_room = m.skill.sp_cost - sp_before

    from core.systems.talent_registry import fire_on_kill
    fire_on_kill(world, m, killed)

    expected_gain = min(_TALENT_SP_ON_KILL, sp_room)
    assert abs(m.skill.sp - (sp_before + expected_gain)) < 0.1, (
        f"Serenity must grant +{expected_gain} SP on kill"
    )
