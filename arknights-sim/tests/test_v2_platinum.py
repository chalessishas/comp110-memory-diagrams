"""Platinum S1 "ATK Up γ" and S2 "Pegasus Vision" (permanent toggle).

Tests cover:
  - S1 config (name, slot, sp_cost=30, initial_sp=15, duration=30, MANUAL)
  - S1: ATK+100% buff applied
  - S1: buff cleared on end
  - S2 config (name, slot, sp_cost=50, initial_sp=0, duration=0, AUTO, requires_target=False)
  - S2: fires without target (instant AUTO)
  - S2: ATK+100% buff applied permanently
  - S2: ASPD-20 buff applied permanently
  - S2: buffs persist after instant skill fires (no on_end)
  - S2: interval increases due to ASPD penalty
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
from data.characters.platnm import (
    make_platnm,
    _S1_TAG, _S1_ATK_RATIO, _S1_BUFF_TAG, _S1_DURATION,
    _S2_TAG, _S2_ATK_RATIO, _S2_ASPD_DELTA, _S2_ATK_BUFF_TAG, _S2_ASPD_BUFF_TAG,
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


# ── S1: ATK Up γ ─────────────────────────────────────────────────────────────

def test_s1_config():
    op = make_platnm(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "ATK Up γ"
    assert sk.sp_cost == 30
    assert sk.initial_sp == 15
    assert abs(sk.duration - _S1_DURATION) < 1e-6
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.requires_target is False
    assert sk.behavior_tag == _S1_TAG


def test_s1_atk_buff_applied():
    w = _world()
    op = make_platnm(slot="S1")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    buff = next((b for b in op.buffs if b.source_tag == _S1_BUFF_TAG), None)
    assert buff is not None and abs(buff.value - _S1_ATK_RATIO) < 1e-6
    assert op.effective_atk == int(op.atk * (1 + _S1_ATK_RATIO))


def test_s1_buff_cleared_on_end():
    w = _world()
    op = make_platnm(slot="S1")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    for _ in range(int(TICK_RATE * (_S1_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S1_BUFF_TAG for b in op.buffs)
    assert op.effective_atk == base_atk


# ── S2: Pegasus Vision (permanent toggle) ─────────────────────────────────────

def test_s2_config():
    op = make_platnm(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Pegasus Vision"
    assert sk.sp_cost == 50
    assert sk.initial_sp == 0
    assert sk.duration == 0.0
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.requires_target is False
    assert sk.behavior_tag == _S2_TAG


def test_s2_fires_without_target():
    """Pegasus Vision auto-fires when SP full, even with no enemies present."""
    w = _world()
    op = make_platnm(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    assert op.skill.fire_count >= 1


def test_s2_atk_buff_permanent():
    w = _world()
    op = make_platnm(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    buff = next((b for b in op.buffs if b.source_tag == _S2_ATK_BUFF_TAG), None)
    assert buff is not None and abs(buff.value - _S2_ATK_RATIO) < 1e-6
    assert op.effective_atk == int(op.atk * (1 + _S2_ATK_RATIO))


def test_s2_aspd_penalty_applied():
    w = _world()
    op = make_platnm(slot="S2")
    base_interval = op.current_atk_interval
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    buff = next((b for b in op.buffs if b.source_tag == _S2_ASPD_BUFF_TAG), None)
    assert buff is not None and abs(buff.value - _S2_ASPD_DELTA) < 1e-6
    # ASPD-20 means interval increases
    assert op.current_atk_interval > base_interval


def test_s2_buffs_persist_permanently():
    """S2 buffs remain active long after firing (no on_end clears them)."""
    w = _world()
    op = make_platnm(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()
    # Run 60 more seconds — buffs should still be there
    for _ in range(int(TICK_RATE * 60.0)):
        w.tick()

    assert any(b.source_tag == _S2_ATK_BUFF_TAG for b in op.buffs)
    assert any(b.source_tag == _S2_ASPD_BUFF_TAG for b in op.buffs)
