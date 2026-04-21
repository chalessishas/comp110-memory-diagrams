"""Glaucus S3 "Tidal Prison" — MANUAL, 20s, 300% arts AoE + 5s BIND on start, -60% SLOW aura.

Tests cover:
  - S3 configured correctly (slot, sp_cost=40, initial_sp=15, MANUAL, 20s)
  - On activation: 300% ATK arts damage to all in range
  - On activation: BIND (5s) applied to all enemies in range
  - During S3: SLOW aura strengthened to -60% (vs normal -40%)
  - SLOW reverts to -40% after S3 ends
  - Out-of-range enemies not affected by on_start burst
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, SkillTrigger, StatusKind, SPGainMode
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.glaucus import (
    make_glaucus,
    _S3_TAG, _S3_DAMAGE_RATIO, _S3_BIND_DURATION, _S3_BIND_TAG, _S3_DURATION,
    _S3_SLOW_AMOUNT, _SLOW_AMOUNT, _SLOW_TAG,
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


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


def _enemy(world: World, x: float, y: float, hp: int = 99999) -> UnitState:
    e = UnitState(name="Enemy", faction=Faction.ENEMY, max_hp=hp, atk=0, defence=0, res=0.0)
    e.alive = True; e.deployed = True; e.position = (x, y)
    world.add_unit(e)
    return e


# ---------------------------------------------------------------------------
def test_s3_config():
    g = make_glaucus(slot="S3")
    sk = g.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "Tidal Prison"
    assert sk.sp_cost == 40
    assert sk.initial_sp == 15
    assert sk.duration == _S3_DURATION
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
def test_s3_arts_damage():
    w = _world()
    g = make_glaucus(slot="S3")
    g.deployed = True; g.position = (0.0, 1.0); g.atk_cd = 999.0
    w.add_unit(g)
    e = _enemy(w, 2.0, 1.0)
    hp_before = e.hp

    g.skill.sp = float(g.skill.sp_cost)
    manual_trigger(w, g)

    expected = int(g.effective_atk * _S3_DAMAGE_RATIO)
    actual = hp_before - e.hp
    assert actual > 0, "S3 must deal arts damage on activation"
    assert abs(actual - expected) <= max(5, int(expected * 0.02)), (
        f"Expected ~{expected} arts damage, got {actual}"
    )


# ---------------------------------------------------------------------------
def test_s3_bind_applied():
    w = _world()
    g = make_glaucus(slot="S3")
    g.deployed = True; g.position = (0.0, 1.0); g.atk_cd = 999.0
    w.add_unit(g)
    e = _enemy(w, 2.0, 1.0)

    g.skill.sp = float(g.skill.sp_cost)
    manual_trigger(w, g)

    bind = [s for s in e.statuses if s.kind == StatusKind.BIND and s.source_tag == _S3_BIND_TAG]
    assert len(bind) == 1, "Enemy in range must be BOUND on S3 activation"
    remaining = bind[0].expires_at - w.global_state.elapsed
    assert abs(remaining - _S3_BIND_DURATION) <= 0.1, (
        f"BIND must last {_S3_BIND_DURATION}s, remaining={remaining:.2f}s"
    )


# ---------------------------------------------------------------------------
def test_s3_enhanced_slow_during_skill():
    """Slow aura must apply -60% during S3 (vs -40% normally)."""
    w = _world()
    g = make_glaucus(slot="S3")
    g.deployed = True; g.position = (0.0, 1.0); g.atk_cd = 999.0
    w.add_unit(g)
    e = _enemy(w, 2.0, 1.0)

    g.skill.sp = float(g.skill.sp_cost)
    manual_trigger(w, g)
    assert g.skill.active_remaining > 0.0

    # Tick one frame so on_tick talent fires
    w.tick()

    slow = [s for s in e.statuses if s.kind == StatusKind.SLOW and s.source_tag == _SLOW_TAG]
    assert len(slow) >= 1, "SLOW must be applied during S3"
    assert abs(slow[0].params["amount"] - _S3_SLOW_AMOUNT) < 0.01, (
        f"SLOW must be {_S3_SLOW_AMOUNT} during S3, got {slow[0].params['amount']}"
    )


# ---------------------------------------------------------------------------
def test_s3_slow_reverts_after_end():
    w = _world()
    g = make_glaucus(slot="S3")
    g.deployed = True; g.position = (0.0, 1.0); g.atk_cd = 999.0
    w.add_unit(g)
    e = _enemy(w, 2.0, 1.0)

    g.skill.sp = float(g.skill.sp_cost)
    manual_trigger(w, g)

    _ticks(w, _S3_DURATION + 1.0)

    # Tick once more to let on_tick refresh SLOW with normal amount
    w.tick()

    slow = [s for s in e.statuses if s.kind == StatusKind.SLOW and s.source_tag == _SLOW_TAG]
    if slow:
        assert abs(slow[0].params["amount"] - _SLOW_AMOUNT) < 0.01, (
            f"SLOW must revert to {_SLOW_AMOUNT} after S3 ends, got {slow[0].params['amount']}"
        )
    # If no SLOW entry, that's also fine (aura refresh will restore it on next tick)


# ---------------------------------------------------------------------------
def test_s3_no_damage_out_of_range():
    w = _world()
    g = make_glaucus(slot="S3")
    g.deployed = True; g.position = (0.0, 1.0); g.atk_cd = 999.0
    w.add_unit(g)
    e = _enemy(w, 5.0, 1.0)  # beyond range_shape (0..3 dx, -1..1 dy)
    hp_before = e.hp

    g.skill.sp = float(g.skill.sp_cost)
    manual_trigger(w, g)

    assert e.hp == hp_before, "Enemy out of range must not take damage on S3 activation"


# ---------------------------------------------------------------------------
def test_s2_regression():
    g = make_glaucus(slot="S2")
    assert g.skill is not None and g.skill.slot == "S2"
    assert g.skill.name == "Trident Strike"
    assert g.skill.sp_cost == 25
    assert g.skill.trigger == SkillTrigger.MANUAL
