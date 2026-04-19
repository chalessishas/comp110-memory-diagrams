"""v2 — Status effect integration tests: STUN halts movement, SLOW reduces speed, both expire."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import StatusEffect
from core.types import TileType, TICK_RATE, DT, StatusKind
from core.systems import register_default_systems
from data.enemies import make_originium_slug


PATH = [(x, 0) for x in range(6)]


def _world() -> World:
    grid = TileGrid(width=6, height=1)
    for i in range(6):
        grid.set_tile(TileState(x=i, y=0, type=TileType.GROUND))
    w = World(tile_grid=grid)
    register_default_systems(w)
    return w


def _apply_stun(world, unit, duration: float) -> None:
    unit.statuses.append(StatusEffect(
        kind=StatusKind.STUN,
        source_tag="test_stun",
        expires_at=world.global_state.elapsed + duration,
    ))


def _apply_slow(world, unit, duration: float, amount: float = 0.3) -> None:
    unit.statuses.append(StatusEffect(
        kind=StatusKind.SLOW,
        source_tag="test_slow",
        expires_at=world.global_state.elapsed + duration,
        params={"amount": amount},
    ))


def test_stun_halts_movement():
    """Stunned enemy must not advance along its path."""
    w = _world()
    slug = make_originium_slug(path=PATH)
    w.add_unit(slug)

    _apply_stun(w, slug, duration=2.0)  # stun for 2 seconds

    for _ in range(TICK_RATE * 2):  # 2 simulated seconds
        w.tick()

    # elapsed increments BEFORE systems run, so stun expires exactly at t=2.0 (final tick).
    # Status decay removes it, then movement gets one free tick. At most 1 tick of movement.
    assert slug.path_progress <= slug.move_speed * DT + 1e-9, \
        f"Stunned enemy must barely move (≤1 tick), got path_progress={slug.path_progress}"


def test_stun_expires_and_movement_resumes():
    """After stun expires, enemy must resume advancing."""
    w = _world()
    slug = make_originium_slug(path=PATH)
    w.add_unit(slug)

    _apply_stun(w, slug, duration=1.0)  # stun for 1 second

    # run 2 seconds: 1s stunned + 1s free
    for _ in range(TICK_RATE * 2):
        w.tick()

    # After stun, 1s at speed 1.0 = 1.0 tiles progress (minus one blocked tick offset)
    assert slug.path_progress > 0.5, \
        f"Enemy must resume moving after stun expires, got path_progress={slug.path_progress}"
    assert not slug.has_status(StatusKind.STUN), "STUN status must have been removed after expiry"


def test_slow_reduces_path_progress():
    """Enemy with SLOW(30%) must cover ~70% of the distance vs no-slow baseline."""
    w_base = _world()
    slug_base = make_originium_slug(path=PATH)
    w_base.add_unit(slug_base)

    w_slow = _world()
    slug_slow = make_originium_slug(path=PATH)
    w_slow.add_unit(slug_slow)
    _apply_slow(w_slow, slug_slow, duration=3.0, amount=0.3)

    ticks = TICK_RATE * 3  # 3 seconds
    for _ in range(ticks):
        w_base.tick()
        w_slow.tick()

    # slowed should cover ~70% vs baseline (allow ±10% tolerance)
    ratio = slug_slow.path_progress / max(slug_base.path_progress, 1e-9)
    assert 0.60 <= ratio <= 0.80, \
        f"SLOW(30%) enemy should move at ~70% speed, got ratio={ratio:.2f} " \
        f"(base={slug_base.path_progress:.2f}, slow={slug_slow.path_progress:.2f})"


def test_slow_expires_and_speed_restores():
    """After SLOW expires, enemy catches up at full speed."""
    w = _world()
    slug = make_originium_slug(path=PATH)
    w.add_unit(slug)

    _apply_slow(w, slug, duration=1.0, amount=0.3)

    for _ in range(TICK_RATE * 2):  # 2 seconds total: 1s slow + 1s normal
        w.tick()

    # 1s at 0.7 speed + 1s at full speed ≈ 1.7 tiles; at least 1.5 to confirm recovery
    assert slug.path_progress >= 1.5, \
        f"Enemy should recover full speed after slow expires, got {slug.path_progress:.2f}"
    assert not slug.has_status(StatusKind.SLOW), "SLOW status must have been removed after expiry"
