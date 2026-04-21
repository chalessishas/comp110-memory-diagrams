"""Bryota S2 "Steadfast as Rock" — 30s MANUAL, ATK+80% DEF+80% STUN 5s.

Tests cover:
  - S2 config (name, sp_cost=50, initial_sp=35, duration=30s, MANUAL)
  - ATK buff applied on trigger
  - DEF buff applied on trigger
  - Enemy in range is STUN'd for 5s on activation
  - Out-of-range enemy unaffected
  - Both buffs cleared after skill ends
  - S1 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, StatusKind, AttackType, Profession
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.bryota import (
    make_bryota, _S2_TAG, _S2_ATK_RATIO, _S2_DEF_RATIO,
    _S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG, _S2_STUN_TAG, _S2_STUN_DURATION, _S2_DURATION,
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


def _enemy(pos=(0.0, 1.0)) -> UnitState:
    e = UnitState(
        name="Enemy", faction=Faction.ENEMY,
        max_hp=3000, atk=100, defence=0, res=0.0,
        atk_interval=1.5, profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL, block=0, cost=0,
    )
    e.deployed = True; e.position = pos; e.path_progress = 1.0
    return e


def test_bryota_s2_config():
    op = make_bryota(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Steadfast as Rock"
    assert sk.sp_cost == 50
    assert sk.initial_sp == 35
    assert sk.duration == _S2_DURATION
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff_applied():
    w = _world()
    op = make_bryota(slot="S2")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    expected = int(base_atk * (1 + _S2_ATK_RATIO))
    assert op.effective_atk == expected
    assert any(b.source_tag == _S2_ATK_BUFF_TAG for b in op.buffs)


def test_s2_def_buff_applied():
    w = _world()
    op = make_bryota(slot="S2")
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    expected = int(base_def * (1 + _S2_DEF_RATIO))
    assert op.effective_def == expected
    assert any(b.source_tag == _S2_DEF_BUFF_TAG for b in op.buffs)


def test_s2_stun_enemy_in_range():
    w = _world()
    op = make_bryota(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    enemy = _enemy(pos=(0.0, 1.0))
    w.add_unit(enemy)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    stun = next((s for s in enemy.statuses if s.source_tag == _S2_STUN_TAG), None)
    assert stun is not None, "Enemy not stunned"
    assert stun.kind == StatusKind.STUN
    assert stun.expires_at - w.global_state.elapsed >= _S2_STUN_DURATION - 0.1


def test_s2_stun_out_of_range_enemy_unaffected():
    w = _world()
    op = make_bryota(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    far_enemy = _enemy(pos=(2.0, 1.0))
    w.add_unit(far_enemy)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert not any(s.source_tag == _S2_STUN_TAG for s in far_enemy.statuses)


def test_s2_buffs_cleared_on_end():
    w = _world()
    op = make_bryota(slot="S2")
    base_atk = op.effective_atk
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag in (_S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG) for b in op.buffs)
    assert op.effective_atk == base_atk
    assert op.effective_def == base_def


def test_s1_regression():
    op = make_bryota(slot="S1")
    assert op.skill is not None and op.skill.slot == "S1"
    assert op.skill.name == "Power Strike β"
