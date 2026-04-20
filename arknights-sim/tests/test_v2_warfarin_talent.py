"""Warfarin — Blood Sample Recycle talent: enemy-killed-in-range SP grant.

Tests cover:
  - Enemy dies in Warfarin's range → Warfarin gains +1 SP
  - Enemy dies outside range → Warfarin gains NO SP
  - Ally in range also gains +1 SP when enemy dies
  - No ally in range → only Warfarin gains SP (no crash)
  - SP capped at sp_cost (does not exceed)
  - SP gain skipped when Warfarin's skill is already active
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, SkillComponent
from core.types import TileType, Faction, Profession, AttackType, SPGainMode, SkillTrigger
from core.systems import register_default_systems
from data.characters.warfarin import make_warfarin, _TALENT_TAG, _TALENT_SP_GAIN
from data.characters.silverash import make_silverash
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=8, height=4)
    for x in range(8):
        for y in range(4):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _dead_slug(pos=(1, 0)) -> UnitState:
    """Pre-killed slug ready to trigger cleanup death dispatch."""
    px, py = int(pos[0]), int(pos[1])
    e = make_originium_slug(path=[(px, py)] * 10)
    e.deployed = True; e.position = (float(px), float(py))
    e.hp = 0; e.alive = False; e._just_died = True
    return e


# ---------------------------------------------------------------------------
# Test 1: Enemy dies in Warfarin's range → Warfarin gains +1 SP
# ---------------------------------------------------------------------------

def test_blood_sample_sp_gain_on_kill_in_range():
    """Enemy dying in Warfarin's range grants +1 SP to Warfarin."""
    w = _world()
    warf = make_warfarin("S2")
    warf.deployed = True; warf.position = (0.0, 0.0); warf.atk_cd = 999.0
    w.add_unit(warf)

    sp_before = warf.skill.sp

    # Warfarin's MEDIC_RANGE tiles: (1,0),(2,0),(3,0) — enemy at (1,0) is in range
    slug = _dead_slug(pos=(1, 0))
    w.add_unit(slug)
    w.tick()  # cleanup fires fire_on_enemy_killed → +1 SP to Warfarin

    # AUTO_TIME also adds 0.1 SP this tick; check talent gain is included
    assert warf.skill.sp >= sp_before + _TALENT_SP_GAIN, (
        f"Warfarin must gain at least {_TALENT_SP_GAIN} SP when enemy dies in range; "
        f"before={sp_before}, after={warf.skill.sp}"
    )


# ---------------------------------------------------------------------------
# Test 2: Enemy dies outside range → no SP gain
# ---------------------------------------------------------------------------

def test_blood_sample_no_sp_out_of_range():
    """Enemy dying outside Warfarin's range must NOT grant SP."""
    w = _world()
    warf = make_warfarin("S2")
    warf.deployed = True; warf.position = (0.0, 0.0); warf.atk_cd = 999.0
    w.add_unit(warf)

    sp_before = warf.skill.sp

    # Position (5,0) is dx=5 from Warfarin — outside MEDIC_RANGE (max dx=3)
    slug = _dead_slug(pos=(5, 0))
    w.add_unit(slug)
    w.tick()

    # AUTO_TIME adds a small SP tick regardless — talent gain is 1.0, so if sp < 0.5 no talent fired
    assert warf.skill.sp < sp_before + _TALENT_SP_GAIN, (
        f"Warfarin must NOT gain talent SP for enemy dying outside range; "
        f"before={sp_before}, after={warf.skill.sp}"
    )


# ---------------------------------------------------------------------------
# Test 3: Ally in range also gains +1 SP
# ---------------------------------------------------------------------------

def test_blood_sample_ally_in_range_gains_sp():
    """An ally within Warfarin's range also gains +1 SP from Blood Sample Recycle."""
    w = _world()
    warf = make_warfarin("S2")
    warf.deployed = True; warf.position = (0.0, 0.0); warf.atk_cd = 999.0
    w.add_unit(warf)

    # SilverAsh at (2,0) — within MEDIC_RANGE of Warfarin at (0,0)
    sa = make_silverash("S3")
    sa.deployed = True; sa.position = (2.0, 0.0); sa.atk_cd = 999.0
    w.add_unit(sa)

    sa_sp_before = sa.skill.sp

    slug = _dead_slug(pos=(1, 0))  # in Warfarin's range
    w.add_unit(slug)
    w.tick()

    # AUTO_TIME adds 0.1 SP; talent adds 1.0 — check at least talent gain received
    assert sa.skill.sp >= sa_sp_before + _TALENT_SP_GAIN, (
        f"Ally in range must gain at least {_TALENT_SP_GAIN} SP; "
        f"before={sa_sp_before}, after={sa.skill.sp}"
    )


# ---------------------------------------------------------------------------
# Test 4: No ally in range → only Warfarin gains SP, no crash
# ---------------------------------------------------------------------------

def test_blood_sample_no_ally_in_range_no_crash():
    """When no ally is in range, only Warfarin gains SP and no error occurs."""
    w = _world()
    warf = make_warfarin("S2")
    warf.deployed = True; warf.position = (0.0, 0.0); warf.atk_cd = 999.0
    w.add_unit(warf)

    sp_before = warf.skill.sp
    slug = _dead_slug(pos=(1, 0))
    w.add_unit(slug)
    w.tick()  # must not crash

    assert warf.skill.sp >= sp_before + _TALENT_SP_GAIN, (
        "Warfarin must still gain SP even with no ally in range"
    )


# ---------------------------------------------------------------------------
# Test 5: SP does not exceed sp_cost
# ---------------------------------------------------------------------------

def test_blood_sample_sp_capped_at_cost():
    """Blood Sample Recycle must not push SP above sp_cost."""
    w = _world()
    warf = make_warfarin("S2")
    warf.deployed = True; warf.position = (0.0, 0.0); warf.atk_cd = 999.0
    # Pre-charge to 1 below max
    warf.skill.sp = float(warf.skill.sp_cost) - 0.5
    w.add_unit(warf)

    slug = _dead_slug(pos=(1, 0))
    w.add_unit(slug)
    w.tick()

    assert warf.skill.sp <= float(warf.skill.sp_cost), (
        f"SP must be capped at sp_cost={warf.skill.sp_cost}; got {warf.skill.sp}"
    )


# ---------------------------------------------------------------------------
# Test 6: SP gain skipped when skill is active
# ---------------------------------------------------------------------------

def test_blood_sample_no_sp_gain_when_skill_active():
    """Blood Sample Recycle must not give SP to Warfarin while her skill is active."""
    w = _world()
    warf = make_warfarin("S2")
    warf.deployed = True; warf.position = (0.0, 0.0); warf.atk_cd = 999.0
    warf.skill.sp = float(warf.skill.sp_cost)  # pre-charged
    w.add_unit(warf)

    # Activate S2 (requires_target=False — will fire unconditionally)
    w.tick()  # S2 fires, skill becomes active
    assert warf.skill.active_remaining > 0.0, "S2 must be active"

    sp_while_active = warf.skill.sp  # sp resets to 0 when skill fires

    slug = _dead_slug(pos=(1, 0))
    w.add_unit(slug)
    w.tick()  # enemy death — talent fires but skill is active

    assert warf.skill.sp == sp_while_active, (
        "No SP gain while Warfarin's skill is active"
    )
