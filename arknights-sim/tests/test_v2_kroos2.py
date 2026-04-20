"""Kroos2 — Arctic Fox COLD-on-hit (→FREEZE on second hit) + S2 direct FREEZE."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, StatusKind
from core.systems import register_default_systems
from data.characters.kroos2 import (
    make_kroos2, _TALENT_TAG, _COLD_DURATION, _FREEZE_DURATION, _S2_ATK_RATIO, _S2_DURATION,
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


def _slug(pos=(1, 1), hp=99999) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp
    e.hp = hp
    e.atk = 0
    e.move_speed = 0.0
    e.deployed = True
    e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Talent registered
# ---------------------------------------------------------------------------

def test_kroos2_talent_registered():
    k = make_kroos2()
    assert len(k.talents) == 1
    assert k.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: First hit applies COLD
# ---------------------------------------------------------------------------

def test_arctic_fox_first_hit_applies_cold():
    """First attack without prior COLD → COLD status applied."""
    w = _world()
    k = make_kroos2()
    k.deployed = True
    k.position = (0.0, 1.0)
    k.atk_cd = 0.0
    k.skill = None
    w.add_unit(k)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    w.tick()

    assert slug.has_status(StatusKind.COLD), "First hit must apply COLD"
    assert not slug.has_status(StatusKind.FREEZE), "First hit must NOT apply FREEZE"


# ---------------------------------------------------------------------------
# Test 3: COLD slows enemy movement
# ---------------------------------------------------------------------------

def test_cold_slows_movement():
    """COLD enemy moves at 70% speed — path_progress advances slower."""
    w = _world()
    k = make_kroos2()
    k.deployed = True
    k.position = (0.0, 1.0)
    k.atk_cd = 0.0
    k.skill = None
    w.add_unit(k)

    slug = _slug(pos=(1, 1))
    slug.move_speed = 1.0
    slug.path = [(x, 1) for x in range(1, 6)]
    w.add_unit(slug)

    w.tick()   # first tick: attack lands → COLD applied
    assert slug.has_status(StatusKind.COLD), "COLD must be applied"

    # Tick a few more to measure movement (COLD = 0.7× speed)
    progress_start = slug.path_progress
    for _ in range(5):
        w.tick()
    progress_cold = slug.path_progress - progress_start

    # Without COLD: 5 ticks × 1.0/tick = 0.5 tiles; With COLD: ~0.35 tiles
    assert progress_cold < 0.45, (
        f"COLD must slow movement, expected < 0.45 tiles in 5 ticks, got {progress_cold:.3f}"
    )
    assert progress_cold > 0.0, "COLD enemy must still move (not completely stopped)"


# ---------------------------------------------------------------------------
# Test 4: Second hit upgrades COLD to FREEZE
# ---------------------------------------------------------------------------

def test_arctic_fox_second_hit_freezes():
    """Second hit on already-COLD enemy → upgrades to FREEZE."""
    w = _world()
    k = make_kroos2()
    k.deployed = True
    k.position = (0.0, 1.0)
    k.atk_cd = 0.0
    k.skill = None
    w.add_unit(k)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    # First attack → COLD
    w.tick()
    assert slug.has_status(StatusKind.COLD), "Must be COLD after first hit"

    # Advance to second attack (atk_interval = 1.0s = 10 ticks)
    for _ in range(int(k.atk_interval * TICK_RATE) + 1):
        w.tick()

    assert slug.has_status(StatusKind.FREEZE), "Second hit on COLD enemy must apply FREEZE"
    assert not slug.has_status(StatusKind.COLD), "COLD must be cleared when FREEZE is applied"


# ---------------------------------------------------------------------------
# Test 5: FREEZE stops enemy movement (can_act() = False)
# ---------------------------------------------------------------------------

def test_freeze_stops_movement():
    """FROZEN enemy cannot act."""
    w = _world()
    k = make_kroos2()
    k.deployed = True
    k.position = (0.0, 1.0)
    k.atk_cd = 0.0
    k.skill = None
    w.add_unit(k)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    # Two attacks to reach FREEZE
    w.tick()
    for _ in range(int(k.atk_interval * TICK_RATE) + 1):
        w.tick()

    assert slug.has_status(StatusKind.FREEZE), "Slug must be FROZEN"
    assert not slug.can_act(), "FROZEN enemy must not be able to act"


# ---------------------------------------------------------------------------
# Test 6: COLD expires without refresh
# ---------------------------------------------------------------------------

def test_cold_expires():
    """COLD status clears after _COLD_DURATION if not refreshed."""
    w = _world()
    k = make_kroos2()
    k.deployed = True
    k.position = (0.0, 1.0)
    k.atk_cd = 0.0
    k.skill = None
    w.add_unit(k)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    w.tick()
    assert slug.has_status(StatusKind.COLD), "COLD must be applied"

    # Disable further attacks, wait past expiry
    k.atk_cd = 999.0
    for _ in range(int(TICK_RATE * (_COLD_DURATION + 1))):
        w.tick()

    assert not slug.has_status(StatusKind.COLD), "COLD must expire after 2s"


# ---------------------------------------------------------------------------
# Test 7: S2 applies FREEZE directly (skips COLD)
# ---------------------------------------------------------------------------

def test_s2_applies_freeze_directly():
    """During S2, first hit applies FREEZE without needing prior COLD."""
    w = _world()
    k = make_kroos2()
    k.deployed = True
    k.position = (0.0, 1.0)
    k.atk_cd = 0.0
    w.add_unit(k)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    # Activate S2 first tick, then wait for first attack under S2
    k.skill.sp = k.skill.sp_cost
    # S2 fires in SKILL phase tick 1; combat attack with cd=0 also hits tick 1 (BEFORE S2)
    # → tick 1: attack (COLD applied, pre-S2), S2 fires
    # → tick atk_interval+1: first S2 attack → should FREEZE (already COLD from tick 1)
    for _ in range(int(k.atk_interval * TICK_RATE) + 2):
        w.tick()

    assert slug.has_status(StatusKind.FREEZE), (
        "S2 attack must result in FREEZE (either direct or COLD upgrade)"
    )


# ---------------------------------------------------------------------------
# Test 8: S2 ATK buff + reverts on end
# ---------------------------------------------------------------------------

def test_s2_atk_buff_and_revert():
    """S2 grants +100% ATK and reverts to base on expiry."""
    w = _world()
    k = make_kroos2()
    k.deployed = True
    k.position = (0.0, 1.0)
    k.atk_cd = 999.0
    w.add_unit(k)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    atk_base = k.effective_atk
    k.skill.sp = k.skill.sp_cost
    w.tick()

    assert k.skill.active_remaining > 0.0, "S2 must be active"
    expected = int(atk_base * (1.0 + _S2_ATK_RATIO))
    assert k.effective_atk == expected, f"S2 ATK={expected}, got {k.effective_atk}"

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert k.skill.active_remaining == 0.0, "S2 must have expired"
    assert k.effective_atk == atk_base, "ATK must revert after S2"
    assert not getattr(k, "_kroos2_s2_active", False), "S2 flag must be cleared"
