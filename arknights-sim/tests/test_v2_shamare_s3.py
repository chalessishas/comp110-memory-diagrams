"""Shamare S3 "Resentment Convergence" — ATK+20% base, +8% per kill (max 5 stacks), 30s MANUAL.

Tests cover:
  - S3 config (slot, sp_cost, MANUAL)
  - ATK +20% base buff applied on start
  - Each kill during S3 adds +8% ATK stack
  - Stacks cap at 5 (max ATK+60%)
  - Outside S3: kills do NOT add stacks
  - ATK buff cleared on end
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, Faction
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from core.systems.talent_registry import fire_on_kill
from core.state.unit_state import UnitState
from data.characters.shamare import (
    make_shamare,
    _S3_TAG, _S3_BASE_ATK_RATIO, _S3_STACK_ATK_RATIO, _S3_MAX_STACKS,
    _S3_DURATION, _S3_ATK_BUFF_TAG, _S3_STACK_ATTR,
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


def _dummy_enemy():
    e = UnitState(name="Enemy", faction=Faction.ENEMY, max_hp=1, atk=0, defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (1.0, 1.0)
    return e


_SHAMARE_POS = (0.0, 1.0)


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    s = make_shamare(slot="S3")
    assert s.skill is not None and s.skill.slot == "S3"
    assert s.skill.name == "Resentment Convergence"
    assert s.skill.sp_cost == 35
    from core.types import SkillTrigger
    assert s.skill.trigger == SkillTrigger.MANUAL
    assert s.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK +20% base buff on start
# ---------------------------------------------------------------------------

def test_s3_base_atk_buff():
    w = _world()
    s = make_shamare(slot="S3")
    s.deployed = True; s.position = _SHAMARE_POS; s.atk_cd = 999.0
    w.add_unit(s)

    enemy = _dummy_enemy()
    w.add_unit(enemy)

    base_atk = s.effective_atk
    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)

    expected = int(base_atk * (1 + _S3_BASE_ATK_RATIO))
    assert abs(s.effective_atk - expected) <= 2, (
        f"S3 base ATK must be ×{1 + _S3_BASE_ATK_RATIO}; expected {expected}, got {s.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: Each kill during S3 adds +8% ATK stack
# ---------------------------------------------------------------------------

def test_s3_kill_adds_stack():
    w = _world()
    s = make_shamare(slot="S3")
    s.deployed = True; s.position = _SHAMARE_POS; s.atk_cd = 999.0
    w.add_unit(s)

    enemy = _dummy_enemy()
    w.add_unit(enemy)

    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)
    atk_before_kill = s.effective_atk

    fire_on_kill(w, s, enemy)

    expected_atk = int(s.atk * (1 + _S3_BASE_ATK_RATIO + _S3_STACK_ATK_RATIO))
    assert abs(s.effective_atk - expected_atk) <= 2, (
        f"After 1 kill, ATK should be base+1 stack; expected {expected_atk}, got {s.effective_atk}"
    )
    assert s.effective_atk > atk_before_kill, "Kill during S3 must increase ATK"


# ---------------------------------------------------------------------------
# Test 4: Stacks cap at 5
# ---------------------------------------------------------------------------

def test_s3_stacks_capped():
    w = _world()
    s = make_shamare(slot="S3")
    s.deployed = True; s.position = _SHAMARE_POS; s.atk_cd = 999.0
    w.add_unit(s)

    enemy = _dummy_enemy()
    w.add_unit(enemy)

    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)

    # Fire 10 kills — stacks should cap at 5
    for _ in range(10):
        fire_on_kill(w, s, enemy)

    assert getattr(s, _S3_STACK_ATTR, 0) == _S3_MAX_STACKS, (
        f"Stacks must cap at {_S3_MAX_STACKS}"
    )
    expected_max_atk = int(s.atk * (1 + _S3_BASE_ATK_RATIO + _S3_MAX_STACKS * _S3_STACK_ATK_RATIO))
    assert abs(s.effective_atk - expected_max_atk) <= 2, (
        f"Max ATK expected {expected_max_atk}, got {s.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 5: Outside S3, kills do NOT add stacks
# ---------------------------------------------------------------------------

def test_no_stack_outside_s3():
    w = _world()
    s = make_shamare(slot="S3")
    s.deployed = True; s.position = _SHAMARE_POS; s.atk_cd = 999.0
    w.add_unit(s)

    enemy = _dummy_enemy()
    w.add_unit(enemy)

    base_atk = s.effective_atk
    # S3 NOT active
    fire_on_kill(w, s, enemy)

    assert s.effective_atk == base_atk, "Kill outside S3 must not add ATK stacks"
    assert getattr(s, _S3_STACK_ATTR, 0) == 0


# ---------------------------------------------------------------------------
# Test 6: ATK buff cleared on end
# ---------------------------------------------------------------------------

def test_s3_atk_buff_cleared_on_end():
    w = _world()
    s = make_shamare(slot="S3")
    s.deployed = True; s.position = _SHAMARE_POS; s.atk_cd = 999.0
    w.add_unit(s)

    enemy = _dummy_enemy()
    w.add_unit(enemy)

    base_atk = s.effective_atk
    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)
    # Add some stacks
    fire_on_kill(w, s, enemy)
    fire_on_kill(w, s, enemy)
    _ticks(w, _S3_DURATION + 1)

    assert s.skill.active_remaining == 0.0
    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in s.buffs), "ATK buff must clear on end"
    assert abs(s.effective_atk - base_atk) <= 2


# ---------------------------------------------------------------------------
# Test 7: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    s = make_shamare(slot="S2")
    assert s.skill is not None and s.skill.slot == "S2"
    assert s.skill.name == "Puppetmaster"
