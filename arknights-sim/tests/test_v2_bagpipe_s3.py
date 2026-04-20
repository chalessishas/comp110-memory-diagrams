"""Bagpipe S3 "Last Wish" — ATK+200% for 40s; attacks SLOW target 50% for 1s.

Tests cover:
  - S3 configured correctly (slot, sp_cost, AUTO trigger, requires_target=True)
  - ATK +200% during S3
  - SLOW status applied to enemy on attack hit during S3
  - SLOW NOT applied when S3 inactive
  - ATK buff removed on skill end
  - S2 regression (Pump Up unchanged)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, SkillTrigger, StatusKind
from core.systems import register_default_systems
from data.characters.bagpipe import (
    make_bagpipe,
    _S3_TAG, _S3_ATK_RATIO, _S3_BUFF_TAG, _S3_SLOW_TAG, _S3_SLOW_DURATION,
)
from data.enemies import make_originium_slug


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
    b = make_bagpipe(slot="S3")
    sk = b.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "Last Wish"
    assert sk.sp_cost == 35
    assert sk.initial_sp == 20
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.requires_target is True
    assert sk.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK +200% during S3
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    b = make_bagpipe(slot="S3")
    base_atk = b.effective_atk
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 999.0
    w.add_unit(b)

    slug_path = [(1, 1)] * 30
    e = make_originium_slug(path=slug_path)
    e.deployed = True; e.position = (1.0, 1.0); e.move_speed = 0.0
    w.add_unit(e)

    b.skill.sp = float(b.skill.sp_cost)
    w.tick()

    assert b.skill.active_remaining > 0.0, "S3 must be active after sp full + enemy present"
    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(b.effective_atk - expected) <= 2, (
        f"S3 ATK must be ×{1+_S3_ATK_RATIO}; expected {expected}, got {b.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: SLOW applied to enemy on attack hit during S3
# ---------------------------------------------------------------------------

def test_s3_slow_on_hit():
    w = _world()
    b = make_bagpipe(slot="S3")
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 0.0
    w.add_unit(b)

    slug_path = [(1, 1)] * 60
    e = make_originium_slug(path=slug_path)
    e.deployed = True; e.position = (1.0, 1.0); e.move_speed = 0.0
    w.add_unit(e)

    b.skill.sp = float(b.skill.sp_cost)
    _ticks(w, 2.0)

    slow_statuses = [s for s in e.statuses if s.kind == StatusKind.SLOW and s.source_tag == _S3_SLOW_TAG]
    assert len(slow_statuses) >= 1, "Enemy must have SLOW status after Bagpipe S3 attack"
    assert slow_statuses[0].params["amount"] == 0.5, "SLOW must reduce speed by 50%"


# ---------------------------------------------------------------------------
# Test 4: SLOW NOT applied when S3 inactive
# ---------------------------------------------------------------------------

def test_s3_slow_not_applied_when_inactive():
    w = _world()
    b = make_bagpipe(slot="S3")
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 0.0
    w.add_unit(b)

    slug_path = [(1, 1)] * 60
    e = make_originium_slug(path=slug_path)
    e.deployed = True; e.position = (1.0, 1.0); e.move_speed = 0.0
    w.add_unit(e)

    # Do NOT fill SP — S3 stays inactive; Bagpipe still auto-attacks via talent
    _ticks(w, 1.5)

    slow_from_s3 = [s for s in e.statuses if s.source_tag == _S3_SLOW_TAG]
    assert len(slow_from_s3) == 0, "SLOW must not be applied when S3 is inactive"


# ---------------------------------------------------------------------------
# Test 5: ATK buff removed on skill end
# ---------------------------------------------------------------------------

def test_s3_buff_cleared_on_end():
    w = _world()
    b = make_bagpipe(slot="S3")
    base_atk = b.effective_atk
    b.deployed = True; b.position = (0.0, 1.0); b.atk_cd = 999.0
    w.add_unit(b)

    slug_path = [(1, 1)] * 100
    e = make_originium_slug(path=slug_path)
    e.deployed = True; e.position = (1.0, 1.0); e.move_speed = 0.0
    w.add_unit(e)

    b.skill.sp = float(b.skill.sp_cost)
    _ticks(w, 42.0)  # 40s duration + buffer

    assert b.skill.active_remaining == 0.0, "S3 must have ended"
    atk_buffs = [buf for buf in b.buffs if buf.source_tag == _S3_BUFF_TAG]
    assert len(atk_buffs) == 0, "S3 ATK buff must be cleared on end"
    assert abs(b.effective_atk - base_atk) <= 2, "ATK must revert to base after S3"


# ---------------------------------------------------------------------------
# Test 6: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    b = make_bagpipe(slot="S2")
    assert b.skill is not None
    assert b.skill.slot == "S2"
    assert b.skill.name == "Pump Up"
    assert b.skill.sp_cost == 20
