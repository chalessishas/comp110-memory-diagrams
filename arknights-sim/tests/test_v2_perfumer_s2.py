"""Perfumer S2 Soothing Fume — ATK +100% for 20s (doubles heal output).

Tests cover:
  - Skill configured correctly (duration=20, AUTO_TIME, requires_target)
  - ATK buff applied during skill (+100%)
  - ATK buff cleared after skill ends
  - Passive HoT talent still fires (backward compat)
  - make_perfumer(slot=None) produces skill-less Perfumer
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, SPGainMode, SkillTrigger
from core.systems import register_default_systems
from data.characters.perfumer import (
    make_perfumer, _S2_ATK_RATIO, _S2_SOURCE_TAG, _HEAL_RATE,
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


def _ally_stub(pos=(1, 1), hp=5000, max_hp=10000) -> object:
    """A low-HP ally Perfumer can target for healing."""
    from data.enemies import make_originium_slug as _slug
    # Reuse slug body but make it an ally by overriding faction
    from core.state.unit_state import UnitState
    from core.types import Faction, Profession, AttackType
    u = UnitState(
        name="AllyStub",
        faction=Faction.ALLY,
        max_hp=max_hp,
        atk=100,
        defence=0,
        res=0.0,
        atk_interval=99.0,
        move_speed=0.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=0,
    )
    u.hp = hp
    u.deployed = True
    u.position = (float(pos[0]), float(pos[1]))
    return u


# ---------------------------------------------------------------------------
# Test 1: S2 skill configured correctly
# ---------------------------------------------------------------------------

def test_perfumer_s2_skill_config():
    p = make_perfumer(slot="S2")
    assert p.skill is not None
    assert p.skill.name == "Soothing Fume"
    assert p.skill.duration == 20.0
    assert p.skill.sp_gain_mode == SPGainMode.AUTO_TIME
    assert p.skill.trigger == SkillTrigger.AUTO
    assert p.skill.requires_target


# ---------------------------------------------------------------------------
# Test 2: ATK buff +100% during skill
# ---------------------------------------------------------------------------

def test_perfumer_s2_atk_buff():
    w = _world()
    p = make_perfumer(slot="S2")
    p.deployed = True; p.position = (0.0, 1.0)
    w.add_unit(p)

    ally = _ally_stub(pos=(1, 1), hp=100, max_hp=10000)
    w.add_unit(ally)

    base_atk = p.effective_atk
    p.skill.sp = float(p.skill.sp_cost)
    w.tick()

    expected = int(p.atk * (1.0 + _S2_ATK_RATIO))
    assert p.effective_atk == expected, (
        f"S2 ATK +{_S2_ATK_RATIO:.0%} must give {expected}; got {p.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: ATK buff cleared after skill ends
# ---------------------------------------------------------------------------

def test_perfumer_s2_atk_buff_cleared():
    w = _world()
    p = make_perfumer(slot="S2")
    p.deployed = True; p.position = (0.0, 1.0)
    w.add_unit(p)

    ally = _ally_stub(pos=(1, 1), hp=100, max_hp=10000)
    w.add_unit(ally)

    base_atk = p.effective_atk
    p.skill.sp = float(p.skill.sp_cost)
    w.tick()  # fire

    for _ in range(int(TICK_RATE * 21)):  # past 20s duration
        w.tick()

    remaining = [b for b in p.buffs if b.source_tag == _S2_SOURCE_TAG]
    assert len(remaining) == 0, f"S2 ATK buff must be cleared; remaining={remaining}"
    assert p.effective_atk == base_atk, "ATK must return to base after S2"


# ---------------------------------------------------------------------------
# Test 4: Passive HoT talent still fires
# ---------------------------------------------------------------------------

def test_perfumer_s2_hot_talent_still_fires():
    """Lavender passive HoT must still tick when S2 is wired."""
    w = _world()
    p = make_perfumer(slot="S2")
    p.deployed = True; p.position = (0.0, 1.0)
    w.add_unit(p)

    # Low-HP ally to receive passive HoT
    ally = _ally_stub(pos=(1, 1), hp=100, max_hp=10000)
    w.add_unit(ally)

    hp_before = ally.hp
    # Run 10s worth of ticks — should accumulate HoT
    for _ in range(int(TICK_RATE * 10)):
        w.tick()

    expected_heal = int(p.atk * _HEAL_RATE * 10)
    assert ally.hp > hp_before, (
        f"Lavender HoT must heal ally over 10s; hp_before={hp_before}, hp_now={ally.hp}"
    )


# ---------------------------------------------------------------------------
# Test 5: slot=None produces skill-less Perfumer
# ---------------------------------------------------------------------------

def test_perfumer_no_slot_no_skill():
    p = make_perfumer(slot=None)
    assert p.skill is None
    assert len(p.talents) == 1, "Lavender talent must still be present"
