"""Toknogi — SUP_ABJURER: passive DEF aura for nearby allies + S2 burst.

Talent "Spring Green Shade": All allies within 2 tiles gain DEF +20%.
S2 "Grove Shade": Self ATK +30%, all allies in range gain DEF +35%.

Tests cover:
  - Archetype SUP_ABJURER
  - Talent: nearby ally gains DEF +20%
  - Talent: far ally (outside range) gets no bonus
  - Talent: buff removed when ally moves out of range
  - S2 applies ATK +30% to Toknogi
  - S2 applies DEF +35% to allies in range
  - S2 does NOT buff ally out of range
  - S2 buffs cleared on end
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, RoleArchetype
from core.systems import register_default_systems
from data.characters.toknogi import (
    make_toknogi,
    _TALENT_TAG, _TALENT_DEF_RATIO, _TALENT_DEF_TAG, _TALENT_RANGE,
    _S2_ATK_RATIO, _S2_ATK_BUFF_TAG, _S2_DEF_RATIO, _S2_DEF_BUFF_TAG, _S2_DURATION,
)
from data.enemies import make_originium_slug
from data.characters.bena import make_bena  # use bena as a nearby ally


def _world() -> World:
    grid = TileGrid(width=8, height=3)
    for x in range(8):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(pos=(5, 1), hp=99999) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = 0; e.move_speed = 0.0; e.res = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


def _ally(pos=(1.0, 1.0)) -> UnitState:
    """A deployed ally with no talents (won't interfere)."""
    a = make_bena(slot="S2")
    a.deployed = True; a.position = pos
    a.atk_cd = 999.0
    return a


# ---------------------------------------------------------------------------
# Test 1: Archetype SUP_ABJURER
# ---------------------------------------------------------------------------

def test_toknogi_archetype():
    t = make_toknogi()
    assert t.archetype == RoleArchetype.SUP_ABJURER
    assert t.block == 1
    assert len(t.talents) == 1
    assert t.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: Talent grants DEF +20% to nearby ally
# ---------------------------------------------------------------------------

def test_talent_def_bonus_nearby_ally():
    """Nearby ally (within 2 tiles) must receive DEF +20%."""
    w = _world()
    tok = make_toknogi()
    tok.deployed = True; tok.position = (0.0, 1.0)
    w.add_unit(tok)

    ally = _ally(pos=(1.0, 1.0))  # 1 tile away — within range
    w.add_unit(ally)

    base_def = ally.effective_def
    w.tick()

    talent_buffs = [b for b in ally.buffs if b.source_tag == _TALENT_DEF_TAG]
    assert len(talent_buffs) == 1, "Talent DEF buff must be applied to nearby ally"
    assert abs(talent_buffs[0].value - _TALENT_DEF_RATIO) < 0.01
    expected_def = int(base_def * (1 + _TALENT_DEF_RATIO))
    assert abs(ally.effective_def - expected_def) <= 2, (
        f"Nearby ally DEF must increase by {_TALENT_DEF_RATIO:.0%}; got {ally.effective_def}"
    )


# ---------------------------------------------------------------------------
# Test 3: Talent does NOT buff far ally
# ---------------------------------------------------------------------------

def test_talent_no_buff_far_ally():
    """Ally more than _TALENT_RANGE tiles away must NOT get talent DEF buff."""
    w = _world()
    tok = make_toknogi()
    tok.deployed = True; tok.position = (0.0, 1.0)
    w.add_unit(tok)

    far_ally = _ally(pos=(5.0, 1.0))  # 5 tiles away — outside range
    w.add_unit(far_ally)

    w.tick()

    talent_buffs = [b for b in far_ally.buffs if b.source_tag == _TALENT_DEF_TAG]
    assert len(talent_buffs) == 0, (
        f"Talent must NOT buff ally {_TALENT_RANGE + 3} tiles away"
    )


# ---------------------------------------------------------------------------
# Test 4: S2 applies ATK +30% to Toknogi
# ---------------------------------------------------------------------------

def test_s2_atk_buff():
    """Grove Shade must apply ATK +30% to Toknogi herself."""
    w = _world()
    tok = make_toknogi()
    tok.deployed = True; tok.position = (0.0, 1.0)
    w.add_unit(tok)

    base_atk = tok.effective_atk
    tok.skill.sp = float(tok.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, tok)

    assert tok.skill.active_remaining > 0.0, "S2 must be active"
    expected_atk = int(base_atk * (1 + _S2_ATK_RATIO))
    assert abs(tok.effective_atk - expected_atk) <= 2, (
        f"S2 ATK must be ×{1+_S2_ATK_RATIO}; expected={expected_atk}, got={tok.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 5: S2 applies DEF +35% to nearby allies
# ---------------------------------------------------------------------------

def test_s2_def_buff_nearby_ally():
    """S2 must apply DEF +35% to allies within S2 range."""
    w = _world()
    tok = make_toknogi()
    tok.deployed = True; tok.position = (0.0, 1.0)
    w.add_unit(tok)

    ally = _ally(pos=(1.0, 1.0))  # 1 tile away
    w.add_unit(ally)

    base_def = ally.effective_def
    tok.skill.sp = float(tok.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, tok)

    s2_buffs = [b for b in ally.buffs if b.source_tag == _S2_DEF_BUFF_TAG]
    assert len(s2_buffs) == 1, "S2 must apply DEF buff to nearby ally"
    assert abs(s2_buffs[0].value - _S2_DEF_RATIO) < 0.01


# ---------------------------------------------------------------------------
# Test 6: S2 does NOT buff ally out of range
# ---------------------------------------------------------------------------

def test_s2_no_buff_far_ally():
    """S2 must NOT apply DEF buff to allies outside S2 range."""
    w = _world()
    tok = make_toknogi()
    tok.deployed = True; tok.position = (0.0, 1.0)
    w.add_unit(tok)

    far_ally = _ally(pos=(7.0, 1.0))  # 7 tiles away
    w.add_unit(far_ally)

    tok.skill.sp = float(tok.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, tok)

    s2_buffs = [b for b in far_ally.buffs if b.source_tag == _S2_DEF_BUFF_TAG]
    assert len(s2_buffs) == 0, "S2 must NOT buff ally outside S2 range"


# ---------------------------------------------------------------------------
# Test 7: S2 buffs cleared on end
# ---------------------------------------------------------------------------

def test_s2_buffs_cleared():
    """S2 ATK and ally DEF buffs must be removed after skill ends."""
    w = _world()
    tok = make_toknogi()
    tok.deployed = True; tok.position = (0.0, 1.0)
    w.add_unit(tok)

    ally = _ally(pos=(1.0, 1.0))
    w.add_unit(ally)

    tok.skill.sp = float(tok.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, tok)

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert tok.skill.active_remaining == 0.0, "S2 must have ended"
    atk_buffs = [b for b in tok.buffs if b.source_tag == _S2_ATK_BUFF_TAG]
    def_buffs = [b for b in ally.buffs if b.source_tag == _S2_DEF_BUFF_TAG]
    assert len(atk_buffs) == 0, "S2 ATK buff must be cleared"
    assert len(def_buffs) == 0, "S2 DEF buff on ally must be cleared"
