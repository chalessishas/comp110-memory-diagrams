"""Gravel S1 Hidden Blade — ATK +100% for 15s.

Tests cover:
  - Skill configured correctly (duration=15, AUTO_TIME, requires_target)
  - ATK buff applied during skill (+100%)
  - ATK buff cleared after skill ends
  - Tactical Concealment talent still fires (backward compat)
  - make_gravel(slot=None) produces skill-less Gravel
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, SPGainMode, SkillTrigger
from core.systems import register_default_systems
from data.characters.gravel import (
    make_gravel, _S1_ATK_RATIO, _S1_SOURCE_TAG,
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


def _slug(pos=(0, 1), hp=9999) -> object:
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 20)
    e.max_hp = hp; e.hp = hp; e.atk = 0; e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: S1 skill configured correctly
# ---------------------------------------------------------------------------

def test_gravel_s1_skill_config():
    g = make_gravel(slot="S1")
    assert g.skill is not None
    assert g.skill.name == "Hidden Blade"
    assert g.skill.duration == 15.0
    assert g.skill.sp_gain_mode == SPGainMode.AUTO_TIME
    assert g.skill.trigger == SkillTrigger.AUTO
    assert g.skill.requires_target


# ---------------------------------------------------------------------------
# Test 2: ATK buff +100% during skill
# ---------------------------------------------------------------------------

def test_gravel_s1_atk_buff():
    w = _world()
    g = make_gravel(slot="S1")
    g.deployed = True; g.position = (0.0, 1.0)
    w.add_unit(g)

    slug = _slug(pos=(0, 1))
    w.add_unit(slug)

    base_atk = g.effective_atk
    g.skill.sp = float(g.skill.sp_cost)
    w.tick()

    expected = int(g.atk * (1.0 + _S1_ATK_RATIO))
    assert g.effective_atk == expected, (
        f"S1 ATK +{_S1_ATK_RATIO:.0%} must give {expected}; got {g.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: ATK buff cleared after skill ends
# ---------------------------------------------------------------------------

def test_gravel_s1_atk_buff_cleared():
    w = _world()
    g = make_gravel(slot="S1")
    g.deployed = True; g.position = (0.0, 1.0)
    w.add_unit(g)

    slug = _slug(pos=(0, 1))
    w.add_unit(slug)

    base_atk = g.effective_atk
    g.skill.sp = float(g.skill.sp_cost)
    w.tick()  # fire

    for _ in range(int(TICK_RATE * 16)):  # past 15s duration
        w.tick()

    remaining = [b for b in g.buffs if b.source_tag == _S1_SOURCE_TAG]
    assert len(remaining) == 0, f"S1 ATK buff must be cleared; remaining={remaining}"
    assert g.effective_atk == base_atk, "ATK must return to base after S1"


# ---------------------------------------------------------------------------
# Test 4: Tactical Concealment talent still activates after add_unit
# ---------------------------------------------------------------------------

def test_gravel_s1_talent_still_activates():
    """Tactical Concealment must still reduce damage when S1 is wired."""
    w = _world()
    g = make_gravel(slot="S1")
    g.deployed = True; g.position = (0.0, 1.0)
    w.add_unit(g)

    # With fresh deploy shield active, 100 raw damage → only 20 dealt
    hp_before = g.hp
    g.take_damage(100)
    assert g.hp > hp_before - 100, "Tactical Concealment must reduce damage while shield is active"


# ---------------------------------------------------------------------------
# Test 5: slot=None produces skill-less Gravel
# ---------------------------------------------------------------------------

def test_gravel_no_slot_no_skill():
    g = make_gravel(slot=None)
    assert g.skill is None
    assert len(g.talents) == 1, "Tactical Concealment talent must still be present"
