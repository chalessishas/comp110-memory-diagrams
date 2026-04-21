"""Tests for Sora S3 "Grand Performance" — SP aura ×3, Inspiration ATK 80, 30s MANUAL."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, SkillComponent
from core.types import Faction, TileType, TICK_RATE, BuffStack, SPGainMode, SkillTrigger
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
import pytest
from data.characters.sora import (
    make_sora, _S3_TAG, _S3_DURATION, _S3_SP_MULTIPLIER, _S3_INSPIRATION_ATK,
    _TRAIT_SP_RATE, _TALENT_SP_BONUS,
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


def _ally_with_skill(x=1.0):
    a = UnitState(name="Fang", faction=Faction.ALLY, max_hp=3000, atk=600, defence=200, res=0.0)
    a.deployed = True
    a.position = (x, 1.0)
    a.skill = SkillComponent(
        name="Test", slot="S2", sp_cost=30, initial_sp=0,
        sp_gain_mode=SPGainMode.AUTO_TIME, trigger=SkillTrigger.AUTO,
        behavior_tag="noop",
    )
    return a


def test_s3_config():
    op = make_sora(slot="S3")
    assert op.skill is not None
    assert op.skill.slot == "S3"
    assert op.skill.behavior_tag == _S3_TAG
    assert op.skill.sp_cost == 35
    assert op.skill.duration == _S3_DURATION


def test_s3_active_flag_set():
    w = _world()
    op = make_sora(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert getattr(op, "_sora_s3_active", False)


def test_s3_sp_aura_multiplier():
    """S3 multiplier constant should be higher than S2 multiplier."""
    from data.characters.sora import _S2_SP_MULTIPLIER
    assert _S3_SP_MULTIPLIER > _S2_SP_MULTIPLIER


def test_s3_inspiration_atk_doubled():
    """During S3, Inspiration buff value should be 80 (vs 40 normally)."""
    w = _world()
    op = make_sora(slot="S3")
    ally = _ally_with_skill(x=1.0)
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    w.add_unit(ally)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    _ticks(w, 0.5)  # let talent tick and push inspiration
    insp = [b for b in ally.buffs if b.stack == BuffStack.INSPIRATION]
    assert len(insp) >= 1
    assert insp[-1].value == float(_S3_INSPIRATION_ATK)


def test_s3_flag_cleared_on_end():
    w = _world()
    op = make_sora(slot="S3")
    op.deployed = True
    op.position = (0.0, 1.0)
    op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    _ticks(w, _S3_DURATION + 0.5)
    assert not getattr(op, "_sora_s3_active", True)
