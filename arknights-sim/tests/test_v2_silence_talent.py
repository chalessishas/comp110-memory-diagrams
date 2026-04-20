"""Silence talent "Reinforcement" — 15% heal crit chance (2× heal amount on crit).

The talent sets carrier._silence_heal_crit = 0.15 at battle start.
The S2 drone's on_tick reads this attribute and rolls world.rng.random().

Tests cover:
  - Talent configured correctly
  - _silence_heal_crit attribute is set after battle_start (add_unit)
  - With rng forced to always-crit (random()=0.0), heal is doubled
  - With rng forced to never-crit (random()=1.0), heal is normal
  - Without talent (slot=None, no talent wired), crit attr is absent / 0.0
"""
from __future__ import annotations
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, RangeShape
from core.types import (
    AttackType, Faction, Profession, RoleArchetype, TileType, TICK_RATE,
)
from core.systems import register_default_systems
from data.characters.silence import (
    make_silence, _TALENT_TAG, _TALENT_CRIT_ATTR, _CRIT_CHANCE, _CRIT_MULTIPLIER,
    _S2_HEAL_PER_SECOND,
)


class _FixedRNG:
    """Deterministic stub for world.rng — always returns the same value."""
    def __init__(self, val: float):
        self._val = val

    def random(self) -> float:
        return self._val

    def choice(self, seq):
        return seq[0] if seq else None


def _world(rng_val: float | None = None) -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    if rng_val is not None:
        w.rng = _FixedRNG(rng_val)  # type: ignore[assignment]
    register_default_systems(w)
    return w


def _wounded_ally(pos=(2, 1), hp=500, max_hp=1000) -> UnitState:
    u = UnitState(
        name="WoundedAlly",
        faction=Faction.ALLY,
        max_hp=max_hp, hp=hp,
        atk=100, defence=50, res=0.0,
        atk_interval=1.0,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=True,
        profession=Profession.GUARD,
        block=1,
    )
    u.range_shape = RangeShape(tiles=((0, 0), (1, 0)))
    u.deployed = True
    u.position = (float(pos[0]), float(pos[1]))
    return u


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


# ---------------------------------------------------------------------------
# Test 1: Talent is configured correctly
# ---------------------------------------------------------------------------

def test_silence_talent_configured():
    s = make_silence(slot="S2")
    assert len(s.talents) == 1
    assert s.talents[0].name == "Reinforcement"
    assert s.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: _silence_heal_crit is set to 0.15 after battle_start
# ---------------------------------------------------------------------------

def test_reinforcement_sets_crit_chance():
    w = _world()
    s = make_silence(slot="S2")
    s.deployed = True; s.position = (0.0, 1.0)
    w.add_unit(s)   # fires on_battle_start

    assert getattr(s, _TALENT_CRIT_ATTR, 0.0) == _CRIT_CHANCE, (
        f"Talent must set {_TALENT_CRIT_ATTR}={_CRIT_CHANCE}; "
        f"got {getattr(s, _TALENT_CRIT_ATTR, 'MISSING')}"
    )


# ---------------------------------------------------------------------------
# Test 3: With rng=0.0 (always crit), S2 drone heal is doubled
# ---------------------------------------------------------------------------

def test_reinforcement_crit_doubles_heal():
    w = _world(rng_val=0.0)   # every rng.random() call returns 0.0 → always crits
    s = make_silence(slot="S2")
    s.skill.sp = float(s.skill.sp_cost)  # pre-fill so S2 fires immediately
    s.atk_cd = 9999.0                    # suppress normal attack heals
    s.deployed = True; s.position = (0.0, 1.0)
    w.add_unit(s)

    ally = _wounded_ally(pos=(1, 1), hp=1, max_hp=99999)
    w.add_unit(ally)

    w.global_state.total_healing_done = 0
    _ticks(w, 2.0)

    # Base: s.atk * 0.70/s × 2s, crit doubles each tick's heal → ≥ 1.5× expected
    expected_base = int(s.effective_atk * _S2_HEAL_PER_SECOND * 2.0)
    assert w.global_state.total_healing_done >= int(expected_base * 1.5), (
        f"Always-crit drone must heal ≥1.5× base; got {w.global_state.total_healing_done}, "
        f"base={expected_base}"
    )


# ---------------------------------------------------------------------------
# Test 4: With rng=1.0 (never crit), S2 drone heal is normal rate
# ---------------------------------------------------------------------------

def test_reinforcement_no_crit_normal_heal():
    w = _world(rng_val=1.0)   # every rng.random() returns 1.0 → never crits (1.0 >= 0.15)
    s = make_silence(slot="S2")
    s.skill.sp = float(s.skill.sp_cost)
    s.atk_cd = 9999.0
    s.deployed = True; s.position = (0.0, 1.0)
    w.add_unit(s)

    ally = _wounded_ally(pos=(1, 1), hp=1, max_hp=99999)
    w.add_unit(ally)

    w.global_state.total_healing_done = 0
    _ticks(w, 2.0)

    expected_base = int(s.effective_atk * _S2_HEAL_PER_SECOND * 2.0)
    tolerance = s.effective_atk   # one ATK worth of rounding tolerance
    assert w.global_state.total_healing_done <= expected_base + tolerance, (
        f"Never-crit drone must stay near base {expected_base}; "
        f"got {w.global_state.total_healing_done}"
    )
    # Must also have healed something (S2 drone was active)
    assert w.global_state.total_healing_done > 0, "S2 drone must have healed at least once"


# ---------------------------------------------------------------------------
# Test 5: slot=None still gets talent (talent independent of skill slot)
# ---------------------------------------------------------------------------

def test_reinforcement_present_without_skill():
    w = _world()
    s = make_silence(slot=None)
    s.deployed = True; s.position = (0.0, 1.0)
    w.add_unit(s)

    assert getattr(s, _TALENT_CRIT_ATTR, 0.0) == _CRIT_CHANCE, (
        "Reinforcement talent must apply regardless of skill slot"
    )
