"""Ines S3 "Obedient Strings" — AoE physical burst (2×ATK), 8s SILENCE on targets, re-CAMOUFLAGE, 1s instant MANUAL.

Tests cover:
  - S3 configured correctly (slot, sp_cost, initial_sp, duration=1.0, MANUAL trigger)
  - In-range enemies take 2×ATK physical damage on S3 start
  - Hit enemies receive 8s SILENCE
  - Out-of-range enemies are NOT hit and NOT silenced
  - Ines re-gains CAMOUFLAGE (20s) after burst
  - S2 regression (Shadow Strike)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, SkillTrigger, SPGainMode, StatusKind
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.ines import (
    make_ines,
    _S3_TAG, _S3_ATK_RATIO, _S3_SILENCE_DURATION, _S3_SILENCE_TAG,
    _S3_CAMO_DURATION, _S3_DURATION, _CAMO_TAG,
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


def _slug(pos=(1, 0), hp=99999, defence=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 20)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = defence; e.res = 0.0
    e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    i = make_ines(slot="S3")
    sk = i.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "Obedient Strings"
    assert sk.sp_cost == 50
    assert sk.initial_sp == 15
    assert sk.duration == _S3_DURATION
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.requires_target is False
    assert sk.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: In-range enemy takes 2×ATK physical damage
# ---------------------------------------------------------------------------

def test_s3_in_range_damage():
    w = _world()
    i = make_ines(slot="S3")
    i.deployed = True; i.position = (0.0, 0.0); i.atk_cd = 999.0
    w.add_unit(i)

    # Range: (0,0) (1,0) (2,0) (3,0) — enemy at (1,0) is in range
    enemy = _slug(pos=(1, 0), hp=99999, defence=0)
    w.add_unit(enemy)

    i.skill.sp = float(i.skill.sp_cost)
    manual_trigger(w, i)

    expected_dmg = int(i.effective_atk * _S3_ATK_RATIO)
    taken = enemy.max_hp - enemy.hp
    assert abs(taken - expected_dmg) <= 2, (
        f"In-range enemy must take {expected_dmg} damage; took {taken}"
    )


# ---------------------------------------------------------------------------
# Test 3: Hit enemies receive SILENCE
# ---------------------------------------------------------------------------

def test_s3_silence_applied():
    w = _world()
    i = make_ines(slot="S3")
    i.deployed = True; i.position = (0.0, 0.0); i.atk_cd = 999.0
    w.add_unit(i)

    enemy = _slug(pos=(2, 0))
    w.add_unit(enemy)

    i.skill.sp = float(i.skill.sp_cost)
    manual_trigger(w, i)

    silence = next(
        (s for s in enemy.statuses if s.kind == StatusKind.SILENCE and s.source_tag == _S3_SILENCE_TAG),
        None,
    )
    assert silence is not None, "In-range enemy must receive SILENCE status"
    assert silence.expires_at > w.global_state.elapsed, "Silence must not be expired"


# ---------------------------------------------------------------------------
# Test 4: Out-of-range enemy NOT hit and NOT silenced
# ---------------------------------------------------------------------------

def test_s3_out_of_range_not_affected():
    w = _world()
    i = make_ines(slot="S3")
    i.deployed = True; i.position = (0.0, 0.0); i.atk_cd = 999.0
    w.add_unit(i)

    # Enemy at (5,0) — outside AGENT_RANGE (max dx=3)
    out_enemy = _slug(pos=(5, 0), hp=99999)
    w.add_unit(out_enemy)

    i.skill.sp = float(i.skill.sp_cost)
    manual_trigger(w, i)

    assert out_enemy.hp == out_enemy.max_hp, "Out-of-range enemy must not take damage"
    has_silence = any(s.source_tag == _S3_SILENCE_TAG for s in out_enemy.statuses)
    assert not has_silence, "Out-of-range enemy must not receive S3 silence"


# ---------------------------------------------------------------------------
# Test 5: Ines re-gains CAMOUFLAGE after burst
# ---------------------------------------------------------------------------

def test_s3_recamouflage():
    w = _world()
    i = make_ines(slot="S3")
    i.deployed = True; i.position = (0.0, 0.0); i.atk_cd = 999.0
    w.add_unit(i)

    enemy = _slug(pos=(1, 0))
    w.add_unit(enemy)

    i.skill.sp = float(i.skill.sp_cost)
    manual_trigger(w, i)

    camo = next(
        (s for s in i.statuses if s.kind == StatusKind.CAMOUFLAGE and s.source_tag == _CAMO_TAG),
        None,
    )
    assert camo is not None, "Ines must re-gain CAMOUFLAGE after S3 burst"
    expected_expires = w.global_state.elapsed + _S3_CAMO_DURATION
    assert abs(camo.expires_at - expected_expires) <= 0.2, (
        f"CAMOUFLAGE duration must be ~{_S3_CAMO_DURATION}s"
    )


# ---------------------------------------------------------------------------
# Test 6: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    i = make_ines(slot="S2")
    sk = i.skill
    assert sk is not None
    assert sk.slot == "S2"
    assert sk.name == "Shadow Strike"
    assert sk.sp_cost == 25
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
