"""Archetto S3 "Tempest" — ATK+150%, all attacks gain 1-tile AoE splash for 25s.

Tests cover:
  - S3 config
  - ATK +150% buff applied
  - splash_radius set to 1.0 during S3
  - Adjacent enemy takes splash damage when primary is hit during S3
  - splash_radius and ATK buff cleared on end
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, Faction
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from core.state.unit_state import UnitState
from data.characters.archetto import (
    make_archetto,
    _S3_TAG, _S3_ATK_RATIO, _S3_SPLASH_RADIUS, _S3_DURATION, _S3_ATK_BUFF_TAG,
)
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=8, height=5)
    for x in range(8):
        for y in range(5):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _enemy(world, x, y, name="Enemy"):
    e = UnitState(name=name, faction=Faction.ENEMY, max_hp=99999, atk=0, defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


def _ticks(w, seconds):
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


_ARCHETTO_POS = (0.0, 2.0)


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    a = make_archetto(slot="S3")
    assert a.skill is not None and a.skill.slot == "S3"
    assert a.skill.name == "Tempest"
    assert a.skill.sp_cost == 40
    from core.types import SkillTrigger
    assert a.skill.trigger == SkillTrigger.MANUAL
    assert a.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK +150% applied
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    a = make_archetto(slot="S3")
    a.deployed = True; a.position = _ARCHETTO_POS; a.atk_cd = 999.0
    w.add_unit(a)
    _enemy(w, 2.0, 2.0)

    base_atk = a.effective_atk
    a.skill.sp = float(a.skill.sp_cost)
    manual_trigger(w, a)

    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(a.effective_atk - expected) <= 2, (
        f"S3 ATK must be ×{1 + _S3_ATK_RATIO}; expected {expected}, got {a.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: splash_radius = 1.0 during S3
# ---------------------------------------------------------------------------

def test_s3_sets_splash_radius():
    w = _world()
    a = make_archetto(slot="S3")
    a.deployed = True; a.position = _ARCHETTO_POS; a.atk_cd = 999.0
    w.add_unit(a)
    _enemy(w, 2.0, 2.0)

    assert a.splash_radius == 0.0, "Archetto must have no splash before S3"
    a.skill.sp = float(a.skill.sp_cost)
    manual_trigger(w, a)

    assert a.splash_radius == _S3_SPLASH_RADIUS, f"S3 must set splash_radius to {_S3_SPLASH_RADIUS}"


# ---------------------------------------------------------------------------
# Test 4: Adjacent enemy takes splash damage during S3
# ---------------------------------------------------------------------------

def test_s3_splash_hits_adjacent_enemy():
    w = _world()
    a = make_archetto(slot="S3")
    a.deployed = True; a.position = _ARCHETTO_POS
    w.add_unit(a)

    primary = _enemy(w, 2.0, 2.0, "Primary")
    adjacent = _enemy(w, 2.0, 3.0, "Adjacent")  # 1 tile from primary

    a.skill.sp = float(a.skill.sp_cost)
    manual_trigger(w, a)

    # Force an attack
    a.atk_cd = 0.0
    for _ in range(5):
        w.tick()

    assert primary.hp < primary.max_hp, "Primary enemy must take damage"
    assert adjacent.hp < adjacent.max_hp, "Adjacent enemy must take splash damage during S3"


# ---------------------------------------------------------------------------
# Test 5: S3 buffs cleared on end
# ---------------------------------------------------------------------------

def test_s3_cleared_on_end():
    w = _world()
    a = make_archetto(slot="S3")
    a.deployed = True; a.position = _ARCHETTO_POS; a.atk_cd = 999.0
    w.add_unit(a)
    _enemy(w, 2.0, 2.0)

    base_atk = a.effective_atk
    a.skill.sp = float(a.skill.sp_cost)
    manual_trigger(w, a)
    _ticks(w, _S3_DURATION + 1)

    assert a.skill.active_remaining == 0.0
    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in a.buffs), "ATK buff must clear"
    assert a.splash_radius == 0.0, "splash_radius must revert to 0 after S3"
    assert abs(a.effective_atk - base_atk) <= 2


# ---------------------------------------------------------------------------
# Test 6: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    a = make_archetto(slot="S2")
    assert a.skill is not None and a.skill.slot == "S2"
    assert a.skill.name == "Tactical Positioning"
