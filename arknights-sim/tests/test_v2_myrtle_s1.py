"""Myrtle S1 Tactical Delivery: 14 DP over 8s, block suppressed during skill."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.myrtle import make_myrtle


def _world() -> World:
    grid = TileGrid(width=4, height=1)
    for i in range(4):
        grid.set_tile(TileState(x=i, y=0, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp = 0
    w.global_state.dp_gain_rate = 0.0  # isolate skill DP from natural gain
    register_default_systems(w)
    return w


def test_myrtle_no_battle_start_dp():
    """Myrtle does not grant battle-start DP (Standard Bearer ≠ Pioneer)."""
    w = _world()
    myrtle = make_myrtle("S1")
    w.add_unit(myrtle)
    assert w.global_state.dp == 0


def test_myrtle_s1_fires_without_target():
    """S1 fires auto at sp_cost=12 with initial_sp=6 → fires after 6s."""
    w = _world()
    myrtle = make_myrtle("S1")
    myrtle.deployed = True
    myrtle.position = (0.0, 0.0)
    myrtle.skill.sp = float(myrtle.skill.initial_sp)  # seed initial SP (normally via world.deploy)
    w.add_unit(myrtle)

    fired = False
    for _ in range(TICK_RATE * 8):
        w.tick()
        if myrtle.skill.fire_count >= 1:
            fired = True
            break

    assert fired, "Myrtle S1 should fire without needing a target"


def test_myrtle_s1_grants_14_dp_over_duration():
    """S1 generates approximately 14 DP over its 8s active window."""
    w = _world()
    myrtle = make_myrtle("S1")
    myrtle.deployed = True
    myrtle.position = (0.0, 0.0)
    w.add_unit(myrtle)

    # Wait for skill to fire and complete
    for _ in range(TICK_RATE * 20):
        w.tick()
        if myrtle.skill.fire_count >= 1 and myrtle.skill.active_remaining <= 0:
            break

    # Allow one extra tick for final fractional DP to flush
    for _ in range(5):
        w.tick()

    # 14 DP total (within ±1 for floating-point rounding)
    assert 13 <= w.global_state.dp <= 15, (
        f"Expected ~14 DP from S1 drip, got {w.global_state.dp}"
    )


def test_myrtle_block_suppressed_during_skill():
    """Block drops to 0 when skill is active, restores to 1 on skill end."""
    w = _world()
    myrtle = make_myrtle("S1")
    myrtle.deployed = True
    myrtle.position = (0.0, 0.0)
    myrtle.skill.sp = float(myrtle.skill.initial_sp)
    w.add_unit(myrtle)

    assert myrtle.block == 1, "Myrtle starts with block=1"

    # Wait for skill to fire
    for _ in range(TICK_RATE * 8):
        w.tick()
        if myrtle.skill.fire_count >= 1 and myrtle.skill.active_remaining > 0:
            break

    assert myrtle.block == 0, "Block must be 0 while S1 is active"

    # Wait for skill to end
    for _ in range(TICK_RATE * 10):
        w.tick()
        if myrtle.skill.active_remaining <= 0:
            break

    assert myrtle.block == 1, "Block must restore to 1 after S1 ends"


def test_myrtle_s1_refires():
    """After S1 ends, SP resets to 0 and accumulates again for a second fire."""
    w = _world()
    myrtle = make_myrtle("S1")
    myrtle.deployed = True
    myrtle.position = (0.0, 0.0)
    w.add_unit(myrtle)

    for _ in range(TICK_RATE * 40):
        w.tick()
        if myrtle.skill.fire_count >= 2:
            break

    assert myrtle.skill.fire_count >= 2, "S1 should re-fire after SP recharges"
