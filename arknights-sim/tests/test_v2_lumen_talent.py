"""Tests for Lumen Intensive Care talent — +1 SP per ally healed.

Lumen heals up to 3 (or 5 during S2) allies simultaneously. Each healed
ally triggers on_attack_hit once, so one attack cycle gives +3 SP.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, Faction, AttackType, TICK_RATE
from core.systems import register_default_systems
from core.systems.talent_registry import fire_on_attack_hit
from data.characters.lumen import make_lumen, _INTENSIVE_CARE_TAG, _SP_PER_HEAL


def _world(w: int = 6, h: int = 3) -> World:
    grid = TileGrid(width=w, height=h)
    for x in range(w):
        for y in range(h):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    world = World(tile_grid=grid)
    world.global_state.dp_gain_rate = 0.0
    register_default_systems(world)
    return world


def _ally(hp: int = 400, max_hp: int = 1000, name: str = "ally") -> UnitState:
    u = UnitState(name=name, faction=Faction.ALLY, max_hp=max_hp, atk=0,
                  defence=0, res=0.0, atk_interval=1.0, move_speed=1.0)
    u.hp = hp
    return u


# ---------------------------------------------------------------------------
# Test 1: Config
# ---------------------------------------------------------------------------

def test_lumen_talent_config():
    op = make_lumen()
    assert op.talents, "Lumen should have Intensive Care talent"
    t = op.talents[0]
    assert t.name == "Intensive Care"
    assert t.behavior_tag == _INTENSIVE_CARE_TAG


# ---------------------------------------------------------------------------
# Test 2: +1 SP per on_attack_hit while skill inactive
# ---------------------------------------------------------------------------

def test_intensive_care_gains_sp_per_heal():
    """Each on_attack_hit call grants +1 SP while skill is not active."""
    op = make_lumen()
    op.skill.sp = 0.0
    world = _world()
    a = _ally()

    fire_on_attack_hit(world, op, a, 200)
    assert op.skill.sp == pytest.approx(_SP_PER_HEAL)


# ---------------------------------------------------------------------------
# Test 3: 3 heals = +3 SP per cycle
# ---------------------------------------------------------------------------

def test_intensive_care_three_heals_per_cycle():
    """3 allies healed → +3 SP total for one attack cycle."""
    op = make_lumen()
    op.skill.sp = 0.0
    world = _world()
    allies = [_ally(name=f"ally{i}") for i in range(3)]

    for a in allies:
        fire_on_attack_hit(world, op, a, 200)
    assert op.skill.sp == pytest.approx(3 * _SP_PER_HEAL)


# ---------------------------------------------------------------------------
# Test 4: SP caps at sp_cost
# ---------------------------------------------------------------------------

def test_intensive_care_caps_at_sp_cost():
    """SP does not exceed sp_cost even with many heals."""
    op = make_lumen()
    op.skill.sp = 19.0
    world = _world()
    a = _ally()

    # Two heals would push to 21 but sp_cost=20
    fire_on_attack_hit(world, op, a, 200)
    fire_on_attack_hit(world, op, a, 200)
    assert op.skill.sp == pytest.approx(float(op.skill.sp_cost))


# ---------------------------------------------------------------------------
# Test 5: No SP gain while skill is active
# ---------------------------------------------------------------------------

def test_intensive_care_inactive_while_skill_active():
    """Talent does not grant SP when S2 is already active."""
    op = make_lumen()
    op.skill.sp = 5.0
    op.skill.active_remaining = 10.0  # simulate active S2
    world = _world()
    a = _ally()

    fire_on_attack_hit(world, op, a, 200)
    assert op.skill.sp == pytest.approx(5.0), "SP must not change while skill is active"


# ---------------------------------------------------------------------------
# Test 6: Multi-heal integration — tick-level SP accumulation
# ---------------------------------------------------------------------------

def test_intensive_care_sp_accumulates_in_world():
    """In a world tick, Lumen healing 2 allies should accumulate +2 SP per attack."""
    world = _world()
    lumen = make_lumen()
    lumen.deployed = True
    lumen.position = (0.0, 1.0)
    lumen.skill.sp = 0.0
    lumen.atk_cd = 0.0
    world.add_unit(lumen)

    # Add 2 injured allies to heal
    for i in range(2):
        a = _ally(hp=200, max_hp=1000, name=f"ally{i}")
        a.deployed = True
        a.position = (1.0, float(i))
        world.add_unit(a)

    sp_before = lumen.skill.sp
    world.tick()  # Lumen attacks; fire_on_attack_hit fires twice
    # AUTO_TIME SP from tick + talent SP: at least 2 extra from healing 2 allies
    assert lumen.skill.sp > sp_before + 1.5, (
        f"Expected SP gain > 1.5 from talent+tick; got {lumen.skill.sp - sp_before:.2f}"
    )
