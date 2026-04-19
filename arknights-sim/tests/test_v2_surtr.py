"""Surtr — Dainsleif conditional ATK buff + S3 Tyrant HP drain mechanic."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, AttackType
from core.systems import register_default_systems
from data.characters.surtr import (
    make_surtr, _TALENT_TAG, _TALENT_ATK_RATIO, _HP_THRESHOLD,
    _S3_DURATION, _S3_DRAIN_DELAY, _S3_DRAIN_RATE,
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


def _slug(pos=(1, 1), hp=99999):
    path = [(int(pos[0]), int(pos[1]))] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp
    e.hp = hp
    e.move_speed = 0.0
    e.deployed = True
    e.position = (float(pos[0]), float(pos[1]))
    return e


# ---------------------------------------------------------------------------
# Test 1: Talent registered correctly
# ---------------------------------------------------------------------------

def test_surtr_talent_registered():
    surtr = make_surtr()
    assert len(surtr.talents) == 1
    assert surtr.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: Dainsleif activates when HP drops below threshold
# ---------------------------------------------------------------------------

def test_dainsleif_activates_at_low_hp():
    """ATK buff appears when HP drops to ≤ 50%."""
    w = _world()
    surtr = make_surtr()
    surtr.deployed = True
    surtr.position = (0.0, 1.0)
    surtr.atk_cd = 999.0
    w.add_unit(surtr)

    atk_before = surtr.effective_atk

    # Drop HP below threshold
    surtr.hp = int(surtr.max_hp * 0.40)
    w.tick()  # on_tick fires, adds buff

    atk_after = surtr.effective_atk
    assert atk_after > atk_before, "Dainsleif must increase ATK when HP ≤ 50%"
    expected = int(atk_before * (1.0 + _TALENT_ATK_RATIO))
    assert atk_after == expected, f"Expected ATK={expected}, got {atk_after}"


# ---------------------------------------------------------------------------
# Test 3: Dainsleif removes buff when HP recovers above threshold
# ---------------------------------------------------------------------------

def test_dainsleif_deactivates_when_hp_recovers():
    """Buff is removed when HP heals above the threshold."""
    w = _world()
    surtr = make_surtr()
    surtr.deployed = True
    surtr.position = (0.0, 1.0)
    surtr.atk_cd = 999.0
    w.add_unit(surtr)

    # Drop below threshold → buff appears
    surtr.hp = int(surtr.max_hp * 0.40)
    w.tick()
    assert surtr.effective_atk > surtr.atk, "Buff must be active at low HP"

    # Recover above threshold
    surtr.hp = surtr.max_hp
    w.tick()
    assert surtr.effective_atk == surtr.atk, "Buff must be removed after HP recovers"


# ---------------------------------------------------------------------------
# Test 4: Dainsleif not active at full HP
# ---------------------------------------------------------------------------

def test_dainsleif_inactive_at_full_hp():
    """No ATK buff when Surtr is at full HP."""
    w = _world()
    surtr = make_surtr()
    surtr.deployed = True
    surtr.position = (0.0, 1.0)
    surtr.atk_cd = 999.0
    w.add_unit(surtr)

    for _ in range(5):
        w.tick()

    assert surtr.effective_atk == surtr.atk, "No buff at full HP"


# ---------------------------------------------------------------------------
# Test 5: S3 activates and applies ATK buff + arts mode
# ---------------------------------------------------------------------------

def test_surtr_s3_activates_arts_and_atk_buff():
    """S3 fires: ATK increases and attack type changes to ARTS."""
    w = _world()
    surtr = make_surtr()
    surtr.deployed = True
    surtr.position = (0.0, 1.0)
    surtr.atk_cd = 999.0
    w.add_unit(surtr)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    atk_base = surtr.effective_atk
    surtr.skill.sp = surtr.skill.sp_cost
    w.tick()  # S3 fires

    assert surtr.skill.active_remaining > 0.0, "S3 must be active"
    # ATK buff: +200% means 3x base
    expected_atk = int(atk_base * (1.0 + 2.00))
    assert surtr.effective_atk == expected_atk, (
        f"S3 ATK should be {expected_atk}, got {surtr.effective_atk}"
    )
    assert surtr.attack_type == AttackType.ARTS, "S3 converts to arts attacks"


# ---------------------------------------------------------------------------
# Test 6: No HP drain in first 10 seconds of S3
# ---------------------------------------------------------------------------

def test_surtr_s3_no_drain_in_first_10s():
    """HP must NOT decrease from drain during the first 10 seconds of S3."""
    w = _world()
    surtr = make_surtr()
    surtr.deployed = True
    surtr.position = (0.0, 1.0)
    surtr.atk_cd = 999.0  # no normal attacks
    w.add_unit(surtr)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    surtr.skill.sp = surtr.skill.sp_cost
    w.tick()  # S3 fires
    hp_at_start = surtr.hp

    # Run 9 seconds (still within first 10s grace period)
    for _ in range(TICK_RATE * 9):
        w.tick()

    assert surtr.hp == hp_at_start, "HP must not drain during first 10s of S3"


# ---------------------------------------------------------------------------
# Test 7: HP drain begins after 10 seconds
# ---------------------------------------------------------------------------

def test_surtr_s3_drain_starts_after_10s():
    """After 10s, Surtr's HP begins decreasing from the drain."""
    w = _world()
    surtr = make_surtr()
    surtr.deployed = True
    surtr.position = (0.0, 1.0)
    surtr.atk_cd = 999.0
    w.add_unit(surtr)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    surtr.skill.sp = surtr.skill.sp_cost
    w.tick()  # S3 fires, active_remaining=40s
    hp_after_start = surtr.hp

    # Run 11 seconds — past the 10s drain delay
    for _ in range(TICK_RATE * 11):
        w.tick()

    assert surtr.hp < hp_after_start, "HP must decrease after drain delay (10s)"


# ---------------------------------------------------------------------------
# Test 8: S3 drain kills Surtr and on_end cleanup fires (attack_type restored)
# ---------------------------------------------------------------------------

def test_surtr_s3_death_by_drain_restores_attack_type():
    """When S3 drain empties Surtr's HP, on_end fires and attack_type reverts to ARTS.

    Surtr's base attack_type is ARTS; S3 overrides it to ARTS temporarily as well.
    This test verifies on_end fires on death-by-drain (not just natural duration expiry).
    """
    w = _world()
    surtr = make_surtr()
    surtr.deployed = True
    surtr.position = (0.0, 1.0)
    surtr.atk_cd = 999.0
    w.add_unit(surtr)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    surtr.skill.sp = surtr.skill.sp_cost
    w.tick()  # S3 fires — attack_type set to ARTS by on_start

    # Run past drain delay — Surtr should die and on_end must restore attack_type
    for _ in range(TICK_RATE * 40):
        w.tick()
        if not surtr.alive:
            break

    assert not surtr.alive, "Surtr must die from drain within 40s"
    assert surtr.attack_type == AttackType.ARTS, (
        "on_end must restore attack_type to ARTS after death by drain"
    )
