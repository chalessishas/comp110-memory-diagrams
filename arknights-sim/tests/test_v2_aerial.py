"""v2 — Aerial enemy (Mobility.AIRBORNE) bypasses melee block tests."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters import make_liskarm
from data.enemies import make_originium_slug, make_drone


PATH = [(0, 0), (1, 0), (2, 0)]


def _world() -> World:
    grid = TileGrid(width=3, height=1)
    for i in range(3):
        grid.set_tile(TileState(x=i, y=0, type=TileType.GROUND))
    w = World(tile_grid=grid)
    register_default_systems(w)
    return w


def test_drone_not_blocked_by_melee():
    """Drone on same tile as melee operator must not be assigned to any block list."""
    w = _world()
    op = make_liskarm()
    op.position = (0.0, 0.0)
    op.deployed = True
    w.add_unit(op)

    drone = make_drone(path=PATH)
    w.add_unit(drone)

    w.tick()  # run one tick to trigger block assignment

    assert drone.blocked_by_unit_ids == [], \
        "Airborne drone must not be assigned to melee block list"


def test_drone_advances_past_melee():
    """Drone must keep moving even while co-located with a melee operator."""
    w = _world()
    op = make_liskarm()
    op.position = (0.0, 0.0)
    op.deployed = True
    w.add_unit(op)

    drone = make_drone(path=PATH)
    w.add_unit(drone)

    for _ in range(TICK_RATE // 2):  # 0.5 simulated seconds → 0.75 tiles at 1.5 tiles/s
        w.tick()

    assert drone.path_progress > 0.0, "Drone must advance along path despite co-located melee op"


def test_ground_enemy_is_blocked_by_melee():
    """Ground enemy on same tile as melee operator must be blocked (regression)."""
    w = _world()
    op = make_liskarm()
    op.position = (0.0, 0.0)
    op.deployed = True
    w.add_unit(op)

    slug = make_originium_slug(path=PATH)
    w.add_unit(slug)

    w.tick()

    assert slug.blocked_by_unit_ids != [], \
        "Ground enemy must be assigned to melee block list"


def test_blocked_ground_enemy_does_not_advance():
    """Ground enemy blocked by melee must stop after the first tick (system order: movement before targeting).

    Movement runs before targeting assigns blocked_by_unit_ids, so the slug always
    gets exactly one tick of free movement before the block takes effect. After that
    it must stay frozen.
    """
    w = _world()
    op = make_liskarm()
    op.position = (0.0, 0.0)
    op.deployed = True
    w.add_unit(op)

    slug = make_originium_slug(path=PATH)
    w.add_unit(slug)

    for _ in range(TICK_RATE):  # 1 simulated second
        w.tick()

    # At most 1 tick of movement (0.1 tiles at speed 1.0) before block kicks in
    assert slug.path_progress <= slug.move_speed * 0.1 + 1e-9, \
        f"Blocked slug must not advance past first tick, got path_progress={slug.path_progress}"
