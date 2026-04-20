"""SilverAsh talent "Silver Sword" — global +20% ATK to all deployed melee operators.

Tests cover:
  - Talent configured correctly (TalentComponent present, tag matches)
  - Melee ally gets +20% ATK after ticks while SilverAsh is deployed
  - Ranged ally does NOT get the buff
  - SilverAsh himself does NOT get the buff
  - Buff is removed when SilverAsh dies/retreats
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, RangeShape
from core.types import (
    AttackType, Faction, TileType, TICK_RATE, Profession, RoleArchetype,
)
from core.systems import register_default_systems
from data.characters.silverash import (
    make_silverash, _TALENT_ATK_RATIO, _TALENT_BUFF_TAG, _TALENT_TAG,
    _talent_on_retreat,
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


def _melee_ally(pos=(2, 1)) -> UnitState:
    u = UnitState(
        name="MeleeAlly",
        faction=Faction.ALLY,
        max_hp=1000, hp=1000,
        atk=200, defence=50, res=0.0,
        atk_interval=1.0,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=True,   # melee → should get buff
        profession=Profession.GUARD,
        block=1,
    )
    u.range_shape = RangeShape(tiles=((0, 0), (1, 0)))
    u.deployed = True
    u.position = (float(pos[0]), float(pos[1]))
    return u


def _ranged_ally(pos=(2, 1)) -> UnitState:
    u = UnitState(
        name="RangedAlly",
        faction=Faction.ALLY,
        max_hp=1000, hp=1000,
        atk=200, defence=50, res=0.0,
        atk_interval=1.0,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=False,  # ranged → must NOT get buff
        profession=Profession.SNIPER,
        block=1,
    )
    u.range_shape = RangeShape(tiles=((1, 0), (2, 0), (3, 0)))
    u.deployed = True
    u.position = (float(pos[0]), float(pos[1]))
    return u


def _ticks(world: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        world.tick()


# ---------------------------------------------------------------------------
# Test 1: Talent is configured
# ---------------------------------------------------------------------------

def test_silverash_talent_present():
    s = make_silverash(slot="S3")
    assert len(s.talents) == 1
    assert s.talents[0].name == "Silver Sword"
    assert s.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: Melee ally gets +20% ATK
# ---------------------------------------------------------------------------

def test_silver_sword_buffs_melee_ally():
    w = _world()
    s = make_silverash(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0)
    w.add_unit(s)

    ally = _melee_ally(pos=(2, 1))
    base_atk = ally.effective_atk
    w.add_unit(ally)

    _ticks(w, 0.5)   # let talent tick apply

    expected = int(ally.atk * (1.0 + _TALENT_ATK_RATIO))
    assert ally.effective_atk == expected, (
        f"Silver Sword must give melee ally ATK {expected}; got {ally.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: Ranged ally does NOT get the buff
# ---------------------------------------------------------------------------

def test_silver_sword_skips_ranged_ally():
    w = _world()
    s = make_silverash(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0)
    w.add_unit(s)

    ranged = _ranged_ally(pos=(2, 1))
    base_atk = ranged.effective_atk
    w.add_unit(ranged)

    _ticks(w, 0.5)

    sword_buffs = [b for b in ranged.buffs if b.source_tag == _TALENT_BUFF_TAG]
    assert len(sword_buffs) == 0, "Silver Sword must not buff ranged operators"
    assert ranged.effective_atk == base_atk, "Ranged ally ATK must be unchanged"


# ---------------------------------------------------------------------------
# Test 4: SilverAsh himself does NOT get the buff
# ---------------------------------------------------------------------------

def test_silver_sword_skips_self():
    w = _world()
    s = make_silverash(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0)
    base_atk = s.effective_atk
    w.add_unit(s)

    _ticks(w, 0.5)

    self_buffs = [b for b in s.buffs if b.source_tag == _TALENT_BUFF_TAG]
    assert len(self_buffs) == 0, "SilverAsh must not buff himself"


# ---------------------------------------------------------------------------
# Test 5: Buff is removed when SilverAsh retreats
# ---------------------------------------------------------------------------

def test_silver_sword_buff_cleared_on_retreat():
    w = _world()
    s = make_silverash(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0)
    w.add_unit(s)

    ally = _melee_ally(pos=(2, 1))
    base_atk = ally.effective_atk
    w.add_unit(ally)

    _ticks(w, 0.5)   # buff applied
    assert ally.effective_atk > base_atk, "Precondition: buff must be active"

    # Simulate retreat by calling the retreat hook directly
    _talent_on_retreat(w, s)

    remaining = [b for b in ally.buffs if b.source_tag == _TALENT_BUFF_TAG]
    assert len(remaining) == 0, "Silver Sword buff must be cleared after retreat"
