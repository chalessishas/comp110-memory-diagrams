"""V2 ECS core integration tests."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.unit_state import UnitState
from core.state.tile_state import TileGrid, TileState
from core.types import Faction, TileType, AttackType
from core.systems import register_default_systems


def _simple_world() -> World:
    grid = TileGrid(width=5, height=1)
    for i in range(4):
        grid.set_tile(TileState(x=i, y=0, type=TileType.GROUND))
    grid.set_tile(TileState(x=4, y=0, type=TileType.GOAL))
    w = World(tile_grid=grid)
    register_default_systems(w)
    return w


def _make_enemy(path=None) -> UnitState:
    if path is None:
        path = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]
    e = UnitState(
        name="slug",
        faction=Faction.ENEMY,
        max_hp=200,
        defence=0,
        move_speed=1.0,
        path=path,
        position=(0.0, 0.0),
    )
    e.deployed = True
    return e


def _make_operator(pos=(2, 0)) -> UnitState:
    op = UnitState(
        name="Liskarm",
        faction=Faction.ALLY,
        max_hp=2000,
        atk=500,
        defence=400,
        atk_interval=1.0,
        attack_type=AttackType.PHYSICAL,
        block=2,
        position=(float(pos[0]), float(pos[1])),
    )
    op.deployed = True
    from core.state.unit_state import RangeShape
    # Melee: can hit 1 tile ahead (+1, 0) and own tile (0, 0)
    op.range_shape = RangeShape(tiles=((0, 0), (1, 0), (-1, 0)))
    return op


# ---- tests -----------------------------------------------------------------

def test_enemy_moves_along_path():
    world = _simple_world()
    enemy = _make_enemy()
    world.add_unit(enemy)

    for _ in range(20):   # 2 seconds at 10 Hz
        world.tick()

    assert enemy.path_progress > 1.5, f"Expected progress > 1.5, got {enemy.path_progress}"


def test_enemy_leaks_decrements_lives():
    world = _simple_world()
    enemy = _make_enemy()
    world.add_unit(enemy)
    assert world.global_state.lives == 3

    result = world.run(max_seconds=10.0)
    assert result in ("loss", "win", "timeout")
    # With no operators, enemy reaches goal
    assert world.global_state.lives < 3


def test_operator_kills_enemy():
    world = _simple_world()
    enemy = _make_enemy()
    op = _make_operator(pos=(0, 0))   # deployed at start of path
    world.add_unit(enemy)
    world.add_unit(op)

    # Run until enemy is dead or 30 seconds
    for _ in range(300):
        world.tick()
        if not enemy.alive:
            break

    assert not enemy.alive, "Operator should kill the low-HP slug"
    assert world.global_state.lives == 3, "No life lost when slug is killed"


def test_world_reports_win_no_enemies():
    world = _simple_world()
    result = world.run(max_seconds=1.0)
    # No enemies and no spawn events = win immediately
    assert result == "win"


def test_damage_tracked_in_global_state():
    world = _simple_world()
    enemy = _make_enemy()
    op = _make_operator(pos=(0, 0))
    world.add_unit(enemy)
    world.add_unit(op)

    world.run(max_seconds=30.0)
    assert world.global_state.total_damage_dealt > 0
