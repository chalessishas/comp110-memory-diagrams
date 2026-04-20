"""Beanstalk — S1 +8 DP instant, S2 12 DP/15s drip + block=0."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.beanstalk import make_beanstalk, _S1_DP, _S2_DP_TOTAL, _S2_DURATION


def _world(dp: float = 0.0) -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    w.global_state.dp = dp
    register_default_systems(w)
    return w


def _deploy(w, op, pos=(0.0, 1.0)):
    op.deployed = True
    op.position = pos
    op.atk_cd = 999.0
    w.add_unit(op)
    return op


# ---------------------------------------------------------------------------
# Test 1: Talent registered
# ---------------------------------------------------------------------------

def test_beanstalk_talent_registered():
    b = make_beanstalk()
    assert len(b.talents) == 1
    assert b.talents[0].name == "Professional Breeder"


# ---------------------------------------------------------------------------
# Test 2: S1 grants +8 DP immediately on activation
# ---------------------------------------------------------------------------

def test_beanstalk_s1_grants_dp():
    """S1 Sentinel Command: instant +8 DP on skill activation."""
    w = _world(dp=10.0)
    b = make_beanstalk(slot="S1")
    _deploy(w, b)

    dp_before = w.global_state.dp
    b.skill.sp = b.skill.sp_cost
    w.tick()

    assert w.global_state.dp == dp_before + _S1_DP, (
        f"S1 must give +{_S1_DP} DP; got {w.global_state.dp - dp_before}"
    )


# ---------------------------------------------------------------------------
# Test 3: S1 fires without target (requires_target=False)
# ---------------------------------------------------------------------------

def test_beanstalk_s1_fires_without_target():
    """S1 must fire even when no enemies are deployed."""
    w = _world(dp=0.0)
    b = make_beanstalk(slot="S1")
    _deploy(w, b)

    b.skill.sp = b.skill.sp_cost
    w.tick()

    assert w.global_state.dp == _S1_DP, "S1 must fire without enemy target"


# ---------------------------------------------------------------------------
# Test 4: S2 drips ~12 DP over 15s
# ---------------------------------------------------------------------------

def test_beanstalk_s2_dp_drip():
    """S2 Everyone Together: 12 DP total over 15s."""
    w = _world(dp=0.0)
    b = make_beanstalk(slot="S2")
    _deploy(w, b)

    b.skill.sp = b.skill.sp_cost
    # Run through full S2 duration + a few extra ticks
    for _ in range(TICK_RATE * int(_S2_DURATION) + 5):
        w.tick()

    # Allow ±1 DP rounding tolerance
    assert abs(w.global_state.dp - _S2_DP_TOTAL) <= 1, (
        f"S2 must drip ~{_S2_DP_TOTAL} DP; got {w.global_state.dp}"
    )


# ---------------------------------------------------------------------------
# Test 5: S2 sets block=0 while active
# ---------------------------------------------------------------------------

def test_beanstalk_s2_block_zero():
    """During S2, Beanstalk's block is set to 0."""
    w = _world(dp=0.0)
    b = make_beanstalk(slot="S2")
    _deploy(w, b)

    assert b.block == 1, "Block must be 1 before S2"
    b.skill.sp = b.skill.sp_cost
    w.tick()

    assert b.skill.active_remaining > 0.0, "S2 must be active"
    assert b.block == 0, "Block must be 0 while S2 is active"


# ---------------------------------------------------------------------------
# Test 6: S2 restores block on end
# ---------------------------------------------------------------------------

def test_beanstalk_s2_block_restored():
    """After S2 expires, block returns to 1."""
    w = _world(dp=0.0)
    b = make_beanstalk(slot="S2")
    _deploy(w, b)

    b.skill.sp = b.skill.sp_cost
    w.tick()

    for _ in range(TICK_RATE * int(_S2_DURATION) + 2):
        w.tick()

    assert b.skill.active_remaining == 0.0, "S2 must have expired"
    assert b.block == 1, "Block must restore to 1 after S2 ends"
