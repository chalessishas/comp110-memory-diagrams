"""Logos S3 "Absolute Logos" — ATK+80%, 30s, AUTO trigger.

Tests cover:
  - S3 configured correctly (slot, sp_cost, initial_sp, duration, requires_target=False)
  - ATK +80% buff applied on S3 start
  - ATK buff removed on S3 end
  - S3 stacks with Stable Hypothesis talent (both ATK buffs active simultaneously)
  - S3 buff source tag distinct from talent buff source tag (no cross-contamination)
  - S2 regression (Theorem Derivation unchanged)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, SkillTrigger, BuffAxis
from core.systems import register_default_systems
from data.characters.logos import (
    make_logos,
    _S3_TAG, _S3_ATK_RATIO, _S3_BUFF_TAG, _S3_DURATION,
    _TALENT_DELAY, _TALENT_ATK_RATIO, _TALENT_BUFF_TAG,
    _S2_ATK_RATIO,
)


def _world(w: int = 6, h: int = 3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


# ---------------------------------------------------------------------------
# Test 1: S3 configured correctly
# ---------------------------------------------------------------------------

def test_s3_config():
    l = make_logos(slot="S3")
    sk = l.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "Absolute Logos"
    assert sk.sp_cost == 40
    assert sk.initial_sp == 20
    assert sk.duration == _S3_DURATION
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.requires_target is False
    assert sk.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK +80% buff applied on S3 start
# ---------------------------------------------------------------------------

def test_s3_atk_buff_applied():
    w = _world()
    l = make_logos(slot="S3")
    base_atk = l.effective_atk
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    w.add_unit(l)

    l.skill.sp = float(l.skill.sp_cost)
    w.tick()

    assert l.skill.active_remaining > 0.0, "S3 must be active"
    buff = next((b for b in l.buffs if b.source_tag == _S3_BUFF_TAG), None)
    assert buff is not None, "S3 ATK buff must be present"
    assert buff.axis == BuffAxis.ATK
    assert buff.value == _S3_ATK_RATIO
    expected = int(base_atk * (1.0 + _S3_ATK_RATIO))
    assert abs(l.effective_atk - expected) <= 2, (
        f"S3 ATK must be ×{1 + _S3_ATK_RATIO}; expected {expected}, got {l.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: ATK buff removed on S3 end
# ---------------------------------------------------------------------------

def test_s3_buff_cleared_on_end():
    w = _world()
    l = make_logos(slot="S3")
    base_atk = l.effective_atk
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    w.add_unit(l)

    l.skill.sp = float(l.skill.sp_cost)
    _ticks(w, _S3_DURATION + 2.0)

    assert l.skill.active_remaining == 0.0, "S3 must have ended"
    assert not any(b.source_tag == _S3_BUFF_TAG for b in l.buffs), "S3 ATK buff must be cleared on end"
    assert abs(l.effective_atk - base_atk) <= 2, "ATK must revert to base after S3"


# ---------------------------------------------------------------------------
# Test 4: S3 stacks with Stable Hypothesis talent
# ---------------------------------------------------------------------------

def test_s3_stacks_with_talent():
    """Both S3 ATK+80% and talent ATK+25% must be active simultaneously."""
    w = _world()
    l = make_logos(slot="S3")
    base_atk = l.effective_atk
    l.deployed = True; l.position = (0.0, 1.0); l.atk_cd = 999.0
    w.add_unit(l)
    l.deploy_time = w.global_state.elapsed

    # Let talent activate first (TALENT_DELAY seconds)
    _ticks(w, _TALENT_DELAY + 1.0)

    assert any(b.source_tag == _TALENT_BUFF_TAG for b in l.buffs), "Talent buff must be active"

    # Now fire S3
    l.skill.sp = float(l.skill.sp_cost)
    w.tick()

    assert l.skill.active_remaining > 0.0, "S3 must be active"
    assert any(b.source_tag == _S3_BUFF_TAG for b in l.buffs), "S3 buff must also be active"
    assert any(b.source_tag == _TALENT_BUFF_TAG for b in l.buffs), "Talent buff must still be active"

    # Total effective ATK = base × (1 + 0.25 + 0.80) = base × 2.05
    expected = int(base_atk * (1.0 + _TALENT_ATK_RATIO + _S3_ATK_RATIO))
    assert abs(l.effective_atk - expected) <= 3, (
        f"Stacked ATK expected {expected}, got {l.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 5: S3 and talent buffs use distinct source tags
# ---------------------------------------------------------------------------

def test_s3_buff_tag_distinct_from_talent():
    """S3 buff source tag must differ from talent buff tag to prevent cross-removal."""
    assert _S3_BUFF_TAG != _TALENT_BUFF_TAG, (
        "S3 and talent must use different source tags to avoid accidental cross-cleanup"
    )


# ---------------------------------------------------------------------------
# Test 6: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    l = make_logos(slot="S2")
    sk = l.skill
    assert sk is not None
    assert sk.slot == "S2"
    assert sk.name == "Theorem Derivation"
    assert sk.sp_cost == 25
