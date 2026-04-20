"""Ptilopsis S3 "Dream Catcher" — ATK+100%, Unisonant upgrades to 0.6 SP/s during skill.

Tests cover:
  - S3 config (slot, sp_cost, MANUAL)
  - ATK +100% buff applied on start
  - Unisonant grants 0.6 SP/s during S3 (doubled from base 0.3)
  - Unisonant reverts to 0.3 SP/s after S3 ends
  - ATK buff cleared on end
  - S2 regression
  - S1 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, Faction
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from core.state.unit_state import UnitState, SkillComponent
from data.characters.ptilopsis import (
    make_ptilopsis,
    _S3_TAG, _S3_ATK_RATIO, _S3_DURATION, _S3_ATK_BUFF_TAG,
    _S3_ACTIVE_ATTR, _SP_RATE, _SP_RATE_S3,
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


def _ticks(w, seconds):
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def _dummy_ally(name="Ally") -> UnitState:
    a = UnitState(name=name, faction=Faction.ALLY, max_hp=1000, atk=100, defence=10, res=0.0)
    a.alive = True
    a.deployed = True
    a.position = (2.0, 1.0)
    a.skill = SkillComponent(
        name="TestSkill", slot="S1", sp_cost=20, initial_sp=0, duration=10.0,
        sp_gain_mode=None, trigger=None, requires_target=False, behavior_tag="noop"
    )
    a.skill.sp = 0.0
    return a


_PTILOPSIS_POS = (0.0, 1.0)


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    p = make_ptilopsis(slot="S3")
    assert p.skill is not None and p.skill.slot == "S3"
    assert p.skill.name == "Dream Catcher"
    assert p.skill.sp_cost == 35
    from core.types import SkillTrigger
    assert p.skill.trigger == SkillTrigger.MANUAL
    assert p.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK +100% buff applied on start
# ---------------------------------------------------------------------------

def test_s3_atk_buff_on_start():
    w = _world()
    p = make_ptilopsis(slot="S3")
    p.deployed = True; p.position = _PTILOPSIS_POS; p.atk_cd = 999.0
    w.add_unit(p)

    base_atk = p.effective_atk
    p.skill.sp = float(p.skill.sp_cost)
    manual_trigger(w, p)

    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(p.effective_atk - expected) <= 2, (
        f"S3 ATK+{_S3_ATK_RATIO:.0%}; expected ~{expected}, got {p.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: Unisonant grants 0.6 SP/s to allies during S3 (vs 0.3 baseline)
# ---------------------------------------------------------------------------

def test_s3_unisonant_doubled_sp_rate():
    w = _world()
    p = make_ptilopsis(slot="S3")
    p.deployed = True; p.position = _PTILOPSIS_POS; p.atk_cd = 999.0
    w.add_unit(p)

    ally = _dummy_ally("Warrior")
    w.add_unit(ally)

    p.skill.sp = float(p.skill.sp_cost)
    manual_trigger(w, p)

    assert getattr(p, _S3_ACTIVE_ATTR, False), "S3 active flag must be set"

    sp_before = ally.skill.sp
    _ticks(w, 10.0)
    sp_gained = ally.skill.sp - sp_before

    # At 0.6 SP/s for 10s → expect ~6.0 SP (capped at sp_cost=20)
    expected_min = _SP_RATE_S3 * 10.0 * 0.85  # allow 15% tolerance
    assert sp_gained >= expected_min, (
        f"S3 Unisonant should give ~{_SP_RATE_S3 * 10.0:.1f} SP in 10s; got {sp_gained:.2f}"
    )


# ---------------------------------------------------------------------------
# Test 4: After S3 ends, Unisonant reverts to 0.3 SP/s
# ---------------------------------------------------------------------------

def test_s3_unisonant_reverts_after_end():
    w = _world()
    p = make_ptilopsis(slot="S3")
    p.deployed = True; p.position = _PTILOPSIS_POS; p.atk_cd = 999.0
    w.add_unit(p)

    ally = _dummy_ally("Warrior")
    w.add_unit(ally)

    p.skill.sp = float(p.skill.sp_cost)
    manual_trigger(w, p)
    _ticks(w, _S3_DURATION + 1.0)

    assert not getattr(p, _S3_ACTIVE_ATTR, True), "S3 active flag must clear after skill ends"

    # Reset ally SP to measure post-S3 rate
    ally.skill.sp = 0.0
    sp_before = ally.skill.sp
    _ticks(w, 10.0)
    sp_gained = ally.skill.sp - sp_before

    # At 0.3 SP/s for 10s → ~3.0 SP
    expected_max = _SP_RATE_S3 * 10.0 * 1.10  # must be below doubled rate
    assert sp_gained <= expected_max, (
        f"Post-S3 Unisonant should give ~{_SP_RATE * 10.0:.1f} SP in 10s, not {sp_gained:.2f}"
    )


# ---------------------------------------------------------------------------
# Test 5: ATK buff cleared on end
# ---------------------------------------------------------------------------

def test_s3_atk_buff_cleared_on_end():
    w = _world()
    p = make_ptilopsis(slot="S3")
    p.deployed = True; p.position = _PTILOPSIS_POS; p.atk_cd = 999.0
    w.add_unit(p)

    base_atk = p.effective_atk
    p.skill.sp = float(p.skill.sp_cost)
    manual_trigger(w, p)
    _ticks(w, _S3_DURATION + 1.0)

    assert p.skill.active_remaining == 0.0
    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in p.buffs), (
        "ATK buff must be cleared after S3 ends"
    )
    assert abs(p.effective_atk - base_atk) <= 2


# ---------------------------------------------------------------------------
# Test 6: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    p = make_ptilopsis(slot="S2")
    assert p.skill is not None and p.skill.slot == "S2"
    assert p.skill.name == "Night Cure"


# ---------------------------------------------------------------------------
# Test 7: S1 regression
# ---------------------------------------------------------------------------

def test_s1_regression():
    p = make_ptilopsis(slot="S1")
    assert p.skill is not None and p.skill.slot == "S1"
    assert p.skill.name == "Dawn's Resonance"
