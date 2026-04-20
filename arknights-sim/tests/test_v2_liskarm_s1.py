"""Liskarm S1 Overcharge — DEF +50% for 35s.

Tests cover:
  - Skill configured correctly (duration=35, AUTO_TIME, requires_target)
  - DEF buff applied during skill (+50%)
  - DEF buff cleared after skill ends
  - Lightning Discharge talent still fires (backward compat)
  - make_liskarm(slot=None) produces skill-less Liskarm
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, SPGainMode, SkillTrigger
from core.systems import register_default_systems
from data.characters.liskarm import (
    make_liskarm, _S1_DEF_RATIO, _S1_SOURCE_TAG,
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


def _slug(pos=(0, 1), hp=9999, atk=500) -> object:
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 20)
    e.max_hp = hp; e.hp = hp; e.atk = atk; e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: S1 skill configured correctly
# ---------------------------------------------------------------------------

def test_liskarm_s1_skill_config():
    lisk = make_liskarm(slot="S1")
    assert lisk.skill is not None
    assert lisk.skill.name == "Overcharge"
    assert lisk.skill.duration == 35.0
    assert lisk.skill.sp_gain_mode == SPGainMode.AUTO_TIME
    assert lisk.skill.trigger == SkillTrigger.AUTO
    assert lisk.skill.requires_target


# ---------------------------------------------------------------------------
# Test 2: DEF buff +50% during skill
# ---------------------------------------------------------------------------

def test_liskarm_s1_def_buff():
    w = _world()
    lisk = make_liskarm(slot="S1")
    lisk.deployed = True; lisk.position = (0.0, 1.0)
    w.add_unit(lisk)

    slug = _slug(pos=(0, 1))
    w.add_unit(slug)

    base_def = lisk.effective_def
    lisk.skill.sp = float(lisk.skill.sp_cost)
    w.tick()

    expected = int(lisk.defence * (1.0 + _S1_DEF_RATIO))
    assert lisk.effective_def == expected, (
        f"S1 DEF +{_S1_DEF_RATIO:.0%} must give {expected}; got {lisk.effective_def}"
    )


# ---------------------------------------------------------------------------
# Test 3: DEF buff cleared after skill ends
# ---------------------------------------------------------------------------

def test_liskarm_s1_def_buff_cleared():
    w = _world()
    lisk = make_liskarm(slot="S1")
    lisk.deployed = True; lisk.position = (0.0, 1.0)
    w.add_unit(lisk)

    slug = _slug(pos=(0, 1))
    w.add_unit(slug)

    base_def = lisk.effective_def
    lisk.skill.sp = float(lisk.skill.sp_cost)
    w.tick()  # fire

    for _ in range(int(TICK_RATE * 36)):  # past 35s
        w.tick()

    remaining = [b for b in lisk.buffs if b.source_tag == _S1_SOURCE_TAG]
    assert len(remaining) == 0, f"S1 DEF buff must be cleared; remaining={remaining}"
    assert lisk.effective_def == base_def, "DEF must return to base after S1"


# ---------------------------------------------------------------------------
# Test 4: Lightning Discharge talent still fires
# ---------------------------------------------------------------------------

def test_liskarm_s1_talent_still_fires():
    """Lightning Discharge must still proc when S1 is wired."""
    w = _world()
    lisk = make_liskarm(slot="S1")
    lisk.deployed = True; lisk.position = (0.0, 1.0); lisk.atk_cd = 999.0
    w.add_unit(lisk)

    attacker = _slug(pos=(0, 1), atk=200, hp=50000)
    w.add_unit(attacker)

    hp_before = attacker.hp
    lisk.take_damage(100)  # trigger on_hit_received
    w.tick()

    assert attacker.hp < hp_before, "Lightning Discharge arc must hit attacker"


# ---------------------------------------------------------------------------
# Test 5: slot=None produces skill-less Liskarm
# ---------------------------------------------------------------------------

def test_liskarm_no_slot_no_skill():
    lisk = make_liskarm(slot=None)
    assert lisk.skill is None
    assert len(lisk.talents) == 1, "Lightning Discharge talent must still be present"
