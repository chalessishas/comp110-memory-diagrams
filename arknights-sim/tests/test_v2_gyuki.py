"""Matoimaru (gyuki) S1 "Regeneration β", S2 "Demonic Power".

Tests cover:
  - S1 config (name, sp_cost=20, initial_sp=10, duration=0, MANUAL, AUTO_TIME)
  - S1: heals 50% max HP
  - S2 config (name, sp_cost=25, initial_sp=10, duration=15s, MANUAL, AUTO_TIME)
  - S2: ATK+150% buff applied
  - S2: effective_def reduced to 0
  - S2: buffs cleared on end; DEF restored
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, SkillTrigger, SPGainMode
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.gyuki import (
    make_gyuki, _S1_TAG, _S1_HEAL_RATIO,
    _S2_TAG, _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_DURATION,
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


def _deploy(w: World, slot: str = "S2") -> object:
    op = make_gyuki(slot=slot)
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    return op


def test_s1_config():
    op = make_gyuki(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Regeneration β"
    assert sk.sp_cost == 20
    assert sk.initial_sp == 10
    assert sk.duration == 0.0
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.behavior_tag == _S1_TAG


def test_s1_heals_hp():
    """S1 restores 50% of max HP."""
    w = _world()
    op = _deploy(w, slot="S1")
    # Damage operator first
    op.hp = int(op.max_hp * 0.4)
    hp_before = op.hp
    expected_heal = int(op.max_hp * _S1_HEAL_RATIO)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert op.hp == min(op.max_hp, hp_before + expected_heal)


def test_s2_config():
    op = make_gyuki(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Demonic Power"
    assert sk.sp_cost == 25
    assert sk.initial_sp == 10
    assert abs(sk.duration - _S2_DURATION) < 1e-6
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff_applied():
    w = _world()
    op = _deploy(w)
    base_atk = op.effective_atk
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert op.effective_atk == int(op.atk * (1 + _S2_ATK_RATIO))
    assert any(b.source_tag == _S2_BUFF_TAG and b.axis.value == "atk" for b in op.buffs)


def test_s2_def_reduced_to_zero():
    """S2 applies flat DEF debuff that zeros effective DEF."""
    w = _world()
    op = _deploy(w)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert op.effective_def == 0


def test_s2_buffs_cleared_on_end():
    w = _world()
    op = _deploy(w)
    base_atk = op.effective_atk
    base_def = op.effective_def
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in op.buffs)
    assert op.effective_atk == base_atk
    assert op.effective_def == base_def
