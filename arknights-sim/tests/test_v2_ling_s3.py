"""Ling S3 "Draconic Inspiration" — summon Long Xian dragon, 30s AUTO.

Tests cover:
  - S3 configured correctly (slot, sp_cost, initial_sp, duration, AUTO trigger)
  - S3 activation adds Long Xian ally unit to world
  - Long Xian has correct base stats (HP=4000, ATK=900, DEF=200, block=2)
  - Dragon is recalled (alive=False) when S3 ends
  - Summon budget: at most 3 Long Xian summons per deployment
  - S2 regression (Dragon's Majesty)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, Faction, SkillTrigger, SPGainMode
from core.systems import register_default_systems
from data.characters.ling import (
    make_ling,
    _S3_TAG, _S3_DURATION, _LING_SUMMON_BUDGET,
    _LONG_XIAN_ATK, _LONG_XIAN_HP, _LONG_XIAN_DEF,
)


def _world(w: int = 8, h: int = 3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    l = make_ling(slot="S3")
    sk = l.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "Draconic Inspiration"
    assert sk.sp_cost == 55
    assert sk.initial_sp == 25
    assert sk.duration == _S3_DURATION
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.requires_target is False
    assert sk.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: S3 activation summons Long Xian into the world
# ---------------------------------------------------------------------------

def test_s3_summons_long_xian():
    w = _world()
    l = make_ling(slot="S3")
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    w.add_unit(l)

    allies_before = len([u for u in w.units if u.faction == Faction.ALLY and u is not l])
    l.skill.sp = float(l.skill.sp_cost)
    w.tick()

    assert l.skill.active_remaining > 0.0, "S3 must be active"
    allies_after = [u for u in w.units if u.faction == Faction.ALLY and u is not l and u.alive]
    assert len(allies_after) == allies_before + 1, "Exactly one Long Xian must be summoned"


# ---------------------------------------------------------------------------
# Test 3: Long Xian has correct stats
# ---------------------------------------------------------------------------

def test_long_xian_stats():
    w = _world()
    l = make_ling(slot="S3")
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    w.add_unit(l)

    l.skill.sp = float(l.skill.sp_cost)
    w.tick()

    summons = [u for u in w.units if u.faction == Faction.ALLY and u is not l and u.alive]
    assert len(summons) == 1
    dragon = summons[0]
    assert dragon.name == "Long Xian"
    assert dragon.max_hp == _LONG_XIAN_HP
    assert dragon.atk == _LONG_XIAN_ATK
    assert dragon.defence == _LONG_XIAN_DEF
    assert dragon.block == 2


# ---------------------------------------------------------------------------
# Test 4: Dragon is recalled when S3 ends
# ---------------------------------------------------------------------------

def test_s3_long_xian_recalled_on_end():
    w = _world()
    l = make_ling(slot="S3")
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    w.add_unit(l)

    l.skill.sp = float(l.skill.sp_cost)
    w.tick()

    summon_id = l._ling_summon_id
    assert summon_id is not None, "Summon ID must be set after S3 starts"

    _ticks(w, _S3_DURATION + 1.0)

    assert l.skill.active_remaining == 0.0, "S3 must have ended"
    dragon = w.unit_by_id(summon_id)
    assert dragon is not None
    assert not dragon.alive, "Long Xian must be recalled (alive=False) on S3 end"


# ---------------------------------------------------------------------------
# Test 5: Summon budget capped at 3
# ---------------------------------------------------------------------------

def test_summon_budget_capped():
    """Ling can only summon _LING_SUMMON_BUDGET (3) Long Xian per deployment."""
    w = _world()
    l = make_ling(slot="S3")
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    l._summons_remaining = _LING_SUMMON_BUDGET
    w.add_unit(l)

    # Exhaust budget by forcing S3 start _LING_SUMMON_BUDGET times
    from data.characters.ling import _s3_on_start
    for _ in range(_LING_SUMMON_BUDGET):
        _s3_on_start(w, l)

    # One more attempt should be a no-op
    summons_before = [u for u in w.units if u.faction == Faction.ALLY and u is not l and u.alive]
    _s3_on_start(w, l)
    summons_after = [u for u in w.units if u.faction == Faction.ALLY and u is not l and u.alive]

    assert len(summons_after) == len(summons_before), "Budget exhausted: 4th summon must not spawn"


# ---------------------------------------------------------------------------
# Test 6: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    l = make_ling(slot="S2")
    sk = l.skill
    assert sk is not None
    assert sk.slot == "S2"
    assert sk.name == "Dragon's Majesty"
    assert sk.sp_cost == 35
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
