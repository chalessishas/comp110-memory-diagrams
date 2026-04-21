"""Bison S1 "DEF Up γ", S2 "Deepen Battleline", Talent "Cross Cover".

Tests cover:
  - Talent: DEF+70 flat buff applied on deploy
  - S1 config (name, slot, sp_cost, initial_sp, duration=40, MANUAL)
  - S1: DEF+100% ratio buff applied
  - S1: buff cleared on end
  - S2 config (name, slot, sp_cost, initial_sp, duration=40, MANUAL)
  - S2: self DEF+120% applied
  - S2: all deployed allies get DEF+30%
  - S2: ally outside deployment not buffed
  - S2: buffs cleared on end (self + allies)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, SkillTrigger, SPGainMode
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from core.systems.talent_registry import fire_on_deploy
from data.characters.bison import (
    make_bison,
    _TALENT_TAG, _TALENT_BUFF_TAG, _TALENT_DEF_FLAT,
    _S1_TAG, _S1_DEF_RATIO, _S1_BUFF_TAG, _S1_DURATION,
    _S2_TAG, _S2_SELF_DEF_RATIO, _S2_ALLY_DEF_RATIO,
    _S2_SELF_BUFF_TAG, _S2_ALLY_BUFF_TAG, _S2_DURATION,
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


def _ally(world: World, x: float, y: float) -> UnitState:
    a = UnitState(name="Ally", faction=Faction.ALLY, max_hp=2000, atk=300, defence=200, res=0)
    a.alive = True; a.deployed = True; a.position = (x, y)
    world.add_unit(a)
    return a


def _deploy_bison(w: World, slot: str = "S2") -> UnitState:
    op = make_bison(slot=slot)
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    fire_on_deploy(w, op)
    return op


# ── Talent ───────────────────────────────────────────────────────────────────

def test_talent_grants_def_flat():
    w = _world()
    op = _deploy_bison(w)
    buff = next((b for b in op.buffs if b.source_tag == _TALENT_BUFF_TAG), None)
    assert buff is not None
    assert abs(buff.value - _TALENT_DEF_FLAT) < 1e-6


def test_talent_increases_effective_def():
    w = _world()
    base_def = make_bison().effective_def  # before deploy (no talent buff)
    op = _deploy_bison(w)
    assert op.effective_def == base_def + int(_TALENT_DEF_FLAT)


# ── S1: DEF Up γ ──────────────────────────────────────────────────────────

def test_s1_config():
    op = make_bison(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "DEF Up γ"
    assert sk.sp_cost == 30
    assert sk.initial_sp == 15
    assert abs(sk.duration - _S1_DURATION) < 1e-6
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.behavior_tag == _S1_TAG


def test_s1_def_buff_applied():
    w = _world()
    op = make_bison(slot="S1")
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    buff = next((b for b in op.buffs if b.source_tag == _S1_BUFF_TAG), None)
    assert buff is not None and abs(buff.value - _S1_DEF_RATIO) < 1e-6
    assert op.effective_def == int(op.defence * (1 + _S1_DEF_RATIO))


def test_s1_buff_cleared_on_end():
    w = _world()
    op = make_bison(slot="S1")
    base_def = op.effective_def
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    for _ in range(int(TICK_RATE * (_S1_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S1_BUFF_TAG for b in op.buffs)
    assert op.effective_def == base_def


# ── S2: Deepen Battleline ─────────────────────────────────────────────────

def test_s2_config():
    op = make_bison(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Deepen Battleline"
    assert sk.sp_cost == 50
    assert sk.initial_sp == 20
    assert abs(sk.duration - _S2_DURATION) < 1e-6
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.behavior_tag == _S2_TAG


def test_s2_self_def_buff():
    w = _world()
    op = make_bison(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    buff = next((b for b in op.buffs if b.source_tag == _S2_SELF_BUFF_TAG), None)
    assert buff is not None and abs(buff.value - _S2_SELF_DEF_RATIO) < 1e-6


def test_s2_ally_def_buff():
    w = _world()
    op = make_bison(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    ally = _ally(w, 1.0, 1.0)
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    buff = next((b for b in ally.buffs if b.source_tag == _S2_ALLY_BUFF_TAG), None)
    assert buff is not None and abs(buff.value - _S2_ALLY_DEF_RATIO) < 1e-6


def test_s2_undeployed_ally_not_buffed():
    w = _world()
    op = make_bison(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    # Create ally but not yet deployed
    a = UnitState(name="Reserve", faction=Faction.ALLY, max_hp=2000, atk=300, defence=200, res=0)
    a.alive = True; a.deployed = False; a.position = (1.0, 1.0)
    w.add_unit(a)
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert not any(b.source_tag == _S2_ALLY_BUFF_TAG for b in a.buffs)


def test_s2_buffs_cleared_on_end():
    w = _world()
    op = make_bison(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    ally = _ally(w, 1.0, 1.0)
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S2_SELF_BUFF_TAG for b in op.buffs)
    assert not any(b.source_tag == _S2_ALLY_BUFF_TAG for b in ally.buffs)
