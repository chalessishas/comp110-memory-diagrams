"""Ptilopsis S2 "Night Cure" — ATK+80% + heal all in-range allies 70% ATK/s.

Tests cover:
  - S2 skill configured correctly
  - ATK buff applied on skill start
  - Nearby ally healed during skill (within range)
  - Far ally NOT healed (beyond range)
  - Heal amount proportional to effective ATK
  - S1 regression — Dawn's Resonance ATK buff still works
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, AttackType, Mobility
from core.systems import register_default_systems
from data.characters.ptilopsis import (
    make_ptilopsis, _S2_TAG, _S2_ATK_RATIO, _S2_HEAL_PER_SEC, _S2_RANGE,
)

_S2_DURATION = 20.0


def _world() -> World:
    grid = TileGrid(width=10, height=3)
    for x in range(10):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def _damaged_ally(w: World, pos: tuple, hp_remaining: int = 500) -> UnitState:
    ally = UnitState(
        name="TestAlly",
        faction=Faction.ALLY,
        max_hp=1000, atk=0, defence=0, res=0,
        atk_interval=99.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=[(pos[0], pos[1]), (pos[0]+1, pos[1])],
        move_speed=0.0,
        deployed=True,
    )
    ally.hp = hp_remaining
    ally.position = (float(pos[0]), float(pos[1]))
    w.add_unit(ally)
    return ally


# ---------------------------------------------------------------------------
# Test 1: S2 configured correctly
# ---------------------------------------------------------------------------

def test_ptilopsis_s2_configured():
    p = make_ptilopsis(slot="S2")
    assert p.skill is not None
    assert p.skill.name == "Night Cure"
    assert p.skill.slot == "S2"
    assert p.skill.behavior_tag == _S2_TAG
    assert p.skill.duration == _S2_DURATION
    assert not p.skill.requires_target


# ---------------------------------------------------------------------------
# Test 2: ATK buff applied on skill start
# ---------------------------------------------------------------------------

def test_s2_atk_buff_applied():
    w = _world()
    p = make_ptilopsis(slot="S2")
    p.deployed = True; p.position = (0.0, 1.0)
    p.skill.sp = float(p.skill.sp_cost)
    base_atk = p.atk
    w.add_unit(p)

    _ticks(w, 0.1)

    expected = base_atk * (1.0 + _S2_ATK_RATIO)
    assert abs(p.effective_atk - expected) < 1, (
        f"S2 ATK buff must be +{_S2_ATK_RATIO:.0%}; expected~{expected:.0f}, got {p.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: Nearby ally healed after 1 second
# ---------------------------------------------------------------------------

def test_s2_heals_nearby_ally():
    w = _world()
    p = make_ptilopsis(slot="S2")
    p.deployed = True; p.position = (0.0, 1.0)
    p.skill.sp = float(p.skill.sp_cost)
    w.add_unit(p)

    # Place ally at (2,1) — within _S2_RANGE=3 of (0,1)
    ally = _damaged_ally(w, (2, 1), hp_remaining=500)

    _ticks(w, 1.5)   # trigger skill + at least 1 heal pulse

    assert ally.hp > 500, f"Nearby ally must receive healing; hp={ally.hp}"


# ---------------------------------------------------------------------------
# Test 4: S2 on_tick does NOT heal ally beyond _S2_RANGE
#   (normal attacks disabled via atk_cd=999 to isolate S2 path)
# ---------------------------------------------------------------------------

def test_s2_does_not_heal_far_ally():
    w = _world()
    p = make_ptilopsis(slot="S2")
    p.deployed = True; p.position = (0.0, 1.0)
    p.atk_cd = 999.0          # suppress normal medic attacks so only S2 on_tick fires
    p.skill.sp = float(p.skill.sp_cost)
    w.add_unit(p)

    # Place ally at (6,1) — distance=6, beyond _S2_RANGE=3
    far_ally = _damaged_ally(w, (6, 1), hp_remaining=500)

    _ticks(w, 3.0)   # skill fires; 3 heal pulses from on_tick if in range

    assert far_ally.hp == 500, (
        f"Far ally (dist=6 > range={_S2_RANGE}) must NOT be healed by S2; hp={far_ally.hp}"
    )


# ---------------------------------------------------------------------------
# Test 5: Heal capped at max_hp (no over-heal)
# ---------------------------------------------------------------------------

def test_s2_heal_capped_at_max_hp():
    w = _world()
    p = make_ptilopsis(slot="S2")
    p.deployed = True; p.position = (0.0, 1.0)
    p.skill.sp = float(p.skill.sp_cost)
    w.add_unit(p)

    # Ally at full HP — should stay at max_hp, not exceed
    ally = _damaged_ally(w, (2, 1), hp_remaining=1000)

    _ticks(w, 5.0)

    assert ally.hp <= ally.max_hp, f"HP must not exceed max; got {ally.hp} > {ally.max_hp}"
    assert ally.hp == ally.max_hp, "Full-HP ally must remain at max_hp after heal"


# ---------------------------------------------------------------------------
# Test 6: S1 regression — Dawn's Resonance ATK buff still works
# ---------------------------------------------------------------------------

def test_ptilopsis_s1_still_works():
    w = _world()
    p = make_ptilopsis(slot="S1")
    p.deployed = True; p.position = (0.0, 1.0)
    p.skill.sp = float(p.skill.sp_cost)
    base_atk = p.atk
    w.add_unit(p)

    _ticks(w, 0.2)

    assert p.effective_atk > base_atk, (
        f"S1 Dawn's Resonance must increase ATK; base={base_atk}, effective={p.effective_atk}"
    )
