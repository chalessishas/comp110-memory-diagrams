"""Fang S1 Assault — ATK +50% for 40s.

Tests cover:
  - Skill configured correctly (duration=40, AUTO_TIME, requires_target)
  - ATK buff applied during skill (+50%)
  - ATK buff cleared after skill ends
  - Charger DP-on-kill talent still fires (backward compat)
  - make_fang(slot=None) produces skill-less Fang
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, SPGainMode, SkillTrigger
from core.systems import register_default_systems
from data.characters.fang import (
    make_fang, _S1_ATK_RATIO, _S1_SOURCE_TAG,
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


def _slug(pos=(0, 1), hp=500) -> object:
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 20)
    e.max_hp = hp; e.hp = hp; e.atk = 0; e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: S1 skill configured correctly
# ---------------------------------------------------------------------------

def test_fang_s1_skill_config():
    f = make_fang(slot="S1")
    assert f.skill is not None
    assert f.skill.name == "Assault"
    assert f.skill.duration == 40.0
    assert f.skill.sp_gain_mode == SPGainMode.AUTO_TIME
    assert f.skill.trigger == SkillTrigger.AUTO
    assert f.skill.requires_target


# ---------------------------------------------------------------------------
# Test 2: ATK buff +50% during skill
# ---------------------------------------------------------------------------

def test_fang_s1_atk_buff():
    w = _world()
    f = make_fang(slot="S1")
    f.deployed = True; f.position = (0.0, 1.0)
    w.add_unit(f)

    slug = _slug(pos=(0, 1))
    w.add_unit(slug)

    base_atk = f.effective_atk
    f.skill.sp = float(f.skill.sp_cost)
    w.tick()

    expected = int(f.atk * (1.0 + _S1_ATK_RATIO))
    assert f.effective_atk == expected, (
        f"S1 ATK +{_S1_ATK_RATIO:.0%} must give {expected}; got {f.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: ATK buff cleared after skill ends
# ---------------------------------------------------------------------------

def test_fang_s1_atk_buff_cleared():
    w = _world()
    f = make_fang(slot="S1")
    f.deployed = True; f.position = (0.0, 1.0)
    w.add_unit(f)

    slug = _slug(pos=(0, 1))
    w.add_unit(slug)

    base_atk = f.effective_atk
    f.skill.sp = float(f.skill.sp_cost)
    w.tick()  # fire

    for _ in range(int(TICK_RATE * 41)):  # past 40s duration
        w.tick()

    remaining = [b for b in f.buffs if b.source_tag == _S1_SOURCE_TAG]
    assert len(remaining) == 0, f"S1 ATK buff must be cleared; remaining={remaining}"
    assert f.effective_atk == base_atk, "ATK must return to base after S1"


# ---------------------------------------------------------------------------
# Test 4: Charger DP-on-kill talent still fires
# ---------------------------------------------------------------------------

def test_fang_s1_charger_talent_still_fires():
    """Charger DP-on-kill talent must still award 1 DP on kill when S1 is wired."""
    w = _world()
    f = make_fang(slot="S1")
    f.deployed = True; f.position = (0.0, 1.0); f.atk_cd = 0.0
    w.add_unit(f)

    slug = _slug(pos=(0, 1), hp=1)   # 1 HP — dies on first attack
    w.add_unit(slug)

    dp_before = w.global_state.dp
    for _ in range(int(TICK_RATE * 3)):
        w.tick()
        if not slug.alive:
            break

    assert not slug.alive, "Slug must die for DP-on-kill test"
    assert w.global_state.dp == dp_before + 1, (
        f"Charger talent must grant +1 DP on kill; dp_before={dp_before}, dp_now={w.global_state.dp}"
    )


# ---------------------------------------------------------------------------
# Test 5: slot=None produces skill-less Fang
# ---------------------------------------------------------------------------

def test_fang_no_slot_no_skill():
    f = make_fang(slot=None)
    assert f.skill is None
    assert len(f.talents) == 1, "Charger talent must still be present"
