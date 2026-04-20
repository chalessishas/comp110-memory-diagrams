"""Spuria — SPEC_DOLLKEEPER substitute body mechanic.

DOLLKEEPER pattern: on fatal damage, undying_charges prevents death;
  passive_talent_system fires on_tick in the same tick and transforms
  the unit into a substitute body (30% HP + self-DOT drain).

Key timing: combat_system (phase COMBAT) writes _undying_just_triggered=True,
  then passive_talent_system (phase SKILL) reads it within the same tick.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, StatusKind
from core.systems import register_default_systems
from data.characters.spuria import (
    make_spuria, _TALENT_TAG, _SUBSTITUTE_HP_RATIO,
    _SUBSTITUTE_DRAIN_DPS, _SUBSTITUTE_DURATION, _SUBSTITUTE_DOT_TAG,
    _S1_ATK_RATIO, _S1_DURATION,
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


def _slug(pos=(1, 1), atk=99999, hp=9999) -> UnitState:
    """High-ATK enemy to deal fatal damage in one hit."""
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp
    e.atk = atk; e.move_speed = 0.0; e.defence = 0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Talent registered and undying_charges = 1
# ---------------------------------------------------------------------------

def test_spuria_talent_and_charges():
    s = make_spuria()
    assert len(s.talents) == 1
    assert s.talents[0].behavior_tag == _TALENT_TAG
    assert s.undying_charges == 1, "Spuria must start with 1 undying charge"


# ---------------------------------------------------------------------------
# Test 2: Spuria survives fatal damage (undying_charges absorbs)
# ---------------------------------------------------------------------------

def test_spuria_survives_fatal_damage():
    w = _world()
    s = make_spuria(slot=None)
    s.deployed = True; s.position = (1.0, 1.0); s.hp = 1  # nearly dead
    s.undying_charges = 1
    w.add_unit(s)

    # Slug deals massive damage; Spuria's undying_charges should save her
    slug = _slug(pos=(1, 1), atk=999999)
    w.add_unit(slug)

    w.tick()

    assert s.alive, "Spuria must survive the first fatal hit via undying_charges"


# ---------------------------------------------------------------------------
# Test 3: Substitute body HP restored in same tick as fatal hit
# ---------------------------------------------------------------------------

def test_substitute_body_hp_restored():
    """In the same tick as fatal damage, talent transforms: hp = 30% max_hp."""
    w = _world()
    s = make_spuria(slot=None)
    s.deployed = True; s.position = (1.0, 1.0); s.hp = 1
    w.add_unit(s)

    slug = _slug(pos=(1, 1), atk=999999)
    w.add_unit(slug)

    w.tick()

    expected_hp = max(1, int(s.max_hp * _SUBSTITUTE_HP_RATIO))
    assert s.hp == expected_hp, (
        f"Substitute body must have {expected_hp} HP; got {s.hp}"
    )


# ---------------------------------------------------------------------------
# Test 4: Self-DOT applied after substitution
# ---------------------------------------------------------------------------

def test_substitute_body_drain_dot_applied():
    w = _world()
    s = make_spuria(slot=None)
    s.deployed = True; s.position = (1.0, 1.0); s.hp = 1
    w.add_unit(s)

    slug = _slug(pos=(1, 1), atk=999999)
    w.add_unit(slug)

    w.tick()  # fatal hit → substitution → DOT applied

    assert s.has_status(StatusKind.DOT), "Substitute body must have self-DOT drain"
    dot = next(st for st in s.statuses if st.kind == StatusKind.DOT)
    assert dot.source_tag == _SUBSTITUTE_DOT_TAG
    assert dot.params.get("dps") == _SUBSTITUTE_DRAIN_DPS


# ---------------------------------------------------------------------------
# Test 5: Substitute body HP drains over time
# ---------------------------------------------------------------------------

def test_substitute_body_drains_over_time():
    """DOT drains Spuria's HP each tick after substitution."""
    w = _world()
    s = make_spuria(slot=None)
    s.deployed = True; s.position = (1.0, 1.0); s.hp = 1
    w.add_unit(s)

    slug = _slug(pos=(1, 1), atk=999999)
    slug.atk_cd = 0.0
    w.add_unit(slug)

    w.tick()  # substitution activates
    assert s.alive

    # Disable slug from attacking further
    slug.atk_cd = 999.0
    hp_after_switch = s.hp

    w.tick()  # DOT drains

    expected_drain = max(1, int(_SUBSTITUTE_DRAIN_DPS * 0.1))  # DT = 0.1
    assert hp_after_switch - s.hp == expected_drain, (
        f"Expected DOT drain {expected_drain}/tick; got {hp_after_switch - s.hp}"
    )


# ---------------------------------------------------------------------------
# Test 6: Undying charge consumed — no second substitution
# ---------------------------------------------------------------------------

def test_second_fatal_hit_kills():
    """After the substitute body is exhausted, a second fatal hit kills Spuria."""
    w = _world()
    s = make_spuria(slot=None)
    s.deployed = True; s.position = (1.0, 1.0); s.hp = 1
    w.add_unit(s)

    slug = _slug(pos=(1, 1), atk=999999)
    w.add_unit(slug)

    w.tick()  # first fatal → substitute activated

    assert s.alive
    assert s.undying_charges == 0, "Charge must be consumed after substitution"

    # Drain substitute body HP completely, then check death
    s.hp = 1  # set to near-death manually
    slug.atk_cd = 0.0
    w.tick()  # second fatal hit with no charges left

    assert not s.alive, "Spuria must die on second fatal hit (no charges left)"


# ---------------------------------------------------------------------------
# Test 7: Normal damage does NOT trigger substitution
# ---------------------------------------------------------------------------

def test_non_fatal_damage_no_substitution():
    """Partial damage leaves Spuria alive without triggering the substitute."""
    w = _world()
    s = make_spuria(slot=None)
    s.deployed = True; s.position = (1.0, 1.0)
    s.hp = s.max_hp  # full HP
    w.add_unit(s)

    slug = _slug(pos=(1, 1), atk=100)  # weak — can't kill Spuria in one hit
    w.add_unit(slug)

    w.tick()

    assert s.alive
    assert s.undying_charges == 1, "Charge must NOT be consumed by non-fatal damage"
    assert not s.has_status(StatusKind.DOT), "No substitute DOT without substitution"


# ---------------------------------------------------------------------------
# Test 8: S1 ATK buff applied and removed correctly
# ---------------------------------------------------------------------------

def test_s1_atk_buff():
    w = _world()
    s = make_spuria()
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    w.add_unit(s)

    atk_base = s.effective_atk
    s.skill.sp = s.skill.sp_cost
    w.tick()

    assert s.skill.active_remaining > 0.0, "S1 must be active"
    assert s.effective_atk == int(atk_base * (1.0 + _S1_ATK_RATIO))

    for _ in range(int(TICK_RATE * (_S1_DURATION + 1))):
        w.tick()

    assert s.skill.active_remaining == 0.0, "S1 must have expired"
    assert s.effective_atk == atk_base, "ATK must revert after S1 ends"
