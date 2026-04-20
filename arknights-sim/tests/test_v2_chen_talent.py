"""Ch'en talent "Swordsman" — first kill spawns "Heartless Act" sword summon.

The talent uses on_kill hook. Only the first kill in a deployment triggers the spawn.
Subsequent kills do NOT spawn additional swords.

Tests cover:
  - Talent configured correctly
  - No Heartless Act on field before first kill
  - Heartless Act spawns after Ch'en's first kill
  - Spawned unit is Faction.ALLY with correct stats
  - Second kill does NOT spawn a second sword (one per deployment only)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, RangeShape
from core.types import (
    AttackType, Faction, Profession, RoleArchetype, TileType, TICK_RATE,
)
from core.systems import register_default_systems
from data.characters.chen import (
    make_chen, _TALENT_TAG, _SWORD_NAME, _SWORD_SPAWNED_ATTR,
    _SWORD_HP, _SWORD_ATK, _SWORD_DEF,
)
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=8, height=3)
    for x in range(8):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _weak_enemy(pos=(1, 0)) -> UnitState:
    """1 HP enemy that Ch'en can kill in one hit."""
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 10)
    e.max_hp = 1; e.hp = 1; e.atk = 0
    e.defence = 0; e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def _count_swords(w: World) -> int:
    return sum(1 for u in w.units if u.name == _SWORD_NAME and u.alive and u.faction == Faction.ALLY)


# ---------------------------------------------------------------------------
# Test 1: Talent configured correctly
# ---------------------------------------------------------------------------

def test_chen_talent_configured():
    c = make_chen(slot="S2")
    assert len(c.talents) == 1
    assert c.talents[0].name == "Swordsman"
    assert c.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: No Heartless Act before any kill
# ---------------------------------------------------------------------------

def test_no_sword_before_kill():
    w = _world()
    c = make_chen(slot=None)
    c.deployed = True; c.position = (0.0, 1.0)
    c.atk_cd = 9999.0   # prevent attacks
    w.add_unit(c)

    _ticks(w, 0.5)

    assert _count_swords(w) == 0, "No Heartless Act before any kill"
    assert not getattr(c, _SWORD_SPAWNED_ATTR, False), "_chen_sword_spawned must be False before kill"


# ---------------------------------------------------------------------------
# Test 3: Heartless Act spawns after first kill
# ---------------------------------------------------------------------------

def test_sword_spawns_after_first_kill():
    w = _world()
    c = make_chen(slot=None)
    c.deployed = True; c.position = (0.0, 1.0)
    c.atk_cd = 0.0
    w.add_unit(c)

    enemy = _weak_enemy(pos=(1, 1))
    w.add_unit(enemy)

    _ticks(w, 0.5)   # Ch'en attacks → kills 1 HP enemy

    assert _count_swords(w) == 1, (
        f"Heartless Act must appear after first kill; found {_count_swords(w)}"
    )
    sword = next(u for u in w.units if u.name == _SWORD_NAME)
    assert sword.faction == Faction.ALLY
    assert sword.hp == _SWORD_HP
    assert sword.atk == _SWORD_ATK
    assert sword.defence == _SWORD_DEF


# ---------------------------------------------------------------------------
# Test 4: Spawned sword is correct ally unit
# ---------------------------------------------------------------------------

def test_sword_is_guard_melee():
    w = _world()
    c = make_chen(slot=None)
    c.deployed = True; c.position = (0.0, 1.0)
    c.atk_cd = 0.0
    w.add_unit(c)
    w.add_unit(_weak_enemy(pos=(1, 1)))

    _ticks(w, 0.5)

    sword = next((u for u in w.units if u.name == _SWORD_NAME), None)
    assert sword is not None, "Sword must exist"
    assert sword.profession == Profession.GUARD
    assert sword.attack_range_melee is True
    assert sword.block == 2


# ---------------------------------------------------------------------------
# Test 5: Second kill does NOT spawn a second sword
# ---------------------------------------------------------------------------

def test_second_kill_no_extra_sword():
    w = _world()
    c = make_chen(slot=None)
    c.deployed = True; c.position = (0.0, 1.0)
    c.atk_cd = 0.0
    w.add_unit(c)

    e1 = _weak_enemy(pos=(1, 1))
    e2 = _weak_enemy(pos=(1, 0))
    w.add_unit(e1)
    w.add_unit(e2)

    _ticks(w, 1.5)   # enough ticks for multiple kills

    assert _count_swords(w) == 1, (
        f"Only one Heartless Act must ever spawn; found {_count_swords(w)}"
    )
    assert getattr(c, _SWORD_SPAWNED_ATTR, False), "Flag must be set after first kill"
