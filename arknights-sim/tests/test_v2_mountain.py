"""Mountain — Natural God talent (ATK+18% when not blocking) + S2/S3."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE
from core.systems import register_default_systems
from data.characters.mountain import (
    make_mountain, _NATURAL_GOD_ATK_RATIO, _S2_ATK_RATIO,
    _S3_ATK_RATIO, _S3_ASPD_FLAT,
    _S2_KILL_EXTENSION, _S2_MAX_EXTENSION,
)
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


def _slug(pos=(1, 1), hp=99999, atk=0):
    path = [(int(pos[0]), int(pos[1]))] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = atk; e.move_speed = 0.0
    e.deployed = True; e.position = (float(pos[0]), float(pos[1]))
    return e


# ---------------------------------------------------------------------------
# Test 1: Talent registered
# ---------------------------------------------------------------------------

def test_mountain_talent_registered():
    m = make_mountain()
    assert len(m.talents) == 1
    assert m.talents[0].name == "Natural God"


# ---------------------------------------------------------------------------
# Test 2: Natural God grants ATK+18% when no enemies blocked
# ---------------------------------------------------------------------------

def test_natural_god_atk_when_not_blocking():
    """Natural God: ATK +18% when not blocking any enemies."""
    w = _world()
    m = make_mountain()
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)

    # No enemies — blocking count = 0
    atk_base = m.effective_atk
    w.tick()

    expected = int(atk_base * (1.0 + _NATURAL_GOD_ATK_RATIO))
    assert m.effective_atk == expected, (
        f"Natural God must give ATK {expected} when not blocking; got {m.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 3: Natural God suppressed when blocking an enemy
# ---------------------------------------------------------------------------

def test_natural_god_suppressed_when_blocking():
    """Natural God must NOT apply when Mountain is blocking an enemy."""
    w = _world()
    m = make_mountain()
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)

    # Enemy at Mountain's EXACT tile — targeting_system will assign blocking
    slug = _slug((0, 1))
    w.add_unit(slug)

    atk_base = m.atk
    w.tick()

    assert m.effective_atk == atk_base, (
        "Natural God must NOT apply when Mountain is blocking an enemy"
    )


# ---------------------------------------------------------------------------
# Test 4: Natural God activates after enemy dies (unblocked)
# ---------------------------------------------------------------------------

def test_natural_god_activates_after_unblock():
    """When blocked enemy dies, Natural God re-activates on next tick."""
    w = _world()
    m = make_mountain()
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)

    slug = _slug((0, 1))  # same tile → targeting_system will block it
    w.add_unit(slug)

    w.tick()  # blocked — no talent buff
    assert m.effective_atk == m.atk, "No buff while blocking"

    # Enemy dies — cleared from enemies() on next tick's cleanup
    slug.alive = False

    w.tick()  # now unblocked — targeting_system skips dead enemies; talent fires

    expected = int(m.atk * (1.0 + _NATURAL_GOD_ATK_RATIO))
    assert m.effective_atk == expected, (
        f"Natural God must re-activate after enemy dies; expected {expected}, got {m.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 5: S2 ATK buff activates
# ---------------------------------------------------------------------------

def test_mountain_s2_atk_buff():
    """S2 Mountain Spirit: ATK +160% (slug at same tile suppresses Natural God)."""
    w = _world()
    m = make_mountain(slot="S2")
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)
    # Slug at Mountain's tile → blocking suppresses Natural God for clean S2-only check
    slug = _slug((0, 1))
    w.add_unit(slug)

    atk_base = m.effective_atk
    m.skill.sp = m.skill.sp_cost
    w.tick()

    expected = int(atk_base * (1.0 + _S2_ATK_RATIO))
    assert m.effective_atk == expected, (
        f"S2 must give ATK {expected}; got {m.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 6: S3 ATK + ASPD buffs
# ---------------------------------------------------------------------------

def test_mountain_s3_atk_aspd():
    """S3 Blood and Iron: ATK +200% + ASPD +40 (slug at same tile suppresses Natural God)."""
    w = _world()
    m = make_mountain(slot="S3")
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)
    slug = _slug((0, 1))  # blocking → no Natural God
    w.add_unit(slug)

    atk_base = m.effective_atk
    m.skill.sp = m.skill.sp_cost
    w.tick()

    expected_atk = int(atk_base * (1.0 + _S3_ATK_RATIO))
    expected_aspd = 100.0 + _S3_ASPD_FLAT
    assert m.effective_atk == expected_atk, (
        f"S3 ATK must be {expected_atk}; got {m.effective_atk}"
    )
    assert m.effective_aspd == expected_aspd, (
        f"S3 ASPD must be {expected_aspd}; got {m.effective_aspd}"
    )


# ---------------------------------------------------------------------------
# Test 7: S2 reverts on end
# ---------------------------------------------------------------------------

def test_mountain_s2_reverts():
    """After S2 expires, ATK returns to base."""
    w = _world()
    m = make_mountain(slot="S2")
    m.deployed = True; m.position = (0.0, 1.0); m.atk_cd = 999.0
    w.add_unit(m)
    slug = _slug((0, 1), hp=9999999)  # huge HP: stays alive through 21s of S2
    w.add_unit(slug)

    m.skill.sp = m.skill.sp_cost
    w.tick()
    atk_buffed = m.effective_atk
    assert atk_buffed > m.atk

    for _ in range(TICK_RATE * 21):
        w.tick()

    assert m.skill.active_remaining == 0.0
    # Slug is at same tile: Mountain still blocking → Natural God suppressed → base ATK
    assert m.effective_atk == m.atk, (
        f"After S2, ATK must revert to base ({m.atk}); got {m.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Tests 8–10: S2 kill-extension mechanic
# ---------------------------------------------------------------------------

def test_s2_kill_extends_duration():
    """Killing an enemy while S2 is active extends active_remaining by 1s."""
    w = _world()
    m = make_mountain("S2")
    m.deployed = True
    m.position = (0.0, 1.0)
    m.atk_cd = 999.0          # don't attack in tick 1
    m.skill.sp = float(m.skill.sp_cost)
    w.add_unit(m)

    # Decoy slug to satisfy requires_target → S2 fires
    decoy = _slug(pos=(1, 1), hp=9999, atk=0)
    w.add_unit(decoy)
    w.tick()  # S2 fires → active_remaining = 20.0
    assert m.skill.active_remaining > 0.0, "S2 must be active"

    # Soft-kill decoy so it's removed from target pool (world.enemies() filters alive=True)
    decoy.alive = False
    m.atk_cd = 0.0
    target = _slug(pos=(1, 1), hp=1, atk=0)
    w.add_unit(target)
    active_before = m.skill.active_remaining

    w.tick()  # Mountain attacks only target → kills it → on_kill extends active_remaining

    assert not target.alive, "Target must die for extension to trigger"
    assert m.skill.active_remaining > active_before, (
        f"Kill must extend S2 duration; before={active_before:.2f}, "
        f"after={m.skill.active_remaining:.2f}"
    )


def test_s2_kill_extension_capped():
    """Kill-extension cannot push active_remaining beyond base_duration + 3s."""
    w = _world()
    m = make_mountain("S2")
    m.deployed = True
    m.position = (0.0, 1.0)
    m.atk_cd = 0.0
    m.skill.sp = float(m.skill.sp_cost)
    w.add_unit(m)

    decoy = _slug(pos=(1, 1), hp=9999, atk=0)
    w.add_unit(decoy)
    w.tick()  # S2 fires

    # Add 4 hp=1 slugs — 4 kills would exceed the 3s cap
    for _ in range(4):
        t = _slug(pos=(1, 1), hp=1, atk=0)
        w.add_unit(t)
        w.tick()

    cap = float(m.skill.duration) + _S2_MAX_EXTENSION
    assert m.skill.active_remaining <= cap, (
        f"active_remaining must not exceed cap={cap:.1f}; got {m.skill.active_remaining:.2f}"
    )


def test_s2_kill_no_extension_when_inactive():
    """Killing before S2 fires must NOT extend duration (skill not active)."""
    w = _world()
    m = make_mountain("S2")
    m.deployed = True
    m.position = (0.0, 1.0)
    m.atk_cd = 0.0
    m.skill.sp = 0.0           # sp empty — S2 cannot fire
    w.add_unit(m)

    slug = _slug(pos=(1, 1), hp=1, atk=0)
    w.add_unit(slug)
    w.tick()  # Mountain attacks and kills; S2 NOT active

    assert m.skill.active_remaining == 0.0, (
        "Kill before S2 fires must not set active_remaining"
    )
