"""Texas Alter S3 "Sword Rain" — MANUAL, instant AoE Arts + 6s SILENCE.

Tests cover:
  - S3 configured correctly (slot, sp_cost=50, initial_sp=25, MANUAL)
  - Arts damage dealt to all in-range enemies on activation
  - SILENCE applied for _S3_SILENCE_DURATION to each hit enemy
  - Out-of-range enemies not hit
  - Multiple enemies all hit simultaneously
  - Surging Current talent regression (kill → atk_cd reset)
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
from data.characters.texas2 import (
    make_texas_alter,
    _S3_TAG, _S3_SILENCE_DURATION, _S3_SILENCE_TAG, _S3_DURATION,
    _TALENT_TAG,
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
    t = make_texas_alter(slot="S3")
    sk = t.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "Sword Rain"
    assert sk.sp_cost == 50
    assert sk.initial_sp == 25
    assert sk.duration == _S3_DURATION
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: Arts damage to in-range enemy
# ---------------------------------------------------------------------------

def test_s3_arts_damage():
    world = _world()
    t = make_texas_alter(slot="S3")
    t.deployed = True; t.position = (0.0, 1.0); t.atk_cd = 999.0
    world.add_unit(t)

    # In-range: (1, 0) is in EXECUTOR_RANGE tiles ((0,0),(1,0)) relative to position
    e = _enemy(world, x=1.0, y=1.0, res=0.0)
    hp_before = e.hp

    t.skill.sp = float(t.skill.sp_cost)
    manual_trigger(world, t)

    assert e.hp < hp_before, "S3 must deal Arts damage to in-range enemy"


# ---------------------------------------------------------------------------
# Test 3: SILENCE applied for correct duration
# ---------------------------------------------------------------------------

def test_s3_silence_applied():
    world = _world()
    t = make_texas_alter(slot="S3")
    t.deployed = True; t.position = (0.0, 1.0); t.atk_cd = 999.0
    world.add_unit(t)

    e = _enemy(world, x=1.0, y=1.0)

    t.skill.sp = float(t.skill.sp_cost)
    manual_trigger(world, t)

    silence = [s for s in e.statuses if s.kind == StatusKind.SILENCE and s.source_tag == _S3_SILENCE_TAG]
    assert len(silence) == 1, "In-range enemy must be SILENCED after Sword Rain"
    expected_expiry = world.global_state.elapsed + _S3_SILENCE_DURATION
    assert abs(silence[0].expires_at - expected_expiry) <= 0.1, (
        f"SILENCE must last {_S3_SILENCE_DURATION}s"
    )


# ---------------------------------------------------------------------------
# Test 4: Out-of-range enemy not hit
# ---------------------------------------------------------------------------

def test_s3_out_of_range_not_hit():
    world = _world(w=8, h=3)
    t = make_texas_alter(slot="S3")
    t.deployed = True; t.position = (0.0, 1.0); t.atk_cd = 999.0
    world.add_unit(t)

    # (3, 1) is outside (0,0),(1,0) relative range
    e_far = _enemy(world, x=3.0, y=1.0)
    hp_before = e_far.hp

    t.skill.sp = float(t.skill.sp_cost)
    manual_trigger(world, t)

    assert e_far.hp == hp_before, "Out-of-range enemy must not be hit by Sword Rain"


# ---------------------------------------------------------------------------
# Test 5: All in-range enemies hit simultaneously
# ---------------------------------------------------------------------------

def test_s3_hits_all_in_range():
    world = _world()
    t = make_texas_alter(slot="S3")
    t.deployed = True; t.position = (0.0, 1.0); t.atk_cd = 999.0
    world.add_unit(t)

    # Both tiles of EXECUTOR_RANGE: (0,0) and (1,0) relative → absolute (0,1) and (1,1)
    e1 = _enemy(world, x=0.0, y=1.0)
    e2 = _enemy(world, x=1.0, y=1.0)
    hp1, hp2 = e1.hp, e2.hp

    t.skill.sp = float(t.skill.sp_cost)
    manual_trigger(world, t)

    assert e1.hp < hp1, "Enemy 1 (tile 0,1) must be hit"
    assert e2.hp < hp2, "Enemy 2 (tile 1,1) must be hit"


# ---------------------------------------------------------------------------
# Test 6: Surging Current talent regression — kill resets atk_cd
# ---------------------------------------------------------------------------

def test_talent_kill_resets_atk_cd():
    world = _world()
    t = make_texas_alter(slot="S3")
    t.deployed = True; t.position = (0.0, 1.0)
    t.atk_cd = 5.0  # non-zero to verify reset
    world.add_unit(t)

    killed = UnitState(name="Killed", faction=Faction.ENEMY, max_hp=1, atk=0, defence=0, res=0.0)
    killed.alive = False

    from core.systems.talent_registry import fire_on_kill
    fire_on_kill(world, t, killed)

    assert t.atk_cd == 0.0, "Surging Current must reset atk_cd to 0 on kill"
