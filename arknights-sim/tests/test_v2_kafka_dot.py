"""Kafka — Anticipation DOT mechanic + status_decay_system DOT processing.

First StatusKind.DOT usage. The DOT is processed by status_decay_system each
tick (status_system.py was extended to handle DOT and REGEN in this session).
DOT = true damage per second, bypasses DEF/RES.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, StatusEffect
from core.types import TileType, TICK_RATE, StatusKind
from core.systems import register_default_systems
from data.characters.kafka import (
    make_kafka, _TALENT_TAG, _DOT_DPS, _DOT_DURATION,
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


def _slug(pos=(1, 1), hp=999999, defence=999) -> UnitState:
    """High-DEF slug so direct attack damage is negligible vs. DOT damage."""
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

def test_kafka_talent_registered():
    k = make_kafka()
    assert len(k.talents) == 1
    assert k.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: DOT status applied on first hit
# ---------------------------------------------------------------------------

def test_anticipation_applies_dot():
    w = _world()
    k = make_kafka(slot=None)
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 0.0
    w.add_unit(k)

    slug = _slug()
    w.add_unit(slug)

    w.tick()

    assert slug.has_status(StatusKind.DOT), "DOT must be applied on first hit"


# ---------------------------------------------------------------------------
# Test 3: DOT status carries correct dps param
# ---------------------------------------------------------------------------

def test_dot_dps_param():
    w = _world()
    k = make_kafka(slot=None)
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 0.0
    w.add_unit(k)

    slug = _slug()
    w.add_unit(slug)

    w.tick()

    dot = next(s for s in slug.statuses if s.kind == StatusKind.DOT)
    assert dot.params.get("dps") == _DOT_DPS


# ---------------------------------------------------------------------------
# Test 4: DOT ticks deal damage each world tick
# ---------------------------------------------------------------------------

def test_dot_deals_damage_each_tick():
    """After DOT is applied, the slug loses HP each tick (bypasses high DEF)."""
    w = _world()
    k = make_kafka(slot=None)
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 0.0
    w.add_unit(k)

    slug = _slug(defence=999999)  # extreme DEF: direct attacks would do min dmg
    w.add_unit(slug)

    w.tick()  # Kafka attacks → DOT applied + minimal direct dmg
    assert slug.has_status(StatusKind.DOT)

    hp_after_first = slug.hp
    k.atk_cd = 999.0  # lock Kafka from attacking further

    w.tick()  # DOT tick only
    hp_after_second = slug.hp

    expected_dot_dmg = max(1, int(_DOT_DPS * 0.1))  # DT = 0.1
    assert hp_after_first - hp_after_second == expected_dot_dmg, (
        f"Expected DOT tick damage {expected_dot_dmg}, got {hp_after_first - hp_after_second}"
    )


# ---------------------------------------------------------------------------
# Test 5: DOT bypasses DEF (true damage)
# ---------------------------------------------------------------------------

def test_dot_bypasses_def():
    """DOT damage is the same regardless of target DEF (true damage)."""
    w1 = _world()
    k1 = make_kafka(slot=None)
    k1.deployed = True; k1.position = (0.0, 1.0); k1.atk_cd = 0.0
    w1.add_unit(k1)
    slug_low_def = _slug(defence=0)
    w1.add_unit(slug_low_def)
    w1.tick()  # apply DOT
    k1.atk_cd = 999.0
    hp_before_low = slug_low_def.hp
    w1.tick()
    dmg_low_def = hp_before_low - slug_low_def.hp

    w2 = _world()
    k2 = make_kafka(slot=None)
    k2.deployed = True; k2.position = (0.0, 1.0); k2.atk_cd = 0.0
    w2.add_unit(k2)
    slug_high_def = _slug(defence=9999)
    w2.add_unit(slug_high_def)
    w2.tick()  # apply DOT
    k2.atk_cd = 999.0
    hp_before_high = slug_high_def.hp
    w2.tick()
    dmg_high_def = hp_before_high - slug_high_def.hp

    assert dmg_low_def == dmg_high_def, (
        f"DOT must bypass DEF: low_def={dmg_low_def}, high_def={dmg_high_def}"
    )


# ---------------------------------------------------------------------------
# Test 6: DOT expires after _DOT_DURATION
# ---------------------------------------------------------------------------

def test_dot_expires():
    w = _world()
    k = make_kafka(slot=None)
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 0.0
    w.add_unit(k)

    slug = _slug()
    w.add_unit(slug)

    w.tick()
    assert slug.has_status(StatusKind.DOT), "DOT must be present"

    k.atk_cd = 999.0
    for _ in range(int(TICK_RATE * (_DOT_DURATION + 1))):
        w.tick()

    assert not slug.has_status(StatusKind.DOT), "DOT must expire after duration"


# ---------------------------------------------------------------------------
# Test 7: DOT refreshes on second hit
# ---------------------------------------------------------------------------

def test_dot_refreshes_on_hit():
    w = _world()
    k = make_kafka(slot=None)
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 0.0
    w.add_unit(k)

    slug = _slug()
    w.add_unit(slug)

    w.tick()  # first hit → DOT applied

    for _ in range(int(TICK_RATE * 1.5)):
        w.tick()

    # second hit → DOT refreshed
    k.atk_cd = 0.0
    w.tick()
    assert slug.has_status(StatusKind.DOT), "DOT refreshed by second hit"

    for _ in range(int(TICK_RATE * 1.0)):
        w.tick()

    assert slug.has_status(StatusKind.DOT), "DOT still active after refresh"


# ---------------------------------------------------------------------------
# Test 8: DOT accumulates significant damage over full duration
# ---------------------------------------------------------------------------

def test_dot_total_damage_over_duration():
    """Over _DOT_DURATION, total DOT damage ≈ _DOT_DPS * _DOT_DURATION."""
    w = _world()
    k = make_kafka(slot=None)
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 0.0
    w.add_unit(k)

    slug = _slug(defence=999999, hp=999999)  # extreme DEF so only DOT damage matters
    w.add_unit(slug)

    w.tick()  # apply DOT
    hp_at_dot_start = slug.hp
    k.atk_cd = 999.0  # no more attacks

    ticks = int(_DOT_DURATION * TICK_RATE)
    for _ in range(ticks):
        w.tick()

    total_dmg = hp_at_dot_start - slug.hp
    expected = _DOT_DPS * _DOT_DURATION  # approximate: 100 * 2 = 200
    # Allow ±(2 * ticks) tolerance due to int truncation per tick
    assert abs(total_dmg - expected) <= ticks * 2, (
        f"Expected ~{expected} total DOT damage over {_DOT_DURATION}s, got {total_dmg}"
    )


# ---------------------------------------------------------------------------
# Test 9: S2 ATK buff
# ---------------------------------------------------------------------------

def test_kafka_s2_atk_buff():
    w = _world()
    k = make_kafka()
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 999.0
    w.add_unit(k)

    slug = _slug()
    w.add_unit(slug)

    atk_base = k.effective_atk
    k.skill.sp = k.skill.sp_cost
    w.tick()

    assert k.skill.active_remaining > 0.0, "S2 must be active"
    expected = int(atk_base * (1.0 + _S2_ATK_RATIO))
    assert k.effective_atk == expected


# ---------------------------------------------------------------------------
# Test 10: S2 buff removed on expiry
# ---------------------------------------------------------------------------

def test_kafka_s2_buff_removed_on_end():
    w = _world()
    k = make_kafka()
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 999.0
    w.add_unit(k)

    slug = _slug()
    w.add_unit(slug)

    atk_base = k.effective_atk
    k.skill.sp = k.skill.sp_cost
    w.tick()

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert k.skill.active_remaining == 0.0, "S2 must have expired"
    assert k.effective_atk == atk_base, "ATK must revert to base"
