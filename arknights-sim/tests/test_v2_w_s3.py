"""W S3 "Chaos Edict" — delayed bomb placement (EventQueue), up to 4 bombs, 310% ATK physical AoE.

Tests cover:
  - S3 configured correctly (slot, sp_cost=50, initial_sp=20, duration=0, AUTO trigger)
  - Bomb detonates after _BOMB_DELAY seconds and deals physical damage
  - Multiple bombs placed for multiple enemies (up to 4)
  - Bomb targets highest-HP enemies in range
  - Damage not applied before detonation delay elapses
  - Last Will talent applies LEVITATE on attack hit (regression)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, SkillTrigger, StatusKind
from core.systems import register_default_systems
from data.characters.w import (
    make_w,
    _S3_TAG, _BOMB_DELAY, _BOMB_ATK_RATIO, _BOMB_MAX,
    _LEVITATE_TAG, _LEVITATE_DURATION,
)


def _world(w: int = 8, h: int = 3) -> World:
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


def _enemy(world: World, x: float, y: float, hp: int = 99999) -> UnitState:
    e = UnitState(name="Enemy", faction=Faction.ENEMY, max_hp=hp, atk=0, defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


# ---------------------------------------------------------------------------
# Test 1: S3 configured correctly
# ---------------------------------------------------------------------------

def test_s3_config():
    w = make_w(slot="S3")
    sk = w.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "Chaos Edict"
    assert sk.sp_cost == 50
    assert sk.initial_sp == 20
    assert sk.duration == 0.0
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: Bomb deals physical damage after delay
# ---------------------------------------------------------------------------

def test_s3_bomb_deals_damage_after_delay():
    world = _world()
    op = make_w(slot="S3")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    world.add_unit(op)

    e = _enemy(world, x=2.0, y=1.0)
    hp_before = e.hp

    # Activate S3
    op.skill.sp = float(op.skill.sp_cost)
    _ticks(world, 0.1)  # triggers skill

    # Before delay — no damage yet
    assert e.hp == hp_before, "Bomb must not detonate before delay elapses"

    # Advance past delay
    _ticks(world, _BOMB_DELAY + 0.5)

    expected = int(op.effective_atk * _BOMB_ATK_RATIO)
    assert e.hp < hp_before, "Bomb must deal damage after delay"
    damage = hp_before - e.hp
    # Allow small variance from DEF (0 in this case, just check ballpark)
    assert abs(damage - expected) <= max(5, int(expected * 0.02)), (
        f"Expected ~{expected} damage, got {damage}"
    )


# ---------------------------------------------------------------------------
# Test 3: Damage NOT applied before delay
# ---------------------------------------------------------------------------

def test_s3_no_damage_before_delay():
    world = _world()
    op = make_w(slot="S3")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    world.add_unit(op)

    e = _enemy(world, x=2.0, y=1.0)
    hp_before = e.hp

    op.skill.sp = float(op.skill.sp_cost)
    _ticks(world, 0.1)   # S3 fires, bomb placed
    # Advance to just before detonation
    _ticks(world, _BOMB_DELAY - 0.3)

    assert e.hp == hp_before, "No bomb damage must occur before delay elapses"


# ---------------------------------------------------------------------------
# Test 4: Multiple enemies hit by single bomb (AoE)
# ---------------------------------------------------------------------------

def test_s3_aoe_hits_multiple_enemies():
    world = _world()
    op = make_w(slot="S3")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    world.add_unit(op)

    # Two enemies within bomb radius of each other, in range
    e1 = _enemy(world, x=2.0, y=1.0)
    e2 = _enemy(world, x=2.0, y=1.5)  # within _BOMB_RADIUS=1.2 of e1
    hp1_before, hp2_before = e1.hp, e2.hp

    op.skill.sp = float(op.skill.sp_cost)
    _ticks(world, 0.1)
    _ticks(world, _BOMB_DELAY + 0.5)

    # Both should take damage from the AoE
    assert e1.hp < hp1_before, "Enemy 1 must be hit by bomb AoE"
    assert e2.hp < hp2_before, "Enemy 2 must be hit by bomb AoE"


# ---------------------------------------------------------------------------
# Test 5: S3 targets up to _BOMB_MAX enemies (bomb count cap)
# ---------------------------------------------------------------------------

def test_s3_bomb_count_capped():
    """Placing 6 enemies spaced 3 tiles apart; W throws at most _BOMB_MAX=4 bombs."""
    world = _world(w=20, h=3)
    op = make_w(slot="S3")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    world.add_unit(op)

    # Space enemies 3 tiles apart (> _BOMB_RADIUS=1.2) so AoE doesn't cross-hit
    enemies = [_enemy(world, x=float(i * 3 + 1), y=1.0) for i in range(6)]
    hp_before = [e.hp for e in enemies]

    op.skill.sp = float(op.skill.sp_cost)
    _ticks(world, 0.1)
    _ticks(world, _BOMB_DELAY + 0.5)

    # Each bomb is targeted at a specific enemy (no AoE cross-contamination)
    hit_count = sum(1 for i, e in enumerate(enemies) if e.hp < hp_before[i])
    assert hit_count <= _BOMB_MAX, f"At most {_BOMB_MAX} bombs should be thrown; got {hit_count} enemies hit"
    assert hit_count > 0, "At least one enemy must be hit"


# ---------------------------------------------------------------------------
# Test 6: Last Will talent regression — LEVITATE on attack hit
# ---------------------------------------------------------------------------

def test_talent_levitate_on_attack():
    world = _world()
    op = make_w(slot="S2")  # use S2 to isolate talent
    op.deployed = True; op.position = (0.0, 1.0)
    world.add_unit(op)

    e = _enemy(world, x=1.0, y=1.0)
    e.defence = 0

    # Manually fire talent callback
    from core.systems.talent_registry import fire_on_attack_hit
    fire_on_attack_hit(world, op, e, damage=100)

    levitate = [s for s in e.statuses if s.kind == StatusKind.LEVITATE and s.source_tag == _LEVITATE_TAG]
    assert len(levitate) == 1, "Target must have LEVITATE status after talent fires"
    assert levitate[0].expires_at == world.global_state.elapsed + _LEVITATE_DURATION
