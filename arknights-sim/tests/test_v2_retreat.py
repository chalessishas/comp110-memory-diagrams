"""v2 — Operator retreat + redeploy cooldown tests."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, DT
from core.systems import register_default_systems
from data.characters import make_liskarm


def _world(dp: float = 30.0) -> World:
    grid = TileGrid(width=3, height=1)
    for i in range(3):
        grid.set_tile(TileState(x=i, y=0, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp = dp
    register_default_systems(w)
    return w


def test_retreat_undeploys_operator():
    """Retreating an operator sets deployed=False."""
    w = _world(dp=30)
    op = make_liskarm()
    op.position = (1.0, 0.0)
    w.deploy(op)
    assert op.deployed

    w.retreat(op)
    assert not op.deployed


def test_retreat_refunds_half_dp():
    """Retreating refunds floor(cost/2) DP."""
    w = _world(dp=30)
    op = make_liskarm()  # cost=22
    op.position = (1.0, 0.0)
    op.cost = 22
    dp_before = w.global_state.dp
    w.deploy(op)
    dp_after_deploy = w.global_state.dp
    assert dp_after_deploy == dp_before - 22

    w.retreat(op)
    # refund = 22 // 2 = 11
    assert w.global_state.dp == dp_after_deploy + 11


def test_retreat_sets_redeploy_cooldown():
    """After retreat, redeploy_available_at = elapsed + redeploy_cd."""
    w = _world(dp=30)
    op = make_liskarm()
    op.position = (1.0, 0.0)
    op.redeploy_cd = 70.0
    w.deploy(op)

    t_retreat = w.global_state.elapsed
    w.retreat(op)

    assert abs(op.redeploy_available_at - (t_retreat + 70.0)) < 1e-9


def test_redeploy_blocked_during_cooldown():
    """Cannot redeploy operator while redeploy_available_at > elapsed."""
    w = _world(dp=100)
    op = make_liskarm()
    op.position = (1.0, 0.0)
    op.cost = 10
    op.redeploy_cd = 70.0
    w.deploy(op)
    w.retreat(op)

    # Immediately after retreat, cooldown not elapsed
    result = w.deploy(op)
    assert result is False, "Must not redeploy during cooldown"


def test_redeploy_allowed_after_cooldown():
    """Can redeploy after redeploy_available_at has elapsed."""
    w = _world(dp=100)
    op = make_liskarm()
    op.position = (1.0, 0.0)
    op.cost = 10
    op.redeploy_cd = 1.0  # 1 second cooldown for fast test
    w.deploy(op)
    w.retreat(op)

    # Advance past cooldown
    for _ in range(TICK_RATE * 2):  # 2 seconds > 1s cooldown
        w.tick()

    result = w.deploy(op)
    assert result is True, "Must allow redeploy after cooldown expires"
    assert op.deployed
