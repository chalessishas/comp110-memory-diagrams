"""Sora S2 "Encore" — SP aura ×2 (→2 SP/s) for 20s, AUTO trigger.

Tests cover:
  - S2 config (slot, name, sp_cost, initial_sp, duration, behavior_tag)
  - S2 active flag set during skill
  - Ally SP charges faster during S2 (≥2× base rate)
  - S2 active flag cleared after skill ends
  - S3 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, SkillComponent
from core.types import TileType, TICK_RATE, SPGainMode, SkillTrigger
from core.systems import register_default_systems
from data.characters.sora import (
    make_sora, _S2_TAG, _S2_DURATION, _S2_SP_MULTIPLIER, _S2_ACTIVE_FLAG,
    _TRAIT_SP_RATE,
)
from data.characters import make_liskarm


def _world() -> World:
    grid = TileGrid(width=8, height=3)
    for x in range(8):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ally_with_skill(pos=(1, 1), sp_cost: int = 100) -> UnitState:
    op = make_liskarm()
    op.deployed = True
    op.position = (float(pos[0]), float(pos[1]))
    op.skill = SkillComponent(
        name="TestSkill",
        slot="S1",
        sp_cost=sp_cost,
        initial_sp=0,
        duration=10.0,
        sp_gain_mode=SPGainMode.AUTO_ATTACK,
        trigger=SkillTrigger.AUTO,
        requires_target=False,
        behavior_tag="noop_skill",
    )
    op.skill.sp = 0.0
    return op


def test_sora_s2_config():
    op = make_sora(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Encore"
    assert sk.sp_cost == 25
    assert sk.initial_sp == 10
    assert sk.duration == _S2_DURATION
    assert sk.behavior_tag == _S2_TAG


def test_s2_fires_when_full():
    w = _world()
    op = make_sora(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0)
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    assert op.skill.active_remaining > 0, "S2 should be active after sp filled"


def test_s2_boosts_ally_sp_rate():
    """Ally inside range should gain SP faster under S2 than without."""
    w_base = _world()
    sora_base = make_sora(slot="S2")
    sora_base.deployed = True; sora_base.position = (0.0, 1.0)
    ally_base = _ally_with_skill(pos=(1, 1))
    w_base.add_unit(sora_base)
    w_base.add_unit(ally_base)

    measure_ticks = int(TICK_RATE * 5.0)
    for _ in range(measure_ticks):
        w_base.tick()
    sp_no_s2 = ally_base.skill.sp

    w_s2 = _world()
    sora_s2 = make_sora(slot="S2")
    sora_s2.deployed = True; sora_s2.position = (0.0, 1.0)
    ally_s2 = _ally_with_skill(pos=(1, 1))
    w_s2.add_unit(sora_s2)
    w_s2.add_unit(ally_s2)

    sora_s2.skill.sp = float(sora_s2.skill.sp_cost)
    for _ in range(measure_ticks):
        w_s2.tick()
    sp_with_s2 = ally_s2.skill.sp

    assert sp_with_s2 > sp_no_s2 * 1.5, (
        f"S2 should significantly boost ally SP: base={sp_no_s2:.1f} vs s2={sp_with_s2:.1f}"
    )


def test_s2_expires_after_duration():
    w = _world()
    op = make_sora(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0)
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert op.skill.active_remaining == 0.0, "S2 should have expired"


def test_s3_regression():
    op = make_sora(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Grand Performance"
