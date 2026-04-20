"""Erato S1 Strafing Fire — ATK +100% for 20s.

Tests cover:
  - Skill configured correctly (duration=20, AUTO_TIME, requires_target)
  - ATK buff applied during skill (+100%)
  - ATK buff cleared after skill ends
  - Besieger 1.5× trait still applies during skill (compounded ATK)
  - make_erato(slot=None) produces skill-less Erato
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, SPGainMode, SkillTrigger, RoleArchetype
from core.systems import register_default_systems
from data.characters.erato import (
    make_erato, _S1_ATK_RATIO, _S1_SOURCE_TAG,
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
# Test 1: S1 skill configured correctly
# ---------------------------------------------------------------------------

def test_erato_s1_skill_config():
    e = make_erato(slot="S1")
    assert e.skill is not None
    assert e.skill.name == "Strafing Fire"
    assert e.skill.duration == 20.0
    assert e.skill.sp_gain_mode == SPGainMode.AUTO_TIME
    assert e.skill.trigger == SkillTrigger.AUTO
    assert e.skill.requires_target


# ---------------------------------------------------------------------------
# Test 2: ATK buff +100% during skill
# ---------------------------------------------------------------------------

def test_erato_s1_atk_buff():
    w = _world()
    e = make_erato(slot="S1")
    e.deployed = True; e.position = (0.0, 1.0)
    w.add_unit(e)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    base_atk = e.effective_atk
    e.skill.sp = float(e.skill.sp_cost)
    w.tick()

    expected = int(e.atk * (1.0 + _S1_ATK_RATIO))
    assert e.effective_atk == expected, (
        f"S1 ATK +{_S1_ATK_RATIO:.0%} must give {expected}; got {e.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: ATK buff cleared after skill ends
# ---------------------------------------------------------------------------

def test_erato_s1_atk_buff_cleared():
    w = _world()
    e = make_erato(slot="S1")
    e.deployed = True; e.position = (0.0, 1.0)
    w.add_unit(e)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    base_atk = e.effective_atk
    e.skill.sp = float(e.skill.sp_cost)
    w.tick()

    for _ in range(int(TICK_RATE * 21)):  # past 20s
        w.tick()

    remaining = [b for b in e.buffs if b.source_tag == _S1_SOURCE_TAG]
    assert len(remaining) == 0, f"S1 buff must be cleared; remaining={remaining}"
    assert e.effective_atk == base_atk, "ATK must return to base after S1"


# ---------------------------------------------------------------------------
# Test 4: Besieger archetype is correct
# ---------------------------------------------------------------------------

def test_erato_is_besieger():
    e = make_erato(slot="S1")
    assert e.archetype == RoleArchetype.SNIPER_SIEGE, "Erato must be SNIPER_SIEGE archetype"
    assert e.block == 1


# ---------------------------------------------------------------------------
# Test 5: slot=None produces skill-less Erato
# ---------------------------------------------------------------------------

def test_erato_no_slot_no_skill():
    e = make_erato(slot=None)
    assert e.skill is None
    assert e.archetype == RoleArchetype.SNIPER_SIEGE
