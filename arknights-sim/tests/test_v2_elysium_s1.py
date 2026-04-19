"""Elysium S1 Support γ: 18 DP over 8s, block suppressed during skill."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.elysium import make_elysium


def _world() -> World:
    grid = TileGrid(width=4, height=1)
    for i in range(4):
        grid.set_tile(TileState(x=i, y=0, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp = 0
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def test_elysium_no_battle_start_dp():
    """Standard Bearer does not grant battle-start DP."""
    w = _world()
    w.add_unit(make_elysium("S1"))
    assert w.global_state.dp == 0


def test_elysium_s1_fires_without_target():
    """S1 fires auto at sp_cost=35, initial_sp=10 → fires after 25s."""
    w = _world()
    el = make_elysium("S1")
    el.deployed = True
    el.position = (0.0, 0.0)
    el.skill.sp = float(el.skill.initial_sp)
    w.add_unit(el)

    fired = False
    for _ in range(TICK_RATE * 30):
        w.tick()
        if el.skill.fire_count >= 1:
            fired = True
            break

    assert fired, "Elysium S1 should fire without needing a target"


def test_elysium_s1_grants_18_dp_over_duration():
    """S1 generates approximately 18 DP over its 8s active window."""
    w = _world()
    el = make_elysium("S1")
    el.deployed = True
    el.position = (0.0, 0.0)
    w.add_unit(el)

    for _ in range(TICK_RATE * 50):
        w.tick()
        if el.skill.fire_count >= 1 and el.skill.active_remaining <= 0:
            break

    for _ in range(5):
        w.tick()

    assert 17 <= w.global_state.dp <= 19, (
        f"Expected ~18 DP from S1 drip, got {w.global_state.dp}"
    )


def test_elysium_block_suppressed_during_skill():
    """Block drops to 0 when skill is active, restores to 1 on skill end."""
    w = _world()
    el = make_elysium("S1")
    el.deployed = True
    el.position = (0.0, 0.0)
    el.skill.sp = float(el.skill.initial_sp)
    w.add_unit(el)

    assert el.block == 1

    for _ in range(TICK_RATE * 30):
        w.tick()
        if el.skill.fire_count >= 1 and el.skill.active_remaining > 0:
            break

    assert el.block == 0, "Block must be 0 while S1 is active"

    for _ in range(TICK_RATE * 10):
        w.tick()
        if el.skill.active_remaining <= 0:
            break

    assert el.block == 1, "Block must restore to 1 after S1 ends"


def test_elysium_generates_more_dp_than_myrtle():
    """Elysium S1 (18 DP) generates more DP per activation than Myrtle S1 (14 DP)."""
    from data.characters.myrtle import make_myrtle

    def _run_skill(op, ticks_budget):
        w = _world()
        op.deployed = True
        op.position = (0.0, 0.0)
        w.add_unit(op)
        for _ in range(ticks_budget):
            w.tick()
            if op.skill.fire_count >= 1 and op.skill.active_remaining <= 0:
                break
        for _ in range(5):
            w.tick()
        return w.global_state.dp

    myrtle_dp = _run_skill(make_myrtle("S1"), TICK_RATE * 25)
    elysium_dp = _run_skill(make_elysium("S1"), TICK_RATE * 50)

    assert elysium_dp > myrtle_dp, (
        f"Elysium S1 ({elysium_dp} DP) should exceed Myrtle S1 ({myrtle_dp} DP) per activation"
    )
