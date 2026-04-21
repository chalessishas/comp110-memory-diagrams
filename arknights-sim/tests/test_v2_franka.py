"""Franka S1 "Swift Strike γ", S2 "Vorpal Edge", Talent "Thermite Blade".

Tests cover:
  - Talent: 20% DEF ignore chance (seed=1 procs, seed=0 no proc)
  - S1 config (name, slot, sp_cost=40, initial_sp=10, duration=35, AUTO, AUTO_TIME)
  - S1: ATK+34% buff applied on fire
  - S1: ASPD+35 buff applied on fire
  - S1: buffs cleared on end
  - S2 config (name, slot, sp_cost=20, initial_sp=5, duration=26, AUTO, AUTO_TIME)
  - S2: ATK+70% buff applied
  - S2: guaranteed DEF ignore (extra true damage every attack)
  - S2: Talent proc chance at 50% during S2 (seed=1, random()=0.134 < 0.50 → procs)
  - S2: buffs cleared on end; _franka_s2_active cleared
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, SkillTrigger, SPGainMode
from core.systems import register_default_systems
from core.systems.skill_system import _fire_skill
from data.characters.franka import (
    make_franka,
    _TALENT_TAG, _TALENT_PROC_CHANCE, _TALENT_S2_PROC_CHANCE,
    _S1_TAG, _S1_ATK_RATIO, _S1_ASPD, _S1_BUFF_TAG, _S1_DURATION,
    _S2_TAG, _S2_ATK_RATIO, _S2_BUFF_TAG, _S2_DURATION,
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


def _enemy(world: World, defence: int = 0) -> UnitState:
    e = UnitState(name="Dummy", faction=Faction.ENEMY, max_hp=999999, atk=0,
                  defence=defence, res=0)
    e.alive = True; e.deployed = True; e.position = (0.0, 1.0)
    world.add_unit(e)
    return e


def _deploy(w: World, slot: str = "S2") -> UnitState:
    op = make_franka(slot=slot)
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    return op


# ── Talent: Thermite Blade ────────────────────────────────────────────────────

def test_talent_def_ignore_procs_seed_1():
    """seed=1 → random()≈0.134 < 0.20 → talent procs: extra true damage = effective_def."""
    w = _world()
    w.rng.seed(1)
    op = _deploy(w)
    e = _enemy(w, defence=300)
    e.blocked_by_unit_ids = []
    op.atk_cd = 0.0

    hp_before = e.hp
    for _ in range(3):
        w.tick()

    single_normal = max(int(op.effective_atk * 0.05), op.effective_atk - 300)
    # With DEF ignore proc: extra = min(300, op.effective_atk)
    expected_def_bonus = min(300, op.effective_atk)
    hp_lost = hp_before - e.hp
    assert hp_lost > single_normal, "DEF ignore should add extra damage"


def test_talent_def_ignore_no_proc_seed_0():
    """seed=0 → random()≈0.844 ≥ 0.20 → talent does NOT proc; only normal damage."""
    w = _world()
    w.rng.seed(0)
    op = _deploy(w)
    e = _enemy(w, defence=300)
    op.atk_cd = 0.0

    hp_before = e.hp
    for _ in range(3):
        w.tick()

    single_normal = max(int(op.effective_atk * 0.05), op.effective_atk - 300)
    hp_lost = hp_before - e.hp
    assert hp_lost == single_normal, f"No DEF ignore expected, got {hp_lost} vs {single_normal}"


# ── S1: Swift Strike γ ────────────────────────────────────────────────────────

def test_s1_config():
    op = make_franka(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Swift Strike γ"
    assert sk.sp_cost == 40
    assert sk.initial_sp == 10
    assert abs(sk.duration - _S1_DURATION) < 1e-6
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.behavior_tag == _S1_TAG


def test_s1_atk_buff_applied():
    w = _world()
    op = _deploy(w, slot="S1")
    base_atk = op.effective_atk
    op.skill.sp = float(op.skill.sp_cost)
    _fire_skill(w, op)

    buff = next((b for b in op.buffs if b.source_tag == _S1_BUFF_TAG and b.axis.value == "atk"), None)
    assert buff is not None and abs(buff.value - _S1_ATK_RATIO) < 1e-6
    assert op.effective_atk == int(op.atk * (1 + _S1_ATK_RATIO))


def test_s1_aspd_buff_applied():
    w = _world()
    op = _deploy(w, slot="S1")
    base_interval = op.current_atk_interval
    op.skill.sp = float(op.skill.sp_cost)
    _fire_skill(w, op)

    buff = next((b for b in op.buffs if b.source_tag == _S1_BUFF_TAG and b.axis.value == "aspd"), None)
    assert buff is not None and abs(buff.value - _S1_ASPD) < 1e-6
    assert op.current_atk_interval < base_interval


def test_s1_buffs_cleared_on_end():
    w = _world()
    op = _deploy(w, slot="S1")
    base_atk = op.effective_atk
    op.skill.sp = float(op.skill.sp_cost)
    _fire_skill(w, op)

    for _ in range(int(TICK_RATE * (_S1_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S1_BUFF_TAG for b in op.buffs)
    assert op.effective_atk == base_atk


# ── S2: Vorpal Edge ───────────────────────────────────────────────────────────

def test_s2_config():
    op = make_franka(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Vorpal Edge"
    assert sk.sp_cost == 20
    assert sk.initial_sp == 5
    assert abs(sk.duration - _S2_DURATION) < 1e-6
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff_applied():
    w = _world()
    op = _deploy(w)
    op.skill.sp = float(op.skill.sp_cost)
    _fire_skill(w, op)

    buff = next((b for b in op.buffs if b.source_tag == _S2_BUFF_TAG), None)
    assert buff is not None and abs(buff.value - _S2_ATK_RATIO) < 1e-6
    assert op.effective_atk == int(op.atk * (1 + _S2_ATK_RATIO))


def test_s2_guaranteed_def_ignore():
    """During S2, every attack adds true damage equal to min(target_def, effective_atk)."""
    w = _world()
    w.rng.seed(99)  # avoid talent bonus proc (first random will be checked for DEF ignore hits)
    op = _deploy(w)
    e = _enemy(w, defence=300)
    op.atk_cd = 0.0
    op.skill.sp = float(op.skill.sp_cost)
    _fire_skill(w, op)

    hp_before = e.hp
    for _ in range(3):  # one attack fires; S2 already active
        w.tick()

    normal_hit = max(int(op.effective_atk * 0.05), op.effective_atk - 300)
    def_bonus = min(300, op.effective_atk)
    # Total per attack = normal + DEF bonus (+ maybe talent proc, but we ignore that here)
    hp_lost = hp_before - e.hp
    assert hp_lost >= normal_hit + def_bonus, (
        f"Expected at least {normal_hit + def_bonus} (normal+DEF ignore), got {hp_lost}"
    )


def test_s2_talent_proc_at_50_percent():
    """During S2, talent proc chance = 50%; seed=1 first random()≈0.134 < 0.50 → procs."""
    w = _world()
    w.rng.seed(1)
    op = _deploy(w)
    e = _enemy(w, defence=0)  # zero DEF so guaranteed DEF-ignore gives 0 extra
    op.atk_cd = 0.0
    op.skill.sp = float(op.skill.sp_cost)
    _fire_skill(w, op)

    hp_before = e.hp
    for _ in range(3):
        w.tick()

    # S2 active: guaranteed DEF ignore (0 bonus since def=0) + 50% talent extra hit
    normal_hit = op.effective_atk  # def=0 so full atk
    # With talent proc: +1 extra physical hit = +normal_hit
    hp_lost = hp_before - e.hp
    assert hp_lost >= normal_hit * 2, f"Expected talent proc for 2× hits, got hp_lost={hp_lost}"


def test_s2_buffs_cleared_on_end():
    w = _world()
    op = _deploy(w)
    base_atk = op.effective_atk
    op.skill.sp = float(op.skill.sp_cost)
    _fire_skill(w, op)

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S2_BUFF_TAG for b in op.buffs)
    assert op.effective_atk == base_atk
    assert not getattr(op, "_franka_s2_active", False)
