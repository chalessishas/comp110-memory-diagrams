"""Quercus — MEDIC_INCANTATION: Arts attack to enemy + simultaneous heal to in-range allies.

MEDIC_INCANTATION trait:
  - Each attack deals Arts damage to the targeted enemy
  - AND heals all allied operators in range for 50% of damage dealt
  - S2 "Blessing of the Woods": ATK+20%, heal ratio increases to 80%

Tests cover:
  - Archetype is MEDIC_INCANTATION
  - Normal attack damages enemy (Arts-type)
  - Trait heals an in-range ally on each hit
  - Heal amount equals 50% of Arts damage dealt to enemy
  - Out-of-range allies are NOT healed
  - S2 applies ATK+20% buff during skill
  - S2 increases heal ratio to 80% of damage
  - After S2 ends, heal ratio returns to 50%
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, RangeShape
from core.types import (
    TileType, TICK_RATE, DT, Faction, AttackType, Profession,
    RoleArchetype,
)
from core.systems import register_default_systems
from data.characters.quercus import (
    make_quercus,
    _TRAIT_HEAL_RATIO, _S2_HEAL_RATIO, _S2_ATK_RATIO, _S2_DURATION,
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


def _slug(pos=(1, 1), hp=99999, defence=0, res=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = defence; e.res = float(res)
    e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


def _ally(pos=(0, 0), hp=2000, max_hp=2000) -> UnitState:
    """A simple ally that can receive heals."""
    return UnitState(
        name="Ally",
        faction=Faction.ALLY,
        max_hp=max_hp, hp=hp, atk=0,
        defence=0, atk_interval=999.0, block=0,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=False,
        range_shape=RangeShape(tiles=()),
        deployed=True, position=(float(pos[0]), float(pos[1])),
    )


# ---------------------------------------------------------------------------
# Test 1: Archetype is MEDIC_INCANTATION
# ---------------------------------------------------------------------------

def test_quercus_archetype():
    q = make_quercus()
    assert q.archetype == RoleArchetype.MEDIC_INCANTATION
    assert q.attack_type == AttackType.ARTS, "Quercus must deal Arts damage"


# ---------------------------------------------------------------------------
# Test 2: Normal attack damages the targeted enemy
# ---------------------------------------------------------------------------

def test_attack_damages_enemy():
    """Quercus's Arts attack deals damage to the enemy (after RES reduction)."""
    w = _world()
    q = make_quercus()
    q.deployed = True; q.position = (0.0, 1.0)
    q.atk_cd = 0.0   # force immediate first attack
    w.add_unit(q)

    enemy = _slug(pos=(1, 1), hp=9999, res=0)
    initial_hp = enemy.hp
    w.add_unit(enemy)

    for _ in range(3):
        w.tick()

    assert enemy.hp < initial_hp, (
        f"Enemy must take Arts damage from Quercus; hp was {initial_hp}, now {enemy.hp}"
    )


# ---------------------------------------------------------------------------
# Test 3: Trait heals in-range ally on each hit
# ---------------------------------------------------------------------------

def test_trait_heals_ally_on_hit():
    """After hitting an enemy, an in-range injured ally is healed."""
    w = _world()
    q = make_quercus()
    q.deployed = True; q.position = (0.0, 1.0)
    q.atk_cd = 0.0
    w.add_unit(q)

    enemy = _slug(pos=(1, 1), hp=9999, res=0)
    w.add_unit(enemy)

    # Injured ally at (1, 1) — same tile as enemy, within Quercus's range
    ally = _ally(pos=(1, 1), hp=500, max_hp=2000)
    w.add_unit(ally)

    for _ in range(3):
        w.tick()

    assert ally.hp > 500, (
        f"In-range ally must be healed by Quercus's incantation; hp was 500, now {ally.hp}"
    )


# ---------------------------------------------------------------------------
# Test 4: Heal amount is 50% of damage dealt
# ---------------------------------------------------------------------------

def test_trait_heal_amount_is_50pct_damage():
    """Heal received by ally equals _TRAIT_HEAL_RATIO * actual damage dealt."""
    w = _world()
    q = make_quercus()
    q.deployed = True; q.position = (0.0, 1.0)
    q.atk_cd = 0.0
    w.add_unit(q)

    # Enemy with 0 RES so damage = full Arts ATK
    enemy = _slug(pos=(1, 1), hp=99999, res=0)
    initial_enemy_hp = enemy.hp
    w.add_unit(enemy)

    # Ally starts at a specific low HP so we can measure exact heal
    ally = _ally(pos=(2, 1), hp=100, max_hp=5000)
    w.add_unit(ally)

    # Single tick attack cycle (atk_cd=0 → fires immediately)
    w.tick()

    damage_dealt = initial_enemy_hp - enemy.hp
    expected_heal = int(damage_dealt * _TRAIT_HEAL_RATIO)
    actual_heal = ally.hp - 100

    assert damage_dealt > 0, "Quercus must have attacked and dealt damage"
    assert abs(actual_heal - expected_heal) <= 1, (
        f"Heal must be {_TRAIT_HEAL_RATIO:.0%} of damage; "
        f"damage={damage_dealt}, expected_heal={expected_heal}, actual_heal={actual_heal}"
    )


# ---------------------------------------------------------------------------
# Test 5: Out-of-range allies are NOT healed
# ---------------------------------------------------------------------------

def test_trait_no_heal_out_of_range_ally():
    """Allies outside Quercus's attack range must not receive incantation heals."""
    w = _world()
    q = make_quercus()
    q.deployed = True; q.position = (0.0, 1.0)
    q.atk_cd = 0.0
    w.add_unit(q)

    enemy = _slug(pos=(1, 1), hp=9999, res=0)
    w.add_unit(enemy)

    # Ally at (5, 1) — out of Quercus's range (max dx=3)
    ally_out = _ally(pos=(5, 1), hp=500, max_hp=2000)
    w.add_unit(ally_out)

    for _ in range(3):
        w.tick()

    assert ally_out.hp == 500, (
        f"Out-of-range ally must NOT be healed; hp was 500, now {ally_out.hp}"
    )


# ---------------------------------------------------------------------------
# Test 6: S2 applies ATK +20% buff during skill
# ---------------------------------------------------------------------------

def test_s2_atk_buff_during_skill():
    """During S2, Quercus's effective_atk should be base * 1.2."""
    w = _world()
    q = make_quercus()
    q.deployed = True; q.position = (0.0, 1.0)
    w.add_unit(q)

    enemy = _slug(pos=(1, 1))
    w.add_unit(enemy)

    base_atk = q.effective_atk

    # Fire S2 manually
    q.skill.sp = float(q.skill.sp_cost)
    w.tick()

    assert q.skill.active_remaining > 0.0, "S2 must be active"
    expected_atk = int(base_atk * (1 + _S2_ATK_RATIO))
    assert abs(q.effective_atk - expected_atk) <= 2, (
        f"ATK during S2 must be base×{1+_S2_ATK_RATIO}; base={base_atk}, expected={expected_atk}, got={q.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 7: S2 increases heal ratio to 80%
# ---------------------------------------------------------------------------

def test_s2_heal_ratio_increases():
    """During S2, the heal per hit should be 80% of damage, not 50%."""
    w = _world()
    q = make_quercus()
    q.deployed = True; q.position = (0.0, 1.0)
    w.add_unit(q)

    # Large RES enemy to control damage (0 RES = full damage)
    enemy = _slug(pos=(1, 1), hp=99999, res=0)
    initial_enemy_hp = enemy.hp
    w.add_unit(enemy)

    ally = _ally(pos=(2, 1), hp=100, max_hp=9999)
    w.add_unit(ally)

    # Activate S2 in one tick (COMBAT fires before SKILL, so S2 is active next tick)
    q.skill.sp = float(q.skill.sp_cost)
    w.tick()   # S2 activates in SKILL phase this tick
    assert q.skill.active_remaining > 0.0, "S2 must be active"

    # Snapshot state right before the next attack
    initial_enemy_hp2 = enemy.hp
    ally_hp_before = ally.hp

    # Force attack while S2 is already active
    q.atk_cd = 0.0
    w.tick()

    damage = initial_enemy_hp2 - enemy.hp
    expected_heal = int(damage * _S2_HEAL_RATIO)
    actual_heal = ally.hp - ally_hp_before

    assert damage > 0, "Must have attacked"
    assert abs(actual_heal - expected_heal) <= 2, (
        f"Heal during S2 must be {_S2_HEAL_RATIO:.0%} of damage; "
        f"damage={damage}, expected_heal={expected_heal}, actual_heal={actual_heal}"
    )


# ---------------------------------------------------------------------------
# Test 8: After S2 ends, heal ratio returns to 50%
# ---------------------------------------------------------------------------

def test_s2_heal_ratio_resets_after_skill():
    """After S2 expires, heal ratio drops back to 50%."""
    w = _world()
    q = make_quercus()
    q.deployed = True; q.position = (0.0, 1.0)
    w.add_unit(q)

    enemy = _slug(pos=(1, 1), hp=99999, res=0)
    w.add_unit(enemy)

    ally = _ally(pos=(2, 1), hp=100, max_hp=9999)
    w.add_unit(ally)

    # Fire S2
    q.skill.sp = float(q.skill.sp_cost)
    w.tick()
    assert q.skill.active_remaining > 0.0, "S2 must be active"

    # Wait for S2 to end
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert q.skill.active_remaining == 0.0, "S2 must have ended"

    # Measure one attack after S2
    initial_enemy_hp = enemy.hp
    ally_hp_before = ally.hp
    q.atk_cd = 0.0
    w.tick()

    damage = initial_enemy_hp - enemy.hp
    if damage > 0:
        expected_heal = int(damage * _TRAIT_HEAL_RATIO)
        actual_heal = ally.hp - ally_hp_before
        assert abs(actual_heal - expected_heal) <= 2, (
            f"After S2, heal must revert to {_TRAIT_HEAL_RATIO:.0%}; "
            f"damage={damage}, expected_heal={expected_heal}, actual_heal={actual_heal}"
        )
