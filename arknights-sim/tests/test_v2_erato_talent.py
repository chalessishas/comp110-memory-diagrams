"""Erato talent "Song of Dreams" — 50% DEF ignore on sleeping targets, don't wake.

Tests cover:
  - Talent configured correctly (Song of Dreams name + tag)
  - No crit_chance set (crit_chance stays 0.0 after deployment)
  - No DEF-ignore bonus when target is NOT sleeping
  - DEF-ignore bonus (50% of DEF) when target IS sleeping
  - Target stays asleep after Erato's hit (don't wake)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import StatusEffect
from core.types import TileType, TICK_RATE, StatusKind
from core.systems import register_default_systems
from core.systems.talent_registry import fire_on_pre_attack_hit, fire_on_attack_hit
from data.characters.erato import (
    make_erato, _TALENT_TAG, _DEF_IGNORE_RATIO,
)
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def _slug() -> object:
    return make_originium_slug(path=[(2, 1)] * 20)


# ---------------------------------------------------------------------------
# Test 1: Talent configured correctly
# ---------------------------------------------------------------------------

def test_erato_talent_configured():
    e = make_erato(slot="S1")
    assert len(e.talents) == 1
    assert e.talents[0].name == "Song of Dreams"
    assert e.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: crit_chance stays 0.0 after deployment
# ---------------------------------------------------------------------------

def test_erato_no_crit_chance():
    w = _world()
    e = make_erato(slot="S1")
    e.deployed = True; e.position = (0.0, 1.0)
    w.add_unit(e)
    assert e.crit_chance == 0.0, (
        f"Song of Dreams must not set crit_chance; got {e.crit_chance}"
    )


# ---------------------------------------------------------------------------
# Test 3: No DEF-ignore bonus when target is NOT sleeping
# ---------------------------------------------------------------------------

def test_song_no_bonus_when_not_sleeping():
    w = _world()
    e = make_erato(slot="S1")
    e.deployed = True; e.position = (0.0, 1.0)
    w.add_unit(e)

    enemy = _slug()
    enemy.deployed = True; enemy.position = (2.0, 1.0); enemy.move_speed = 0.0
    w.add_unit(enemy)

    assert not any(s.kind == StatusKind.SLEEP for s in enemy.statuses)

    dmg_before = w.global_state.total_damage_dealt
    fire_on_pre_attack_hit(w, e, enemy)
    phys = enemy.take_physical(e.effective_atk)
    w.global_state.total_damage_dealt += phys
    fire_on_attack_hit(w, e, enemy, phys)
    dmg_after = w.global_state.total_damage_dealt

    bonus_dealt = dmg_after - dmg_before - phys
    assert bonus_dealt == 0, f"No DEF-ignore bonus expected when not sleeping; got {bonus_dealt}"


# ---------------------------------------------------------------------------
# Test 4: DEF-ignore bonus (50% of DEF) when target IS sleeping
# ---------------------------------------------------------------------------

def test_song_def_ignore_when_sleeping():
    w = _world()
    e = make_erato(slot="S1")
    e.deployed = True; e.position = (0.0, 1.0)
    w.add_unit(e)

    enemy = _slug()
    enemy.deployed = True; enemy.position = (2.0, 1.0); enemy.move_speed = 0.0
    w.add_unit(enemy)

    # Apply SLEEP to enemy
    enemy.statuses.append(StatusEffect(
        kind=StatusKind.SLEEP,
        source_tag="test_sleep",
        expires_at=w.global_state.elapsed + 10.0,
    ))
    enemy_def = enemy.effective_def

    dmg_before = w.global_state.total_damage_dealt
    fire_on_pre_attack_hit(w, e, enemy)
    phys = enemy.take_physical(e.effective_atk)
    w.global_state.total_damage_dealt += phys
    fire_on_attack_hit(w, e, enemy, phys)
    dmg_after = w.global_state.total_damage_dealt

    bonus_dealt = dmg_after - dmg_before - phys
    expected_bonus = int(enemy_def * _DEF_IGNORE_RATIO)
    assert abs(bonus_dealt - expected_bonus) <= 1, (
        f"DEF-ignore bonus must be ≈{expected_bonus}; got {bonus_dealt}"
    )


# ---------------------------------------------------------------------------
# Test 5: Target stays asleep after Erato's hit (don't wake)
# ---------------------------------------------------------------------------

def test_song_target_stays_asleep():
    w = _world()
    e = make_erato(slot="S1")
    e.deployed = True; e.position = (0.0, 1.0)
    w.add_unit(e)

    enemy = _slug()
    enemy.deployed = True; enemy.position = (2.0, 1.0); enemy.move_speed = 0.0
    w.add_unit(enemy)

    enemy.statuses.append(StatusEffect(
        kind=StatusKind.SLEEP,
        source_tag="test_sleep",
        expires_at=w.global_state.elapsed + 10.0,
    ))

    fire_on_pre_attack_hit(w, e, enemy)
    phys = enemy.take_physical(e.effective_atk)
    fire_on_attack_hit(w, e, enemy, phys)

    still_asleep = any(s.kind == StatusKind.SLEEP for s in enemy.statuses)
    assert still_asleep, "Song of Dreams must keep target asleep after hit"
