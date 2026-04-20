"""Zima S3 "March Order" — instant 15 DP + ATK+60% to all deployed Vanguards for 25s.

Tests cover:
  - S3 configured correctly (slot, sp_cost=45, MANUAL, duration=25s)
  - Instantly grants 15 DP on activation
  - ATK+60% buff applied to all deployed Vanguard allies (including Zima)
  - Non-Vanguard ally does NOT receive buff
  - ATK buff cleared on S3 end
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, BuffAxis, SPGainMode, Profession
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.zima import (
    make_zima,
    _S3_TAG, _S3_ATK_RATIO, _S3_ATK_BUFF_TAG, _S3_DP_GAIN,
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


def _vanguard_ally(world: World, x: float, y: float) -> UnitState:
    a = UnitState(name="VanAlly", faction=Faction.ALLY, max_hp=3000, atk=600,
                  defence=150, res=0.0, atk_interval=1.5)
    a.alive = True; a.deployed = True; a.position = (x, y)
    a.profession = Profession.VANGUARD
    world.add_unit(a)
    return a


def _guard_ally(world: World, x: float, y: float) -> UnitState:
    a = UnitState(name="GuardAlly", faction=Faction.ALLY, max_hp=3000, atk=800,
                  defence=200, res=0.0, atk_interval=1.2)
    a.alive = True; a.deployed = True; a.position = (x, y)
    a.profession = Profession.GUARD
    world.add_unit(a)
    return a


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    z = make_zima(slot="S3")
    assert z.skill is not None
    assert z.skill.slot == "S3"
    assert z.skill.name == "March Order"
    assert z.skill.sp_cost == 45
    assert z.skill.initial_sp == 15
    assert z.skill.duration == 25.0
    from core.types import SkillTrigger
    assert z.skill.trigger == SkillTrigger.MANUAL
    assert z.skill.sp_gain_mode == SPGainMode.AUTO_TIME
    assert z.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: Instantly grants 15 DP
# ---------------------------------------------------------------------------

def test_s3_dp_grant():
    w = _world()
    z = make_zima(slot="S3")
    z.deployed = True; z.position = (0.0, 1.0); z.atk_cd = 999.0
    w.add_unit(z)

    dp_before = w.global_state.dp
    z.skill.sp = float(z.skill.sp_cost)
    manual_trigger(w, z)

    assert abs((w.global_state.dp - dp_before) - _S3_DP_GAIN) <= 0.1, (
        f"S3 must grant {_S3_DP_GAIN} DP; got {w.global_state.dp - dp_before}"
    )


# ---------------------------------------------------------------------------
# Test 3: ATK+60% buff applied to all deployed Vanguards (including Zima)
# ---------------------------------------------------------------------------

def test_s3_atk_buff_vanguards():
    w = _world()
    z = make_zima(slot="S3")
    z.deployed = True; z.position = (0.0, 1.0); z.atk_cd = 999.0
    w.add_unit(z)
    van_ally = _vanguard_ally(w, 2.0, 1.0)
    base_atk_zima = z.effective_atk
    base_atk_ally = van_ally.effective_atk

    z.skill.sp = float(z.skill.sp_cost)
    manual_trigger(w, z)

    # Zima herself (Vanguard) receives buff
    zima_buff = next((b for b in z.buffs if b.source_tag == _S3_ATK_BUFF_TAG), None)
    assert zima_buff is not None, "Zima must receive ATK buff (she is a Vanguard)"
    assert abs(zima_buff.value - _S3_ATK_RATIO) <= 0.001

    # Vanguard ally also receives buff
    ally_buff = next((b for b in van_ally.buffs if b.source_tag == _S3_ATK_BUFF_TAG), None)
    assert ally_buff is not None, "Vanguard ally must receive ATK buff"
    assert abs(ally_buff.value - _S3_ATK_RATIO) <= 0.001

    expected_ally = int(base_atk_ally * (1 + _S3_ATK_RATIO))
    assert abs(van_ally.effective_atk - expected_ally) <= 2


# ---------------------------------------------------------------------------
# Test 4: Non-Vanguard ally does NOT receive buff
# ---------------------------------------------------------------------------

def test_s3_no_buff_for_non_vanguard():
    w = _world()
    z = make_zima(slot="S3")
    z.deployed = True; z.position = (0.0, 1.0); z.atk_cd = 999.0
    w.add_unit(z)
    guard = _guard_ally(w, 2.0, 1.0)

    z.skill.sp = float(z.skill.sp_cost)
    manual_trigger(w, z)

    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in guard.buffs), (
        "Non-Vanguard ally must NOT receive March Order ATK buff"
    )


# ---------------------------------------------------------------------------
# Test 5: ATK buff cleared on S3 end
# ---------------------------------------------------------------------------

def test_s3_cleanup_on_end():
    w = _world()
    z = make_zima(slot="S3")
    z.deployed = True; z.position = (0.0, 1.0); z.atk_cd = 999.0
    w.add_unit(z)
    van_ally = _vanguard_ally(w, 2.0, 1.0)
    base_atk_ally = van_ally.effective_atk

    z.skill.sp = float(z.skill.sp_cost)
    manual_trigger(w, z)
    _ticks(w, 26.0)

    assert z.skill.active_remaining == 0.0, "S3 must have ended"
    assert not any(b.source_tag == _S3_ATK_BUFF_TAG for b in van_ally.buffs), (
        "Vanguard ATK buff must clear on S3 end"
    )
    assert abs(van_ally.effective_atk - base_atk_ally) <= 2


# ---------------------------------------------------------------------------
# Test 6: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    z = make_zima(slot="S2")
    assert z.skill is not None and z.skill.slot == "S2"
    assert z.skill.name == "Battle Cry"
    assert z.skill.sp_cost == 40
