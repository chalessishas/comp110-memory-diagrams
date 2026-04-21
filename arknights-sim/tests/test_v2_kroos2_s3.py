"""Kroos the Keen Glint S3 "Blizzard Barrage" — ATK+200%, MANUAL, 35s, FREEZE(3s) on all hits.

Tests cover:
  - S3 configured correctly (slot, sp_cost=40, initial_sp=15, MANUAL, 35s)
  - ATK+200% buff applied on activation
  - Hits apply 3s FREEZE directly (longer than S2's 1.5s)
  - ATK buff cleared on S3 end
  - Talent still fires during S3 (FREEZE applied via talent on_attack_hit)
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
from data.characters.kroos2 import (
    make_kroos2,
    _S3_TAG, _S3_ATK_RATIO, _S3_BUFF_TAG, _S3_DURATION, _S3_FREEZE_DURATION,
    _TALENT_TAG, _FREEZE_TAG,
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
    k = make_kroos2(slot="S3")
    sk = k.skill
    assert sk is not None
    assert sk.slot == "S3"
    assert sk.name == "Blizzard Barrage"
    assert sk.sp_cost == 40
    assert sk.initial_sp == 15
    assert sk.duration == _S3_DURATION
    assert sk.trigger == SkillTrigger.MANUAL
    assert sk.sp_gain_mode == SPGainMode.AUTO_TIME
    assert sk.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
def test_s3_atk_buff():
    w = _world()
    k = make_kroos2(slot="S3")
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 999.0
    w.add_unit(k)
    _enemy(w, 2.0, 1.0)
    base_atk = k.effective_atk

    k.skill.sp = float(k.skill.sp_cost)
    manual_trigger(w, k)

    buff = next((b for b in k.buffs if b.source_tag == _S3_BUFF_TAG), None)
    assert buff is not None, "ATK buff must be applied on S3 activation"
    assert abs(buff.value - _S3_ATK_RATIO) <= 0.001

    expected = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(k.effective_atk - expected) <= 2


# ---------------------------------------------------------------------------
def test_s3_freeze_on_hit():
    """During S3, on_attack_hit must FREEZE the target for _S3_FREEZE_DURATION."""
    w = _world()
    k = make_kroos2(slot="S3")
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 0.0
    w.add_unit(k)
    e = _enemy(w, 2.0, 1.0)

    k.skill.sp = float(k.skill.sp_cost)
    manual_trigger(w, k)
    assert k.skill.active_remaining > 0.0, "S3 must be active"

    # Advance until Kroos2 attacks
    _ticks(w, 3.0)

    freeze = [s for s in e.statuses if s.kind == StatusKind.FREEZE and s.source_tag == _FREEZE_TAG]
    assert len(freeze) == 1, "Enemy must be FROZEN after being hit during S3"
    assert (freeze[0].expires_at - w.global_state.elapsed) > 2.0, (
        f"S3 FREEZE should last ~{_S3_FREEZE_DURATION}s, remaining: {freeze[0].expires_at - w.global_state.elapsed:.2f}s"
    )


# ---------------------------------------------------------------------------
def test_s3_buff_cleared_on_end():
    w = _world()
    k = make_kroos2(slot="S3")
    k.deployed = True; k.position = (0.0, 1.0); k.atk_cd = 999.0
    w.add_unit(k)
    _enemy(w, 2.0, 1.0)

    k.skill.sp = float(k.skill.sp_cost)
    manual_trigger(w, k)
    assert k.skill.active_remaining > 0.0

    _ticks(w, _S3_DURATION + 1.0)

    assert not any(b.source_tag == _S3_BUFF_TAG for b in k.buffs), (
        "ATK buff must be cleared after S3 ends"
    )
    assert not getattr(k, "_kroos2_s3_active", False), "S3 active flag must be False after end"


# ---------------------------------------------------------------------------
def test_s3_stronger_than_s2():
    """S3 ATK ratio must exceed S2 and S3 FREEZE duration must exceed S2's."""
    from data.characters.kroos2 import _S2_ATK_RATIO, _FREEZE_DURATION as _s2_freeze_dur
    assert _S3_ATK_RATIO > _S2_ATK_RATIO, "S3 ATK ratio must exceed S2"
    assert _S3_FREEZE_DURATION > _s2_freeze_dur, "S3 FREEZE duration must exceed S2"


# ---------------------------------------------------------------------------
def test_s2_regression():
    k = make_kroos2(slot="S2")
    assert k.skill is not None and k.skill.slot == "S2"
    assert k.skill.name == "Permafrost Hail"
    assert k.skill.sp_cost == 30
    assert k.skill.trigger == SkillTrigger.AUTO
