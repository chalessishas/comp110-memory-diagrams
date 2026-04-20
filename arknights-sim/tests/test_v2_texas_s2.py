"""Texas S2 Sword Rain — instant burst: ATK +200%, 2 hits, +3 DP.

Tests cover:
  - S2 skill is correctly configured on make_texas()
  - Activating S2 restores +3 DP
  - S2 deals exactly 2 physical hits to the target
  - ATK buff is applied during the burst (boosted damage)
  - Tactical Delivery talent grants +2 DP at battle start (existing test sanity check)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, Faction, SPGainMode, SkillTrigger
from core.systems import register_default_systems
from data.characters.texas import (
    make_texas,
    _S2_ATK_RATIO, _S2_HIT_COUNT, _S2_DP_GAIN, _S2_BUFF_TAG,
)
from data.enemies import make_originium_slug


def _world(starting_dp: int = 0) -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp = starting_dp
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(pos=(1, 1), hp=99999, defence=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = defence; e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: S2 skill is configured on make_texas()
# ---------------------------------------------------------------------------

def test_texas_s2_skill_config():
    """make_texas(slot='S2') must have Sword Rain wired correctly."""
    tex = make_texas(slot="S2")
    assert tex.skill is not None, "Texas must have a skill when slot='S2'"
    assert tex.skill.name == "Sword Rain"
    assert tex.skill.sp_gain_mode == SPGainMode.AUTO_ATTACK
    assert tex.skill.trigger == SkillTrigger.AUTO
    assert tex.skill.sp_cost == 18
    assert tex.skill.duration == 0.0, "Sword Rain is an instant skill (duration=0)"


# ---------------------------------------------------------------------------
# Test 2: S2 activation grants +3 DP
# ---------------------------------------------------------------------------

def test_texas_s2_grants_dp():
    """When S2 fires, global DP increases by _S2_DP_GAIN (3)."""
    w = _world(starting_dp=10)
    tex = make_texas(slot="S2")
    tex.deployed = True; tex.position = (0.0, 1.0); tex.atk_cd = 999.0
    w.add_unit(tex)

    enemy = _slug(pos=(1, 1))
    w.add_unit(enemy)

    # Account for Tactical Delivery +2 DP on add_unit
    dp_after_deploy = w.global_state.dp

    # Force skill to fire on next tick
    tex.skill.sp = float(tex.skill.sp_cost)
    w.tick()

    assert w.global_state.dp == dp_after_deploy + _S2_DP_GAIN, (
        f"S2 must grant +{_S2_DP_GAIN} DP; before={dp_after_deploy}, "
        f"after={w.global_state.dp}"
    )


# ---------------------------------------------------------------------------
# Test 3: S2 deals exactly 2 physical hits
# ---------------------------------------------------------------------------

def test_texas_s2_deals_two_hits():
    """Sword Rain delivers exactly 2 physical hits to the target."""
    w = _world()
    tex = make_texas(slot="S2")
    tex.deployed = True; tex.position = (0.0, 1.0); tex.atk_cd = 999.0
    w.add_unit(tex)

    # Zero-defence enemy so each hit = full ATK
    enemy = _slug(pos=(1, 1), hp=99999, defence=0)
    w.add_unit(enemy)

    hp_before = enemy.hp
    tex.skill.sp = float(tex.skill.sp_cost)
    w.tick()

    damage_dealt = hp_before - enemy.hp
    # Each hit = effective_atk (with +200% buff active during burst)
    boosted_atk = int(tex.atk * (1.0 + _S2_ATK_RATIO))
    expected_damage = boosted_atk * _S2_HIT_COUNT
    assert damage_dealt == expected_damage, (
        f"Sword Rain must deal {expected_damage} total ({_S2_HIT_COUNT}×{boosted_atk}); "
        f"got {damage_dealt}"
    )


# ---------------------------------------------------------------------------
# Test 4: ATK buff removed after S2 (instant skill — no lingering buff)
# ---------------------------------------------------------------------------

def test_texas_s2_atk_buff_cleared_after_skill():
    """ATK buff from Sword Rain must be gone after the instant skill fires."""
    w = _world()
    tex = make_texas(slot="S2")
    tex.deployed = True; tex.position = (0.0, 1.0); tex.atk_cd = 999.0
    w.add_unit(tex)

    enemy = _slug(pos=(1, 1))
    w.add_unit(enemy)

    base_atk = tex.effective_atk
    tex.skill.sp = float(tex.skill.sp_cost)
    w.tick()  # skill fires and ends in same tick

    atk_after = tex.effective_atk
    assert atk_after == base_atk, (
        f"ATK buff must be cleared after instant S2; base={base_atk}, after={atk_after}"
    )
    sword_rain_buffs = [b for b in tex.buffs if b.source_tag == _S2_BUFF_TAG]
    assert len(sword_rain_buffs) == 0, "No Sword Rain buffs may remain after skill ends"


# ---------------------------------------------------------------------------
# Test 5: Tactical Delivery still fires (+2 DP) when Texas has S2 slot
# ---------------------------------------------------------------------------

def test_tactical_delivery_still_fires_with_s2_slot():
    """Tactical Delivery (+2 DP) must still fire even when S2 skill is wired."""
    w = _world(starting_dp=0)
    tex = make_texas(slot="S2")
    dp_before = w.global_state.dp
    w.add_unit(tex)
    assert w.global_state.dp == dp_before + 2, (
        f"Tactical Delivery must give +2 DP on add_unit; got dp={w.global_state.dp}"
    )
