"""Siege S1 "Charge γ" and S3 "Skull Breaker".

Tests cover:
  - S1 config (name, slot, sp_cost, initial_sp, duration=0, AUTO, requires_target=False)
  - S1 fires: DP increases by 12
  - S1 repeats after SP recharges (fire_count increments)
  - S3 config (name, slot, sp_cost, initial_sp, duration=25, MANUAL)
  - S3 ATK buff applied (+280%)
  - S3 attack interval increases by 1s
  - S3 stun fires when RNG < 0.40
  - S3 no stun when S3 inactive
  - S3 buffs cleared on end
"""
from __future__ import annotations
import random
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, StatusKind, SkillTrigger, SPGainMode
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from core.systems.talent_registry import fire_on_attack_hit
from data.characters.siege import (
    make_siege,
    _S1_TAG, _S1_DP_GAIN,
    _S3_TAG, _S3_ATK_RATIO, _S3_ATK_BUFF_TAG, _S3_INTERVAL_TAG,
    _S3_STUN_CHANCE, _S3_STUN_DURATION, _S3_STUN_TAG,
    _S3_DURATION,
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
    e = UnitState(name="Slug", faction=Faction.ENEMY, max_hp=9999, atk=0, defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


# ── S1: Charge γ ─────────────────────────────────────────────────────────────

def test_s1_config():
    op = make_siege(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Charge γ"
    assert sk.sp_cost == 35
    assert sk.initial_sp == 20
    assert sk.duration == 0.0
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.requires_target is False
    assert sk.behavior_tag == _S1_TAG


def test_s1_gains_dp():
    w = _world()
    op = make_siege(slot="S1")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    w.global_state.dp = 5

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    assert w.global_state.dp == 5 + _S1_DP_GAIN


def test_s1_fires_without_target():
    """Charge γ fires even when no enemy is present (requires_target=False)."""
    w = _world()
    op = make_siege(slot="S1")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    w.global_state.dp = 0

    op.skill.sp = float(op.skill.sp_cost)
    w.tick()

    assert w.global_state.dp == _S1_DP_GAIN
    assert op.skill.fire_count >= 1


def test_s1_repeats_on_recharge():
    """Charge γ auto-fires again after SP recharges."""
    w = _world()
    op = make_siege(slot="S1")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    w.global_state.dp = 0

    # First fire
    op.skill.sp = float(op.skill.sp_cost)
    w.tick()
    assert w.global_state.dp == _S1_DP_GAIN

    # Recharge SP and fire again
    op.skill.sp = float(op.skill.sp_cost)
    w.tick()
    assert w.global_state.dp == 2 * _S1_DP_GAIN
    assert op.skill.fire_count >= 2


# ── S3: Skull Breaker ────────────────────────────────────────────────────────

def test_s3_config():
    op = make_siege(slot="S3")
    sk = op.skill
    assert sk is not None and sk.slot == "S3"
    assert sk.name == "Skull Breaker"
    assert sk.sp_cost == 30
    assert sk.initial_sp == 25
    assert abs(sk.duration - _S3_DURATION) < 1e-6
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.behavior_tag == _S3_TAG


def test_s3_atk_buff_applied():
    w = _world()
    op = make_siege(slot="S3")
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    buff = next((b for b in op.buffs if b.source_tag == _S3_ATK_BUFF_TAG), None)
    assert buff is not None and abs(buff.value - _S3_ATK_RATIO) < 1e-6
    expected_atk = int(op.atk * (1 + _S3_ATK_RATIO))
    assert op.effective_atk == expected_atk


def test_s3_interval_increases():
    w = _world()
    op = make_siege(slot="S3")
    base_interval = op.current_atk_interval
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    assert abs(op.current_atk_interval - (base_interval + 1.0)) < 1e-6


def test_s3_stun_fires_when_rng_low():
    """40% stun fires when RNG < 0.40 (seed=1 gives ~0.134)."""
    w = _world()
    w.rng = random.Random(1)
    op = make_siege(slot="S3")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    enemy = _enemy(w, 1.0, 1.0)
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    fire_on_attack_hit(w, op, enemy, 300)
    assert any(s.kind == StatusKind.STUN for s in enemy.statuses)


def test_s3_stun_misses_when_rng_high():
    """No stun when RNG >= 0.40 (seed=0 gives ~0.844)."""
    w = _world()
    w.rng = random.Random(0)
    op = make_siege(slot="S3")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    enemy = _enemy(w, 1.0, 1.0)
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    fire_on_attack_hit(w, op, enemy, 300)
    assert not any(s.kind == StatusKind.STUN for s in enemy.statuses)


def test_s3_no_stun_when_inactive():
    """Stun hook does not fire when S3 is not active."""
    w = _world()
    w.rng = random.Random(1)
    op = make_siege(slot="S3")
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    enemy = _enemy(w, 1.0, 1.0)
    w.add_unit(op)

    # S3 not started — _siege_s3_active should be False
    fire_on_attack_hit(w, op, enemy, 300)
    assert not any(s.kind == StatusKind.STUN for s in enemy.statuses)


def test_s3_buffs_cleared_on_end():
    w = _world()
    op = make_siege(slot="S3")
    base_interval = op.current_atk_interval
    base_atk = op.effective_atk
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    op.skill.sp = float(op.skill.sp_cost)
    manual_trigger(w, op)

    for _ in range(int(TICK_RATE * (_S3_DURATION + 1.0))):
        w.tick()

    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in op.buffs)
    assert not any(b.source_tag == _S3_INTERVAL_TAG for b in op.buffs)
    assert op.effective_atk == base_atk
    assert abs(op.current_atk_interval - base_interval) < 1e-6
