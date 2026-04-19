"""v2 — Operator retreat + redeploy cooldown tests."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, DT
from core.systems import register_default_systems
from data.characters import make_liskarm
from data.characters.angelina import make_angelina


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


def test_retreat_no_op_on_dead_operator():
    """Retreating a dead operator must be a no-op — no DP refund, no cooldown set."""
    w = _world(dp=50)
    op = make_liskarm()
    op.position = (1.0, 0.0)
    op.cost = 22
    w.deploy(op)

    dp_after_deploy = w.global_state.dp
    op.alive = False   # simulate operator killed in combat
    op.deployed = True  # cleanup_system doesn't clear deployed for allies

    w.retreat(op)

    assert op.deployed, "deployed should stay True — retreat was no-op"
    assert w.global_state.dp == dp_after_deploy, "no DP refund for dead operator"
    assert op.redeploy_available_at == 0.0, "no cooldown set for dead operator"


def _world_with_elevated(dp: float = 100.0) -> World:
    grid = TileGrid(width=3, height=2)
    for i in range(3):
        grid.set_tile(TileState(x=i, y=0, type=TileType.GROUND))
        grid.set_tile(TileState(x=i, y=1, type=TileType.ELEVATED))
    w = World(tile_grid=grid)
    w.global_state.dp = dp
    register_default_systems(w)
    return w


def test_melee_blocked_from_elevated_tile():
    """Melee operator (attack_range_melee=True) cannot deploy on ELEVATED tile."""
    w = _world_with_elevated()
    op = make_liskarm()   # Defender — melee
    op.position = (1.0, 1.0)   # elevated tile
    result = w.deploy(op)
    assert result is False, "Melee must not deploy on elevated"
    assert not op.deployed


def test_ranged_blocked_from_ground_tile():
    """Ranged operator (attack_range_melee=False) cannot deploy on GROUND tile."""
    w = _world_with_elevated()
    ang = make_angelina()   # Supporter — ranged
    ang.position = (1.0, 0.0)   # ground tile
    result = w.deploy(ang)
    assert result is False, "Ranged must not deploy on ground"
    assert not ang.deployed


def test_melee_allowed_on_ground_tile():
    """Melee operator can deploy on GROUND tile."""
    w = _world_with_elevated()
    op = make_liskarm()
    op.position = (1.0, 0.0)   # ground tile
    result = w.deploy(op)
    assert result is True, "Melee must be allowed on ground"
    assert op.deployed


def test_ranged_allowed_on_elevated_tile():
    """Ranged operator can deploy on ELEVATED tile."""
    w = _world_with_elevated()
    ang = make_angelina()
    ang.position = (1.0, 1.0)   # elevated tile
    result = w.deploy(ang)
    assert result is True, "Ranged must be allowed on elevated"
    assert ang.deployed


def test_tile_rejection_refunds_dp():
    """DP is refunded when deployment is rejected due to wrong tile type."""
    w = _world_with_elevated(dp=100)
    op = make_liskarm()
    op.position = (1.0, 1.0)   # wrong tile (elevated for melee)
    dp_before = w.global_state.dp
    w.deploy(op)
    assert w.global_state.dp == dp_before, "DP must be fully refunded on tile-type rejection"
