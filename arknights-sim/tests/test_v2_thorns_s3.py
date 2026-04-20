"""Thorns S3 "Annihilation" — attack-all-in-range mode for 30s, AUTO trigger.

Tests cover:
  - S3 configured correctly (sp_cost=40, AUTO trigger, 30s, requires_target=False)
  - _attack_all_in_range flag set True on S3 start
  - Flag cleared False on S3 end
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, SPGainMode
from core.systems import register_default_systems
from data.characters.thorns import make_thorns, _S3_TAG


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    t = make_thorns(slot="S3")
    assert t.skill is not None
    assert t.skill.slot == "S3"
    assert t.skill.name == "Annihilation"
    assert t.skill.sp_cost == 40
    assert t.skill.initial_sp == 20
    assert t.skill.duration == 30.0
    from core.types import SkillTrigger
    assert t.skill.trigger == SkillTrigger.AUTO
    assert t.skill.sp_gain_mode == SPGainMode.AUTO_TIME
    assert not t.skill.requires_target
    assert t.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: _attack_all_in_range set True on S3 start (fires without enemies)
# ---------------------------------------------------------------------------

def test_s3_attack_all_in_range_on():
    w = _world()
    t = make_thorns(slot="S3")
    t.deployed = True; t.position = (0.0, 1.0); t.atk_cd = 999.0
    w.add_unit(t)
    assert not getattr(t, "_attack_all_in_range", False), "Flag must be off before S3"

    # requires_target=False → fires without enemy on next tick
    t.skill.sp = float(t.skill.sp_cost)
    w.tick()

    assert t.skill.active_remaining > 0.0, "S3 must have fired"
    assert getattr(t, "_attack_all_in_range", False), "_attack_all_in_range must be True during S3"


# ---------------------------------------------------------------------------
# Test 3: Flag cleared on S3 end
# ---------------------------------------------------------------------------

def test_s3_attack_all_in_range_off_on_end():
    w = _world()
    t = make_thorns(slot="S3")
    t.deployed = True; t.position = (0.0, 1.0); t.atk_cd = 999.0
    w.add_unit(t)

    t.skill.sp = float(t.skill.sp_cost)
    w.tick()
    assert t.skill.active_remaining > 0.0, "S3 must have fired"

    _ticks(w, 31.0)

    assert t.skill.active_remaining == 0.0, "S3 must have ended"
    assert not getattr(t, "_attack_all_in_range", False), "Flag must be False after S3"


# ---------------------------------------------------------------------------
# Test 4: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    t = make_thorns(slot="S2")
    assert t.skill is not None and t.skill.slot == "S2"
    assert t.skill.name == "Thorn Field"
    assert t.skill.sp_cost == 35
