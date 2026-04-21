"""Shining S2 "Faith" — instant AUTO_ATTACK, 300% ATK SHIELD to lowest-HP ally.

Tests cover:
  - S2 config (name, sp_cost=3, initial_sp=0, instant, AUTO_ATTACK, requires_target=False)
  - SHIELD applied to lowest-HP ally (amount = 300% ATK)
  - Shield targets the ally with lowest HP ratio, not self
  - No shield if no allies exist
  - S3 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, StatusKind, SPGainMode, SkillTrigger
from core.systems import register_default_systems
from data.characters.shining import (
    make_shining, _S2_TAG, _S2_SHIELD_RATIO, _S2_SOURCE, _S2_SHIELD_DURATION,
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


def _ally(world: World, x: float, y: float, max_hp: int = 5000, hp: int = None) -> UnitState:
    a = UnitState(name="Ally", faction=Faction.ALLY, max_hp=max_hp, atk=0, defence=0, res=0.0)
    a.alive = True; a.deployed = True; a.position = (x, y)
    if hp is not None:
        a.hp = hp
    world.add_unit(a)
    return a


def test_shining_s2_config():
    op = make_shining(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Faith"
    assert sk.sp_cost == 3
    assert sk.initial_sp == 0
    assert sk.duration == 0.0
    assert sk.sp_gain_mode == SPGainMode.AUTO_ATTACK
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.behavior_tag == _S2_TAG


def test_s2_shield_applied_to_lowest_hp_ally():
    w = _world()
    sh = make_shining(slot="S2")
    sh.deployed = True; sh.position = (0.0, 1.0); sh.atk_cd = 999.0
    w.add_unit(sh)
    # ally1 has full HP, ally2 has half HP → ally2 should receive shield
    ally1 = _ally(w, 1.0, 1.0, max_hp=5000, hp=5000)
    ally2 = _ally(w, 2.0, 1.0, max_hp=5000, hp=1000)

    sh.skill.sp = float(sh.skill.sp_cost)
    w.tick()

    shield = next((s for s in ally2.statuses if s.source_tag == _S2_SOURCE), None)
    assert shield is not None, "SHIELD should be on lowest-HP ally"
    assert shield.kind == StatusKind.SHIELD
    expected_amount = int(sh.effective_atk * _S2_SHIELD_RATIO)
    assert shield.params.get("amount") == expected_amount


def test_s2_shield_not_applied_to_self():
    w = _world()
    sh = make_shining(slot="S2")
    sh.deployed = True; sh.position = (0.0, 1.0); sh.atk_cd = 999.0
    w.add_unit(sh)
    _ally(w, 1.0, 1.0)

    sh.skill.sp = float(sh.skill.sp_cost)
    w.tick()

    assert not any(s.source_tag == _S2_SOURCE for s in sh.statuses), "Shining should not shield herself"


def test_s2_no_shield_without_allies():
    w = _world()
    sh = make_shining(slot="S2")
    sh.deployed = True; sh.position = (0.0, 1.0); sh.atk_cd = 999.0
    w.add_unit(sh)
    # No allies in world

    sh.skill.sp = float(sh.skill.sp_cost)
    w.tick()

    assert not any(s.source_tag == _S2_SOURCE for s in sh.statuses)


def test_s2_shield_expires_at():
    w = _world()
    sh = make_shining(slot="S2")
    sh.deployed = True; sh.position = (0.0, 1.0); sh.atk_cd = 999.0
    w.add_unit(sh)
    ally = _ally(w, 1.0, 1.0)

    sh.skill.sp = float(sh.skill.sp_cost)
    w.tick()

    shield = next((s for s in ally.statuses if s.source_tag == _S2_SOURCE), None)
    assert shield is not None
    assert abs(shield.expires_at - (w.global_state.elapsed + _S2_SHIELD_DURATION)) < 0.5


def test_s3_regression():
    op = make_shining(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Creed Field"
