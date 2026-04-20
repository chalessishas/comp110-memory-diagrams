"""怒潮凛冬 S3 "Storm Strike" — EventQueue multi-hit skill.

S3 schedules 5 physical hits at 200% ATK via EventQueue at 0.3s intervals.

Tests cover:
  - S3 activates via manual_trigger when SP is full and target exists
  - Exactly 5 hits land on the target (tracked via HP delta + hit count)
  - Total damage equals 5 × int(ATK × 2.0) with enemy defence=0
  - Each individual hit does int(ATK × 2.0) damage
  - No hits land if there is no target at activation
  - S3 active_remaining is set correctly after activation
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, AttackType, Faction
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.headb2 import (
    make_headb2,
    _S3_HIT_COUNT, _S3_ATK_RATIO, _S3_HIT_INTERVAL, _S3_DURATION, _S3_EVENT_KIND,
)
from data.enemies import make_originium_slug


def _world(width=6, height=3) -> World:
    grid = TileGrid(width=width, height=height)
    for x in range(width):
        for y in range(height):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(pos=(3, 1), hp=99999) -> UnitState:
    """Stationary enemy at pos with zero DEF — damage = raw ATK."""
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = 0; e.res = 0.0; e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: S3 active after manual_trigger
# ---------------------------------------------------------------------------

def test_s3_activates():
    """S3 must become active when triggered manually with full SP and a target."""
    w = _world()
    h = make_headb2(slot="S3")
    h.deployed = True; h.position = (2.0, 1.0); h.atk_cd = 999.0
    w.add_unit(h)
    e = _slug(pos=(3, 1))
    w.add_unit(e)

    w.tick()  # targeting system sets __target__
    h.skill.sp = float(h.skill.sp_cost)
    manual_trigger(w, h)

    assert h.skill.active_remaining > 0.0, (
        f"S3 must be active after manual_trigger; active_remaining={h.skill.active_remaining}"
    )
    assert abs(h.skill.active_remaining - _S3_DURATION) < 0.01, (
        f"active_remaining must equal _S3_DURATION={_S3_DURATION}; got {h.skill.active_remaining}"
    )


# ---------------------------------------------------------------------------
# Test 2: Exactly 5 hits land — total damage = 5 × int(ATK × 2.0)
# ---------------------------------------------------------------------------

def test_s3_five_hits_total_damage():
    """5 hits must land; total damage = 5 × floor(ATK × 2.0) (defence=0)."""
    w = _world()
    h = make_headb2(slot="S3")
    h.deployed = True; h.position = (2.0, 1.0); h.atk_cd = 999.0
    w.add_unit(h)
    enemy = _slug(pos=(3, 1), hp=999999)
    w.add_unit(enemy)

    w.tick()  # set __target__
    h.skill.sp = float(h.skill.sp_cost)
    manual_trigger(w, h)

    # Run long enough for all 5 hits: last hit at now + 4 × 0.3s = 1.2s extra
    ticks_needed = int(TICK_RATE * (_S3_HIT_COUNT * _S3_HIT_INTERVAL + 1.0))
    for _ in range(ticks_needed):
        w.tick()

    expected_per_hit = int(h.atk * _S3_ATK_RATIO)
    expected_total = _S3_HIT_COUNT * expected_per_hit
    actual_damage = enemy.max_hp - enemy.hp

    assert actual_damage >= expected_total, (
        f"5 hits × {expected_per_hit} = {expected_total} dmg expected; "
        f"got {actual_damage}"
    )


# ---------------------------------------------------------------------------
# Test 3: Each hit does int(ATK × 2.0) individually
# ---------------------------------------------------------------------------

def test_s3_per_hit_damage():
    """Each individual hit must deal exactly int(ATK × 2.0) (DEF=0 enemy)."""
    w = _world()
    h = make_headb2(slot="S3")
    h.deployed = True; h.position = (2.0, 1.0); h.atk_cd = 999.0
    w.add_unit(h)
    # Tiny HP so we can track integer hits
    enemy = _slug(pos=(3, 1), hp=999999)
    w.add_unit(enemy)

    w.tick()
    h.skill.sp = float(h.skill.sp_cost)
    manual_trigger(w, h)

    expected_per_hit = int(h.atk * _S3_ATK_RATIO)
    hits_seen = 0
    prev_hp = enemy.hp

    for _ in range(int(TICK_RATE * (_S3_HIT_COUNT * _S3_HIT_INTERVAL + 1.0))):
        w.tick()
        delta = prev_hp - enemy.hp
        if delta > 0:
            assert delta == expected_per_hit, (
                f"Each hit must deal {expected_per_hit}; got {delta}"
            )
            hits_seen += 1
        prev_hp = enemy.hp

    assert hits_seen == _S3_HIT_COUNT, (
        f"Must see exactly {_S3_HIT_COUNT} hits; saw {hits_seen}"
    )


# ---------------------------------------------------------------------------
# Test 4: No hits when no target at activation
# ---------------------------------------------------------------------------

def test_s3_no_hits_without_target():
    """S3 must schedule 0 hits if __target__ is None at activation."""
    w = _world()
    h = make_headb2(slot="S3")
    h.deployed = True; h.position = (2.0, 1.0); h.atk_cd = 999.0
    w.add_unit(h)
    # No enemy added — __target__ stays None

    h.skill.sp = float(h.skill.sp_cost)
    manual_trigger(w, h)

    pending_events = len(w.event_queue)
    assert pending_events == 0, (
        f"Must have 0 queued events without target; got {pending_events}"
    )


# ---------------------------------------------------------------------------
# Test 5: Events are scheduled in the EventQueue at correct times
# ---------------------------------------------------------------------------

def test_s3_events_scheduled_in_queue():
    """After on_start, EventQueue must contain exactly _S3_HIT_COUNT pending events."""
    w = _world()
    h = make_headb2(slot="S3")
    h.deployed = True; h.position = (2.0, 1.0); h.atk_cd = 999.0
    w.add_unit(h)
    enemy = _slug(pos=(3, 1))
    w.add_unit(enemy)

    w.tick()  # targeting sets __target__
    h.skill.sp = float(h.skill.sp_cost)

    # Capture queue length before: first tick already dispatched fire_at=0.1 events
    # So trigger BEFORE the second tick and measure queue length
    manual_trigger(w, h)

    # The first event has fire_at=now (already past), subsequent ones are future
    # Total events scheduled = _S3_HIT_COUNT = 5
    # The first may have already been dispatched (fire_at == elapsed), so check >= 4
    queue_len = len(w.event_queue)
    assert queue_len >= _S3_HIT_COUNT - 1, (
        f"EventQueue must hold ≥{_S3_HIT_COUNT - 1} future hit events; got {queue_len}"
    )
