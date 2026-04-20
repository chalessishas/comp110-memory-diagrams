"""Lappland — Blade Arts SILENCE-on-hit talent + S2 ATK burst."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState, SkillComponent
from core.types import TileType, TICK_RATE, Faction, StatusKind, SPGainMode, SkillTrigger
from core.systems import register_default_systems
from data.characters.lappland import (
    make_lappland, _TALENT_TAG, _SILENCE_DURATION, _S2_ATK_RATIO, _S2_DURATION,
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


def _slug(pos=(1, 1), hp=99999) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp
    e.hp = hp
    e.atk = 0
    e.move_speed = 0.0
    e.deployed = True
    e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Talent registered
# ---------------------------------------------------------------------------

def test_lappland_talent_registered():
    lap = make_lappland()
    assert len(lap.talents) == 1
    assert lap.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: First hit applies SILENCE
# ---------------------------------------------------------------------------

def test_blade_arts_applies_silence():
    """After Lappland hits an enemy, that enemy has SILENCE status."""
    w = _world()
    lap = make_lappland()
    lap.deployed = True
    lap.position = (0.0, 1.0)
    lap.atk_cd = 0.0
    lap.skill = None
    w.add_unit(lap)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    w.tick()  # Lappland attacks → on_attack_hit fires

    assert slug.has_status(StatusKind.SILENCE), "Enemy must be SILENCED after hit"


# ---------------------------------------------------------------------------
# Test 3: SILENCE blocks skill use but NOT movement
# ---------------------------------------------------------------------------

def test_silence_blocks_skill_not_movement():
    """SILENCE: can_use_skill() = False, but can_act() = True."""
    w = _world()
    lap = make_lappland()
    lap.deployed = True
    lap.position = (0.0, 1.0)
    lap.atk_cd = 0.0
    lap.skill = None
    w.add_unit(lap)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    w.tick()

    assert slug.has_status(StatusKind.SILENCE), "SILENCE must be applied"
    assert not slug.can_use_skill(), "SILENCED enemy must not use skills"
    assert slug.can_act(), "SILENCED enemy must still be able to act (move/attack)"


# ---------------------------------------------------------------------------
# Test 4: SILENCE prevents SP accumulation
# ---------------------------------------------------------------------------

def test_silence_prevents_sp_gain():
    """A unit with AUTO_TIME skill cannot gain SP while SILENCED."""
    w = _world()
    lap = make_lappland()
    lap.deployed = True
    lap.position = (0.0, 1.0)
    lap.atk_cd = 0.0
    lap.skill = None
    w.add_unit(lap)

    # Give the slug a skill so its SP can be tracked
    slug = _slug(pos=(1, 1))
    slug.skill = SkillComponent(
        name="test_skill",
        slot="S1",
        sp_cost=100,
        initial_sp=0,
        duration=1.0,
        sp_gain_mode=SPGainMode.AUTO_TIME,
        trigger=SkillTrigger.AUTO,
        requires_target=False,
        behavior_tag="__noop__",
    )
    w.add_unit(slug)

    w.tick()  # hit lands → SILENCE applied
    assert slug.has_status(StatusKind.SILENCE), "SILENCE must be applied"

    sp_after_silence = slug.skill.sp
    # Prevent further attacks; tick forward — SP must NOT increase
    lap.atk_cd = 999.0
    for _ in range(5):
        w.tick()

    assert slug.skill.sp == sp_after_silence, (
        f"SP must not accumulate while SILENCED: expected {sp_after_silence}, "
        f"got {slug.skill.sp}"
    )


# ---------------------------------------------------------------------------
# Test 5: SILENCE expires after _SILENCE_DURATION
# ---------------------------------------------------------------------------

def test_silence_expires():
    """SILENCE clears after _SILENCE_DURATION seconds without refresh."""
    w = _world()
    lap = make_lappland()
    lap.deployed = True
    lap.position = (0.0, 1.0)
    lap.atk_cd = 0.0
    lap.skill = None
    w.add_unit(lap)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    w.tick()
    assert slug.has_status(StatusKind.SILENCE), "SILENCE must be present"

    # Disable further attacks, wait past expiry
    lap.atk_cd = 999.0
    for _ in range(int(TICK_RATE * (_SILENCE_DURATION + 1))):
        w.tick()

    assert not slug.has_status(StatusKind.SILENCE), (
        "SILENCE must expire after 3s without refresh"
    )


# ---------------------------------------------------------------------------
# Test 6: SILENCE refreshes on re-hit (doesn't stack, resets timer)
# ---------------------------------------------------------------------------

def test_silence_refreshes_on_rehit():
    """A second hit resets the SILENCE timer, keeping the enemy silenced."""
    w = _world()
    lap = make_lappland()
    lap.deployed = True
    lap.position = (0.0, 1.0)
    lap.atk_cd = 0.0
    lap.skill = None
    w.add_unit(lap)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    w.tick()  # first hit → SILENCE

    # Advance most of the SILENCE duration without expiring it
    lap.atk_cd = 999.0
    partial_wait = int(TICK_RATE * (_SILENCE_DURATION - 0.5))
    for _ in range(partial_wait):
        w.tick()

    assert slug.has_status(StatusKind.SILENCE), "SILENCE should still be active"

    # Second hit refreshes SILENCE timer
    lap.atk_cd = 0.0
    for _ in range(int(lap.atk_interval * TICK_RATE) + 1):
        w.tick()

    assert slug.has_status(StatusKind.SILENCE), "SILENCE must be refreshed"
    # Check exactly one SILENCE status (no stacking)
    silence_count = sum(1 for s in slug.statuses if s.kind == StatusKind.SILENCE)
    assert silence_count == 1, f"Must have exactly 1 SILENCE, got {silence_count}"


# ---------------------------------------------------------------------------
# Test 7: S2 activates ATK buff
# ---------------------------------------------------------------------------

def test_lappland_s2_atk_buff():
    """S2 fires: ATK increases by +80%."""
    w = _world()
    lap = make_lappland()
    lap.deployed = True
    lap.position = (0.0, 1.0)
    lap.atk_cd = 999.0
    w.add_unit(lap)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    atk_base = lap.effective_atk
    lap.skill.sp = lap.skill.sp_cost
    w.tick()

    assert lap.skill.active_remaining > 0.0, "S2 must be active"
    expected = int(atk_base * (1.0 + _S2_ATK_RATIO))
    assert lap.effective_atk == expected, (
        f"S2 ATK should be {expected}, got {lap.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 8: S2 ATK buff removed on expiry
# ---------------------------------------------------------------------------

def test_lappland_s2_buff_removed_on_end():
    """ATK reverts to base after S2 expires."""
    w = _world()
    lap = make_lappland()
    lap.deployed = True
    lap.position = (0.0, 1.0)
    lap.atk_cd = 999.0
    w.add_unit(lap)

    slug = _slug(pos=(1, 1))
    w.add_unit(slug)

    atk_base = lap.effective_atk
    lap.skill.sp = lap.skill.sp_cost
    w.tick()

    for _ in range(int(TICK_RATE * (_S2_DURATION + 1))):
        w.tick()

    assert lap.skill.active_remaining == 0.0, "S2 must have expired"
    assert lap.effective_atk == atk_base, "ATK must revert to base after S2"
