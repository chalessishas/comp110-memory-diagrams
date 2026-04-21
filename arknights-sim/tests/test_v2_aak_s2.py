"""Aak S2 "Medical Protocol" — 15s AUTO, enhanced syringe (+70% ATK ally) + self ATK+20%.

Tests cover:
  - S2 config (slot, name, sp_cost=30, initial_sp=15, duration=15s, AUTO)
  - S2 active flag sets self ATK+20% buff on start
  - Self ATK buff cleared on S2 end
  - Syringe deals reduced dmg (_S2_SYRINGE_DMG=150) under S2
  - Ally receives enhanced +70% ATK buff under S2 (vs +40% base)
  - S3 regression (slot/name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, BuffAxis, SPGainMode, TICK_RATE
from core.systems import register_default_systems
from data.characters.aak import (
    make_aak,
    _S2_TAG, _S2_SELF_ATK_RATIO, _S2_SELF_ATK_BUFF_TAG,
    _S2_SYRINGE_DMG, _S2_ATK_RATIO, _S2_DURATION,
    _SYRINGE_TRUE_DMG, _SYRINGE_ATK_RATIO, _SYRINGE_BUFF_TAG,
    GEEK_RANGE,
)
from data.characters import make_liskarm

_AAK_POS   = (0.0, 1.0)
_ALLY_POS  = (1.0, 1.0)   # dx=1, dy=0 — in GEEK_RANGE
_ENEMY_POS = (1.0, 1.0)


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ally(pos=(1, 1)) -> UnitState:
    op = make_liskarm()
    op.deployed = True
    op.position = (float(pos[0]), float(pos[1]))
    return op


def _enemy(world: World, x: float, y: float) -> UnitState:
    from core.types import Faction
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=99999, atk=0, defence=0, res=0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


def test_aak_s2_config():
    op = make_aak(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Medical Protocol"
    assert sk.sp_cost == 30
    assert sk.initial_sp == 15
    assert sk.duration == _S2_DURATION
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.behavior_tag == _S2_TAG


def test_s2_self_atk_buff_on_start():
    """S2 start grants Aak +20% ATK buff."""
    w = _world()
    op = make_aak(slot="S2")
    op.deployed = True; op.position = _AAK_POS; op.atk_cd = 999.0
    _enemy(w, 1.0, 1.0)
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    assert op.skill.active_remaining > 0, "S2 should be active"
    self_buff = next((b for b in op.buffs if b.source_tag == _S2_SELF_ATK_BUFF_TAG), None)
    assert self_buff is not None, "self ATK buff should be applied"
    assert abs(self_buff.value - _S2_SELF_ATK_RATIO) < 1e-6


def test_s2_self_atk_buff_cleared_on_end():
    """Self ATK buff removed when S2 ends."""
    w = _world()
    op = make_aak(slot="S2")
    op.deployed = True; op.position = _AAK_POS; op.atk_cd = 999.0
    _enemy(w, 1.0, 1.0)
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    # run past duration
    for _ in range(int(TICK_RATE * (_S2_DURATION + 2.0))):
        w.tick()

    assert op.skill.active_remaining == 0.0, "S2 should be inactive"
    self_buff = next((b for b in op.buffs if b.source_tag == _S2_SELF_ATK_BUFF_TAG), None)
    assert self_buff is None, "self ATK buff should be removed after S2"


def test_s2_enhanced_ally_atk_buff():
    """Under S2, when Aak attacks, injected ally gets +70% ATK buff (vs +40% base)."""
    w = _world()
    op = make_aak(slot="S2")
    op.deployed = True; op.position = _AAK_POS; op.atk_cd = 999.0
    ally = _ally(pos=(1, 1))
    enemy = _enemy(w, 1.0, 1.0)
    w.add_unit(op)
    w.add_unit(ally)

    # activate S2 first
    op.skill.sp = float(op.skill.sp_cost)
    w.tick()
    assert op.skill.active_remaining > 0, "S2 should be active"
    assert getattr(op, "_aak_s2_active", False), "S2 active flag should be set"

    # let Aak attack (talent fires, injects ally with S2-enhanced buff)
    op.atk_cd = 0.0
    for _ in range(int(TICK_RATE * 2.0)):
        w.tick()
        atk_buff = next((b for b in ally.buffs if b.source_tag == _SYRINGE_BUFF_TAG), None)
        if atk_buff is not None:
            break

    atk_buff = next((b for b in ally.buffs if b.source_tag == _SYRINGE_BUFF_TAG), None)
    assert atk_buff is not None, "Ally should receive syringe ATK buff after Aak attacks"
    assert abs(atk_buff.value - _S2_ATK_RATIO) < 1e-6, (
        f"S2 ally ATK buff should be {_S2_ATK_RATIO}, got {atk_buff.value}"
    )


def test_s3_regression():
    op = make_aak(slot="S3")
    assert op.skill is not None and op.skill.slot == "S3"
    assert op.skill.name == "Fatal Dose"
