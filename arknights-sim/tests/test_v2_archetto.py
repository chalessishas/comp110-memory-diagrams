"""Archetto — Heartseeker DEF_DOWN-on-3rd-hit + S2 ATK burst.

DEF_DOWN is the first enemy-DEF debuff mechanic. It is implemented as a
dual StatusEffect + Buff pair (same pattern as Gnosis's RES_DOWN):
  - StatusEffect(DEF_DOWN) for visibility / has_status() checks
  - Buff(axis=DEF, FLAT, -100) for mechanical effect in effective_def
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, StatusKind, BuffAxis
from core.systems import register_default_systems
from data.characters.archetto import (
    make_archetto, _TALENT_TAG, _DEF_DOWN_AMOUNT, _DEF_DOWN_DURATION,
    _S2_ATK_RATIO, _S2_DURATION, _HIT_MODULO,
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


def _slug(pos=(1, 1), hp=999999, defence=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp
    e.atk = 0; e.move_speed = 0.0; e.defence = defence
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Talent registered
# ---------------------------------------------------------------------------

def test_archetto_talent_registered():
    a = make_archetto()
    assert len(a.talents) == 1
    assert a.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: First hit — no DEF_DOWN yet
# ---------------------------------------------------------------------------

def test_heartseeker_no_def_down_on_first_hit():
    w = _world()
    a = make_archetto(slot=None)
    a.deployed = True; a.position = (0.0, 1.0); a.atk_cd = 0.0
    w.add_unit(a)

    slug = _slug()
    w.add_unit(slug)

    w.tick()

    assert not slug.has_status(StatusKind.DEF_DOWN), "No DEF_DOWN on hit 1"


# ---------------------------------------------------------------------------
# Test 3: Second hit — still no DEF_DOWN
# ---------------------------------------------------------------------------

def test_heartseeker_no_def_down_on_second_hit():
    w = _world()
    a = make_archetto(slot=None)
    a.deployed = True; a.position = (0.0, 1.0); a.atk_cd = 0.0
    w.add_unit(a)

    slug = _slug()
    w.add_unit(slug)

    w.tick()  # hit 1
    a.atk_cd = 0.0
    w.tick()  # hit 2

    assert not slug.has_status(StatusKind.DEF_DOWN), "No DEF_DOWN on hit 2"


# ---------------------------------------------------------------------------
# Test 4: Third hit — DEF_DOWN applied
# ---------------------------------------------------------------------------

def test_heartseeker_def_down_on_third_hit():
    w = _world()
    a = make_archetto(slot=None)
    a.deployed = True; a.position = (0.0, 1.0); a.atk_cd = 0.0
    w.add_unit(a)

    slug = _slug()
    w.add_unit(slug)

    for _ in range(3):
        a.atk_cd = 0.0
        w.tick()

    assert slug.has_status(StatusKind.DEF_DOWN), "DEF_DOWN must be applied on 3rd hit"


# ---------------------------------------------------------------------------
# Test 5: DEF_DOWN status carries correct amount param
# ---------------------------------------------------------------------------

def test_def_down_amount_param():
    w = _world()
    a = make_archetto(slot=None)
    a.deployed = True; a.position = (0.0, 1.0); a.atk_cd = 0.0
    w.add_unit(a)

    slug = _slug()
    w.add_unit(slug)

    for _ in range(3):
        a.atk_cd = 0.0
        w.tick()

    dd = next(s for s in slug.statuses if s.kind == StatusKind.DEF_DOWN)
    assert dd.params.get("amount") == _DEF_DOWN_AMOUNT


# ---------------------------------------------------------------------------
# Test 6: DEF_DOWN reduces effective_def
# ---------------------------------------------------------------------------

def test_def_down_reduces_effective_def():
    w = _world()
    a = make_archetto(slot=None)
    a.deployed = True; a.position = (0.0, 1.0); a.atk_cd = 0.0
    w.add_unit(a)

    slug = _slug(defence=300)
    w.add_unit(slug)

    assert slug.effective_def == 300

    for _ in range(3):
        a.atk_cd = 0.0
        w.tick()

    assert slug.effective_def == 300 - _DEF_DOWN_AMOUNT, (
        f"Expected DEF {300 - _DEF_DOWN_AMOUNT}, got {slug.effective_def}"
    )


# ---------------------------------------------------------------------------
# Test 7: DEF_DOWN increases physical damage on subsequent hit
# ---------------------------------------------------------------------------

def test_def_down_amplifies_physical_damage():
    """Hit 4 (after DEF_DOWN active) deals more physical damage than hit 1."""
    w = _world()
    a = make_archetto(slot=None)
    a.deployed = True; a.position = (0.0, 1.0); a.atk_cd = 0.0
    w.add_unit(a)

    slug = _slug(defence=50, hp=999999)
    w.add_unit(slug)

    hp_before = slug.hp
    a.atk_cd = 0.0
    w.tick()  # hit 1 — no DEF_DOWN
    dmg_first = hp_before - slug.hp

    for _ in range(2):
        a.atk_cd = 0.0
        w.tick()  # hits 2 and 3 — DEF_DOWN applied on hit 3

    hp_before4 = slug.hp
    a.atk_cd = 0.0
    w.tick()  # hit 4 — DEF_DOWN active
    dmg_fourth = hp_before4 - slug.hp

    assert slug.has_status(StatusKind.DEF_DOWN), "DEF_DOWN must be active"
    assert dmg_fourth > dmg_first, (
        f"Hit 4 ({dmg_fourth}) must exceed hit 1 ({dmg_first}) due to DEF_DOWN"
    )
    expected = max(int(a.atk * 0.05), a.atk - (50 - _DEF_DOWN_AMOUNT))
    assert dmg_fourth == expected, f"Expected {expected}, got {dmg_fourth}"


# ---------------------------------------------------------------------------
# Test 8: DEF_DOWN expires after _DEF_DOWN_DURATION
# ---------------------------------------------------------------------------

def test_def_down_expires():
    w = _world()
    a = make_archetto(slot=None)
    a.deployed = True; a.position = (0.0, 1.0); a.atk_cd = 0.0
    w.add_unit(a)

    slug = _slug()
    w.add_unit(slug)

    for _ in range(3):
        a.atk_cd = 0.0
        w.tick()

    assert slug.has_status(StatusKind.DEF_DOWN), "DEF_DOWN must be present"

    a.atk_cd = 999.0  # lock attacker out
    for _ in range(int(TICK_RATE * (_DEF_DOWN_DURATION + 1))):
        w.tick()

    assert not slug.has_status(StatusKind.DEF_DOWN), "DEF_DOWN must expire"
    def_down_buffs = [b for b in slug.buffs if b.axis == BuffAxis.DEF and b.value < 0]
    assert len(def_down_buffs) == 0, "DEF_DOWN buff must also expire"


# ---------------------------------------------------------------------------
# Test 9: Cycle resets — 6th hit re-applies DEF_DOWN
# ---------------------------------------------------------------------------

def test_heartseeker_cycle_resets_at_six():
    w = _world()
    a = make_archetto(slot=None)
    a.deployed = True; a.position = (0.0, 1.0); a.atk_cd = 0.0
    w.add_unit(a)

    slug = _slug()
    w.add_unit(slug)

    for _ in range(6):
        a.atk_cd = 0.0
        w.tick()

    # After 6 hits the count is 6 → 6 % 3 == 0 → DEF_DOWN refreshed
    assert slug.has_status(StatusKind.DEF_DOWN), "DEF_DOWN must be (re-)applied on hit 6"


# ---------------------------------------------------------------------------
# Test 10: S2 ATK buff activation
# ---------------------------------------------------------------------------

def test_archetto_s2_atk_buff():
    w = _world()
    a = make_archetto()
    a.deployed = True; a.position = (0.0, 1.0); a.atk_cd = 999.0
    w.add_unit(a)

    slug = _slug()
    w.add_unit(slug)

    atk_base = a.effective_atk
    a.skill.sp = a.skill.sp_cost
    w.tick()

    assert a.skill.active_remaining > 0.0, "S2 must be active"
    expected = int(atk_base * (1.0 + _S2_ATK_RATIO))
    assert a.effective_atk == expected, (
        f"S2 ATK should be {expected}, got {a.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 11: S2 ATK buff removed on expiry
# ---------------------------------------------------------------------------

def test_archetto_s2_buff_removed_on_end():
    w = _world()
    a = make_archetto()
    a.deployed = True; a.position = (0.0, 1.0); a.atk_cd = 999.0
    w.add_unit(a)

    slug = _slug()
    w.add_unit(slug)

    atk_base = a.effective_atk
    a.skill.sp = a.skill.sp_cost
    w.tick()

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert a.skill.active_remaining == 0.0, "S2 must have expired"
    assert a.effective_atk == atk_base, "ATK must revert to base after S2"
