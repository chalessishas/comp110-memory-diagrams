"""Targeting system: path_distance_remaining priority.

Key invariant: attack priority = min(path_distance_remaining), NOT max(path_progress).
These diverge on multi-route stages where enemies have different total path lengths.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, RangeShape
from core.types import TileType, Faction, AttackType, Mobility, TICK_RATE
from core.systems import register_default_systems
from core.systems.targeting_system import targeting_system, _targeting_for_operator


def _world() -> World:
    grid = TileGrid(width=12, height=2)
    for x in range(12):
        for y in range(2):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _static_op(x: int, y: int, block: int = 0) -> UnitState:
    """Operator with wide range. block=0 by default to prevent auto-block in targeting tests."""
    return UnitState(
        name="TestGuard",
        faction=Faction.ALLY,
        max_hp=1000,
        hp=1000,
        atk=0,
        atk_interval=9999.0,
        block=block,
        attack_type=AttackType.PHYSICAL,
        range_shape=RangeShape(tiles=tuple((dx, 0) for dx in range(-6, 7))),
        deployed=True,
        position=(float(x), float(y)),
        alive=True,
    )


def _slug_at_progress(path: list, progress: float) -> UnitState:
    """Enemy pinned at a specific path_progress (no movement)."""
    e = UnitState(
        name="Slug",
        faction=Faction.ENEMY,
        max_hp=9999,
        hp=9999,
        atk=0,
        atk_interval=9999.0,
        block=0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        move_speed=0.0,
        path=list(path),
        deployed=True,
        alive=True,
    )
    e.path_progress = progress
    idx = int(progress)
    frac = progress - idx
    x0, y0 = path[min(idx, len(path) - 1)]
    if idx + 1 < len(path):
        x1, y1 = path[idx + 1]
        e.position = (x0 + frac * (x1 - x0), y0 + frac * (y1 - y0))
    else:
        e.position = (float(x0), float(y0))
    return e


# ---------------------------------------------------------------------------
# Test 1: same path length — both metrics agree
# ---------------------------------------------------------------------------

def test_same_path_prefers_higher_progress():
    """Two enemies on identical-length paths: max(progress) == min(remaining)."""
    w = _world()
    op = _static_op(5, 0, block=0)
    w.add_unit(op)

    path = [(i, 0) for i in range(10)]
    close = _slug_at_progress(path, 7.0)   # remaining = 2
    far   = _slug_at_progress(path, 3.0)   # remaining = 6
    w.add_unit(close)
    w.add_unit(far)

    targeting_system(w, 0.0)
    assert getattr(op, "__target__") is close, "Should target the closer-to-exit enemy"


# ---------------------------------------------------------------------------
# Test 2: multi-route divergence — the case where max(progress) is WRONG
# ---------------------------------------------------------------------------

def test_multi_route_prefers_min_remaining():
    """Enemy on short path (4 tiles, progress=2.5, remaining=0.5) must be preferred
    over enemy on long path (10 tiles, progress=5.0, remaining=4.0).
    max(path_progress) wrongly picks the long-path enemy (progress=5 > 2.5).
    min(remaining) correctly picks the short-path enemy (remaining=0.5 < 4.0).

    Uses block=0 to prevent _update_block_assignments from auto-assigning and
    testing only the unblocked-enemy priority branch.
    """
    w = _world()
    op = _static_op(5, 0, block=0)
    w.add_unit(op)

    short_path = [(i, 0) for i in range(4)]   # total length 3 tiles
    long_path  = [(i, 0) for i in range(10)]  # total length 9 tiles

    slug_a = _slug_at_progress(short_path, 2.5)   # remaining = 3 - 2.5 = 0.5
    slug_b = _slug_at_progress(long_path,  5.0)   # remaining = 9 - 5.0 = 4.0

    w.add_unit(slug_a)
    w.add_unit(slug_b)

    targeting_system(w, 0.0)
    assert getattr(op, "__target__") is slug_a, (
        "min(remaining) must pick slug_a (remaining=0.5) over slug_b (remaining=4.0). "
        "max(progress) would incorrectly pick slug_b (progress=5.0 > 2.5)."
    )


# ---------------------------------------------------------------------------
# Test 3: blocked enemy always wins over unblocked regardless of remaining
# ---------------------------------------------------------------------------

def test_blocked_enemy_prioritized_over_closer_unblocked():
    """Rule 1: blocked enemy is always targeted first, even if the unblocked enemy
    has less path_distance_remaining.

    Uses _targeting_for_operator directly to control blocked_by_unit_ids
    without interference from _update_block_assignments clearing them.
    """
    w = _world()
    op = _static_op(5, 0, block=0)
    w.add_unit(op)

    path = [(i, 0) for i in range(10)]
    blocked_slug   = _slug_at_progress(path, 4.0)   # remaining = 5.0 — will be blocked
    unblocked_slug = _slug_at_progress(path, 8.5)   # remaining = 0.5 — NOT blocked

    w.add_unit(blocked_slug)
    w.add_unit(unblocked_slug)

    # Set block assignment directly (bypasses _update_block_assignments clearing)
    blocked_slug.blocked_by_unit_ids   = [op.unit_id]
    unblocked_slug.blocked_by_unit_ids = []

    # Call targeting logic directly (skip _update_block_assignments)
    result = _targeting_for_operator(w, op)
    assert result is blocked_slug, (
        "Blocked enemy must always be targeted before unblocked, "
        "even if unblocked has less remaining distance (0.5 vs 5.0)"
    )


# ---------------------------------------------------------------------------
# Test 4: among multiple blocked enemies, pick the one with least remaining
# ---------------------------------------------------------------------------

def test_among_blocked_pick_min_remaining():
    """When two enemies are both blocked, pick the one closest to exit (min remaining)."""
    w = _world()
    op = _static_op(5, 0, block=0)
    w.add_unit(op)

    short_path = [(i, 0) for i in range(4)]
    long_path  = [(i, 0) for i in range(10)]

    near_exit = _slug_at_progress(short_path, 2.8)   # remaining = 0.2
    far_exit  = _slug_at_progress(long_path,  5.0)   # remaining = 4.0

    w.add_unit(near_exit)
    w.add_unit(far_exit)

    near_exit.blocked_by_unit_ids = [op.unit_id]
    far_exit.blocked_by_unit_ids  = [op.unit_id]

    result = _targeting_for_operator(w, op)
    assert result is near_exit, (
        "Among blocked enemies, target the one with minimum path_distance_remaining "
        "(near_exit=0.2 vs far_exit=4.0)"
    )


# ---------------------------------------------------------------------------
# Test 5: Deadeye Sniper targets lowest-DEF enemy in range
# ---------------------------------------------------------------------------

def _deadeye_op(x: int, y: int) -> UnitState:
    from core.types import RoleArchetype
    op = _static_op(x, y, block=0)
    op.archetype = RoleArchetype.SNIPER_DEADEYE
    return op


def test_deadeye_targets_lowest_def():
    """Deadeye Sniper trait: targets the enemy with the lowest DEF value."""
    w = _world()
    op = _deadeye_op(5, 0)
    w.add_unit(op)

    path = [(i, 0) for i in range(10)]
    low_def  = _slug_at_progress(path, 3.0)   # remaining = 6.0 — would normally be deprioritized
    high_def = _slug_at_progress(path, 7.0)   # remaining = 2.0 — would normally win
    low_def.defence  = 50
    high_def.defence = 300

    w.add_unit(low_def)
    w.add_unit(high_def)

    result = _targeting_for_operator(w, op)
    assert result is low_def, (
        "Deadeye Sniper must target enemy with lowest DEF (50), not closest to exit (DEF=300)"
    )


def test_deadeye_falls_back_to_dist_on_equal_def():
    """When two enemies have equal DEF, Deadeye falls back to min distance remaining."""
    w = _world()
    op = _deadeye_op(5, 0)
    w.add_unit(op)

    path = [(i, 0) for i in range(10)]
    close_slug = _slug_at_progress(path, 7.5)   # remaining = 1.5
    far_slug   = _slug_at_progress(path, 3.0)   # remaining = 6.0
    close_slug.defence = 100
    far_slug.defence   = 100   # equal DEF

    w.add_unit(close_slug)
    w.add_unit(far_slug)

    result = _targeting_for_operator(w, op)
    assert result is close_slug, (
        "Equal DEF tie-break: Deadeye picks closer-to-exit (remaining=1.5 vs 6.0)"
    )


# ---------------------------------------------------------------------------
# Test 6: Besieger Sniper targets heaviest enemy in range
# ---------------------------------------------------------------------------

def _besieger_op(x: int, y: int) -> UnitState:
    from core.types import RoleArchetype
    op = _static_op(x, y, block=0)
    op.archetype = RoleArchetype.SNIPER_SIEGE
    return op


def test_besieger_targets_heaviest():
    """Besieger Sniper trait: targets the enemy with the highest weight."""
    w = _world()
    op = _besieger_op(5, 0)
    w.add_unit(op)

    path = [(i, 0) for i in range(10)]
    heavy  = _slug_at_progress(path, 3.0)   # remaining = 6.0 — far from exit
    light  = _slug_at_progress(path, 7.0)   # remaining = 2.0 — close to exit
    heavy.weight = 3
    light.weight = 1

    w.add_unit(heavy)
    w.add_unit(light)

    result = _targeting_for_operator(w, op)
    assert result is heavy, (
        "Besieger Sniper must target heaviest enemy (weight=3), not closest to exit (weight=1)"
    )


def test_besieger_falls_back_to_dist_on_equal_weight():
    """When two enemies have equal weight, Besieger picks closest to exit."""
    w = _world()
    op = _besieger_op(5, 0)
    w.add_unit(op)

    path = [(i, 0) for i in range(10)]
    close_slug = _slug_at_progress(path, 7.5)   # remaining = 1.5
    far_slug   = _slug_at_progress(path, 3.0)   # remaining = 6.0
    close_slug.weight = 2
    far_slug.weight   = 2   # equal weight

    w.add_unit(close_slug)
    w.add_unit(far_slug)

    result = _targeting_for_operator(w, op)
    assert result is close_slug, (
        "Equal weight tie-break: Besieger picks closer-to-exit (remaining=1.5 vs 6.0)"
    )
