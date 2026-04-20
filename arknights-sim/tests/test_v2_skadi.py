"""Skadi — Predator kill-heal talent + S2 Surge ATK buff."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, AttackType
from core.systems import register_default_systems
from data.characters.skadi import (
    make_skadi, _TALENT_TAG, _TALENT_HEAL_RATIO,
    _S2_ATK_RATIO, _S2_DURATION,
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


def _slug(pos=(1, 1), hp=100, atk=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp
    e.hp = hp
    e.atk = atk
    e.move_speed = 0.0
    e.deployed = True
    e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Talent registered correctly
# ---------------------------------------------------------------------------

def test_skadi_talent_registered():
    skadi = make_skadi()
    assert len(skadi.talents) == 1
    assert skadi.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: Predator heals Skadi when she kills an enemy
# ---------------------------------------------------------------------------

def test_predator_heals_on_kill():
    """When Skadi kills an enemy, she recovers 15% of max HP."""
    w = _world()
    skadi = make_skadi()
    skadi.deployed = True
    skadi.position = (0.0, 1.0)
    skadi.atk_cd = 0.0        # ready to attack immediately
    skadi.skill = None        # no skill to simplify
    w.add_unit(skadi)

    # Injure Skadi first so the heal is detectable
    skadi.hp = int(skadi.max_hp * 0.50)
    hp_before = skadi.hp

    # Weak slug — Skadi will kill it in one hit
    slug = _slug(pos=(1, 1), hp=1, atk=0)
    w.add_unit(slug)

    # Tick until slug is dead (should be first tick)
    for _ in range(10):
        w.tick()
        if not slug.alive:
            break

    assert not slug.alive, "Slug must die for Predator to trigger"
    assert skadi.hp > hp_before, "Predator must heal Skadi after kill"

    expected_heal = int(skadi.max_hp * _TALENT_HEAL_RATIO)
    assert skadi.hp == min(skadi.max_hp, hp_before + expected_heal), (
        f"Heal should be exactly {expected_heal} HP"
    )


# ---------------------------------------------------------------------------
# Test 3: Predator does not overheal above max HP
# ---------------------------------------------------------------------------

def test_predator_no_overheal():
    """Predator heal is capped at max HP."""
    w = _world()
    skadi = make_skadi()
    skadi.deployed = True
    skadi.position = (0.0, 1.0)
    skadi.atk_cd = 0.0
    skadi.skill = None
    w.add_unit(skadi)

    # Skadi nearly full HP — heal should not push above max
    skadi.hp = skadi.max_hp - 1

    slug = _slug(pos=(1, 1), hp=1, atk=0)
    w.add_unit(slug)

    for _ in range(10):
        w.tick()
        if not slug.alive:
            break

    assert not slug.alive, "Slug must die"
    assert skadi.hp <= skadi.max_hp, "HP must never exceed max_hp"


# ---------------------------------------------------------------------------
# Test 4: Predator does NOT fire when Skadi does not land the kill
# ---------------------------------------------------------------------------

def test_predator_no_heal_without_kill():
    """No heal when Skadi attacks but doesn't kill."""
    w = _world()
    skadi = make_skadi()
    skadi.deployed = True
    skadi.position = (0.0, 1.0)
    skadi.atk_cd = 0.0
    skadi.skill = None
    w.add_unit(skadi)

    skadi.hp = int(skadi.max_hp * 0.50)
    hp_before = skadi.hp

    # Tanky slug — will survive many hits
    slug = _slug(pos=(1, 1), hp=9999999, atk=0)
    w.add_unit(slug)

    # Run 5 ticks — Skadi attacks but never kills
    for _ in range(5):
        w.tick()

    assert slug.alive, "Slug should still be alive"
    assert skadi.hp == hp_before, "No heal without a kill"


# ---------------------------------------------------------------------------
# Test 5: S2 Surge activates and applies ATK buff
# ---------------------------------------------------------------------------

def test_skadi_s2_atk_buff():
    """S2 fires: ATK increases by +130%."""
    w = _world()
    skadi = make_skadi()
    skadi.deployed = True
    skadi.position = (0.0, 1.0)
    skadi.atk_cd = 999.0
    w.add_unit(skadi)

    slug = _slug(pos=(1, 1), hp=99999, atk=0)
    w.add_unit(slug)

    atk_base = skadi.effective_atk
    skadi.skill.sp = skadi.skill.sp_cost
    w.tick()  # S2 fires

    assert skadi.skill.active_remaining > 0.0, "S2 must be active after firing"
    expected = int(atk_base * (1.0 + _S2_ATK_RATIO))
    assert skadi.effective_atk == expected, (
        f"S2 ATK should be {expected}, got {skadi.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 6: S2 ATK buff removed when duration expires
# ---------------------------------------------------------------------------

def test_skadi_s2_buff_removed_on_end():
    """ATK returns to base value after S2 expires."""
    w = _world()
    skadi = make_skadi()
    skadi.deployed = True
    skadi.position = (0.0, 1.0)
    skadi.atk_cd = 999.0
    w.add_unit(skadi)

    slug = _slug(pos=(1, 1), hp=99999, atk=0)
    w.add_unit(slug)

    atk_base = skadi.effective_atk
    skadi.skill.sp = skadi.skill.sp_cost
    w.tick()  # S2 fires

    # Run past the full duration
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert skadi.skill.active_remaining == 0.0, "S2 should have expired"
    assert skadi.effective_atk == atk_base, "ATK must revert to base after S2 ends"


# ---------------------------------------------------------------------------
# Test 7: Predator + S2 — kill during S2 still heals
# ---------------------------------------------------------------------------

def test_predator_heals_during_s2():
    """Predator kill-heal fires even while S2 is active."""
    w = _world()
    skadi = make_skadi()
    skadi.deployed = True
    skadi.position = (0.0, 1.0)
    skadi.atk_cd = 0.0
    w.add_unit(skadi)

    skadi.hp = int(skadi.max_hp * 0.50)
    hp_before = skadi.hp

    # Activate S2
    skadi.skill.sp = skadi.skill.sp_cost
    slug = _slug(pos=(1, 1), hp=1, atk=0)
    w.add_unit(slug)

    for _ in range(10):
        w.tick()
        if not slug.alive:
            break

    assert not slug.alive, "Slug must die"
    assert skadi.hp > hp_before, "Predator must heal even during S2"
