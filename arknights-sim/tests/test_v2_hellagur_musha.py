"""Hellagur — GUARD_MUSHA: external heal restriction + lifesteal.

GUARD_MUSHA trait: Cannot be healed by allied Medics when HP > 50%.
  Below 50% HP, normal healing applies (Musha can be rescued when critical).
Talent "True Warrior": 8% of damage dealt restores HP (lifesteal, always active).

Tests cover:
  - Archetype and heal_block_threshold
  - Medic does NOT heal Hellagur when HP > 50%
  - Medic DOES heal Hellagur when HP ≤ 50%
  - Medic still heals other (non-Musha) allies normally when Hellagur is above threshold
  - Lifesteal: each attack restores 8% of damage dealt
  - Lifesteal restores HP when below max
  - Lifesteal does NOT over-heal past max_hp
  - S2 ATK buff activates and reverts
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, RoleArchetype, BuffAxis
from core.systems import register_default_systems
from data.characters.hellagur import (
    make_hellagur, _MUSHA_HEAL_BLOCK_THRESHOLD, _LIFESTEAL_RATIO,
    _S2_ATK_RATIO, _S2_DURATION,
)
from data.characters import make_liskarm
from data.characters.warfarin import make_warfarin
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


def _slug(pos=(3, 1), hp=9999, defence=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = defence; e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Archetype and heal_block_threshold
# ---------------------------------------------------------------------------

def test_hellagur_archetype_and_heal_threshold():
    h = make_hellagur()
    assert h.archetype == RoleArchetype.GUARD_MUSHA
    assert abs(h.heal_block_threshold - _MUSHA_HEAL_BLOCK_THRESHOLD) < 0.01


# ---------------------------------------------------------------------------
# Test 2: Medic does NOT heal Hellagur when HP > 50%
# ---------------------------------------------------------------------------

def test_external_heal_blocked_above_threshold():
    """Warfarin must not restore HP to Hellagur when he is above 50% HP."""
    w = _world()
    h = make_hellagur()
    h.deployed = True; h.position = (1.0, 1.0)
    h.hp = int(h.max_hp * 0.80)  # 80% HP — above threshold
    w.add_unit(h)

    healer = make_warfarin()
    healer.deployed = True; healer.position = (0.0, 1.0); healer.atk_cd = 0.0
    w.add_unit(healer)

    hp_before = h.hp
    # Run enough ticks for Warfarin to attempt healing
    for _ in range(TICK_RATE * 6):
        w.tick()

    assert h.hp == hp_before, (
        f"Musha above threshold must not receive external heals; "
        f"hp changed from {hp_before} to {h.hp}"
    )


# ---------------------------------------------------------------------------
# Test 3: Medic DOES heal Hellagur when HP ≤ 50%
# ---------------------------------------------------------------------------

def test_external_heal_allowed_below_threshold():
    """Warfarin must heal Hellagur when his HP drops to or below 50%."""
    w = _world()
    h = make_hellagur()
    h.deployed = True; h.position = (1.0, 1.0)
    h.hp = int(h.max_hp * 0.40)  # 40% HP — below threshold
    w.add_unit(h)

    healer = make_warfarin()
    healer.deployed = True; healer.position = (0.0, 1.0); healer.atk_cd = 0.0
    w.add_unit(healer)

    hp_before = h.hp
    for _ in range(TICK_RATE * 6):
        w.tick()

    assert h.hp > hp_before, (
        f"Musha below threshold must receive external heals; hp={h.hp}/{hp_before}"
    )


# ---------------------------------------------------------------------------
# Test 4: Healer still heals other (non-Musha) allies when Hellagur is blocked
# ---------------------------------------------------------------------------

def test_healer_heals_other_ally_when_musha_blocked():
    """When Hellagur is above threshold, healer should target the other injured ally."""
    w = _world()
    h = make_hellagur()
    h.deployed = True; h.position = (1.0, 1.0)
    h.hp = int(h.max_hp * 0.80)  # above threshold — no heal
    w.add_unit(h)

    normal_ally = make_liskarm()
    normal_ally.deployed = True; normal_ally.position = (2.0, 1.0)
    normal_ally.hp = int(normal_ally.max_hp * 0.50)  # 50% HP — healable
    w.add_unit(normal_ally)

    healer = make_warfarin()
    healer.deployed = True; healer.position = (0.0, 1.0); healer.atk_cd = 0.0
    w.add_unit(healer)

    ally_hp_before = normal_ally.hp
    for _ in range(TICK_RATE * 6):
        w.tick()

    assert normal_ally.hp > ally_hp_before, (
        f"Healer must target normal ally when Musha is blocked; "
        f"ally hp={normal_ally.hp}/{ally_hp_before}"
    )


# ---------------------------------------------------------------------------
# Test 5: Lifesteal restores HP on each attack
# ---------------------------------------------------------------------------

def test_lifesteal_heals_on_attack():
    """True Warrior talent: each attack restores 8% of damage dealt."""
    w = _world()
    h = make_hellagur()
    h.deployed = True; h.position = (0.0, 1.0)
    h.atk_cd = 0.0
    h.hp = int(h.max_hp * 0.50)  # set below max so lifesteal can register
    w.add_unit(h)

    enemy = _slug(pos=(1, 1), hp=99999, defence=0)
    w.add_unit(enemy)

    hp_before = h.hp
    w.tick()  # one attack

    # Damage dealt by Hellagur = effective_atk (no DEF on slug)
    # Lifesteal = 8% of damage
    assert h.hp > hp_before, (
        f"Lifesteal must restore HP after attack; hp={h.hp}, before={hp_before}"
    )


# ---------------------------------------------------------------------------
# Test 6: Lifesteal amount scales with damage dealt
# ---------------------------------------------------------------------------

def test_lifesteal_amount_proportional_to_damage():
    """Lifesteal heals max(1, floor(8% × damage))."""
    w = _world()
    h = make_hellagur()
    h.deployed = True; h.position = (0.0, 1.0)
    h.atk_cd = 0.0
    h.hp = 1  # near-dead so lifesteal is clearly visible
    w.add_unit(h)

    enemy = _slug(pos=(1, 1), hp=99999, defence=0)
    w.add_unit(enemy)

    w.tick()

    damage = h.effective_atk   # slug has 0 DEF, so damage = effective_atk
    expected_heal = max(1, int(damage * _LIFESTEAL_RATIO))
    gained = h.hp - 1   # started at 1
    assert abs(gained - expected_heal) <= 2, (  # ±2 for integer rounding
        f"Lifesteal should restore ~{expected_heal} HP; got {gained}"
    )


# ---------------------------------------------------------------------------
# Test 7: Lifesteal does not overheal past max_hp
# ---------------------------------------------------------------------------

def test_lifesteal_does_not_overheal():
    """Hellagur's HP must never exceed max_hp even with lifesteal."""
    w = _world()
    h = make_hellagur()
    h.deployed = True; h.position = (0.0, 1.0)
    h.atk_cd = 0.0
    h.hp = h.max_hp  # already full HP
    w.add_unit(h)

    enemy = _slug(pos=(1, 1), hp=99999, defence=0)
    w.add_unit(enemy)

    for _ in range(TICK_RATE * 5):
        w.tick()

    assert h.hp <= h.max_hp, f"HP must not exceed max_hp: {h.hp}/{h.max_hp}"


# ---------------------------------------------------------------------------
# Test 8: S2 ATK buff activates and is removed on expiry
# ---------------------------------------------------------------------------

def test_s2_atk_buff():
    w = _world()
    h = make_hellagur(slot="S2")
    h.deployed = True; h.position = (0.0, 1.0); h.atk_cd = 999.0
    w.add_unit(h)

    enemy = _slug(pos=(1, 1))
    w.add_unit(enemy)

    base_atk = h.effective_atk
    h.skill.sp = h.skill.sp_cost
    w.tick()

    expected_atk = int(base_atk * (1.0 + _S2_ATK_RATIO))
    assert h.effective_atk == expected_atk, (
        f"S2 ATK should be {expected_atk}, got {h.effective_atk}"
    )

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert h.effective_atk == base_atk, "ATK must revert after S2 ends"
