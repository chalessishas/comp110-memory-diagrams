"""Vigna S2 "Hammer-On" — ATK +200%, interval +0.5s, crit 30% for 30s.

Tests cover:
  - S2 config (slot, name, sp_cost, initial_sp, duration, behavior_tag)
  - ATK buff applied on start: effective_atk = base * (1 + 2.0)
  - Attack interval increased by 0.5s during S2
  - Crit chance set to 30% during S2
  - All buffs cleared after skill ends
  - S3 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.vigna import (
    make_vigna, _S2_TAG, _S2_ATK_RATIO, _S2_ATK_TAG, _S2_INTERVAL_TAG,
    _S2_INTERVAL, _CRIT_SKILL, _CRIT_BASE,
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


def test_vigna_s2_config():
    op = make_vigna(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Hammer-On"
    assert sk.sp_cost == 25
    assert sk.initial_sp == 10
    assert sk.duration == 30.0
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff_applied():
    w = _world()
    op = make_vigna(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    w.tick()

    assert op.effective_atk > base_atk
    assert any(b.source_tag == _S2_ATK_TAG for b in op.buffs)


def test_s2_atk_amount():
    w = _world()
    op = make_vigna(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    w.tick()

    expected = int(base_atk * (1 + _S2_ATK_RATIO))
    assert op.effective_atk == expected


def test_s2_interval_increased():
    w = _world()
    op = make_vigna(slot="S2")
    base_interval = op.current_atk_interval
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    w.tick()

    assert op.current_atk_interval == base_interval + _S2_INTERVAL
    assert any(b.source_tag == _S2_INTERVAL_TAG and b.axis == BuffAxis.ATK_INTERVAL
               for b in op.buffs)


def test_s2_crit_chance():
    w = _world()
    op = make_vigna(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    w.tick()

    assert op.crit_chance == _CRIT_SKILL


def test_s2_buffs_cleared_on_end():
    w = _world()
    op = make_vigna(slot="S2")
    base_atk = op.effective_atk
    base_interval = op.current_atk_interval
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (30.0 + 1.0))):
        w.tick()

    assert not any(b.source_tag in (_S2_ATK_TAG, _S2_INTERVAL_TAG) for b in op.buffs)
    assert op.effective_atk == base_atk
    assert op.current_atk_interval == base_interval
    assert op.crit_chance == _CRIT_BASE


def test_s3_regression():
    op = make_vigna(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Fierce Overdrive"
