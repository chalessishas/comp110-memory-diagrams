"""Saileach S3 "Battle Hymn" — 30 DP/20s + ATK+40% to all deployed allies, 20s MANUAL.

Tests cover:
  - S3 configured correctly (slot, sp_cost=40, MANUAL, AUTO_TIME)
  - ATK+40% buff applied to all deployed allies on S3 start
  - DP drip generates ~30 DP over 20s
  - Block drops to 0 during S3
  - ATK buff cleared on S3 end, block restored
  - S2 regression
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, BuffAxis, SPGainMode
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.saileach import (
    make_saileach,
    _S3_TAG, _S3_ATK_RATIO, _S3_BUFF_TAG, _S3_DP_RATE,
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


def _ally(world: World, x: float, y: float) -> UnitState:
    a = UnitState(name="Ally", faction=Faction.ALLY, max_hp=5000, atk=500,
                  defence=200, res=0.0, atk_interval=1.5)
    a.alive = True; a.deployed = True; a.position = (x, y)
    world.add_unit(a)
    return a


# ---------------------------------------------------------------------------
# Test 1: S3 config
# ---------------------------------------------------------------------------

def test_s3_config():
    s = make_saileach(slot="S3")
    assert s.skill is not None
    assert s.skill.slot == "S3"
    assert s.skill.name == "Battle Hymn"
    assert s.skill.sp_cost == 40
    assert s.skill.initial_sp == 20
    from core.types import SkillTrigger
    assert s.skill.trigger == SkillTrigger.MANUAL
    assert s.skill.sp_gain_mode == SPGainMode.AUTO_TIME
    assert s.skill.behavior_tag == _S3_TAG


# ---------------------------------------------------------------------------
# Test 2: ATK+40% buff applied to all deployed allies on S3 start
# ---------------------------------------------------------------------------

def test_s3_atk_buff_applied_to_allies():
    w = _world()
    s = make_saileach(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    w.add_unit(s)

    ally = _ally(w, 2.0, 1.0)
    ally_base_atk = ally.effective_atk

    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)

    assert s.skill.active_remaining > 0.0
    buff = next((b for b in ally.buffs if b.source_tag == _S3_BUFF_TAG), None)
    assert buff is not None, "Ally must receive ATK buff from S3"
    assert buff.axis == BuffAxis.ATK
    assert abs(buff.value - _S3_ATK_RATIO) <= 0.001

    expected = int(ally_base_atk * (1 + _S3_ATK_RATIO))
    assert abs(ally.effective_atk - expected) <= 2, (
        f"Ally ATK must be ×{1 + _S3_ATK_RATIO}; expected {expected}, got {ally.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: DP drip generates ~30 DP over 20s
# ---------------------------------------------------------------------------

def test_s3_dp_generation():
    w = _world()
    s = make_saileach(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    w.add_unit(s)

    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)

    dp_start = w.global_state.dp
    _ticks(w, 20.0)
    dp_gained = w.global_state.dp - dp_start

    assert abs(dp_gained - 30) <= 2, f"S3 must generate ~30 DP over 20s; got {dp_gained}"


# ---------------------------------------------------------------------------
# Test 4: Block drops to 0 during S3
# ---------------------------------------------------------------------------

def test_s3_block_drops_to_zero():
    w = _world()
    s = make_saileach(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    w.add_unit(s)
    assert s.block == 1, "Saileach block must be 1 before S3"

    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)

    assert s.block == 0, "Block must drop to 0 during S3"


# ---------------------------------------------------------------------------
# Test 5: ATK buff cleared and block restored on S3 end
# ---------------------------------------------------------------------------

def test_s3_cleanup_on_end():
    w = _world()
    s = make_saileach(slot="S3")
    s.deployed = True; s.position = (0.0, 1.0); s.atk_cd = 999.0
    w.add_unit(s)

    ally = _ally(w, 2.0, 1.0)
    ally_base_atk = ally.effective_atk

    s.skill.sp = float(s.skill.sp_cost)
    manual_trigger(w, s)
    _ticks(w, 21.0)

    assert s.skill.active_remaining == 0.0, "S3 must have ended"
    assert not any(b.source_tag == _S3_BUFF_TAG for b in ally.buffs), "ATK buff must clear on end"
    assert abs(ally.effective_atk - ally_base_atk) <= 2, "Ally ATK must revert to base"
    assert s.block == 1, "Block must be restored after S3"


# ---------------------------------------------------------------------------
# Test 6: S2 regression
# ---------------------------------------------------------------------------

def test_s2_regression():
    s = make_saileach(slot="S2")
    assert s.skill is not None and s.skill.slot == "S2"
    assert s.skill.name == "Flagship Order"
    assert s.skill.sp_cost == 35
