"""Mlynar — GUARD_LIBERATOR: passive ATK ramp + combat suppression when inactive.

GUARD_LIBERATOR trait:
  - block=0, cannot attack while skill is inactive
  - ATK passively ramps up to +200% over 40s while skill is off
  - When skill fires: block=3 restored, attacks resume with ramped ATK
  - When skill ends: ramp resets to 0, block=0, attacks suspended again

Tests cover:
  - Archetype is GUARD_LIBERATOR
  - block=0 on deploy (skill inactive)
  - Cannot attack while skill inactive (atk_cd stays high)
  - ATK ramp buff increases each tick
  - ATK ramp caps at +200%
  - S3 on_start: block restored to 3, atk_cd=0, ASPD+90
  - S3 on_end: ramp reset to 0, block=0, ASPD buff removed
  - ATK during S3 reflects accumulated ramp (ramped value carries into skill)
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, DT, Faction, RoleArchetype, BuffAxis
from core.systems import register_default_systems
from data.characters.mlynar import (
    make_mlynar, _RAMP_MAX_RATIO, _RAMP_RATE, _RAMP_ATTR,
    _RAMP_BUFF_TAG, _S3_ASPD_BUFF_TAG, _S3_BLOCK, _S3_ASPD_FLAT,
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


def _slug(pos=(1, 1), hp=99999, defence=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = 0
    e.defence = defence; e.move_speed = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Archetype is GUARD_LIBERATOR
# ---------------------------------------------------------------------------

def test_mlynar_archetype():
    m = make_mlynar()
    assert m.archetype == RoleArchetype.GUARD_LIBERATOR
    assert m.block == 0, "Should start with block=0 (skill inactive)"


# ---------------------------------------------------------------------------
# Test 2: block=0 while skill inactive; no enemies are blocked
# ---------------------------------------------------------------------------

def test_block_zero_when_skill_inactive():
    """Mlynar must not block enemies while his skill is inactive."""
    w = _world()
    m = make_mlynar()
    m.deployed = True; m.position = (0.0, 1.0)
    m.skill.sp = 0.0  # no SP — skill cannot fire
    w.add_unit(m)

    enemy = _slug(pos=(0, 1), hp=9999)
    w.add_unit(enemy)

    for _ in range(5):
        w.tick()

    assert m.block == 0, f"Block must be 0 when skill inactive; got {m.block}"
    assert len(enemy.blocked_by_unit_ids) == 0, (
        f"Enemy must not be blocked by inactive Mlynar; blocked_by={enemy.blocked_by_unit_ids}"
    )


# ---------------------------------------------------------------------------
# Test 3: Cannot attack while skill inactive (atk_cd held high)
# ---------------------------------------------------------------------------

def test_no_attack_when_skill_inactive():
    """Mlynar must not deal damage while his skill is inactive."""
    w = _world()
    m = make_mlynar()
    m.deployed = True; m.position = (0.0, 1.0)
    m.skill.sp = 0.0  # no SP, skill can't fire
    w.add_unit(m)

    enemy = _slug(pos=(1, 1), hp=9999)
    initial_hp = enemy.hp
    w.add_unit(enemy)

    for _ in range(TICK_RATE * 3):
        w.tick()

    assert enemy.hp == initial_hp, (
        f"Mlynar must not attack when inactive; enemy hp changed from {initial_hp} to {enemy.hp}"
    )


# ---------------------------------------------------------------------------
# Test 4: ATK ramp buff increases over time
# ---------------------------------------------------------------------------

def test_atk_ramp_increases():
    """ATK ramp grows each tick while skill is inactive."""
    w = _world()
    m = make_mlynar()
    m.deployed = True; m.position = (0.0, 1.0)
    m.skill.sp = 0.0
    w.add_unit(m)

    initial_atk = m.effective_atk

    # Run for 10 seconds
    for _ in range(TICK_RATE * 10):
        w.tick()

    ramp = getattr(m, _RAMP_ATTR, 0.0)
    assert ramp > 0.0, f"Ramp must have increased; got {ramp}"
    assert m.effective_atk > initial_atk, (
        f"effective_atk must grow with ramp; was {initial_atk}, now {m.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 5: ATK ramp caps at +200%
# ---------------------------------------------------------------------------

def test_atk_ramp_caps_at_max():
    """ATK ramp must not exceed _RAMP_MAX_RATIO (+200%)."""
    w = _world()
    m = make_mlynar()
    m.deployed = True; m.position = (0.0, 1.0)
    m.skill.sp = 0.0
    w.add_unit(m)

    base_atk = m.atk  # raw base stat before buffs

    # Run for 50 seconds (past the 40s ramp-up period)
    for _ in range(TICK_RATE * 50):
        w.tick()

    ramp = getattr(m, _RAMP_ATTR, 0.0)
    assert abs(ramp - _RAMP_MAX_RATIO) < 0.01, (
        f"Ramp must cap at {_RAMP_MAX_RATIO}; got {ramp}"
    )
    # effective_atk should be base × (1 + 2.0) = 3× base
    expected = int(base_atk * (1.0 + _RAMP_MAX_RATIO))
    assert abs(m.effective_atk - expected) <= 2, (
        f"ATK at max ramp should be ~{expected}; got {m.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 6: S3 restores block=3, enables attacks, adds ASPD+90
# ---------------------------------------------------------------------------

def test_s3_restores_block_and_aspd():
    """When S3 fires, block=3 is restored and ASPD+90 buff applied."""
    w = _world()
    m = make_mlynar()
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    enemy = _slug(pos=(1, 1))
    w.add_unit(enemy)

    # Force skill active
    m.skill.sp = float(m.skill.sp_cost)
    w.tick()  # should fire the skill

    assert m.skill.active_remaining > 0.0, "S3 must have fired"
    assert m.block == _S3_BLOCK, f"Block must be {_S3_BLOCK} during S3; got {m.block}"

    aspd_buffs = [b for b in m.buffs if b.source_tag == _S3_ASPD_BUFF_TAG]
    assert len(aspd_buffs) == 1, "ASPD buff must be applied during S3"
    assert abs(aspd_buffs[0].value - _S3_ASPD_FLAT) < 0.1


# ---------------------------------------------------------------------------
# Test 7: S3 end resets ramp to 0 and clears block
# ---------------------------------------------------------------------------

def test_s3_end_resets_ramp_and_block():
    """After S3 ends, ramp resets to 0 and block goes back to 0."""
    w = _world()
    m = make_mlynar()
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    enemy = _slug(pos=(1, 1))
    w.add_unit(enemy)

    # Build some ramp first
    for _ in range(TICK_RATE * 5):
        w.tick()

    ramp_before_skill = getattr(m, _RAMP_ATTR, 0.0)
    assert ramp_before_skill > 0.0, "Ramp should have built up before skill fires"

    # Fire skill manually
    m.skill.sp = float(m.skill.sp_cost)
    w.tick()
    assert m.skill.active_remaining > 0.0, "S3 should be active"

    # Wait for S3 to end (duration + 1s)
    from data.characters.mlynar import _S3_DURATION
    for _ in range(int(TICK_RATE * (_S3_DURATION + 1))):
        w.tick()

    assert m.skill.active_remaining == 0.0, "S3 must have ended"
    ramp_after = getattr(m, _RAMP_ATTR, 0.0)
    # Ramp resets to 0 on skill end, then re-accumulates each tick.
    # After ~1 extra second the value is ~0.05 — far below the pre-skill 0.25.
    # Assert less than 2 full seconds of accumulation to confirm the reset fired.
    assert ramp_after < _RAMP_RATE * 2.0, (
        f"Ramp must have been reset after S3 ends; was {ramp_before_skill:.3f} before skill, "
        f"now {ramp_after:.3f} (expected < {_RAMP_RATE * 2.0:.3f})"
    )
    assert m.block == 0, f"Block must return to 0 after S3 ends; got {m.block}"


# ---------------------------------------------------------------------------
# Test 8: ATK during S3 reflects accumulated ramp
# ---------------------------------------------------------------------------

def test_s3_atk_reflects_ramp():
    """Mlynar's effective_atk during S3 should reflect the pre-skill ramp value."""
    w = _world()
    m = make_mlynar()
    m.deployed = True; m.position = (0.0, 1.0)
    w.add_unit(m)

    enemy = _slug(pos=(1, 1))
    w.add_unit(enemy)

    # Ramp for 20 seconds (half max ramp = +100%)
    for _ in range(TICK_RATE * 20):
        w.tick()

    ramp = getattr(m, _RAMP_ATTR, 0.0)
    assert ramp > 0.5, f"Expected significant ramp after 20s; got {ramp}"

    # Record expected ATK at this ramp level
    expected_atk_with_ramp = m.effective_atk  # includes ramp buff

    # Fire skill
    m.skill.sp = float(m.skill.sp_cost)
    w.tick()
    assert m.skill.active_remaining > 0.0, "S3 must fire"

    # ATK during skill should be the ramped value (ramp buff stays until skill ends)
    # plus ASPD — ATK axis is unchanged
    assert abs(m.effective_atk - expected_atk_with_ramp) <= 5, (
        f"ATK during S3 must reflect ramp; expected ~{expected_atk_with_ramp}, got {m.effective_atk}"
    )
