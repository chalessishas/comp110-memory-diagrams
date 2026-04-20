"""Courier (讯使) — Vanguard Tactician: S1 instant DP, S2 DP drip."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, RoleArchetype
from core.systems import register_default_systems
from data.characters.courier import make_courier


def _world() -> World:
    grid = TileGrid(width=4, height=3)
    for x in range(4):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


# ---------------------------------------------------------------------------
# Test 1: Courier archetype is VAN_TACTICIAN
# ---------------------------------------------------------------------------

def test_courier_archetype():
    assert make_courier().archetype == RoleArchetype.VAN_TACTICIAN


# ---------------------------------------------------------------------------
# Test 2: S1 grants DP instantly on activation
# ---------------------------------------------------------------------------

def test_courier_s1_instant_dp():
    """S1 fires and immediately grants 8 DP without a duration."""
    w = _world()
    courier = make_courier(slot="S1")
    courier.deployed = True
    courier.position = (0.0, 1.0)
    courier.atk_cd = 999.0
    w.add_unit(courier)

    # Charge SP to full
    courier.skill.sp = courier.skill.sp_cost

    dp_before = w.global_state.dp
    w.tick()   # SKILL phase fires S1

    assert courier.skill.active_remaining == 0.0, "S1 is instant (no duration)"
    assert w.global_state.dp == dp_before + 8, (
        f"S1 must grant 8 DP instantly; got {w.global_state.dp - dp_before}"
    )


# ---------------------------------------------------------------------------
# Test 3: S1 SP resets and recharges after firing
# ---------------------------------------------------------------------------

def test_courier_s1_sp_resets():
    """After S1 fires, SP should reset to 0 and begin recharging."""
    w = _world()
    courier = make_courier(slot="S1")
    courier.deployed = True
    courier.position = (0.0, 1.0)
    courier.atk_cd = 999.0
    w.add_unit(courier)

    courier.skill.sp = courier.skill.sp_cost
    w.tick()  # S1 fires

    assert courier.skill.sp < courier.skill.sp_cost, "SP must reset after S1 fires"


# ---------------------------------------------------------------------------
# Test 4: S2 generates ~12 DP over 15 seconds
# ---------------------------------------------------------------------------

def test_courier_s2_dp_drip():
    """S2 generates approximately 12 DP over its 15s duration."""
    w = _world()
    courier = make_courier(slot="S2")
    courier.deployed = True
    courier.position = (0.0, 1.0)
    courier.atk_cd = 999.0
    w.add_unit(courier)

    courier.skill.sp = courier.skill.sp_cost
    dp_before = w.global_state.dp

    # Run 16s (15s skill duration + 1s buffer)
    for _ in range(TICK_RATE * 16):
        w.tick()

    dp_gained = w.global_state.dp - dp_before
    assert 10 <= dp_gained <= 14, (
        f"S2 should drip ~12 DP over 15s; got {dp_gained}"
    )


# ---------------------------------------------------------------------------
# Test 5: S2 sets block=0 during active and restores on end
# ---------------------------------------------------------------------------

def test_courier_s2_block_removed_during_skill():
    """S2 sets block=0 at start and restores original block when it ends."""
    w = _world()
    courier = make_courier(slot="S2")
    courier.deployed = True
    courier.position = (0.0, 1.0)
    courier.atk_cd = 999.0
    w.add_unit(courier)

    courier.skill.sp = courier.skill.sp_cost
    w.tick()  # S2 fires

    assert courier.skill.active_remaining > 0.0, "S2 must be active"
    assert courier.block == 0, "block must be 0 during S2"

    # Advance past full duration
    for _ in range(TICK_RATE * 16):
        w.tick()

    assert courier.skill.active_remaining == 0.0, "S2 must have ended"
    assert courier.block == 2, "block must be restored to 2 after S2"
