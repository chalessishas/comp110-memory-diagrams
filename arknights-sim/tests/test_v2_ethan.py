"""Ethan — Neurotoxin ATK_DOWN-on-hit.

ATK_DOWN is the first enemy-ATK debuff mechanic. When applied, the enemy's
effective_atk decreases, so damage they deal to blocked operators is reduced.
Pattern mirrors Archetto's DEF_DOWN but on the ATK axis.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, StatusKind, BuffAxis
from core.systems import register_default_systems
from data.characters.ethan import (
    make_ethan, _TALENT_TAG, _ATK_DOWN_AMOUNT, _ATK_DOWN_DURATION,
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


def _slug(pos=(1, 1), hp=999999, atk=500) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp
    e.atk = atk; e.move_speed = 0.0; e.defence = 0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Talent registered
# ---------------------------------------------------------------------------

def test_ethan_talent_registered():
    e = make_ethan()
    assert len(e.talents) == 1
    assert e.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: First hit applies ATK_DOWN
# ---------------------------------------------------------------------------

def test_neurotoxin_applies_atk_down():
    w = _world()
    e = make_ethan(slot=None)
    e.deployed = True; e.position = (0.0, 1.0); e.atk_cd = 0.0
    w.add_unit(e)

    slug = _slug()
    w.add_unit(slug)

    w.tick()

    assert slug.has_status(StatusKind.ATK_DOWN), "ATK_DOWN must be applied on first hit"


# ---------------------------------------------------------------------------
# Test 3: ATK_DOWN status carries correct amount param
# ---------------------------------------------------------------------------

def test_atk_down_amount_param():
    w = _world()
    e = make_ethan(slot=None)
    e.deployed = True; e.position = (0.0, 1.0); e.atk_cd = 0.0
    w.add_unit(e)

    slug = _slug()
    w.add_unit(slug)

    w.tick()

    ad = next(s for s in slug.statuses if s.kind == StatusKind.ATK_DOWN)
    assert ad.params.get("amount") == _ATK_DOWN_AMOUNT


# ---------------------------------------------------------------------------
# Test 4: ATK_DOWN reduces effective_atk
# ---------------------------------------------------------------------------

def test_atk_down_reduces_effective_atk():
    """After Ethan's hit, the enemy's effective_atk drops by _ATK_DOWN_AMOUNT."""
    w = _world()
    e = make_ethan(slot=None)
    e.deployed = True; e.position = (0.0, 1.0); e.atk_cd = 0.0
    w.add_unit(e)

    slug = _slug(atk=500)
    w.add_unit(slug)

    atk_before = slug.effective_atk
    assert atk_before == 500

    w.tick()

    atk_after = slug.effective_atk
    expected = 500 - _ATK_DOWN_AMOUNT
    assert atk_after == expected, (
        f"Expected ATK {expected} after ATK_DOWN, got {atk_after}"
    )


# ---------------------------------------------------------------------------
# Test 5: ATK_DOWN reduces damage the enemy deals to a blocker
# ---------------------------------------------------------------------------

def test_atk_down_reduces_physical_damage_via_effective_atk():
    """effective_atk with ATK_DOWN feeds into take_physical → less damage to a dummy defender."""
    w = _world()
    e = make_ethan(slot=None)
    e.deployed = True; e.position = (0.0, 1.0); e.atk_cd = 0.0
    w.add_unit(e)

    slug = _slug(atk=500)
    w.add_unit(slug)

    # Baseline: slug.effective_atk before any ATK_DOWN
    baseline_atk = slug.effective_atk
    assert baseline_atk == 500

    w.tick()  # Ethan hits → ATK_DOWN applied
    assert slug.has_status(StatusKind.ATK_DOWN)

    # With ATK_DOWN active, effective_atk is reduced
    reduced_atk = slug.effective_atk
    assert reduced_atk == 500 - _ATK_DOWN_AMOUNT

    # Damage formula uses effective_atk: dmg = max(5% raw, raw - def)
    # Verify that take_physical(reduced_atk) < take_physical(baseline_atk) on a dummy with 0 DEF
    from core.state.unit_state import UnitState as _U
    from core.types import Faction
    dummy = _U(name="D", faction=Faction.ALLY, max_hp=99999, atk=0, defence=0,
               atk_interval=1.0, block=0, cost=0)
    dummy.hp = 99999

    dmg_baseline = dummy.take_physical(baseline_atk)
    dummy.hp = 99999
    dmg_reduced = dummy.take_physical(reduced_atk)

    assert dmg_reduced < dmg_baseline, (
        f"Damage with ATK_DOWN ({dmg_reduced}) must be < baseline ({dmg_baseline})"
    )


# ---------------------------------------------------------------------------
# Test 6: ATK_DOWN expires after _ATK_DOWN_DURATION
# ---------------------------------------------------------------------------

def test_atk_down_expires():
    w = _world()
    e = make_ethan(slot=None)
    e.deployed = True; e.position = (0.0, 1.0); e.atk_cd = 0.0
    w.add_unit(e)

    slug = _slug()
    w.add_unit(slug)

    w.tick()
    assert slug.has_status(StatusKind.ATK_DOWN), "ATK_DOWN must be present"

    e.atk_cd = 999.0
    for _ in range(int(TICK_RATE * (_ATK_DOWN_DURATION + 1))):
        w.tick()

    assert not slug.has_status(StatusKind.ATK_DOWN), "ATK_DOWN must expire"
    atk_down_buffs = [b for b in slug.buffs if b.axis == BuffAxis.ATK and b.value < 0]
    assert len(atk_down_buffs) == 0, "ATK_DOWN buff must also expire"


# ---------------------------------------------------------------------------
# Test 7: Refresh — re-hit extends duration
# ---------------------------------------------------------------------------

def test_atk_down_refreshes_on_hit():
    """Hitting again while ATK_DOWN is active resets the timer."""
    w = _world()
    e = make_ethan(slot=None)
    e.deployed = True; e.position = (0.0, 1.0); e.atk_cd = 0.0
    w.add_unit(e)

    slug = _slug()
    w.add_unit(slug)

    w.tick()  # first hit → ATK_DOWN, expires at t=DT + 2.0

    # Advance to just before expiry
    for _ in range(int(TICK_RATE * 1.5)):
        w.tick()

    # Hit again → refresh
    e.atk_cd = 0.0
    w.tick()
    assert slug.has_status(StatusKind.ATK_DOWN), "ATK_DOWN refreshed"

    # Advance beyond original expiry — should still be active (refreshed)
    for _ in range(int(TICK_RATE * 1.0)):
        w.tick()

    assert slug.has_status(StatusKind.ATK_DOWN), "ATK_DOWN must still be active after refresh"


# ---------------------------------------------------------------------------
# Test 8: S2 ATK buff activation
# ---------------------------------------------------------------------------

def test_ethan_s2_atk_buff():
    w = _world()
    e = make_ethan()
    e.deployed = True; e.position = (0.0, 1.0); e.atk_cd = 999.0
    w.add_unit(e)

    slug = _slug()
    w.add_unit(slug)

    atk_base = e.effective_atk
    e.skill.sp = e.skill.sp_cost
    w.tick()

    assert e.skill.active_remaining > 0.0, "S2 must be active"
    expected = int(atk_base * (1.0 + _S2_ATK_RATIO))
    assert e.effective_atk == expected, (
        f"S2 ATK should be {expected}, got {e.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 9: S2 ATK buff removed on expiry
# ---------------------------------------------------------------------------

def test_ethan_s2_buff_removed_on_end():
    w = _world()
    e = make_ethan()
    e.deployed = True; e.position = (0.0, 1.0); e.atk_cd = 999.0
    w.add_unit(e)

    slug = _slug()
    w.add_unit(slug)

    atk_base = e.effective_atk
    e.skill.sp = e.skill.sp_cost
    w.tick()

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert e.skill.active_remaining == 0.0, "S2 must have expired"
    assert e.effective_atk == atk_base, "ATK must revert to base after S2"
