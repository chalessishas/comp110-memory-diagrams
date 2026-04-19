"""Warfarin S2 Sanguinelant — unconditional team ATK +35% for 10s."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis
from core.systems import register_default_systems
from data.characters.warfarin import make_warfarin
from data.characters.silverash import make_silverash


def _world() -> World:
    grid = TileGrid(width=6, height=2)
    for x in range(6):
        for y in range(2):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    register_default_systems(w)
    return w


def test_s2_fires_without_heal_target():
    """S2 must fire even when all allies are at full HP (requires_target=False)."""
    w = _world()
    warf = make_warfarin("S2")
    warf.deployed = True
    warf.position = (0.0, 0.0)
    warf.skill.sp = float(warf.skill.sp_cost)   # pre-charged
    w.add_unit(warf)

    sa = make_silverash("S3")
    sa.deployed = True
    sa.position = (2.0, 0.0)
    w.add_unit(sa)

    # No enemies, no injured allies — lockout would block a requires_target skill
    w.tick()

    assert warf.skill.active_remaining > 0, \
        "S2 must fire even with no heal target (requires_target=False)"
    assert not warf.skill.locked_out, "locked_out must be False after firing"


def test_s2_buffs_all_deployed_allies():
    """S2 on_start grants ATK+35% to every deployed ally including self."""
    w = _world()
    warf = make_warfarin("S2")
    warf.deployed = True
    warf.position = (0.0, 0.0)
    warf.skill.sp = float(warf.skill.sp_cost)
    w.add_unit(warf)

    sa = make_silverash("S3")
    sa.deployed = True
    sa.position = (2.0, 0.0)
    base_sa_atk = sa.effective_atk
    w.add_unit(sa)

    w.tick()  # S2 fires

    from math import floor
    for ally in [warf, sa]:
        atk_buffs = [b for b in ally.buffs if b.axis == BuffAxis.ATK
                     and b.source_tag == "warfarin_s2_atk"]
        assert atk_buffs, f"{ally.name} missing S2 ATK buff"

    expected_sa = int(floor(base_sa_atk * 1.35))
    assert sa.effective_atk == expected_sa, \
        f"SilverAsh buffed ATK should be {expected_sa}, got {sa.effective_atk}"


def test_s2_buffs_removed_on_end():
    """All S2 ATK buffs are cleaned up when skill expires."""
    w = _world()
    warf = make_warfarin("S2")
    warf.deployed = True
    warf.position = (0.0, 0.0)
    warf.skill.sp = float(warf.skill.sp_cost)
    warf.skill.duration = 0.5   # short for fast test
    w.add_unit(warf)

    sa = make_silverash("S3")
    sa.deployed = True
    sa.position = (2.0, 0.0)
    w.add_unit(sa)

    w.tick()  # S2 fires
    assert warf.skill.active_remaining > 0

    # Prevent re-fire and run past duration
    warf.skill.sp = 0.0
    for _ in range(TICK_RATE * 2):
        w.tick()

    assert warf.skill.active_remaining == 0.0
    for ally in [warf, sa]:
        leftovers = [b for b in ally.buffs if b.source_tag == "warfarin_s2_atk"]
        assert not leftovers, f"{ally.name} still has S2 buff after skill ended"
