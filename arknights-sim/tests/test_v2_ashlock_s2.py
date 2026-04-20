"""Ashlock S2 Torrent — ATK +80% + forced ranged mode for 25s.

Tests cover:
  - Skill configured correctly (duration=25, requires_target=False)
  - ATK buff applied during skill (+80%)
  - _force_ranged_mode True during skill, False after
  - ATK buff cleared after skill ends
  - make_ashlock(slot=None) produces skill-less Ashlock
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, SPGainMode, SkillTrigger
from core.systems import register_default_systems
from data.characters.ashlock import (
    make_ashlock, _S2_ATK_RATIO, _S2_SOURCE_TAG,
)


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


# ---------------------------------------------------------------------------
# Test 1: S2 skill configured correctly
# ---------------------------------------------------------------------------

def test_ashlock_s2_skill_config():
    a = make_ashlock(slot="S2")
    assert a.skill is not None
    assert a.skill.name == "Torrent"
    assert a.skill.duration == 25.0
    assert a.skill.sp_gain_mode == SPGainMode.AUTO_TIME
    assert a.skill.trigger == SkillTrigger.AUTO
    assert not a.skill.requires_target   # fires unconditionally (no target needed)


# ---------------------------------------------------------------------------
# Test 2: ATK buff +80% during skill
# ---------------------------------------------------------------------------

def test_ashlock_s2_atk_buff():
    from core.types import BuffAxis, BuffStack
    w = _world()
    a = make_ashlock(slot="S2")
    a.deployed = True; a.position = (0.0, 1.0)
    w.add_unit(a)

    a.skill.sp = float(a.skill.sp_cost)
    w.tick()

    # Check the S2 buff is present with correct value (talent also fires on same tick)
    s2_buff = next((b for b in a.buffs if b.source_tag == _S2_SOURCE_TAG), None)
    assert s2_buff is not None, "S2 ATK buff must be applied"
    assert s2_buff.axis == BuffAxis.ATK
    assert s2_buff.stack == BuffStack.RATIO
    assert s2_buff.value == _S2_ATK_RATIO


# ---------------------------------------------------------------------------
# Test 3: _force_ranged_mode is True during skill, False after
# ---------------------------------------------------------------------------

def test_ashlock_s2_force_ranged_during_skill():
    w = _world()
    a = make_ashlock(slot="S2")
    a.deployed = True; a.position = (0.0, 1.0)
    w.add_unit(a)

    assert not getattr(a, "_force_ranged_mode", False), "Must be False before skill"

    a.skill.sp = float(a.skill.sp_cost)
    w.tick()  # fire

    assert getattr(a, "_force_ranged_mode", False), "Must be True during skill"

    for _ in range(int(TICK_RATE * 26)):  # past 25s
        w.tick()

    assert not getattr(a, "_force_ranged_mode", False), "Must be False after skill ends"


# ---------------------------------------------------------------------------
# Test 4: ATK buff cleared after skill ends
# ---------------------------------------------------------------------------

def test_ashlock_s2_atk_buff_cleared():
    w = _world()
    a = make_ashlock(slot="S2")
    a.deployed = True; a.position = (0.0, 1.0)
    w.add_unit(a)

    base_atk = a.effective_atk
    a.skill.sp = float(a.skill.sp_cost)
    w.tick()

    for _ in range(int(TICK_RATE * 26)):
        w.tick()

    remaining = [b for b in a.buffs if b.source_tag == _S2_SOURCE_TAG]
    assert len(remaining) == 0, f"S2 buff must be cleared; remaining={remaining}"
    assert a.effective_atk == base_atk, "ATK must return to base after S2"


# ---------------------------------------------------------------------------
# Test 5: slot=None produces skill-less Ashlock
# ---------------------------------------------------------------------------

def test_ashlock_no_slot_no_skill():
    a = make_ashlock(slot=None)
    assert a.skill is None
    assert a.archetype.value == "def_fortress"
