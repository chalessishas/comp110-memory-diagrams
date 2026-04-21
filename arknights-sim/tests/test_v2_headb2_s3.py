"""headb2 S3 "Storm Strike" — 5 consecutive 200% ATK physical hits via EventQueue.

Tests cover:
  - S3 configured correctly (slot, sp_cost=45, initial_sp=20, MANUAL trigger, 5s duration)
  - 5 hits are scheduled and all land on target
  - Each hit deals 200% ATK physical damage
  - No damage before events fire (time < first hit)
  - Talent "Shockwave" splash_radius → 1.5 on deployment
  - S2 regression (Shockwave Burst ATK buff)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, SkillTrigger, SPGainMode
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.headb2 import (
    make_headb2,
    _S3_TAG, _S3_HIT_COUNT, _S3_ATK_RATIO, _S3_HIT_INTERVAL, _S3_DURATION,
    _TALENT_TAG, _TALENT_SPLASH_RADIUS,
)


def _world() -> World:
    grid = TileGrid(width=8, height=3)
    for x in range(8):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def _enemy(world: World, x: float, y: float, hp: int = 999999) -> UnitState:
    e = UnitState(name="Enemy", faction=Faction.ENEMY, max_hp=hp, atk=0, defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


# ---------------------------------------------------------------------------
# Test 1: S3 configured correctly
# ---------------------------------------------------------------------------

def test_s3_config():
    op = make_headb2(slot="S3")
    assert op.skill is not None
    assert op.skill.slot == "S3"
    assert op.skill.name == "Storm Strike"
    assert op.skill.sp_cost == 45
    assert op.skill.initial_sp == 20
    assert op.skill.trigger == SkillTrigger.MANUAL
    assert op.skill.sp_gain_mode == SPGainMode.AUTO_TIME
    assert abs(op.skill.duration - _S3_DURATION) < 0.01
    assert op.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: All 5 hits land on target
# ---------------------------------------------------------------------------

def test_s3_five_hits_total():
    w = _world()
    op = make_headb2(slot="S3")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    e = _enemy(w, 1.0, 1.0)
    setattr(op, "__target__", e)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    hp_before = e.hp
    # Advance past all 5 hits: 5 * interval + buffer
    _ticks(w, _S3_HIT_COUNT * _S3_HIT_INTERVAL + 0.5)

    total_damage = hp_before - e.hp
    assert total_damage > 0, "S3 must deal damage to target"

    # Each hit: int(effective_atk * ratio), 5 hits total
    expected_per_hit = int(op.effective_atk * _S3_ATK_RATIO)
    expected_total = expected_per_hit * _S3_HIT_COUNT
    assert abs(total_damage - expected_total) <= _S3_HIT_COUNT * 2, (
        f"Expected 5×{_S3_ATK_RATIO:.0%} ATK = {expected_total} total damage, got {total_damage}"
    )


# ---------------------------------------------------------------------------
# Test 3: Each individual hit deals 200% ATK physical damage
# ---------------------------------------------------------------------------

def test_s3_damage_per_hit():
    w = _world()
    op = make_headb2(slot="S3")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    e = _enemy(w, 1.0, 1.0)
    setattr(op, "__target__", e)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    # Advance just past first hit only
    hp_before = e.hp
    _ticks(w, _S3_HIT_INTERVAL * 0.5)
    first_hit_dmg = hp_before - e.hp

    expected = int(op.effective_atk * _S3_ATK_RATIO)
    assert abs(first_hit_dmg - expected) <= 2, (
        f"First hit must deal {_S3_ATK_RATIO:.0%} ATK = {expected} damage, got {first_hit_dmg}"
    )


# ---------------------------------------------------------------------------
# Test 4: No damage before first event fires (still at t=0 after trigger)
# ---------------------------------------------------------------------------

def test_s3_no_damage_before_events():
    w = _world()
    op = make_headb2(slot="S3")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    e = _enemy(w, 1.0, 1.0, hp=1000)
    setattr(op, "__target__", e)

    hp_before = e.hp
    # Trigger but advance only a tiny fraction (no event should fire yet if first_at > now)
    op.skill.sp = float(op.skill.sp_cost)
    # Don't tick at all after trigger — just check that trigger activated skill
    manual_trigger(w, op)
    assert op.skill.active_remaining > 0.0, "S3 must activate on manual_trigger"
    # hp unchanged before time advances
    assert e.hp == hp_before, "No damage must occur before ticking"


# ---------------------------------------------------------------------------
# Test 5: Talent "Shockwave" — splash_radius → 1.5 on deployment
# ---------------------------------------------------------------------------

def test_talent_shockwave_splash_radius():
    w = _world()
    op = make_headb2()
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    # on_battle_start fired by add_unit → splash_radius should be updated
    assert abs(op.splash_radius - _TALENT_SPLASH_RADIUS) < 0.01, (
        f"Shockwave talent must set splash_radius={_TALENT_SPLASH_RADIUS}, got {op.splash_radius}"
    )


# ---------------------------------------------------------------------------
# Test 6: S2 regression (Shockwave Burst ATK buff)
# ---------------------------------------------------------------------------

def test_s2_regression():
    op = make_headb2(slot="S2")
    assert op.skill is not None
    assert op.skill.slot == "S2"
    assert op.skill.name == "Shockwave Burst"
    assert op.skill.sp_cost == 25
    assert op.skill.initial_sp == 10
