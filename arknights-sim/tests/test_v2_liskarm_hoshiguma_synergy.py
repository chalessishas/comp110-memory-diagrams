"""Liskarm + Hoshiguma synergy integration test.

Classic team composition: Liskarm (Sentinel Defender) tanks hits and fires
her SP battery → Hoshiguma (Juggernaut Defender) accumulates SP faster,
enabling more frequent Unshakeable (S2) activations.

This test validates the cross-unit SP flow end-to-end with real operator
instances (not synthetic test allies), proving the mechanics compose correctly.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.liskarm import make_liskarm
from data.characters.hoshiguma import make_hoshiguma, _S2_DEF_FLAT
from data.enemies import make_originium_slug


PATH = [(1, 0)] * 20


def _world() -> World:
    grid = TileGrid(width=4, height=2)
    for x in range(4):
        for y in range(2):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


# ---------------------------------------------------------------------------
# Test 1: Liskarm hit → Hoshiguma (adjacent) gains SP
# ---------------------------------------------------------------------------

def test_liskarm_charges_hoshiguma_sp():
    """When Liskarm is hit, adjacent Hoshiguma's S2 SP should increase."""
    w = _world()

    lisk = make_liskarm()
    lisk.deployed = True; lisk.position = (1.0, 0.0); lisk.atk_cd = 999.0
    w.add_unit(lisk)

    hoshi = make_hoshiguma()
    hoshi.deployed = True; hoshi.position = (1.0, 1.0)   # distance=1.0 ≤ _SP_RADIUS=1.5
    hoshi.atk_cd = 999.0
    w.add_unit(hoshi)

    slug = make_originium_slug(path=PATH)
    slug.deployed = True; slug.position = (1.0, 0.0)
    slug.blocked_by_unit_ids = [lisk.unit_id]
    slug.move_speed = 0.0; slug.atk_cd = 0.0; slug.atk = 200
    w.add_unit(slug)

    hoshi_sp_before = hoshi.skill.sp

    for _ in range(TICK_RATE * 5):
        w.tick()
        if hoshi.skill.sp > hoshi_sp_before:
            break

    assert hoshi.skill.sp > hoshi_sp_before, (
        f"Hoshiguma must gain SP from Liskarm battery when adjacent; "
        f"sp stayed at {hoshi.skill.sp:.1f}"
    )


# ---------------------------------------------------------------------------
# Test 2: SP accumulation rate is faster with Liskarm present (vs solo)
# ---------------------------------------------------------------------------

def test_liskarm_accelerates_hoshiguma_sp_vs_solo():
    """Hoshiguma next to Liskarm (being attacked) charges S2 faster than solo."""
    ticks = TICK_RATE * 8   # 8s of simulation

    # Solo Hoshiguma — only AUTO_TIME SP gain (no battery)
    w_solo = _world()
    hoshi_solo = make_hoshiguma()
    hoshi_solo.deployed = True; hoshi_solo.position = (1.0, 0.0)
    hoshi_solo.atk_cd = 999.0
    w_solo.add_unit(hoshi_solo)
    for _ in range(ticks):
        w_solo.tick()
    solo_sp = hoshi_solo.skill.sp

    # Hoshiguma + Liskarm + attacking slug
    w_team = _world()
    lisk = make_liskarm()
    lisk.deployed = True; lisk.position = (1.0, 0.0); lisk.atk_cd = 999.0
    w_team.add_unit(lisk)

    hoshi_team = make_hoshiguma()
    hoshi_team.deployed = True; hoshi_team.position = (1.0, 1.0)
    hoshi_team.atk_cd = 999.0
    w_team.add_unit(hoshi_team)

    slug = make_originium_slug(path=PATH)
    slug.deployed = True; slug.position = (1.0, 0.0)
    slug.blocked_by_unit_ids = [lisk.unit_id]
    slug.move_speed = 0.0; slug.atk_cd = 0.0; slug.atk = 200
    w_team.add_unit(slug)

    for _ in range(ticks):
        w_team.tick()
    team_sp = hoshi_team.skill.sp

    assert team_sp > solo_sp, (
        f"Hoshiguma with Liskarm battery should charge faster: "
        f"team={team_sp:.1f} vs solo={solo_sp:.1f}"
    )


# ---------------------------------------------------------------------------
# Test 3: Hoshiguma S2 DEF buff applies when skill activates
# ---------------------------------------------------------------------------

def test_hoshiguma_s2_def_buff_on_activation():
    """When Hoshiguma S2 fires, her effective_def increases by _S2_DEF_FLAT."""
    w = _world()
    hoshi = make_hoshiguma()
    hoshi.deployed = True; hoshi.position = (1.0, 0.0); hoshi.atk_cd = 999.0
    w.add_unit(hoshi)

    def_before = hoshi.effective_def

    # Fill SP and let AUTO trigger fire the skill
    hoshi.skill.sp = float(hoshi.skill.sp_cost)
    w.tick()   # AUTO trigger fires on this tick

    assert hoshi.skill.active_remaining > 0.0, "S2 must be active after SP full + tick"
    assert hoshi.effective_def == def_before + _S2_DEF_FLAT, (
        f"DEF must be {def_before + _S2_DEF_FLAT} during S2; got {hoshi.effective_def}"
    )


# ---------------------------------------------------------------------------
# Test 4: Hoshiguma S2 DEF buff removed when skill expires
# ---------------------------------------------------------------------------

def test_hoshiguma_s2_def_buff_removed_on_expiry():
    """After S2 expires, Hoshiguma's DEF returns to base value."""
    w = _world()
    hoshi = make_hoshiguma()
    hoshi.deployed = True; hoshi.position = (1.0, 0.0); hoshi.atk_cd = 999.0
    w.add_unit(hoshi)

    def_before = hoshi.effective_def

    hoshi.skill.sp = float(hoshi.skill.sp_cost)
    w.tick()   # skill fires

    expire_ticks = int(hoshi.skill.duration / (1.0 / TICK_RATE)) + TICK_RATE
    for _ in range(expire_ticks):
        w.tick()

    assert hoshi.skill.active_remaining == 0.0, "S2 must have expired"
    assert hoshi.effective_def == def_before, (
        f"DEF must revert to {def_before} after S2 ends; got {hoshi.effective_def}"
    )


# ---------------------------------------------------------------------------
# Test 5: Overweight talent still active during S2 (talents + skill stack)
# ---------------------------------------------------------------------------

def test_overweight_still_reduces_damage_during_s2():
    """During S2, Hoshiguma's Overweight talent (20% DR) still applies."""
    w = _world()
    hoshi = make_hoshiguma()
    hoshi.deployed = True; hoshi.position = (1.0, 0.0); hoshi.atk_cd = 999.0
    w.add_unit(hoshi)

    hoshi.skill.sp = float(hoshi.skill.sp_cost)
    w.tick()   # activate S2

    assert hoshi.skill.active_remaining > 0.0
    assert hoshi.hp / hoshi.max_hp > 0.5   # still above threshold

    raw_dmg = 1000
    actual = hoshi.take_damage(raw_dmg)
    # 20% reduction still applies
    expected = int(raw_dmg * 0.80)
    assert actual == max(1, expected), (
        f"Overweight must reduce damage 20% during S2; expected {expected}, got {actual}"
    )
