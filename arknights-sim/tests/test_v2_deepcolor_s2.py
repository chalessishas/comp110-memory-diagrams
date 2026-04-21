"""Deepcolor S2 "Tentacle Feast" — 30s AUTO, deploys 1 Jellyfish G1 at operator's position.

Tests cover:
  - S2 config (name="Tentacle Feast", sp_cost=28, initial_sp=0, duration=30s, AUTO, behavior_tag)
  - S2 activation deploys 1 Jellyfish G1 in world
  - Jellyfish G1 has correct HP
  - Jellyfish G1 is alive and deployed at carrier's position
  - Skill end despawns the jellyfish
  - S3 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, SkillTrigger, SPGainMode
from core.systems import register_default_systems
from data.characters.deepcolor import (
    make_deepcolor, _S2_TAG, _JELLY_G1_HP,
)


_S2_SP_COST = 28
_S2_DURATION = 30.0


def _world() -> World:
    grid = TileGrid(width=8, height=5)
    for x in range(8):
        for y in range(5):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def test_deepcolor_s2_config():
    op = make_deepcolor(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Tentacle Feast"
    assert sk.sp_cost == _S2_SP_COST
    assert sk.duration == _S2_DURATION
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.behavior_tag == _S2_TAG


def test_s2_deploys_one_jellyfish():
    w = _world()
    dc = make_deepcolor(slot="S2")
    dc.deployed = True; dc.position = (2.0, 2.0); dc.atk_cd = 999.0
    w.add_unit(dc)

    units_before = len(w.units)
    dc.skill.sp = float(dc.skill.sp_cost)
    w.tick()

    units_after = len(w.units)
    assert units_after == units_before + 1, "S2 should deploy exactly 1 jellyfish"


def test_s2_jellyfish_has_correct_hp():
    w = _world()
    dc = make_deepcolor(slot="S2")
    dc.deployed = True; dc.position = (2.0, 2.0); dc.atk_cd = 999.0
    w.add_unit(dc)

    dc.skill.sp = float(dc.skill.sp_cost)
    w.tick()

    jelly_id = getattr(dc, "_dc_jelly_id", None)
    assert jelly_id is not None
    jelly = w.unit_by_id(jelly_id)
    assert jelly is not None
    assert jelly.max_hp == _JELLY_G1_HP


def test_s2_jellyfish_deployed_at_carrier_position():
    w = _world()
    dc = make_deepcolor(slot="S2")
    dc.deployed = True; dc.position = (3.0, 1.0); dc.atk_cd = 999.0
    w.add_unit(dc)

    dc.skill.sp = float(dc.skill.sp_cost)
    w.tick()

    jelly_id = getattr(dc, "_dc_jelly_id", None)
    jelly = w.unit_by_id(jelly_id)
    assert jelly is not None and jelly.alive and jelly.deployed
    assert jelly.position == (3.0, 1.0)


def test_s2_skill_end_despawns_jellyfish():
    w = _world()
    dc = make_deepcolor(slot="S2")
    dc.deployed = True; dc.position = (2.0, 2.0); dc.atk_cd = 999.0
    w.add_unit(dc)

    dc.skill.sp = float(dc.skill.sp_cost)
    w.tick()

    jelly_id = getattr(dc, "_dc_jelly_id", None)
    # Run skill to completion
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    jelly = w.unit_by_id(jelly_id)
    assert jelly is None or not jelly.alive


def test_s3_regression():
    op = make_deepcolor(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Abyssal Tide"
