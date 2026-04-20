"""Bard Inspiration ATK aura — Sora E2 Mellow Flow.

Inspiration gives allies a flat ATK bonus equal to _INSPIRATION_ATK.
BuffStack.INSPIRATION uses highest-wins semantics: multiple Bards deployed
→ only the largest single source applies, not the sum.

Tests cover:
  - Inspiration buff applied to in-range ally each tick
  - Inspiration gives correct flat ATK bonus
  - Out-of-range ally does NOT receive Inspiration
  - Two Bards deployed: ally gains MAX(A, B), not A+B
  - Sora retreats: Inspiration buff removed from allies
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, Buff
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, TileType, TICK_RATE,
)
from core.systems import register_default_systems
from data.characters.sora import (
    make_sora, _INSPIRATION_ATK, _INSPIRATION_SOURCE_TAG, BARD_RANGE,
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


def _dummy_ally(pos=(2, 2), base_atk=200) -> UnitState:
    """Simple melee ally with known base ATK and no buffs."""
    op = UnitState(
        name="DummyAlly",
        faction=Faction.ALLY,
        max_hp=3000, hp=3000,
        atk=base_atk, defence=0, res=0.0,
        atk_interval=1.0,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=True,
        block=1, cost=0,
        deployed=True, position=(float(pos[0]), float(pos[1])),
    )
    return op


# ---------------------------------------------------------------------------
# Test 1: Inspiration buff applied to in-range ally after one tick
# ---------------------------------------------------------------------------

def test_inspiration_buff_applied_to_in_range_ally():
    """After Sora ticks, in-range allies must have an Inspiration ATK buff."""
    w = _world()
    sora = make_sora(slot=None)
    sora.deployed = True; sora.position = (0.0, 2.0)
    w.add_unit(sora)

    # Place ally at (2, 2) — dx=2, dy=0 → in BARD_RANGE (covers dx 0..3, dy -1..1)
    ally = _dummy_ally(pos=(2, 2))
    w.add_unit(ally)

    w.tick()

    inspiration_buffs = [b for b in ally.buffs if b.source_tag == _INSPIRATION_SOURCE_TAG]
    assert len(inspiration_buffs) == 1, (
        f"In-range ally must have exactly 1 Inspiration buff; found {len(inspiration_buffs)}"
    )
    assert inspiration_buffs[0].stack == BuffStack.INSPIRATION
    assert inspiration_buffs[0].axis == BuffAxis.ATK


# ---------------------------------------------------------------------------
# Test 2: Inspiration gives correct flat ATK bonus
# ---------------------------------------------------------------------------

def test_inspiration_gives_correct_atk_bonus():
    """Ally's effective_atk must increase by exactly _INSPIRATION_ATK."""
    w = _world()
    sora = make_sora(slot=None)
    sora.deployed = True; sora.position = (0.0, 2.0)
    w.add_unit(sora)

    ally = _dummy_ally(pos=(1, 2), base_atk=200)
    base_atk = ally.effective_atk
    w.add_unit(ally)

    w.tick()

    expected = base_atk + _INSPIRATION_ATK
    assert ally.effective_atk == expected, (
        f"Effective ATK must be {expected} with Inspiration; got {ally.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: Out-of-range ally does NOT receive Inspiration
# ---------------------------------------------------------------------------

def test_inspiration_not_applied_to_out_of_range_ally():
    """Ally beyond Sora's range must not receive any Inspiration buff."""
    w = _world()
    sora = make_sora(slot=None)
    sora.deployed = True; sora.position = (0.0, 2.0)
    w.add_unit(sora)

    # BARD_RANGE covers dx 0..3 — ally at dx=5 is out of range
    ally = _dummy_ally(pos=(5, 2))
    w.add_unit(ally)

    w.tick()

    inspiration_buffs = [b for b in ally.buffs if b.source_tag == _INSPIRATION_SOURCE_TAG]
    assert len(inspiration_buffs) == 0, (
        f"Out-of-range ally must NOT receive Inspiration; found {len(inspiration_buffs)}"
    )


# ---------------------------------------------------------------------------
# Test 4: Two Bards deployed — ally gains MAX, not sum
# ---------------------------------------------------------------------------

def test_two_bards_inspiration_is_highest_wins_not_additive():
    """When two Bards are deployed, the ally's ATK bonus must be max(A,B), not A+B."""
    w = _world()

    # Sora at (0,2): Inspiration = _INSPIRATION_ATK (≈40)
    sora = make_sora(slot=None)
    sora.deployed = True; sora.position = (0.0, 2.0)
    w.add_unit(sora)

    # Fake second Bard with a higher Inspiration value (simulate by directly pushing buff)
    # We test the BuffStack.INSPIRATION semantics directly on the ally
    ally = _dummy_ally(pos=(1, 2), base_atk=200)
    base_atk = ally.effective_atk
    w.add_unit(ally)

    # Manually push a second Inspiration buff from a "stronger Bard" (value 80)
    ally.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.INSPIRATION,
        value=80.0, source_tag="other_bard_inspiration",
    ))
    # Sora's on_tick will push her own Inspiration buff (value ~40)
    w.tick()

    # Ally should have two INSPIRATION buffs: 40 (Sora) and 80 (other bard)
    # effective_atk must use max(40, 80) = 80, not sum(40+80)=120
    insp_buffs = [b for b in ally.buffs if b.stack == BuffStack.INSPIRATION]
    assert len(insp_buffs) >= 2, "Both Inspiration buffs must be present"

    expected_atk = base_atk + 80  # max(40, 80)
    wrong_additive_atk = base_atk + 40 + 80  # 120 — must NOT be this

    assert ally.effective_atk == expected_atk, (
        f"Highest-wins: ATK must be {expected_atk} (max of buffs); "
        f"got {ally.effective_atk}. Additive would be {wrong_additive_atk}."
    )


# ---------------------------------------------------------------------------
# Test 5: Sora retreats — Inspiration buff removed from allies
# ---------------------------------------------------------------------------

def test_inspiration_removed_when_sora_retreats():
    """After Sora retreats, the Inspiration buff must be cleared from all allies."""
    w = _world()
    sora = make_sora(slot=None)
    sora.deployed = True; sora.position = (0.0, 2.0)
    w.add_unit(sora)

    ally = _dummy_ally(pos=(2, 2))
    w.add_unit(ally)

    w.tick()  # Inspiration applied

    inspiration_before = [b for b in ally.buffs if b.source_tag == _INSPIRATION_SOURCE_TAG]
    assert len(inspiration_before) == 1, "Inspiration must be present before retreat"

    w.retreat(sora)

    inspiration_after = [b for b in ally.buffs if b.source_tag == _INSPIRATION_SOURCE_TAG]
    assert len(inspiration_after) == 0, (
        "Inspiration buff must be removed from allies after Sora retreats"
    )
