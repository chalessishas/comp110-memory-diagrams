"""Vigil S3 'Packleader's Dignity': 12 DP over 15s drip, block=0 during skill."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, RoleArchetype
from core.systems import register_default_systems
from data.characters.vigil import make_vigil


def _world() -> World:
    grid = TileGrid(width=4, height=3)
    for x in range(4):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def test_vigil_archetype():
    assert make_vigil().archetype == RoleArchetype.VAN_TACTICIAN


def test_vigil_s3_fires_auto():
    """S3 fires automatically once SP reaches sp_cost."""
    w = _world()
    v = make_vigil(slot="S3")
    v.deployed = True
    v.position = (0.0, 1.0)
    v.atk_cd = 999.0
    w.add_unit(v)

    v.skill.sp = v.skill.sp_cost
    w.tick()

    assert v.skill.active_remaining > 0.0, "S3 must be active after SP reaches cost"


def test_vigil_s3_block_zero_during_skill():
    """block drops to 0 when S3 is active."""
    w = _world()
    v = make_vigil(slot="S3")
    v.deployed = True
    v.position = (0.0, 1.0)
    v.atk_cd = 999.0
    w.add_unit(v)

    v.skill.sp = v.skill.sp_cost
    w.tick()  # S3 fires

    assert v.block == 0, "block must be 0 during S3"


def test_vigil_s3_dp_drip():
    """S3 generates ~12 DP over 15s duration."""
    w = _world()
    v = make_vigil(slot="S3")
    v.deployed = True
    v.position = (0.0, 1.0)
    v.atk_cd = 999.0
    w.add_unit(v)

    v.skill.sp = v.skill.sp_cost
    dp_before = w.global_state.dp

    for _ in range(TICK_RATE * 16):
        w.tick()

    dp_gained = w.global_state.dp - dp_before
    assert 10 <= dp_gained <= 14, (
        f"S3 should drip ~12 DP over 15s; got {dp_gained}"
    )


def test_vigil_s3_block_restored_on_end():
    """block returns to 1 when S3 ends."""
    w = _world()
    v = make_vigil(slot="S3")
    v.deployed = True
    v.position = (0.0, 1.0)
    v.atk_cd = 999.0
    w.add_unit(v)

    v.skill.sp = v.skill.sp_cost
    w.tick()  # S3 fires

    for _ in range(TICK_RATE * 16):
        w.tick()

    assert v.skill.active_remaining == 0.0, "S3 must have ended"
    assert v.block == 1, "block must be restored to 1 after S3"
