"""Specter S2 "Pather's Light" — 30s AUTO, ATK+160%, 5% lifesteal on hit, STUN 10s on end.

Tests cover:
  - S2 config (name, sp_cost=40, initial_sp=20, duration=30s, AUTO, requires_target)
  - ATK buff: effective_atk = base * (1 + 1.6)
  - _specter_s2_active flag set during skill
  - ATK buff cleared on skill end
  - Post-skill STUN applied for 10s
  - S3 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, StatusKind, SkillTrigger
from core.systems import register_default_systems
from data.characters.specter import (
    make_specter, _S2_TAG, _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_STUN_DURATION, _S2_STUN_TAG,
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
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=99999, atk=0, defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


def test_specter_s2_config():
    op = make_specter(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Pather's Light"
    assert sk.sp_cost == 40
    assert sk.initial_sp == 20
    assert sk.duration == 30.0
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff_applied():
    w = _world()
    op = make_specter(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _enemy(w, 1.0, 1.0)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    expected = int(base_atk * (1 + _S2_ATK_RATIO))
    assert op.effective_atk == expected
    assert any(b.source_tag == _S2_BUFF_TAG for b in op.buffs)


def test_s2_active_flag_set():
    w = _world()
    op = make_specter(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _enemy(w, 1.0, 1.0)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    assert getattr(op, "_specter_s2_active", False) is True


def test_s2_buff_cleared_on_end():
    w = _world()
    op = make_specter(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _enemy(w, 1.0, 1.0)

    op.skill.sp = float(op.skill.sp_cost)
    for _ in range(int(TICK_RATE * (30.0 + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in op.buffs)
    assert op.effective_atk == base_atk


def test_s2_stun_applied_on_end():
    w = _world()
    op = make_specter(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    _enemy(w, 1.0, 1.0)

    op.skill.sp = float(op.skill.sp_cost)
    for _ in range(int(TICK_RATE * (30.0 + 0.5))):
        w.tick()

    stun = next((s for s in op.statuses if s.source_tag == _S2_STUN_TAG), None)
    assert stun is not None, "post-skill STUN not applied"
    assert stun.kind == StatusKind.STUN
    assert stun.expires_at > w.global_state.elapsed


def test_s3_regression():
    op = make_specter(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Deathless Aegis"
