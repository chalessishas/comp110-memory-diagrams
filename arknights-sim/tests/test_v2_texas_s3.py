"""Texas S3 "Texas Rhapsody" — instant 350% ATK Arts AoE + 2s STUN + 3 DP.

Tests cover:
  - S3 configured correctly (slot, sp_cost=30, MANUAL, instant)
  - Deals arts damage to all in-range enemies
  - Out-of-range enemy takes no damage
  - Enemies receive 2s STUN
  - DP is refunded by 3 on activation
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, StatusKind, Faction
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.texas import (
    make_texas,
    _S3_TAG, _S3_ATK_MULTIPLIER, _S3_STUN_DURATION, _S3_DP_GAIN,
    PIONEER_RANGE,
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


def _enemy(world: World, x: float, y: float, res: float = 0.0) -> UnitState:
    e = UnitState(name="Enemy", faction=Faction.ENEMY, max_hp=99999, atk=0,
                  defence=0, res=res)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


_TEXAS_POS = (0.0, 1.0)
_ENEMY_IN = (1.0, 1.0)    # dx=1 — in PIONEER_RANGE
_ENEMY_OUT = (2.0, 1.0)   # dx=2 — outside PIONEER_RANGE


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    t = make_texas(slot="S3")
    assert t.skill is not None
    assert t.skill.slot == "S3"
    assert t.skill.name == "Texas Rhapsody"
    assert t.skill.sp_cost == 30
    assert t.skill.initial_sp == 15
    assert t.skill.duration == 0.0, "S3 must be instant"
    from core.types import SkillTrigger
    assert t.skill.trigger == SkillTrigger.MANUAL
    assert t.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: Deals arts damage to in-range enemies
# ---------------------------------------------------------------------------

def test_s3_damages_in_range():
    w = _world()
    t = make_texas(slot="S3")
    t.deployed = True; t.position = _TEXAS_POS; t.atk_cd = 999.0
    w.add_unit(t)
    enemy = _enemy(w, *_ENEMY_IN)

    t.skill.sp = float(t.skill.sp_cost)
    manual_trigger(w, t)

    assert enemy.hp < enemy.max_hp, "In-range enemy must take damage"
    expected = int(t.effective_atk * _S3_ATK_MULTIPLIER)
    damage = enemy.max_hp - enemy.hp
    assert abs(damage - expected) <= 2, f"Expected {expected} dmg, got {damage}"


# ---------------------------------------------------------------------------
# Test 3: Out-of-range enemy takes no damage
# ---------------------------------------------------------------------------

def test_s3_no_damage_out_of_range():
    w = _world()
    t = make_texas(slot="S3")
    t.deployed = True; t.position = _TEXAS_POS; t.atk_cd = 999.0
    w.add_unit(t)
    enemy_out = _enemy(w, *_ENEMY_OUT)

    t.skill.sp = float(t.skill.sp_cost)
    manual_trigger(w, t)

    assert enemy_out.hp == enemy_out.max_hp, "Out-of-range enemy must not take damage"


# ---------------------------------------------------------------------------
# Test 4: In-range enemies receive STUN
# ---------------------------------------------------------------------------

def test_s3_stun_applied():
    w = _world()
    t = make_texas(slot="S3")
    t.deployed = True; t.position = _TEXAS_POS; t.atk_cd = 999.0
    w.add_unit(t)
    enemy = _enemy(w, *_ENEMY_IN)

    t.skill.sp = float(t.skill.sp_cost)
    manual_trigger(w, t)

    stun = next((s for s in enemy.statuses if s.kind == StatusKind.STUN), None)
    assert stun is not None, "In-range enemy must be STUNned"
    assert abs(stun.expires_at - (w.global_state.elapsed + _S3_STUN_DURATION)) <= 0.1


# ---------------------------------------------------------------------------
# Test 5: DP refunded by 3
# ---------------------------------------------------------------------------

def test_s3_dp_refund():
    w = _world()
    t = make_texas(slot="S3")
    t.deployed = True; t.position = _TEXAS_POS; t.atk_cd = 999.0
    w.add_unit(t)
    _enemy(w, *_ENEMY_IN)

    dp_before = w.global_state.dp
    t.skill.sp = float(t.skill.sp_cost)
    manual_trigger(w, t)
    dp_after = w.global_state.dp

    assert abs((dp_after - dp_before) - _S3_DP_GAIN) <= 0.1, (
        f"S3 must refund {_S3_DP_GAIN} DP; got {dp_after - dp_before:.2f}"
    )


# ---------------------------------------------------------------------------
# Test 6: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    t = make_texas(slot="S2")
    assert t.skill is not None and t.skill.slot == "S2"
    assert t.skill.name == "Sword Rain"
    assert t.skill.sp_cost == 18
