"""Totter S1 "Sunpiercer", S2 "Prism Break", Talent "Illuminating Eyes".

Tests cover:
  - Talent: ATK+17% buff applied when CAMOUFLAGE enemy is in range
  - Talent: no buff when no CAMOUFLAGE enemies in range
  - S1 config (name, slot, sp_cost=3, initial_sp=0, duration=0, AUTO, AUTO_ATTACK)
  - S1: deals 220% ATK physical damage to __target__
  - S1: no crash when no target
  - S2 config (name, slot, sp_cost=40, initial_sp=25, duration=30, MANUAL, AUTO_TIME)
  - S2: ATK+125% buff applied on fire
  - S2: ASPD+50 buff applied on fire
  - S2: each attack fires 2 extra physical hits (S2 active flag)
  - S2: buffs cleared on end; _totter_s2_active cleared
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, StatusEffect
from core.types import TileType, TICK_RATE, Faction, SkillTrigger, SPGainMode, StatusKind
from core.systems import register_default_systems
from core.systems.skill_system import _fire_skill
from data.characters.totter import (
    make_totter,
    _TALENT_TAG, _TALENT_ATK_RATIO, _TALENT_BUFF_TAG,
    _S1_TAG, _S1_ATK_RATIO,
    _S2_TAG, _S2_ATK_RATIO, _S2_ASPD, _S2_BUFF_TAG, _S2_DURATION,
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


def _enemy(world: World, x: float = 1.0, y: float = 1.0, defence: int = 0) -> UnitState:
    e = UnitState(name="Dummy", faction=Faction.ENEMY, max_hp=999999, atk=0,
                  defence=defence, res=0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    e.blocked_by_unit_ids = []
    world.add_unit(e)
    return e


def _deploy(w: World, slot: str = "S2") -> UnitState:
    op = make_totter(slot=slot)
    op.deployed = True; op.position = (0.0, 1.0); op.atk_cd = 999.0
    w.add_unit(op)
    return op


# ── Talent: Illuminating Eyes ─────────────────────────────────────────────────

def test_talent_atk_buff_with_camouflage_enemy():
    """When a CAMOUFLAGE enemy is in attack range, ATK+17% buff is applied each tick."""
    w = _world()
    op = _deploy(w)
    e = _enemy(w, x=1.0, y=1.0)  # tile (1,0) relative to op — in BESIEGER_RANGE
    # Apply CAMOUFLAGE status to enemy
    e.statuses.append(StatusEffect(
        kind=StatusKind.CAMOUFLAGE, source_tag="test_camo",
    ))

    for _ in range(3):
        w.tick()

    buff = next((b for b in op.buffs if b.source_tag == _TALENT_BUFF_TAG), None)
    assert buff is not None, "ATK buff should be applied when CAMOUFLAGE enemy in range"
    assert abs(buff.value - _TALENT_ATK_RATIO) < 1e-6
    assert op.effective_atk == int(op.atk * (1 + _TALENT_ATK_RATIO))


def test_talent_no_buff_without_camouflage():
    """Without CAMOUFLAGE enemies in range, no ATK buff is applied."""
    w = _world()
    op = _deploy(w)
    e = _enemy(w, x=1.0, y=1.0)  # normal (non-CAMOUFLAGE) enemy

    for _ in range(3):
        w.tick()

    buff = next((b for b in op.buffs if b.source_tag == _TALENT_BUFF_TAG), None)
    assert buff is None, "No ATK buff should be applied without CAMOUFLAGE enemies"


# ── S1: Sunpiercer ────────────────────────────────────────────────────────────

def test_s1_config():
    op = make_totter(slot="S1")
    sk = op.skill
    assert sk is not None and sk.slot == "S1"
    assert sk.name == "Sunpiercer"
    assert sk.sp_cost == 3
    assert sk.initial_sp == 0
    assert sk.duration == 0.0
    assert sk.trigger == SkillTrigger.AUTO
    assert sk.sp_gain_mode == SPGainMode.AUTO_ATTACK
    assert sk.requires_target is True
    assert sk.behavior_tag == _S1_TAG


def test_s1_deals_damage_to_target():
    """S1 deals 220% ATK physical damage to __target__."""
    w = _world()
    op = _deploy(w, slot="S1")
    e = _enemy(w)
    hp_before = e.hp

    op.__target__ = e
    op.skill.sp = float(op.skill.sp_cost)
    _fire_skill(w, op)

    expected = max(int(op.atk * _S1_ATK_RATIO * 0.05),
                   int(op.atk * _S1_ATK_RATIO) - e.effective_def)
    assert hp_before - e.hp == expected


def test_s1_no_crash_without_target():
    """S1 on_start with no target should not raise."""
    w = _world()
    op = _deploy(w, slot="S1")
    op.skill.sp = float(op.skill.sp_cost)
    _fire_skill(w, op)  # no __target__ set, should not raise


# ── S2: Prism Break ───────────────────────────────────────────────────────────

def test_s2_config():
    op = make_totter(slot="S2")
    sk = op.skill
    assert sk is not None and sk.slot == "S2"
    assert sk.name == "Prism Break"
    assert sk.sp_cost == 40
    assert sk.initial_sp == 25
    assert abs(sk.duration - _S2_DURATION) < 1e-6
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.behavior_tag == _S2_TAG


def test_s2_atk_buff_applied():
    w = _world()
    op = _deploy(w)
    op.skill.sp = float(op.skill.sp_cost)
    _fire_skill(w, op)

    buff = next((b for b in op.buffs if b.source_tag == _S2_BUFF_TAG
                 and b.axis.value == "atk"), None)
    assert buff is not None and abs(buff.value - _S2_ATK_RATIO) < 1e-6
    assert op.effective_atk == int(op.atk * (1 + _S2_ATK_RATIO))


def test_s2_aspd_buff_applied():
    w = _world()
    op = _deploy(w)
    base_interval = op.current_atk_interval
    op.skill.sp = float(op.skill.sp_cost)
    _fire_skill(w, op)

    buff = next((b for b in op.buffs if b.source_tag == _S2_BUFF_TAG
                 and b.axis.value == "aspd"), None)
    assert buff is not None and abs(buff.value - _S2_ASPD) < 1e-6
    assert op.current_atk_interval < base_interval


def test_s2_extra_hits_on_attack():
    """During S2, each attack fires 2 extra physical hits on random enemies."""
    w = _world()
    w.rng.seed(42)
    op = _deploy(w)
    e = _enemy(w, x=1.0, y=1.0)  # in BESIEGER_RANGE tile (1,0)
    op.atk_cd = 0.0
    op.skill.sp = float(op.skill.sp_cost)
    _fire_skill(w, op)  # activate S2

    hp_before = e.hp
    for _ in range(3):  # one attack fires on tick 1
        w.tick()

    # With S2: 1 main hit + 2 extra hits = 3 total at boosted ATK
    per_hit = max(int(op.effective_atk * 0.05), op.effective_atk - e.effective_def)
    hp_lost = hp_before - e.hp
    assert hp_lost >= 3 * per_hit, (
        f"Expected at least 3 hits ({3 * per_hit}), got hp_lost={hp_lost}"
    )


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
    assert not getattr(op, "_totter_s2_active", False)
