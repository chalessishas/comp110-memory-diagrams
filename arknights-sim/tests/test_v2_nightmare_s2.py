"""Nightmare S2 "Darkening" — ATK+60% for 20s, AUTO trigger.

Tests cover:
  - S2 config (slot, sp_cost, initial_sp, duration, behavior_tag)
  - ATK buff applied on skill start
  - effective_atk = base_atk * (1 + 0.60)
  - ATK buff cleared after skill ends
  - S3 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, Faction
from core.systems import register_default_systems
from core.state.unit_state import UnitState
from data.characters.nightmare import (
    make_nightmare, _S2_TAG, _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_DURATION,
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


def _enemy(world: World, x: float, y: float) -> UnitState:
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=99999, atk=0, defence=0, res=0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


# ---------------------------------------------------------------------------
# Test 1: S2 configured correctly
# ---------------------------------------------------------------------------

def test_nightmare_s2_config():
    n = make_nightmare(slot="S2")
    sk = n.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Darkening"
    assert sk.sp_cost == 25
    assert sk.initial_sp == 10
    assert sk.duration == _S2_DURATION
    assert sk.behavior_tag == _S2_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK buff applied on skill start
# ---------------------------------------------------------------------------

def test_s2_atk_buff_applied():
    w = _world()
    n = make_nightmare(slot="S2")
    base_atk = n.effective_atk
    n.deployed = True; n.position = (0.0, 1.0); n.atk_cd = 999.0
    w.add_unit(n)
    _enemy(w, 1.0, 1.0)

    n.skill.sp = float(n.skill.sp_cost)
    w.tick()

    assert n.effective_atk > base_atk, "S2 must increase ATK"
    assert any(b.source_tag == _S2_BUFF_TAG for b in n.buffs), "ATK buff must be present"


# ---------------------------------------------------------------------------
# Test 3: effective_atk = base * (1 + ratio)
# ---------------------------------------------------------------------------

def test_s2_atk_amount():
    w = _world()
    n = make_nightmare(slot="S2")
    base_atk = n.effective_atk
    n.deployed = True; n.position = (0.0, 1.0); n.atk_cd = 999.0
    w.add_unit(n)
    _enemy(w, 1.0, 1.0)

    n.skill.sp = float(n.skill.sp_cost)
    w.tick()

    expected = int(base_atk * (1 + _S2_ATK_RATIO))
    assert n.effective_atk == expected, f"expected ATK={expected}, got {n.effective_atk}"


# ---------------------------------------------------------------------------
# Test 4: ATK buff cleared after skill ends
# ---------------------------------------------------------------------------

def test_s2_buff_cleared_on_end():
    w = _world()
    n = make_nightmare(slot="S2")
    base_atk = n.effective_atk
    n.deployed = True; n.position = (0.0, 1.0); n.atk_cd = 999.0
    w.add_unit(n)
    _enemy(w, 1.0, 1.0)

    n.skill.sp = float(n.skill.sp_cost)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in n.buffs), "buff must be removed"
    assert n.effective_atk == base_atk, "ATK must return to base after S2"


# ---------------------------------------------------------------------------
# Test 5: S3 regression
# ---------------------------------------------------------------------------

def test_s3_regression():
    n = make_nightmare(slot="S3")
    assert n.skill is not None and n.skill.slot == "S3"
    assert n.skill.name == "Eternal Sleep"
