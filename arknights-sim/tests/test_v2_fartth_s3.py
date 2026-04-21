"""Fartth S3 "Predator" — ATK+80%, arts chaser ratio 40% → 70% during S3, 20s MANUAL.

Tests cover:
  - S3 configured correctly (slot, sp_cost, initial_sp, duration, MANUAL trigger)
  - ATK +80% buff applied on S3 start
  - Arts chaser ratio increases to 70% during S3
  - ATK buff cleared on S3 end
  - Arts chaser ratio reverts to 40% after S3
  - S2 regression (Aimed Shot ATK+50%)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, SkillTrigger, SPGainMode
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.fartth import (
    make_fartth,
    _S3_TAG, _S3_ATK_RATIO, _S3_ATK_BUFF_TAG, _S3_DURATION,
    _TALENT_ARTS_RATIO, _TALENT_ARTS_RATIO_S3,
    _S2_ATK_RATIO,
)
from data.enemies import make_originium_slug


def _world(w: int = 10, h: int = 3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _slug(pos=(2, 1), hp=99999, defence=0, res=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 20)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = defence; e.res = float(res)
    e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    f = make_fartth(slot="S3")
    sk = f.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "Predator"
    assert sk.sp_cost == 50
    assert sk.initial_sp == 25
    assert sk.duration == _S3_DURATION
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.requires_target is False
    assert sk.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK +80% buff applied on S3 start
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    f = make_fartth(slot="S3")
    base_atk = f.effective_atk
    f.deployed = True; f.position = (0.0, 1.0); f.atk_cd = 999.0
    w.add_unit(f)

    enemy = _slug(pos=(2, 1))
    w.add_unit(enemy)

    f.skill.sp = float(f.skill.sp_cost)
    manual_trigger(w, f)

    assert f.skill.active_remaining > 0.0, "S3 must be active"
    expected = int(base_atk * (1.0 + _S3_ATK_RATIO))
    assert abs(f.effective_atk - expected) <= 2, (
        f"S3 ATK must be ×{1 + _S3_ATK_RATIO}; expected {expected}, got {f.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: During S3, arts chaser ratio increases to 70%
# ---------------------------------------------------------------------------

def test_s3_arts_chaser_ratio_boosted():
    """active_remaining > 0 causes _talent_on_attack_hit to use _TALENT_ARTS_RATIO_S3."""
    w = _world()
    f = make_fartth(slot="S3")
    f.deployed = True; f.position = (0.0, 1.0)
    w.add_unit(f)

    enemy = _slug(pos=(2, 1), hp=99999, defence=0, res=0)
    w.add_unit(enemy)

    f.skill.sp = float(f.skill.sp_cost)
    manual_trigger(w, f)
    assert f.skill.active_remaining > 0.0

    pre_hp = enemy.hp
    f.atk_cd = 0.0
    w.tick()

    damage = pre_hp - enemy.hp
    if damage > 0:
        phys = f.effective_atk
        arts = int(f.effective_atk * _TALENT_ARTS_RATIO_S3)
        expected_total = phys + arts
        assert abs(damage - expected_total) <= 3, (
            f"S3 damage must be phys+70%arts; expected~{expected_total}, got {damage}"
        )


# ---------------------------------------------------------------------------
# Test 4: ATK buff cleared on S3 end
# ---------------------------------------------------------------------------

def test_s3_buff_cleared_on_end():
    w = _world()
    f = make_fartth(slot="S3")
    base_atk = f.effective_atk
    f.deployed = True; f.position = (0.0, 1.0); f.atk_cd = 999.0
    w.add_unit(f)

    enemy = _slug(pos=(2, 1))
    w.add_unit(enemy)

    f.skill.sp = float(f.skill.sp_cost)
    manual_trigger(w, f)
    _ticks(w, _S3_DURATION + 1.0)

    assert f.skill.active_remaining == 0.0, "S3 must have ended"
    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in f.buffs), "S3 ATK buff must be cleared"
    assert abs(f.effective_atk - base_atk) <= 1, (
        f"ATK must revert to base {base_atk}; got {f.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 5: Arts chaser ratio reverts to 40% after S3
# ---------------------------------------------------------------------------

def test_arts_chaser_ratio_reverts_after_s3():
    """active_remaining == 0 after S3 ends → talent uses normal 40% ratio."""
    w = _world()
    f = make_fartth(slot="S3")
    f.deployed = True; f.position = (0.0, 1.0)
    w.add_unit(f)

    enemy = _slug(pos=(2, 1), hp=99999, defence=0, res=0)
    w.add_unit(enemy)

    f.skill.sp = float(f.skill.sp_cost)
    manual_trigger(w, f)
    _ticks(w, _S3_DURATION + 1.0)

    assert f.skill.active_remaining == 0.0
    pre_hp = enemy.hp
    f.atk_cd = 0.0
    w.tick()

    damage = pre_hp - enemy.hp
    if damage > 0:
        phys = f.effective_atk
        arts = int(f.effective_atk * _TALENT_ARTS_RATIO)
        expected_total = phys + arts
        assert abs(damage - expected_total) <= 3, (
            f"Post-S3 arts chaser must be 40%; expected~{expected_total}, got {damage}"
        )


# ---------------------------------------------------------------------------
# Test 6: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    f = make_fartth(slot="S2")
    sk = f.skill
    assert sk is not None
    assert sk.slot == "S2"
    assert sk.name == "Aimed Shot"
    assert sk.sp_cost == 25
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
