"""Nearl S2 Justice — dual ATK+100% / DEF+55% buff for 30s.

Tests cover:
  - Skill configured correctly (duration=30, AUTO_TIME, requires_target)
  - ATK buff applied during skill (+100%)
  - DEF buff applied during skill (+55%)
  - Both buffs cleared after skill ends
  - Holy Knight talent still fires (backward compat — make_nearl(slot=None) still works)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, SPGainMode, SkillTrigger
from core.systems import register_default_systems
from data.characters.nearl import (
    make_nearl, _S2_ATK_RATIO, _S2_DEF_RATIO, _S2_SOURCE_TAG, _HEAL_INTERVAL,
)
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(pos=(1, 1), hp=99999) -> object:
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 20)
    e.max_hp = hp; e.hp = hp; e.atk = 0; e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Skill configured correctly
# ---------------------------------------------------------------------------

def test_nearl_s2_skill_config():
    n = make_nearl(slot="S2")
    assert n.skill is not None
    assert n.skill.name == "Justice"
    assert n.skill.duration == 30.0
    assert n.skill.sp_gain_mode == SPGainMode.AUTO_TIME
    assert n.skill.trigger == SkillTrigger.AUTO
    assert n.skill.requires_target


# ---------------------------------------------------------------------------
# Test 2: ATK buff +100% during skill
# ---------------------------------------------------------------------------

def test_nearl_s2_atk_buff():
    w = _world()
    n = make_nearl(slot="S2")
    n.deployed = True; n.position = (0.0, 1.0)
    w.add_unit(n)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    base_atk = n.effective_atk
    n.skill.sp = float(n.skill.sp_cost)
    w.tick()

    expected = int(base_atk * (1.0 + _S2_ATK_RATIO))
    assert n.effective_atk == expected, (
        f"S2 ATK +{_S2_ATK_RATIO:.0%} must give {expected}; got {n.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: DEF buff +55% during skill
# ---------------------------------------------------------------------------

def test_nearl_s2_def_buff():
    w = _world()
    n = make_nearl(slot="S2")
    n.deployed = True; n.position = (0.0, 1.0)
    w.add_unit(n)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    base_def = n.effective_def
    n.skill.sp = float(n.skill.sp_cost)
    w.tick()

    expected = int(n.defence * (1.0 + _S2_DEF_RATIO))
    assert n.effective_def == expected, (
        f"S2 DEF +{_S2_DEF_RATIO:.0%} must give {expected}; got {n.effective_def}"
    )


# ---------------------------------------------------------------------------
# Test 4: Both buffs cleared after 30s
# ---------------------------------------------------------------------------

def test_nearl_s2_buffs_cleared_after_skill():
    w = _world()
    n = make_nearl(slot="S2")
    n.deployed = True; n.position = (0.0, 1.0)
    w.add_unit(n)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    base_atk = n.effective_atk
    base_def = n.effective_def
    n.skill.sp = float(n.skill.sp_cost)
    w.tick()  # fire

    for _ in range(int(TICK_RATE * 31)):  # past 30s duration
        w.tick()

    remaining = [b for b in n.buffs if b.source_tag == _S2_SOURCE_TAG]
    assert len(remaining) == 0, f"Both S2 buffs must be cleared; remaining={remaining}"
    assert n.effective_atk == base_atk, f"ATK must return to base after S2"
    assert n.effective_def == base_def, f"DEF must return to base after S2"


# ---------------------------------------------------------------------------
# Test 5: make_nearl(slot=None) still has no skill (backward compat)
# ---------------------------------------------------------------------------

def test_nearl_no_slot_has_no_skill():
    n = make_nearl(slot=None)
    assert n.skill is None, "slot=None must produce a skill-less Nearl"
    assert len(n.talents) == 1, "Talent must still be present"
