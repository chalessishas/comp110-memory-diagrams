"""Mudrock S3 "Surge of Rocks" — 2-phase: 10s invuln then 5 AoE rock strikes.

Tests cover:
  - S3 configured correctly (slot, sp_cost=30, AUTO trigger, duration=40s)
  - ATK +100% buff during S3
  - Phase 1: DAMAGE_IMMUNE status active for first 10s
  - Phase 1: lethal damage dealt during Phase 1 does not kill Mudrock
  - Phase 2: rock strikes land and deal damage to enemies in AoE
  - ATK buff cleared on S3 end
  - S2 regression (Rockfall unchanged)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, SkillTrigger, StatusKind
from core.systems import register_default_systems
from data.characters.mudrock import (
    make_mudrock,
    _S3_TAG, _S3_ATK_RATIO, _S3_ATK_BUFF_TAG, _S3_DURATION,
    _PHASE1_DURATION, _PHASE1_STATUS_TAG,
)
from data.enemies import make_originium_slug


def _world(w: int = 6, h: int = 4) -> World:
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
    m = make_mudrock(slot="S3")
    sk = m.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "Surge of Rocks"
    assert sk.sp_cost == 30
    assert sk.initial_sp == 15
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.behavior_tag == _S3_TAG
    assert abs(sk.duration - (_PHASE1_DURATION + _S3_DURATION)) < 0.01


# ---------------------------------------------------------------------------
# Test 2: ATK +100% during S3
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    m = make_mudrock(slot="S3")
    base_atk = m.effective_atk
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()

    assert m.skill.active_remaining > 0.0, "S3 must be active"
    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(m.effective_atk - expected) <= 2, (
        f"S3 ATK must be ×{1+_S3_ATK_RATIO}; expected {expected}, got {m.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: Phase 1 — DAMAGE_IMMUNE status applied
# ---------------------------------------------------------------------------

def test_s3_phase1_invuln_status():
    w = _world()
    m = make_mudrock(slot="S3")
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()

    assert m.skill.active_remaining > 0.0
    immune = [s for s in m.statuses if s.kind == StatusKind.DAMAGE_IMMUNE and s.source_tag == _PHASE1_STATUS_TAG]
    assert len(immune) == 1, "DAMAGE_IMMUNE status must be present during Phase 1"


# ---------------------------------------------------------------------------
# Test 4: Phase 1 — lethal damage does not kill Mudrock
# ---------------------------------------------------------------------------

def test_s3_phase1_survives_lethal():
    w = _world()
    m = make_mudrock(slot="S3")
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)

    m.skill.sp = float(m.skill.sp_cost)
    w.tick()

    assert m.skill.active_remaining > 0.0
    m.take_physical(999999)  # lethal

    assert m.alive, "Mudrock must survive lethal damage during Phase 1 invuln"


# ---------------------------------------------------------------------------
# Test 5: Phase 2 — rock strikes deal damage to enemies in AoE
# ---------------------------------------------------------------------------

def test_s3_phase2_strikes_deal_damage():
    w = _world()
    m = make_mudrock(slot="S3")
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)

    slug_path = [(1, 1)] * 200
    e = make_originium_slug(path=slug_path)
    e.deployed = True; e.position = (1.0, 1.0); e.move_speed = 0.0
    # Give enemy high DEF to ensure it can survive multiple hits
    e.max_hp = 200000; e.hp = 200000
    w.add_unit(e)

    m.skill.sp = float(m.skill.sp_cost)
    # Tick through Phase 1 (10s) + some of Phase 2
    _ticks(w, _PHASE1_DURATION + 5.0)

    assert w.global_state.total_damage_dealt > 0, "Rock strikes must deal damage in Phase 2"
    assert e.hp < e.max_hp, "Enemy HP must drop after rock strikes"


# ---------------------------------------------------------------------------
# Test 6: ATK buff cleared on S3 end
# ---------------------------------------------------------------------------

def test_s3_atk_buff_cleared_on_end():
    w = _world()
    m = make_mudrock(slot="S3")
    base_atk = m.effective_atk
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    m.max_hp = 999999; m.hp = 999999  # prevent drain from Rocksteady
    w.add_unit(m)

    m.skill.sp = float(m.skill.sp_cost)
    _ticks(w, _PHASE1_DURATION + _S3_DURATION + 2.0)

    assert m.skill.active_remaining == 0.0, "S3 must have ended"
    atk_buffs = [b for b in m.buffs if b.source_tag == _S3_ATK_BUFF_TAG]
    assert len(atk_buffs) == 0, "S3 ATK buff must be cleared on end"


# ---------------------------------------------------------------------------
# Test 7: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    m = make_mudrock(slot="S2")
    assert m.skill is not None
    assert m.skill.slot == "S2"
    assert m.skill.name == "Rockfall"
    assert m.skill.sp_cost == 30
