"""Surtr S3 "Tyrant of the Undying Flames" — ATK+200%, 4% max HP/s drain after 10s.

Note: Surtr is GUARD_REAPER — her base attack type is ARTS (not physical).
The S3 saves/restores attack_type but it's already ARTS, so no conversion occurs.

Tests cover:
  - S3 configured correctly (sp_cost=40, AUTO trigger, 40s duration)
  - ATK+200% buff applied when skill fires
  - No HP drain in the first 10s
  - HP drain begins after 10s into the skill
  - ATK buff cleared on S3 end
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, BuffAxis, SPGainMode
from core.systems import register_default_systems
from data.characters.surtr import (
    make_surtr,
    _S3_TAG, _S3_ATK_RATIO, _S3_BUFF_TAG,
    _S3_DURATION, _S3_DRAIN_DELAY, _S3_DRAIN_RATE,
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


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def _enemy(world: World, x: float, y: float) -> UnitState:
    e = UnitState(name="Enemy", faction=Faction.ENEMY, max_hp=99999, atk=0,
                  defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


def _activate(w: World, s) -> None:
    """Fire AUTO skill by setting SP full and ticking (requires __target__ set by targeting system)."""
    s.skill.sp = float(s.skill.sp_cost)
    w.tick()  # targeting system runs first, then AUTO skill fires


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    s = make_surtr(slot="S3")
    assert s.skill is not None
    assert s.skill.slot == "S3"
    assert s.skill.name == "Tyrant of the Undying Flames"
    assert s.skill.sp_cost == 40
    assert s.skill.initial_sp == 20
    assert s.skill.duration == 40.0
    from core.types import SkillTrigger
    assert s.skill.trigger == SkillTrigger.AUTO
    assert s.skill.sp_gain_mode == SPGainMode.AUTO_TIME
    assert s.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK+200% buff applied when skill fires
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    s = make_surtr(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    w.add_unit(s)
    _enemy(w, 1.0, 1.0)   # enemy in range so AUTO trigger can fire
    base_atk = s.effective_atk

    _activate(w, s)

    buff = next((b for b in s.buffs if b.source_tag == _S3_BUFF_TAG), None)
    assert buff is not None, "ATK buff must be applied when S3 fires"
    assert abs(buff.value - _S3_ATK_RATIO) <= 0.001

    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(s.effective_atk - expected) <= 2, (
        f"Surtr ATK must be ×{1 + _S3_ATK_RATIO}; expected ~{expected}, got {s.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: No HP drain in first 10s
# ---------------------------------------------------------------------------

def test_s3_no_drain_early():
    w = _world()
    s = make_surtr(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    w.add_unit(s)
    _enemy(w, 1.0, 1.0)

    _activate(w, s)
    assert s.skill.active_remaining > 0.0, "Skill must have fired"
    hp_after_start = s.hp

    _ticks(w, 9.0)

    assert s.hp == hp_after_start, (
        f"Surtr must NOT lose HP in first {_S3_DRAIN_DELAY}s; lost {hp_after_start - s.hp}"
    )


# ---------------------------------------------------------------------------
# Test 4: HP drain begins after 10s
# ---------------------------------------------------------------------------

def test_s3_drain_after_delay():
    w = _world()
    s = make_surtr(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    w.add_unit(s)
    _enemy(w, 1.0, 1.0)
    s.hp = s.max_hp

    _activate(w, s)
    assert s.skill.active_remaining > 0.0, "Skill must have fired"
    hp_at_start = s.hp

    _ticks(w, _S3_DRAIN_DELAY + 3.0)   # 13s total = 3s of drain

    expected_drain = int(s.max_hp * _S3_DRAIN_RATE * 3.0)
    actual_drain = hp_at_start - s.hp
    assert actual_drain > 0, "Surtr must lose HP after drain delay"
    assert abs(actual_drain - expected_drain) <= 10, (
        f"Drain should be ~{expected_drain} HP over 3s; got {actual_drain}"
    )


# ---------------------------------------------------------------------------
# Test 5: Drain kills Surtr; ATK buff cleaned up at death
# (Surtr always dies before 40s expiry: 30s drain × 4%/s = 120% max HP)
# ---------------------------------------------------------------------------

def test_s3_drain_kills_surtr_and_clears_buff():
    w = _world()
    s = make_surtr(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    w.add_unit(s)
    _enemy(w, 1.0, 1.0)

    _activate(w, s)
    assert s.skill.active_remaining > 0.0, "Skill must fire"

    # Tick 40s — drain started at 10s, ~25s of drain (max_hp/drain_rate) kills Surtr
    _ticks(w, 40.0)

    assert not s.alive, "Drain must kill Surtr before skill expires"
    assert not any(b.source_tag == _S3_BUFF_TAG for b in s.buffs), (
        "ATK buff must be cleaned up when drain kills Surtr"
    )


# ---------------------------------------------------------------------------
# Test 6: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    s = make_surtr(slot="S2")
    assert s.skill is not None and s.skill.slot == "S2"
    assert s.skill.name == "Radiant Phoenix"
    assert s.skill.sp_cost == 25
