"""Rosa (poca), Ambriel (glaze), Lunacub (lunacu) — Sniper S1/S2 tests.

Tests cover for each:
  - S1 config (slot, sp_cost, behavior_tag)
  - S1 buff applied on trigger
  - S1 buff cleared on end
  - S2 regression (slot name)

Lunacu S2 also tests ASPD buff applied and cleared.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.poca import make_poca, _S1_TAG as P_S1_TAG, _S1_ATK_RATIO as P_S1_RATIO, _S1_BUFF_TAG as P_S1_BUF, _S1_DURATION as P_S1_DUR
from data.characters.glaze import make_glaze, _S1_TAG as G_S1_TAG, _S1_ATK_RATIO as G_S1_RATIO, _S1_BUFF_TAG as G_S1_BUF, _S1_DURATION as G_S1_DUR, _S2_TAG as G_S2_TAG, _S2_ATK_RATIO as G_S2_RATIO, _S2_BUFF_TAG as G_S2_BUF, _S2_DURATION as G_S2_DUR
from data.characters.lunacu import make_lunacu, _S1_TAG as L_S1_TAG, _S1_ATK_RATIO as L_S1_RATIO, _S1_BUFF_TAG as L_S1_BUF, _S1_DURATION as L_S1_DUR, _S2_TAG as L_S2_TAG, _S2_ASPD_BONUS as L_S2_ASPD, _S2_BUFF_TAG as L_S2_BUF, _S2_DURATION as L_S2_DUR


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


# ── Rosa (poca) ────────────────────────────────────────────────────────────────

def test_poca_s1_config():
    op = make_poca(slot="S1")
    assert op.skill.slot == "S1" and op.skill.sp_cost == 30
    assert op.skill.behavior_tag == P_S1_TAG


def test_poca_s1_atk_buff():
    w = _world()
    op = _deploy(w, make_poca)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert op.effective_atk == int(op.atk * (1 + P_S1_RATIO))
    assert any(b.source_tag == P_S1_BUF for b in op.buffs)


def test_poca_s1_buff_cleared():
    w = _world()
    op = _deploy(w, make_poca)
    base_atk = op.effective_atk
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (P_S1_DUR + 1.0))):
        w.tick()
    assert not any(b.source_tag == P_S1_BUF for b in op.buffs)
    assert op.effective_atk == base_atk


def test_poca_s2_regression():
    op = make_poca(slot="S2")
    assert op.skill is not None and op.skill.slot == "S2"


# ── Ambriel (glaze) ───────────────────────────────────────────────────────────

def test_glaze_s1_config():
    op = make_glaze(slot="S1")
    assert op.skill.slot == "S1" and op.skill.sp_cost == 30
    assert op.skill.behavior_tag == G_S1_TAG


def test_glaze_s1_atk_buff():
    w = _world()
    op = _deploy(w, make_glaze)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert op.effective_atk == int(op.atk * (1 + G_S1_RATIO))
    assert any(b.source_tag == G_S1_BUF for b in op.buffs)


def test_glaze_s1_buff_cleared():
    w = _world()
    op = _deploy(w, make_glaze)
    base_atk = op.effective_atk
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (G_S1_DUR + 1.0))):
        w.tick()
    assert not any(b.source_tag == G_S1_BUF for b in op.buffs)
    assert op.effective_atk == base_atk


def test_glaze_s2_atk_buff():
    w = _world()
    op = _deploy(w, make_glaze, slot="S2")
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert op.effective_atk == int(op.atk * (1 + G_S2_RATIO))
    assert any(b.source_tag == G_S2_BUF for b in op.buffs)


def test_glaze_s2_buff_cleared():
    w = _world()
    op = _deploy(w, make_glaze, slot="S2")
    base_atk = op.effective_atk
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (G_S2_DUR + 1.0))):
        w.tick()
    assert not any(b.source_tag == G_S2_BUF for b in op.buffs)
    assert op.effective_atk == base_atk


# ── Lunacub (lunacu) ──────────────────────────────────────────────────────────

def test_lunacu_s1_config():
    op = make_lunacu(slot="S1")
    assert op.skill.slot == "S1" and op.skill.sp_cost == 25
    assert op.skill.behavior_tag == L_S1_TAG


def test_lunacu_s1_atk_buff():
    w = _world()
    op = _deploy(w, make_lunacu)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert op.effective_atk == int(op.atk * (1 + L_S1_RATIO))
    assert any(b.source_tag == L_S1_BUF for b in op.buffs)


def test_lunacu_s1_buff_cleared():
    w = _world()
    op = _deploy(w, make_lunacu)
    base_atk = op.effective_atk
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (L_S1_DUR + 1.0))):
        w.tick()
    assert not any(b.source_tag == L_S1_BUF for b in op.buffs)
    assert op.effective_atk == base_atk


def test_lunacu_s2_aspd_buff():
    w = _world()
    op = _deploy(w, make_lunacu, slot="S2")
    base_aspd = op.effective_aspd
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    assert op.effective_aspd == base_aspd + L_S2_ASPD
    assert any(b.source_tag == L_S2_BUF for b in op.buffs)


def test_lunacu_s2_aspd_cleared():
    w = _world()
    op = _deploy(w, make_lunacu, slot="S2")
    base_aspd = op.effective_aspd
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)
    for _ in range(int(TICK_RATE * (L_S2_DUR + 1.0))):
        w.tick()
    assert not any(b.source_tag == L_S2_BUF for b in op.buffs)
    assert op.effective_aspd == base_aspd
