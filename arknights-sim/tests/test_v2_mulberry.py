"""Mulberry — MEDIC_WANDERING heal-all + Natural Recovery elemental bar cleanse.

Two integration points tested:
  1. MEDIC_WANDERING heal pattern: a single attack heals ALL injured allies.
  2. Natural Recovery talent: each heal reduces elemental injury bars by 50%.
  3. S2 Spring Breeze: instant full-cleanse + 150% ATK heal for all allies.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, RangeShape
from core.types import (
    TileType, TICK_RATE, Faction, AttackType, ElementType,
    ELEMENTAL_PROC_THRESHOLD,
)
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.mulberry import (
    make_mulberry, _TALENT_TAG, _ELEMENTAL_CLEAR_RATIO,
    _S2_HEAL_RATIO,
)
from data.characters.fang import make_fang
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


def _ally(pos=(1, 1), hp=1000, max_hp=1000) -> UnitState:
    a = make_fang()
    a.deployed = True
    a.position = (float(int(pos[0])), float(int(pos[1])))
    a.max_hp = max_hp; a.hp = hp
    return a


# ---------------------------------------------------------------------------
# Test 1: Talent registered
# ---------------------------------------------------------------------------

def test_mulberry_talent_registered():
    m = make_mulberry()
    assert len(m.talents) == 1
    assert m.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: Mulberry heals ALL injured allies simultaneously
# ---------------------------------------------------------------------------

def test_heals_all_injured_allies():
    """A single attack heals every injured deployed ally (MEDIC_WANDERING trait)."""
    w = _world()
    m = make_mulberry(slot=None)
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 0.0
    w.add_unit(m)

    ally1 = _ally(pos=(1, 1), hp=500, max_hp=1000)
    ally2 = _ally(pos=(2, 1), hp=400, max_hp=1000)
    w.add_unit(ally1)
    w.add_unit(ally2)

    w.tick()

    assert ally1.hp > 500, "ally1 must be healed"
    assert ally2.hp > 400, "ally2 must be healed"


# ---------------------------------------------------------------------------
# Test 3: Full-HP ally is skipped (no overheal)
# ---------------------------------------------------------------------------

def test_full_hp_ally_not_healed():
    w = _world()
    m = make_mulberry(slot=None)
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 0.0
    w.add_unit(m)

    full = _ally(pos=(1, 1), hp=1000, max_hp=1000)  # full HP
    injured = _ally(pos=(2, 1), hp=500, max_hp=1000)
    w.add_unit(full)
    w.add_unit(injured)

    w.tick()

    assert full.hp == 1000, "Full-HP ally must not gain HP"
    assert injured.hp > 500, "Injured ally must be healed"


# ---------------------------------------------------------------------------
# Test 4: Natural Recovery — elemental bars reduced 50% on each heal
# ---------------------------------------------------------------------------

def test_talent_reduces_elemental_bars():
    """After Mulberry heals an ally with elemental bars, bars drop by 50%."""
    w = _world()
    m = make_mulberry(slot=None)
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 0.0
    w.add_unit(m)

    ally = _ally(pos=(1, 1), hp=500, max_hp=1000)
    # Manually inject elemental bar buildup
    ally.elemental_bars[ElementType.COMBUSTION.value] = 800.0
    w.add_unit(ally)

    w.tick()

    remaining = ally.elemental_bars.get(ElementType.COMBUSTION.value, 0.0)
    expected = 800.0 * (1.0 - _ELEMENTAL_CLEAR_RATIO)  # 50% → 400
    assert abs(remaining - expected) < 1.0, (
        f"Bar should be ~{expected:.0f} after heal, got {remaining:.0f}"
    )


# ---------------------------------------------------------------------------
# Test 5: Bars not reduced if ally is at full HP (no actual healing)
# ---------------------------------------------------------------------------

def test_talent_no_clear_when_no_heal():
    """If ally is at full HP (dealt=0), elemental bars must not be touched."""
    w = _world()
    m = make_mulberry(slot=None)
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 0.0
    w.add_unit(m)

    full = _ally(pos=(1, 1), hp=1000, max_hp=1000)
    full.elemental_bars[ElementType.NECROSIS.value] = 600.0
    w.add_unit(full)

    # Tick until Mulberry attacks (but she targets injured allies first)
    # Since full.hp == max_hp, she won't target it → bars unchanged
    for _ in range(5):
        w.tick()

    bar = full.elemental_bars.get(ElementType.NECROSIS.value, 0.0)
    assert bar == 600.0, (
        f"Bars must not change when ally is full HP; got {bar}"
    )


# ---------------------------------------------------------------------------
# Test 6: Multiple elemental bar types all reduced
# ---------------------------------------------------------------------------

def test_talent_reduces_all_bar_types():
    """Natural Recovery clears bars for every active ElementType."""
    w = _world()
    m = make_mulberry(slot=None)
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 0.0
    w.add_unit(m)

    ally = _ally(pos=(1, 1), hp=500, max_hp=1000)
    ally.elemental_bars[ElementType.COMBUSTION.value] = 700.0
    ally.elemental_bars[ElementType.NECROSIS.value] = 500.0
    w.add_unit(ally)

    w.tick()

    for etype in (ElementType.COMBUSTION, ElementType.NECROSIS):
        remaining = ally.elemental_bars.get(etype.value, 0.0)
        assert remaining < 700.0, f"{etype.value} bar must have been reduced"


# ---------------------------------------------------------------------------
# Test 7: Bar cleared after multiple consecutive heals
# ---------------------------------------------------------------------------

def test_bars_approach_zero_with_repeated_heals():
    """Repeated heals should drive elemental bars toward zero (50% each time)."""
    w = _world()
    m = make_mulberry(slot=None)
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    ally = _ally(pos=(1, 1), hp=1, max_hp=9999)
    ally.elemental_bars[ElementType.EROSION.value] = 900.0
    w.add_unit(ally)

    # Run 10 seconds — multiple heals
    for _ in range(TICK_RATE * 10):
        w.tick()

    bar = ally.elemental_bars.get(ElementType.EROSION.value, 0.0)
    assert bar < 200.0, f"After repeated heals, bar should be much lower; got {bar:.1f}"


# ---------------------------------------------------------------------------
# Test 8: S2 clears ALL elemental bars from ALL deployed allies
# ---------------------------------------------------------------------------

def test_s2_clears_elemental_bars():
    w = _world()
    m = make_mulberry()
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    ally = _ally(pos=(1, 1), hp=500, max_hp=1000)
    ally.elemental_bars[ElementType.COMBUSTION.value] = 900.0
    ally.elemental_bars[ElementType.NECROSIS.value] = 400.0
    w.add_unit(ally)

    m.skill.sp = m.skill.sp_cost
    manual_trigger(w, m)

    assert not ally.elemental_bars, (
        f"S2 must clear ALL elemental bars; remaining: {ally.elemental_bars}"
    )


# ---------------------------------------------------------------------------
# Test 9: S2 heals all deployed allies for 150% ATK
# ---------------------------------------------------------------------------

def test_s2_heals_all_allies():
    w = _world()
    m = make_mulberry()
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    ally1 = _ally(pos=(1, 1), hp=500, max_hp=9999)
    ally2 = _ally(pos=(2, 1), hp=300, max_hp=9999)
    w.add_unit(ally1)
    w.add_unit(ally2)

    hp1_before = ally1.hp
    hp2_before = ally2.hp
    m.skill.sp = m.skill.sp_cost
    manual_trigger(w, m)

    expected = int(m.effective_atk * _S2_HEAL_RATIO)
    assert ally1.hp - hp1_before == expected, (
        f"ally1 should receive {expected} heal, got {ally1.hp - hp1_before}"
    )
    assert ally2.hp - hp2_before == expected, (
        f"ally2 should receive {expected} heal, got {ally2.hp - hp2_before}"
    )


# ---------------------------------------------------------------------------
# Test 10: S2 heals even full-bars-but-injured allies (no elemental needed)
# ---------------------------------------------------------------------------

def test_s2_heals_ally_with_no_elemental_bars():
    """S2 also heals allies that have no elemental bars at all."""
    w = _world()
    m = make_mulberry()
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    ally = _ally(pos=(1, 1), hp=200, max_hp=9999)  # injured, no elemental
    w.add_unit(ally)

    hp_before = ally.hp
    m.skill.sp = m.skill.sp_cost
    manual_trigger(w, m)

    assert ally.hp > hp_before, "S2 must heal even allies with no elemental bars"
