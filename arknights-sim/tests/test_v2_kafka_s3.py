"""Kafka S3 "Iron Judgment" — instant 500% ATK Arts AoE + 2.5s Stun to all in range.

Tests cover:
  - S3 config (slot, sp_cost, MANUAL, instant)
  - Deals arts damage to all in-range enemies
  - Damage amount is 500% ATK (arts, so RES applies)
  - Out-of-range enemy takes no damage
  - All hit enemies receive 2.5s STUN
  - Stun expires after 2.5s
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, StatusKind
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from core.state.unit_state import UnitState
from core.types import Faction
from data.characters.kafka import (
    make_kafka,
    _S3_TAG, _S3_ATK_MULTIPLIER, _S3_STUN_DURATION,
    EXECUTOR_RANGE,
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


def _enemy(world: World, x: float, y: float, res: float = 0.0, max_hp: int = 99999) -> UnitState:
    e = UnitState(name="Enemy", faction=Faction.ENEMY, max_hp=max_hp, atk=0,
                  defence=0, res=res)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


_KAFKA_POS = (0.0, 1.0)
# Executor range: (0,0) and (1,0) → enemies at dx=0,1
_ENEMY_IN_RANGE = (1.0, 1.0)    # dx=1, in range
_ENEMY_IN_RANGE_NEAR = (0.0, 1.0)  # dx=0 (same tile), in range
_ENEMY_OUT = (2.0, 1.0)         # dx=2, outside EXECUTOR_RANGE


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    k = make_kafka(slot="S3")
    assert k.skill is not None
    assert k.skill.slot == "S3"
    assert k.skill.name == "Iron Judgment"
    assert k.skill.sp_cost == 30
    assert k.skill.duration == 0.0, "S3 must be instant (duration=0)"
    from core.types import SkillTrigger
    assert k.skill.trigger == SkillTrigger.MANUAL
    assert k.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: Damages in-range enemies
# ---------------------------------------------------------------------------

def test_s3_damages_in_range_enemies():
    w = _world()
    k = make_kafka(slot="S3")
    k.deployed = True; k.position = _KAFKA_POS; k.atk_cd = 999.0
    w.add_unit(k)

    enemy1 = _enemy(w, *_ENEMY_IN_RANGE)
    enemy2 = _enemy(w, *_ENEMY_IN_RANGE_NEAR)

    k.skill.sp = float(k.skill.sp_cost)
    manual_trigger(w, k)

    assert enemy1.hp < enemy1.max_hp, "In-range enemy must take damage"
    assert enemy2.hp < enemy2.max_hp, "Same-tile enemy must take damage"


# ---------------------------------------------------------------------------
# Test 3: Damage amount = 500% ATK (arts)
# ---------------------------------------------------------------------------

def test_s3_damage_amount():
    w = _world()
    k = make_kafka(slot="S3")
    k.deployed = True; k.position = _KAFKA_POS; k.atk_cd = 999.0
    w.add_unit(k)

    enemy = _enemy(w, *_ENEMY_IN_RANGE, res=0.0)
    base_atk = k.effective_atk

    k.skill.sp = float(k.skill.sp_cost)
    manual_trigger(w, k)

    expected = int(base_atk * _S3_ATK_MULTIPLIER)
    taken = enemy.max_hp - enemy.hp
    assert abs(taken - expected) <= 2, (
        f"S3 damage must be {_S3_ATK_MULTIPLIER:.0%} ATK arts; expected {expected}, got {taken}"
    )


# ---------------------------------------------------------------------------
# Test 4: Out-of-range enemy takes no damage
# ---------------------------------------------------------------------------

def test_s3_no_damage_out_of_range():
    w = _world()
    k = make_kafka(slot="S3")
    k.deployed = True; k.position = _KAFKA_POS; k.atk_cd = 999.0
    w.add_unit(k)

    enemy = _enemy(w, *_ENEMY_OUT)
    k.skill.sp = float(k.skill.sp_cost)
    manual_trigger(w, k)

    assert enemy.hp == enemy.max_hp, "Out-of-range enemy must not take damage"


# ---------------------------------------------------------------------------
# Test 5: RES reduces S3 arts damage
# ---------------------------------------------------------------------------

def test_s3_res_reduces_damage():
    w = _world()
    k = make_kafka(slot="S3")
    k.deployed = True; k.position = _KAFKA_POS; k.atk_cd = 999.0
    w.add_unit(k)

    enemy_no_res = _enemy(w, *_ENEMY_IN_RANGE, res=0.0)
    base_atk = k.effective_atk

    k.skill.sp = float(k.skill.sp_cost)
    manual_trigger(w, k)
    damage_no_res = enemy_no_res.max_hp - enemy_no_res.hp

    # res is stored as 0-100 (percentage), so 50 = 50% RES
    w2 = _world()
    k2 = make_kafka(slot="S3")
    k2.deployed = True; k2.position = _KAFKA_POS; k2.atk_cd = 999.0
    w2.add_unit(k2)
    enemy_res50 = _enemy(w2, *_ENEMY_IN_RANGE, res=50.0)
    k2.skill.sp = float(k2.skill.sp_cost)
    manual_trigger(w2, k2)
    damage_res50 = enemy_res50.max_hp - enemy_res50.hp

    assert damage_res50 < damage_no_res, "50% RES must reduce S3 arts damage"
    assert abs(damage_res50 - damage_no_res * 0.5) <= 2, "Damage reduction must be ~50%"


# ---------------------------------------------------------------------------
# Test 6: All hit enemies receive STUN
# ---------------------------------------------------------------------------

def test_s3_stuns_in_range_enemies():
    w = _world()
    k = make_kafka(slot="S3")
    k.deployed = True; k.position = _KAFKA_POS; k.atk_cd = 999.0
    w.add_unit(k)

    enemy1 = _enemy(w, *_ENEMY_IN_RANGE)
    enemy2 = _enemy(w, *_ENEMY_IN_RANGE_NEAR)

    k.skill.sp = float(k.skill.sp_cost)
    manual_trigger(w, k)

    assert enemy1.has_status(StatusKind.STUN), "In-range enemy must be stunned"
    assert enemy2.has_status(StatusKind.STUN), "Same-tile enemy must be stunned"


# ---------------------------------------------------------------------------
# Test 7: Out-of-range enemy is NOT stunned
# ---------------------------------------------------------------------------

def test_s3_no_stun_out_of_range():
    w = _world()
    k = make_kafka(slot="S3")
    k.deployed = True; k.position = _KAFKA_POS; k.atk_cd = 999.0
    w.add_unit(k)

    enemy = _enemy(w, *_ENEMY_OUT)
    k.skill.sp = float(k.skill.sp_cost)
    manual_trigger(w, k)

    assert not enemy.has_status(StatusKind.STUN), "Out-of-range enemy must not be stunned"


# ---------------------------------------------------------------------------
# Test 8: Stun expires after 2.5s
# ---------------------------------------------------------------------------

def test_s3_stun_expires():
    w = _world()
    k = make_kafka(slot="S3")
    k.deployed = True; k.position = _KAFKA_POS; k.atk_cd = 999.0
    w.add_unit(k)

    enemy = _enemy(w, *_ENEMY_IN_RANGE)
    k.skill.sp = float(k.skill.sp_cost)
    manual_trigger(w, k)

    assert enemy.has_status(StatusKind.STUN), "Enemy must be stunned after S3"

    for _ in range(int(TICK_RATE * (_S3_STUN_DURATION + 0.5))):
        w.tick()

    assert not enemy.has_status(StatusKind.STUN), "Stun must expire after 2.5s"


# ---------------------------------------------------------------------------
# Test 9: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    k = make_kafka(slot="S2")
    assert k.skill is not None and k.skill.slot == "S2"
    assert k.skill.name == "Electrocute"
