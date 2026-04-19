"""v2 — Healer (Medic) targeting and HP restore tests."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, DT
from core.systems import register_default_systems
from data.characters import make_warfarin, make_liskarm


def _world() -> World:
    grid = TileGrid(width=3, height=1)
    for i in range(3):
        grid.set_tile(TileState(x=i, y=0, type=TileType.GROUND))
    w = World(tile_grid=grid)
    register_default_systems(w)
    return w


def test_healer_restores_injured_ally():
    w = _world()
    tank = make_liskarm()
    tank.position = (0.0, 0.0)
    tank.deployed = True
    tank.hp = tank.max_hp - 500

    healer = make_warfarin()
    healer.position = (1.0, 0.0)
    healer.deployed = True

    w.add_unit(tank)
    w.add_unit(healer)

    initial_hp = tank.hp
    for _ in range(TICK_RATE * 4):   # 4 seconds — warfarin atk_interval=2.85s
        w.tick()

    assert tank.hp > initial_hp, "Healer must restore HP to injured tank"


def test_healer_idles_when_all_full_hp():
    w = _world()
    tank = make_liskarm()
    tank.position = (0.0, 0.0)
    tank.deployed = True
    # tank at full HP

    healer = make_warfarin()
    healer.position = (1.0, 0.0)
    healer.deployed = True

    w.add_unit(tank)
    w.add_unit(healer)

    for _ in range(TICK_RATE * 4):
        w.tick()

    assert tank.hp == tank.max_hp, "No overhealing when all allies are at full HP"
    heal_entries = [e for e in w.log_entries if "heal" in e]
    assert len(heal_entries) == 0, "No heal log when all allies are at full HP"


def test_healer_targets_lowest_hp_ratio():
    w = _world()
    tank1 = make_liskarm()
    tank1.position = (0.0, 0.0)
    tank1.deployed = True
    tank1.hp = int(tank1.max_hp * 0.25)  # 25% HP

    tank2 = make_liskarm()
    tank2.position = (2.0, 0.0)
    tank2.deployed = True
    tank2.hp = int(tank2.max_hp * 0.50)  # 50% HP

    healer = make_warfarin()
    healer.position = (1.0, 0.0)
    healer.deployed = True

    w.add_unit(tank1)
    w.add_unit(tank2)
    w.add_unit(healer)

    hp1_before, hp2_before = tank1.hp, tank2.hp
    for _ in range(TICK_RATE * 4):
        w.tick()

    assert tank1.hp > hp1_before, "Most-injured (25% HP) must be healed first"
