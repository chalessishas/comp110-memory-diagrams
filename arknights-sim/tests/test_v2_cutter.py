"""Cutter S1 "Redshift" and S2 "Crimson Crescent", Talent "Photoetched Marks".

Tests cover:
  - Trait: each normal attack deals damage twice (second hit via on_attack_hit)
  - Talent: 20% chance per hit to recover 1 SP (seed=1 procs, seed=0 does not)
  - S1 config (name, slot, sp_cost=15, initial_sp=5, duration=0, MANUAL, AUTO_ATTACK)
  - S1: fires 4 attacks at 260% ATK against enemies
  - S1: total damage = 4 × int(effective_atk * 2.60) minus DEF × 4 (0 DEF enemies)
  - S2 config (name, slot, sp_cost=16, initial_sp=1, duration=0, MANUAL, AUTO_ATTACK)
  - S2: hits up to 5 enemies at 360% ATK
  - S2: does not crash with no enemies
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
from data.characters.cutter import (
    make_cutter,
    _TALENT_TAG, _TALENT_SP_CHANCE,
    _S1_TAG, _S1_ATK_RATIO, _S1_HIT_COUNT,
    _S2_TAG, _S2_ATK_RATIO, _S2_MAX_TARGETS,
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


def _enemy(world: World, x: float = 0.0, y: float = 1.0) -> UnitState:
    e = UnitState(name="Dummy", faction=Faction.ENEMY, max_hp=999999, atk=0, defence=0, res=0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


# ── Trait: double-hit ─────────────────────────────────────────────────────────

def test_trait_double_hit():
    """Each normal attack should deal damage twice: hp loss > single-hit damage."""
    w = _world()
    op = make_cutter()
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 0.0
    w.add_unit(op)
    e = _enemy(w)
    hp_before = e.hp

    # 3 ticks: atk_cd=0 so first attack fires on tick 1; stops well before second attack
    for _ in range(3):
        w.tick()

    single_hit_dmg = max(int(op.effective_atk * 0.05), op.effective_atk - e.effective_def)
    hp_lost = hp_before - e.hp
    assert hp_lost == single_hit_dmg * 2, (
        f"Expected exactly 2 hits ({single_hit_dmg * 2}), got hp_lost={hp_lost}"
    )


# ── Talent: SP recovery ───────────────────────────────────────────────────────

def test_talent_sp_procs_with_seed_1():
    """seed=1 → first random() ≈ 0.134 < 0.20 → SP recovery procs."""
    w = _world()
    w.rng.seed(1)
    op = make_cutter()
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 0.0
    w.add_unit(op)
    e = _enemy(w)

    sp_before = op.skill.sp
    # 3 ticks: first attack fires immediately (atk_cd=0), no second attack yet
    for _ in range(3):
        w.tick()

    # AUTO_ATTACK gives +1, talent proc gives +1 extra → total +2
    assert op.skill.sp == sp_before + 2.0 or op.skill.sp == float(op.skill.sp_cost)


def test_talent_sp_no_proc_with_seed_0():
    """seed=0 → first random() ≈ 0.844 >= 0.20 → talent does NOT proc."""
    w = _world()
    w.rng.seed(0)
    op = make_cutter()
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 0.0
    w.add_unit(op)
    e = _enemy(w)

    sp_before = op.skill.sp
    # 3 ticks: one attack fires, second attack has not had time to fire
    for _ in range(3):
        w.tick()

    # Only AUTO_ATTACK +1; talent did not proc
    expected_sp = min(sp_before + 1.0, float(op.skill.sp_cost))
    assert abs(op.skill.sp - expected_sp) < 1e-6


# ── S1: Redshift ──────────────────────────────────────────────────────────────

def test_s1_config():
    op = make_cutter(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Redshift"
    assert sk.sp_cost == 15
    assert sk.initial_sp == 5
    assert sk.duration == 0.0
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.sp_gain_mode == SPGainMode.AUTO_ATTACK
    assert sk.requires_target is False
    assert sk.behavior_tag == _S1_TAG


def test_s1_deals_damage_to_enemy():
    w = _world()
    op = make_cutter(slot="S1")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    e = _enemy(w)
    hp_before = e.hp

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert e.hp < hp_before, "S1 Redshift should deal damage to enemies"


def test_s1_total_damage():
    """S1 deals 4 hits at 260% ATK; with 0-DEF dummy, total damage = 4 × int(atk * 2.60)."""
    w = _world()
    op = make_cutter(slot="S1")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    e = _enemy(w)
    hp_before = e.hp

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    expected_per_hit = max(int(op.effective_atk * _S1_ATK_RATIO * 0.05),
                           int(op.effective_atk * _S1_ATK_RATIO) - e.defence)
    expected_total = expected_per_hit * _S1_HIT_COUNT
    assert hp_before - e.hp == expected_total


def test_s1_fires_without_enemies_gracefully():
    """S1 on_start with no enemies should not raise."""
    w = _world()
    op = make_cutter(slot="S1")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)  # should not raise


# ── S2: Crimson Crescent ──────────────────────────────────────────────────────

def test_s2_config():
    op = make_cutter(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Crimson Crescent"
    assert sk.sp_cost == 16
    assert sk.initial_sp == 1
    assert sk.duration == 0.0
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.sp_gain_mode == SPGainMode.AUTO_ATTACK
    assert sk.behavior_tag == _S2_TAG


def test_s2_hits_single_enemy():
    w = _world()
    op = make_cutter(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    e = _enemy(w)
    hp_before = e.hp

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    expected = max(int(op.effective_atk * _S2_ATK_RATIO * 0.05),
                   int(op.effective_atk * _S2_ATK_RATIO) - e.defence)
    assert hp_before - e.hp == expected


def test_s2_hits_multiple_enemies():
    w = _world()
    op = make_cutter(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    enemies = [_enemy(w, float(i), 0.0) for i in range(3)]
    hp_befores = [e.hp for e in enemies]

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    for e, hp_before in zip(enemies, hp_befores):
        assert e.hp < hp_before, f"Enemy {e.name} at {e.position} should take damage"


def test_s2_respects_max_targets():
    """S2 hits at most 5 enemies; 7 enemies → exactly 5 take damage."""
    w = _world()
    op = make_cutter(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    enemies = [_enemy(w, float(i), 0.0) for i in range(7)]
    hp_befores = [e.hp for e in enemies]

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    damaged = sum(1 for e, h in zip(enemies, hp_befores) if e.hp < h)
    assert damaged == _S2_MAX_TARGETS


def test_s2_fires_without_enemies_gracefully():
    w = _world()
    op = make_cutter(slot="S2")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)

    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)  # should not raise
