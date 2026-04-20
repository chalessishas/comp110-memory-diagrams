"""Nightmare S3 "Eternal Sleep" — instant 400% ATK Arts AoE + 4s SLEEP on all in range.

Tests cover:
  - S3 config (slot, sp_cost, MANUAL, instant)
  - Deals arts damage to in-range enemies
  - Damage amount = 400% ATK arts
  - Out-of-range enemy takes no damage
  - All hit enemies receive 4s SLEEP
  - SLEEP prevents movement/attack (can_act=False)
  - SLEEP expires after 4s
  - Out-of-range enemy not slept
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
from data.characters.nightmare import (
    make_nightmare,
    _S3_TAG, _S3_ATK_MULTIPLIER, _S3_SLEEP_DURATION,
    CASTER_RANGE,
)


def _world() -> World:
    grid = TileGrid(width=8, height=5)
    for x in range(8):
        for y in range(5):
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


_NM_POS = (0.0, 2.0)
# CASTER_RANGE: dx=0..3, dy=-1..1
_ENEMY_IN = (2.0, 2.0)     # dx=2, in range
_ENEMY_OUT = (4.0, 2.0)    # dx=4, outside


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    nm = make_nightmare(slot="S3")
    assert nm.skill is not None
    assert nm.skill.slot == "S3"
    assert nm.skill.name == "Eternal Sleep"
    assert nm.skill.sp_cost == 35
    assert nm.skill.duration == 0.0, "Must be instant"
    from core.types import SkillTrigger
    assert nm.skill.trigger == SkillTrigger.MANUAL
    assert nm.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: Damages in-range enemy
# ---------------------------------------------------------------------------

def test_s3_damages_in_range():
    w = _world()
    nm = make_nightmare(slot="S3")
    nm.deployed = True; nm.position = _NM_POS; nm.atk_cd = 999.0
    w.add_unit(nm)

    enemy = _enemy(w, *_ENEMY_IN)
    nm.skill.sp = float(nm.skill.sp_cost)
    manual_trigger(w, nm)

    assert enemy.hp < enemy.max_hp, "In-range enemy must take damage"


# ---------------------------------------------------------------------------
# Test 3: Damage = 400% ATK arts
# ---------------------------------------------------------------------------

def test_s3_damage_amount():
    w = _world()
    nm = make_nightmare(slot="S3")
    nm.deployed = True; nm.position = _NM_POS; nm.atk_cd = 999.0
    w.add_unit(nm)

    enemy = _enemy(w, *_ENEMY_IN, res=0.0)
    base_atk = nm.effective_atk

    nm.skill.sp = float(nm.skill.sp_cost)
    manual_trigger(w, nm)

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
    nm = make_nightmare(slot="S3")
    nm.deployed = True; nm.position = _NM_POS; nm.atk_cd = 999.0
    w.add_unit(nm)

    enemy = _enemy(w, *_ENEMY_OUT)
    nm.skill.sp = float(nm.skill.sp_cost)
    manual_trigger(w, nm)

    assert enemy.hp == enemy.max_hp, "Out-of-range enemy must not take damage"


# ---------------------------------------------------------------------------
# Test 5: In-range enemy receives SLEEP
# ---------------------------------------------------------------------------

def test_s3_sleeps_in_range_enemies():
    w = _world()
    nm = make_nightmare(slot="S3")
    nm.deployed = True; nm.position = _NM_POS; nm.atk_cd = 999.0
    w.add_unit(nm)

    enemy = _enemy(w, *_ENEMY_IN)
    nm.skill.sp = float(nm.skill.sp_cost)
    manual_trigger(w, nm)

    assert enemy.has_status(StatusKind.SLEEP), "In-range enemy must be put to sleep"


# ---------------------------------------------------------------------------
# Test 6: SLEEP prevents can_act
# ---------------------------------------------------------------------------

def test_s3_sleep_prevents_can_act():
    w = _world()
    nm = make_nightmare(slot="S3")
    nm.deployed = True; nm.position = _NM_POS; nm.atk_cd = 999.0
    w.add_unit(nm)

    enemy = _enemy(w, *_ENEMY_IN)
    nm.skill.sp = float(nm.skill.sp_cost)
    manual_trigger(w, nm)

    assert not enemy.can_act(), "SLEEP must prevent enemy can_act()"


# ---------------------------------------------------------------------------
# Test 7: Out-of-range enemy not slept
# ---------------------------------------------------------------------------

def test_s3_no_sleep_out_of_range():
    w = _world()
    nm = make_nightmare(slot="S3")
    nm.deployed = True; nm.position = _NM_POS; nm.atk_cd = 999.0
    w.add_unit(nm)

    enemy = _enemy(w, *_ENEMY_OUT)
    nm.skill.sp = float(nm.skill.sp_cost)
    manual_trigger(w, nm)

    assert not enemy.has_status(StatusKind.SLEEP), "Out-of-range enemy must not sleep"


# ---------------------------------------------------------------------------
# Test 8: SLEEP expires after 4s
# ---------------------------------------------------------------------------

def test_s3_sleep_expires():
    w = _world()
    nm = make_nightmare(slot="S3")
    nm.deployed = True; nm.position = _NM_POS; nm.atk_cd = 999.0
    w.add_unit(nm)

    enemy = _enemy(w, *_ENEMY_IN)
    nm.skill.sp = float(nm.skill.sp_cost)
    manual_trigger(w, nm)

    assert enemy.has_status(StatusKind.SLEEP), "Enemy must be asleep after S3"

    for _ in range(int(TICK_RATE * (_S3_SLEEP_DURATION + 0.5))):
        w.tick()

    assert not enemy.has_status(StatusKind.SLEEP), f"SLEEP must expire after {_S3_SLEEP_DURATION}s"


# ---------------------------------------------------------------------------
# Test 9: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    nm = make_nightmare(slot="S2")
    assert nm.skill is not None and nm.skill.slot == "S2"
    assert nm.skill.name == "Darkening"
