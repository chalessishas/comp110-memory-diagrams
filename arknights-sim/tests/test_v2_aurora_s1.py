"""Aurora S1 "Defend the Homeland" — 30s MANUAL, DEF+210% block+2 STUN 5s.

Tests cover:
  - S1 config (name, sp_cost=20, initial_sp=10, duration=30s, MANUAL)
  - DEF buff applied on trigger
  - block increases by 2 on trigger
  - Enemies in range are STUN'd for 5s on activation
  - DEF buff and block restored after skill ends
  - S2 regression (slot/name)
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
from data.characters.aurora import (
    make_aurora, _S1_TAG, _S1_DEF_RATIO, _S1_DEF_BUFF_TAG,
    _S1_BLOCK_BONUS, _S1_STUN_DURATION, _S1_STUN_TAG, _S1_DURATION,
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
        max_hp=3000, atk=200, defence=100, res=0.0,
        atk_interval=1.5, profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL, block=0, cost=0,
    )
    e.deployed = True; e.position = pos; e.path_progress = 1.0
    return e


def test_aurora_s1_config():
    op = make_aurora(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Defend the Homeland"
    assert sk.sp_cost == 20
    assert sk.initial_sp == 10
    assert sk.duration == _S1_DURATION
    assert sk.behavior_tag == _S1_TAG


def test_s1_def_buff_applied():
    w = _world()
    op = make_aurora(slot="S1")
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    expected = int(base_def * (1 + _S1_DEF_RATIO))
    assert op.effective_def == expected
    assert any(b.source_tag == _S1_DEF_BUFF_TAG for b in op.buffs)


def test_s1_block_increases():
    w = _world()
    op = make_aurora(slot="S1")
    base_block = op.block
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert op.block == base_block + _S1_BLOCK_BONUS


def test_s1_stun_enemy_in_range():
    w = _world()
    op = make_aurora(slot="S1")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    enemy = _enemy(pos=(0.0, 1.0))  # same tile → in range (0,0)
    w.add_unit(enemy)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    stun = next((s for s in enemy.statuses if s.source_tag == _S1_STUN_TAG), None)
    assert stun is not None, "Enemy not stunned"
    assert stun.kind == StatusKind.STUN
    elapsed = w.global_state.elapsed
    assert stun.expires_at - elapsed >= _S1_STUN_DURATION - 0.1


def test_s1_stun_out_of_range_enemy_unaffected():
    w = _world()
    op = make_aurora(slot="S1")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    far_enemy = _enemy(pos=(2.0, 1.0))  # dx=2, out of (0,0) range
    w.add_unit(far_enemy)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert not any(s.source_tag == _S1_STUN_TAG for s in far_enemy.statuses)


def test_s1_buffs_cleared_on_end():
    w = _world()
    op = make_aurora(slot="S1")
    base_block = op.block
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (_S1_DURATION + 1.0))):
        w.tick()

    assert op.block == base_block
    assert op.effective_def == base_def
    assert not any(b.source_tag == _S1_DEF_BUFF_TAG for b in op.buffs)


def test_s2_regression():
    op = make_aurora(slot="S2")
    assert op.skill is not None and op.skill.slot == "S2"
    assert op.skill.name == "Artificial Snowfall"
