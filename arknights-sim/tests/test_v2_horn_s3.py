"""Horn S3 "Pursuit" — ATK+250%, forced ranged mode, 40s, MANUAL.

Tests cover:
  - S3 configured correctly (slot, sp_cost, MANUAL trigger, requires_target=False)
  - ATK +250% during S3
  - _force_ranged_mode=True during S3
  - ATK buff cleared on skill end
  - _force_ranged_mode=False on skill end
  - S2 regression (S2 still configured correctly)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.horn import (
    make_horn,
    _S3_TAG, _S3_DURATION, _S3_ATK_RATIO, _S3_ATK_BUFF_TAG,
)
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=8, height=3)
    for x in range(8):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


# ---------------------------------------------------------------------------
# Test 1: S3 configured correctly
# ---------------------------------------------------------------------------

def test_s3_config():
    h = make_horn(slot="S3")
    assert h.skill is not None
    assert h.skill.slot == "S3"
    assert h.skill.name == "Pursuit"
    assert h.skill.sp_cost == 50
    assert h.skill.initial_sp == 25
    from core.types import SkillTrigger
    assert h.skill.trigger == SkillTrigger.MANUAL
    assert not h.skill.requires_target
    assert h.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK +250% during S3
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    # talent=False isolates S3 ATK buff from Pioneer's Creed +12% passive
    h = make_horn(slot="S3", talent=False)
    h.deployed = True; h.position = (0.0, 1.0); h.atk_cd = 999.0
    w.add_unit(h)

    base_atk = h.effective_atk
    h.skill.sp = float(h.skill.sp_cost)
    manual_trigger(w, h)

    assert h.skill.active_remaining > 0.0, "S3 must be active after manual_trigger"
    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(h.effective_atk - expected) <= 2, (
        f"S3 ATK must be ×{1 + _S3_ATK_RATIO}; expected {expected}, got {h.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: _force_ranged_mode=True during S3
# ---------------------------------------------------------------------------

def test_s3_force_ranged_mode():
    w = _world()
    h = make_horn(slot="S3")
    h.deployed = True; h.position = (0.0, 1.0); h.atk_cd = 999.0
    w.add_unit(h)

    assert not getattr(h, "_force_ranged_mode", False), "ranged mode must be off before S3"

    h.skill.sp = float(h.skill.sp_cost)
    manual_trigger(w, h)

    assert getattr(h, "_force_ranged_mode", False), "S3 must set _force_ranged_mode=True"


# ---------------------------------------------------------------------------
# Test 4: ATK buff cleared on skill end
# ---------------------------------------------------------------------------

def test_s3_atk_buff_cleared_on_end():
    w = _world()
    h = make_horn(slot="S3", talent=False)
    h.deployed = True; h.position = (0.0, 1.0); h.atk_cd = 999.0
    w.add_unit(h)

    base_atk = h.effective_atk

    h.skill.sp = float(h.skill.sp_cost)
    manual_trigger(w, h)
    assert h.skill.active_remaining > 0.0

    _ticks(w, _S3_DURATION + 1)

    assert h.skill.active_remaining == 0.0, "S3 must have ended"
    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in h.buffs), "ATK buff must clear on end"
    assert abs(h.effective_atk - base_atk) <= 2, "ATK must revert to base after S3"


# ---------------------------------------------------------------------------
# Test 5: _force_ranged_mode=False on skill end
# ---------------------------------------------------------------------------

def test_s3_ranged_mode_cleared_on_end():
    w = _world()
    h = make_horn(slot="S3")
    h.deployed = True; h.position = (0.0, 1.0); h.atk_cd = 999.0
    w.add_unit(h)

    h.skill.sp = float(h.skill.sp_cost)
    manual_trigger(w, h)
    assert getattr(h, "_force_ranged_mode", False), "ranged mode must be on during S3"

    _ticks(w, _S3_DURATION + 1)

    assert h.skill.active_remaining == 0.0, "S3 must have ended"
    assert not getattr(h, "_force_ranged_mode", False), "_force_ranged_mode must be False after S3"


# ---------------------------------------------------------------------------
# Test 6: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    h = make_horn(slot="S2")
    assert h.skill is not None
    assert h.skill.slot == "S2"
    assert h.skill.name == "Support Ray"
    assert h.skill.sp_cost == 30
