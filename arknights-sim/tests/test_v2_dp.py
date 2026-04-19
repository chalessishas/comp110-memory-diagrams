"""v2 — DP accumulation and deploy gate tests."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, Faction, TICK_RATE, DT
from core.systems import register_default_systems
from data.characters import make_liskarm


def _simple_world(dp: int = 0, dp_rate: float = 1.0) -> World:
    grid = TileGrid(width=3, height=1)
    grid.set_tile(TileState(x=0, y=0, type=TileType.GROUND))
    grid.set_tile(TileState(x=1, y=0, type=TileType.GROUND))
    grid.set_tile(TileState(x=2, y=0, type=TileType.GOAL))
    w = World(tile_grid=grid)
    w.global_state.dp = dp
    w.global_state.dp_gain_rate = dp_rate
    register_default_systems(w)
    return w


def test_dp_accumulates_at_rate():
    w = _simple_world(dp=0, dp_rate=1.0)
    for _ in range(TICK_RATE * 10):   # 10 simulated seconds
        w.tick()
    assert w.global_state.dp == 10, f"Expected 10 DP after 10s, got {w.global_state.dp}"


def test_deploy_succeeds_with_sufficient_dp():
    op = make_liskarm()
    op.cost = 15
    w = _simple_world(dp=20)
    result = w.deploy(op)
    assert result is True
    assert op in w.units
    assert op.deployed
    assert w.global_state.dp == 5


def test_deploy_fails_with_insufficient_dp():
    op = make_liskarm()
    op.cost = 30
    w = _simple_world(dp=10)
    result = w.deploy(op)
    assert result is False
    assert op not in w.units
    assert w.global_state.dp == 10


def test_deploy_after_accumulation():
    op = make_liskarm()
    op.cost = 8
    w = _simple_world(dp=0, dp_rate=1.0)
    for _ in range(TICK_RATE * 8):
        w.tick()
    assert w.global_state.dp >= 8
    result = w.deploy(op)
    assert result is True
