"""nearl2 (Penance) S3 "Purgatorio" — block→3, ATK+20%, 20s AUTO trigger.

Tests cover:
  - S3 configured correctly (slot, sp_cost=60, initial_sp=30, AUTO trigger, AUTO_TIME SP)
  - block increases to 3 during S3
  - ATK +20% during S3
  - block and ATK buff cleared on S3 end
  - Talent "Penitence, Absolution" regression (ATK per blocked enemy stack)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, SkillTrigger, SPGainMode
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.nearl2 import (
    make_penance,
    _S3_TAG, _S3_BLOCK, _S3_ATK_RATIO, _S3_BUFF_TAG, _S3_DURATION,
    _TALENT_TAG, _TALENT_ATK_PER_STACK,
)


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


def _enemy(world: World, x: float, y: float) -> UnitState:
    e = UnitState(name="Enemy", faction=Faction.ENEMY, max_hp=99999, atk=0, defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


# ---------------------------------------------------------------------------
# Test 1: S3 configured correctly
# ---------------------------------------------------------------------------

def test_s3_config():
    p = make_penance(slot="S3")
    assert p.skill is not None
    assert p.skill.slot == "S3"
    assert p.skill.name == "Purgatorio"
    assert p.skill.sp_cost == 60
    assert p.skill.initial_sp == 30
    assert p.skill.trigger == SkillTrigger.AUTO
    assert p.skill.sp_gain_mode == SPGainMode.AUTO_TIME
    assert abs(p.skill.duration - _S3_DURATION) < 0.01
    assert p.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: block increases to 3 during S3
# ---------------------------------------------------------------------------

def test_s3_block_increases():
    w = _world()
    p = make_penance(slot="S3")
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    w.add_unit(p)

    assert p.block == 1, "Penance base block must be 1"

    p.skill.sp = float(p.skill.sp_cost)
    # AUTO trigger activates on next tick when SP is full
    w.tick()

    assert p.skill.active_remaining > 0.0, "S3 must be active"
    assert p.block == _S3_BLOCK, f"S3 must set block={_S3_BLOCK}, got {p.block}"


# ---------------------------------------------------------------------------
# Test 3: ATK +20% during S3
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    p = make_penance(slot="S3")
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    w.add_unit(p)

    base_atk = p.effective_atk
    p.skill.sp = float(p.skill.sp_cost)
    w.tick()

    assert p.skill.active_remaining > 0.0
    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(p.effective_atk - expected) <= 2, (
        f"S3 ATK must be ×{1 + _S3_ATK_RATIO}; expected {expected}, got {p.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 4: block and ATK buff cleared on S3 end
# ---------------------------------------------------------------------------

def test_s3_cleared_on_end():
    w = _world()
    p = make_penance(slot="S3")
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    w.add_unit(p)

    base_atk = p.effective_atk
    p.skill.sp = float(p.skill.sp_cost)
    w.tick()
    assert p.skill.active_remaining > 0.0

    _ticks(w, _S3_DURATION + 1)

    assert p.skill.active_remaining == 0.0, "S3 must have ended"
    assert not any(b.source_tag == _S3_BUFF_TAG for b in p.buffs), "ATK buff must clear"
    assert abs(p.effective_atk - base_atk) <= 2, "ATK must revert to base"
    assert p.block == 1, f"block must revert to 1, got {p.block}"


# ---------------------------------------------------------------------------
# Test 5: Talent "Penitence, Absolution" — ATK scales with blocked enemies
# ---------------------------------------------------------------------------

def test_talent_atk_per_blocked_enemy():
    w = _world()
    p = make_penance(slot="S3")
    p.deployed = True; p.position = (0.0, 1.0); p.atk_cd = 999.0
    w.add_unit(p)

    p.skill.sp = float(p.skill.sp_cost)
    w.tick()
    assert p.block == _S3_BLOCK

    e = _enemy(w, 0.5, 1.0)
    e.blocked_by_unit_ids = [p.unit_id]

    _ticks(w, 0.1)

    # Ratio buffs are additive: effective = base × (1 + S3_ratio + talent_ratio)
    expected = int(p.atk * (1 + _S3_ATK_RATIO + _TALENT_ATK_PER_STACK))
    assert abs(p.effective_atk - expected) <= 2, (
        f"Talent must add +{_TALENT_ATK_PER_STACK:.0%} ATK for 1 blocked enemy; "
        f"expected ~{expected}, got {p.effective_atk}"
    )
