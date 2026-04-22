"""Huang, Varkis, Hongxue (bgsnow) — conservative ATK-buff S1 tests.

Tests cover for each:
  - S1 config (slot, sp_cost, behavior_tag)
  - S1 ATK buff applied on trigger
  - S1 ATK buff cleared on end
  - S2 regression (slot name)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.huang import make_huang, _S1_TAG as H_S1_TAG, _S1_ATK_RATIO as H_S1_RATIO, _S1_BUFF_TAG as H_S1_BUF, _S1_DURATION as H_S1_DUR
from data.characters.varkis import make_varkis, _S1_TAG as V_S1_TAG, _S1_ATK_RATIO as V_S1_RATIO, _S1_BUFF_TAG as V_S1_BUF, _S1_DURATION as V_S1_DUR
from data.characters.bgsnow import make_bgsnow, _S1_TAG as B_S1_TAG, _S1_ATK_RATIO as B_S1_RATIO, _S1_BUFF_TAG as B_S1_BUF, _S1_DURATION as B_S1_DUR


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _deploy(w, make_fn, slot="S1"):
    op = make_fn(slot=slot)
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    return op


# ── Huang ─────────────────────────────────────────────────────────────────────

def test_huang_s1_config():
    op = make_huang(slot="S1")
    assert op.skill.slot == "S1" and op.skill.sp_cost == 20
    assert op.skill.behavior_tag == H_S1_TAG


def test_huang_s1_atk_buff():
    w = _world()
    op = _deploy(w, make_huang)
    base_atk = op.effective_atk
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert op.effective_atk == int(op.atk * (1 + H_S1_RATIO))
    assert any(b.source_tag == H_S1_BUF for b in op.buffs)


def test_huang_s1_buff_cleared():
    w = _world()
    op = _deploy(w, make_huang)
    base_atk = op.effective_atk
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (H_S1_DUR + 1.0))):
        w.tick()
    assert not any(b.source_tag == H_S1_BUF for b in op.buffs)
    assert op.effective_atk == base_atk


def test_huang_s2_regression():
    op = make_huang(slot="S2")
    assert op.skill is not None and op.skill.slot == "S2"


# ── Varkis ────────────────────────────────────────────────────────────────────

def test_varkis_s1_config():
    op = make_varkis(slot="S1")
    assert op.skill.slot == "S1" and op.skill.sp_cost == 20
    assert op.skill.behavior_tag == V_S1_TAG


def test_varkis_s1_atk_buff():
    w = _world()
    op = _deploy(w, make_varkis)
    base_atk = op.effective_atk
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert op.effective_atk == int(op.atk * (1 + V_S1_RATIO))
    assert any(b.source_tag == V_S1_BUF for b in op.buffs)


def test_varkis_s1_buff_cleared():
    w = _world()
    op = _deploy(w, make_varkis)
    base_atk = op.effective_atk
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (V_S1_DUR + 1.0))):
        w.tick()
    assert not any(b.source_tag == V_S1_BUF for b in op.buffs)
    assert op.effective_atk == base_atk


def test_varkis_s2_regression():
    op = make_varkis(slot="S2")
    assert op.skill is not None and op.skill.slot == "S2"


# ── Hongxue (bgsnow) ──────────────────────────────────────────────────────────

def test_bgsnow_s1_config():
    op = make_bgsnow(slot="S1")
    assert op.skill.slot == "S1" and op.skill.sp_cost == 30
    assert op.skill.behavior_tag == B_S1_TAG


def test_bgsnow_s1_atk_buff():
    w = _world()
    op = _deploy(w, make_bgsnow)
    base_atk = op.effective_atk
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert op.effective_atk == int(op.atk * (1 + B_S1_RATIO))
    assert any(b.source_tag == B_S1_BUF for b in op.buffs)


def test_bgsnow_s1_buff_cleared():
    w = _world()
    op = _deploy(w, make_bgsnow)
    base_atk = op.effective_atk
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (B_S1_DUR + 1.0))):
        w.tick()
    assert not any(b.source_tag == B_S1_BUF for b in op.buffs)
    assert op.effective_atk == base_atk


def test_bgsnow_s2_regression():
    op = make_bgsnow(slot="S2")
    assert op.skill is not None and op.skill.slot == "S2"
