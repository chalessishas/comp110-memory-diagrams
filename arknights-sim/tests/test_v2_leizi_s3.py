"""Leizi S3 "Thunderstruck Mane" — ATK+50%, chain_count→5 (6 total), 20s.

Tests cover:
  - S3 configured correctly (slot, sp_cost, initial_sp, duration, requires_target)
  - ATK +50% during S3
  - chain_count set to 5 during S3 (6 total targets)
  - ATK buff and chain_count reverted on skill end
  - Voltage talent does NOT override chain_count while S3 is active
  - S2 regression (Thunderclap unchanged)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, SkillTrigger
from core.systems import register_default_systems
from data.characters.leizi import (
    make_leizi,
    _S3_TAG, _S3_ATK_RATIO, _S3_ATK_BUFF_TAG, _S3_CHAIN_COUNT, _BASE_CHAIN_COUNT,
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


def _slug(pos, hp: int = 99999):
    path = [(int(pos[0]), int(pos[1]))] * 30
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0; e.move_speed = 0.0
    e.defence = 0; e.res = 0.0
    e.deployed = True; e.position = (float(pos[0]), float(pos[1]))
    return e


# ---------------------------------------------------------------------------
# Test 1: S3 configured correctly
# ---------------------------------------------------------------------------

def test_s3_config():
    lei = make_leizi(slot="S3")
    sk = lei.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "Thunderstruck Mane"
    assert sk.sp_cost == 40
    assert sk.initial_sp == 20
    assert sk.duration == 20.0
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.requires_target is True
    assert sk.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK +50% during S3
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    lei = make_leizi(slot="S3")
    base_atk = lei.effective_atk
    lei.deployed = True; lei.position = (0.0, 1.0); lei.atk_cd = 999.0
    w.add_unit(lei)

    slug = _slug((2, 1))
    w.add_unit(slug)

    lei.skill.sp = float(lei.skill.sp_cost)
    w.tick()

    assert lei.skill.active_remaining > 0.0, "S3 must be active after sp full + enemy present"
    expected = int(base_atk * (1.0 + _S3_ATK_RATIO))
    assert abs(lei.effective_atk - expected) <= 2, (
        f"S3 ATK must be ×{1 + _S3_ATK_RATIO}; expected {expected}, got {lei.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: chain_count set to 5 during S3
# ---------------------------------------------------------------------------

def test_s3_chain_count():
    w = _world()
    lei = make_leizi(slot="S3")
    assert lei.chain_count == _BASE_CHAIN_COUNT, "Baseline chain_count must be 2"
    lei.deployed = True; lei.position = (0.0, 1.0); lei.atk_cd = 999.0
    w.add_unit(lei)

    slug = _slug((2, 1))
    w.add_unit(slug)

    lei.skill.sp = float(lei.skill.sp_cost)
    w.tick()

    assert lei.skill.active_remaining > 0.0
    assert lei.chain_count == _S3_CHAIN_COUNT, (
        f"S3 must set chain_count to {_S3_CHAIN_COUNT}; got {lei.chain_count}"
    )


# ---------------------------------------------------------------------------
# Test 4: ATK buff and chain_count reverted on S3 end
# ---------------------------------------------------------------------------

def test_s3_cleanup_on_end():
    w = _world()
    lei = make_leizi(slot="S3")
    base_atk = lei.effective_atk
    lei.deployed = True; lei.position = (0.0, 1.0); lei.atk_cd = 999.0
    w.add_unit(lei)

    slug = _slug((2, 1))
    w.add_unit(slug)

    lei.skill.sp = float(lei.skill.sp_cost)
    _ticks(w, 22.0)  # 20s duration + buffer

    assert lei.skill.active_remaining == 0.0, "S3 must have ended"
    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in lei.buffs), "S3 ATK buff must be cleared"
    assert lei.chain_count == _BASE_CHAIN_COUNT, (
        f"chain_count must revert to {_BASE_CHAIN_COUNT} after S3; got {lei.chain_count}"
    )
    assert abs(lei.effective_atk - base_atk) <= 2, "ATK must revert to base after S3"


# ---------------------------------------------------------------------------
# Test 5: Voltage talent does not override chain_count while S3 is active
# ---------------------------------------------------------------------------

def test_voltage_talent_respects_s3_chain_count():
    """Voltage on_tick skips chain_count override when S3 is active."""
    w = _world()
    lei = make_leizi(slot="S3")
    lei.deployed = True; lei.position = (0.0, 1.0); lei.atk_cd = 999.0
    w.add_unit(lei)

    slug = _slug((2, 1))
    w.add_unit(slug)

    # Fill SP to max so Voltage would compute max bonus (40/10 = 4 → capped at 3 → chain=5)
    lei.skill.sp = float(lei.skill.sp_cost)
    _ticks(w, 1.0)

    assert lei.skill.active_remaining > 0.0, "S3 must be active"
    assert lei.chain_count == _S3_CHAIN_COUNT, (
        f"Voltage must not override S3 chain_count ({_S3_CHAIN_COUNT}); got {lei.chain_count}"
    )


# ---------------------------------------------------------------------------
# Test 6: S2 regression (Thunderclap unchanged)
# ---------------------------------------------------------------------------

def test_s2_regression():
    lei = make_leizi(slot="S2")
    sk = lei.skill
    assert sk is not None
    assert sk.slot == "S2"
    assert sk.name == "Thunderclap"
    assert sk.sp_cost == 35
