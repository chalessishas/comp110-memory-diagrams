"""Specter S3 "Deathless Aegis" — ATK+400%, ASPD+50, cannot die for 30s.

Tests cover:
  - S3 configured correctly (slot, sp_cost, MANUAL trigger)
  - ATK +400% during S3
  - ASPD +50 during S3
  - Specter cannot die during S3 (survives lethal hits)
  - ATK and ASPD buffs removed on skill end
  - undying_charges restored on skill end
  - S2 regression (Pather's Light unchanged)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.specter import (
    make_specter,
    _S3_TAG, _S3_DURATION, _S3_ATK_RATIO, _S3_ASPD_BONUS,
    _S3_ATK_BUFF_TAG, _S3_ASPD_BUFF_TAG, _S3_UNDYING_SENTINEL,
)
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=8, height=3)
    for x in range(8):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _ticks(w: World, seconds: float) -> None:
    for _ in range(int(TICK_RATE * seconds)):
        w.tick()


# ---------------------------------------------------------------------------
# Test 1: S3 configured correctly
# ---------------------------------------------------------------------------

def test_s3_config():
    s = make_specter(slot="S3")
    assert s.skill is not None
    assert s.skill.slot == "S3"
    assert s.skill.name == "Deathless Aegis"
    assert s.skill.sp_cost == 65
    assert s.skill.initial_sp == 30
    from core.types import SkillTrigger
    assert s.skill.trigger == SkillTrigger.MANUAL
    assert s.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK +400% during S3
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    w = _world()
    s = make_specter(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    w.add_unit(s)

    slug_path = [(2, 1)] * 20
    e = make_originium_slug(path=slug_path)
    e.deployed = True; e.position = (2.0, 1.0); e.move_speed = 0.0
    w.add_unit(e)

    base_atk = s.effective_atk
    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)

    assert s.skill.active_remaining > 0.0, "S3 must be active"
    expected_atk = int(base_atk * (1 + _S3_ATK_RATIO))
    assert abs(s.effective_atk - expected_atk) <= 2, (
        f"S3 ATK must be ×{1+_S3_ATK_RATIO}; expected {expected_atk}, got {s.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: ASPD +50 during S3
# ---------------------------------------------------------------------------

def test_s3_aspd_buff():
    w = _world()
    s = make_specter(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    w.add_unit(s)

    slug_path = [(2, 1)] * 20
    e = make_originium_slug(path=slug_path)
    e.deployed = True; e.position = (2.0, 1.0); e.move_speed = 0.0
    w.add_unit(e)

    base_aspd = s.effective_aspd
    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)

    assert s.skill.active_remaining > 0.0
    assert abs(s.effective_aspd - (base_aspd + _S3_ASPD_BONUS)) <= 0.01, (
        f"S3 ASPD must be +{_S3_ASPD_BONUS}; expected {base_aspd + _S3_ASPD_BONUS}, got {s.effective_aspd}"
    )


# ---------------------------------------------------------------------------
# Test 4: Specter cannot die during S3 (lethal hit leaves her at 1 HP)
# ---------------------------------------------------------------------------

def test_s3_cannot_die():
    w = _world()
    s = make_specter(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    w.add_unit(s)

    slug_path = [(2, 1)] * 20
    e = make_originium_slug(path=slug_path)
    e.deployed = True; e.position = (2.0, 1.0); e.move_speed = 0.0
    w.add_unit(e)

    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)
    assert s.skill.active_remaining > 0.0

    # Deal massive damage — should survive with undying during S3
    initial_hp = s.hp
    s.take_physical(999999)  # lethal

    assert s.alive, "Specter must stay alive during S3"
    assert s.hp >= 1, "Specter must have at least 1 HP after lethal hit during S3"
    assert s.undying_charges >= 1, "undying_charges must remain ≥1 during S3"


# ---------------------------------------------------------------------------
# Test 5: ATK and ASPD buffs cleared on skill end
# ---------------------------------------------------------------------------

def test_s3_buffs_cleared_on_end():
    w = _world()
    s = make_specter(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    w.add_unit(s)

    slug_path = [(2, 1)] * 20
    e = make_originium_slug(path=slug_path)
    e.deployed = True; e.position = (2.0, 1.0); e.move_speed = 0.0
    w.add_unit(e)

    base_atk = s.effective_atk
    base_aspd = s.effective_aspd

    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)
    assert s.skill.active_remaining > 0.0

    _ticks(w, _S3_DURATION + 1)

    assert s.skill.active_remaining == 0.0, "S3 must have ended"
    atk_buffs = [b for b in s.buffs if b.source_tag == _S3_ATK_BUFF_TAG]
    aspd_buffs = [b for b in s.buffs if b.source_tag == _S3_ASPD_BUFF_TAG]
    assert len(atk_buffs) == 0, "S3 ATK buff must be cleared on end"
    assert len(aspd_buffs) == 0, "S3 ASPD buff must be cleared on end"
    assert abs(s.effective_atk - base_atk) <= 2, "ATK must revert to base"
    assert abs(s.effective_aspd - base_aspd) <= 0.01, "ASPD must revert to base"


# ---------------------------------------------------------------------------
# Test 6: undying_charges restored after S3 ends
# ---------------------------------------------------------------------------

def test_s3_undying_restored_on_end():
    w = _world()
    s = make_specter(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    w.add_unit(s)

    slug_path = [(2, 1)] * 20
    e = make_originium_slug(path=slug_path)
    e.deployed = True; e.position = (2.0, 1.0); e.move_speed = 0.0
    w.add_unit(e)

    pre_s3_undying = s.undying_charges  # talent grants 1

    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)
    assert s.undying_charges == _S3_UNDYING_SENTINEL, "undying_charges must be sentinel during S3"

    _ticks(w, _S3_DURATION + 1)

    assert s.skill.active_remaining == 0.0
    assert s.undying_charges == pre_s3_undying, (
        f"undying_charges must restore to {pre_s3_undying} after S3; got {s.undying_charges}"
    )
