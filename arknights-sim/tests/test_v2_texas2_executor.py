"""Texas Alter — SPEC_EXECUTOR kill-reset + S3 AoE arts + SILENCE.

Talent "Surging Current": After killing an enemy, atk_cd resets to 0,
  so the next attack fires on the following tick (kill → chain).

S3 "Sword Rain": Instant manual AoE — deals arts damage to ALL enemies
  in range and applies SILENCE for 6s to each.

Tests cover:
  - Archetype is SPEC_EXECUTOR
  - Talent registered
  - After killing an enemy, atk_cd resets to 0
  - Kill-reset enables same-tick follow-up attack
  - Non-kill hit does NOT reset atk_cd
  - S3 deals arts damage to enemy in range
  - S3 silences all enemies in range
  - S3 does not hit out-of-range enemies
  - SILENCE expires after duration
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.types import TileType, TICK_RATE, DT, StatusKind, RoleArchetype
from core.systems import register_default_systems
from data.characters.texas2 import (
    make_texas_alter, _TALENT_TAG, _S3_SILENCE_DURATION, _S3_SILENCE_TAG,
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


def _slug(pos=(1, 1), hp=9999, atk=0, defence=0) -> UnitState:
    px, py = int(pos[0]), int(pos[1])
    path = [(px, py)] * 20
    e = make_originium_slug(path=path)
    e.max_hp = hp; e.hp = hp; e.atk = atk
    e.defence = defence; e.move_speed = 0.0; e.res = 0.0
    e.deployed = True; e.position = (float(px), float(py))
    return e


# ---------------------------------------------------------------------------
# Test 1: Archetype and talent
# ---------------------------------------------------------------------------

def test_texas_alter_archetype():
    t = make_texas_alter()
    assert t.archetype == RoleArchetype.SPEC_EXECUTOR
    assert len(t.talents) == 1
    assert t.talents[0].behavior_tag == _TALENT_TAG


# ---------------------------------------------------------------------------
# Test 2: atk_cd resets to 0 after killing an enemy
# ---------------------------------------------------------------------------

def test_kill_resets_atk_cd():
    """After Texas Alter kills an enemy, atk_cd must be 0 (instant re-attack)."""
    w = _world()
    t = make_texas_alter()
    t.deployed = True; t.position = (0.0, 1.0)
    w.add_unit(t)

    # Very low-HP enemy — one hit kills
    weak = _slug(pos=(1, 1), hp=1, defence=0)
    w.add_unit(weak)

    # Force immediate attack
    t.atk_cd = 0.0
    w.tick()  # Texas attacks → kills → on_kill fires → atk_cd=0

    assert not weak.alive, "Enemy must be dead"
    assert t.atk_cd == 0.0, (
        f"atk_cd must be 0 after kill-reset; got {t.atk_cd:.3f}"
    )


# ---------------------------------------------------------------------------
# Test 3: Kill-reset enables follow-up attack on next tick
# ---------------------------------------------------------------------------

def test_kill_chain_attack():
    """Kill-reset means Texas Alter attacks twice in quick succession: kill + follow-up."""
    w = _world()
    t = make_texas_alter()
    t.deployed = True; t.position = (0.0, 1.0)
    w.add_unit(t)

    # Two enemies: first weak (dies on tick 1), second survives
    weak = _slug(pos=(1, 1), hp=1, defence=0)
    strong = _slug(pos=(1, 1), hp=99999, defence=0)
    w.add_unit(weak)
    w.add_unit(strong)

    t.atk_cd = 0.0
    w.tick()  # Kills weak → on_kill fires → atk_cd=0
    # Kill-reset sets atk_cd=0; next tick Texas attacks immediately
    w.tick()

    # After two ticks: weak dead, strong took damage from follow-up
    assert not weak.alive
    assert strong.hp < strong.max_hp, (
        "Kill-reset follow-up: Texas must attack again on the tick after the kill"
    )


# ---------------------------------------------------------------------------
# Test 4: Non-kill hit does NOT reset atk_cd
# ---------------------------------------------------------------------------

def test_non_kill_no_reset():
    """Hitting a durable enemy (not killed) must NOT reset atk_cd."""
    w = _world()
    t = make_texas_alter()
    t.deployed = True; t.position = (0.0, 1.0)
    t.skill.sp = 0.0  # prevent skill firing
    w.add_unit(t)

    tough = _slug(pos=(1, 1), hp=99999, defence=0)
    w.add_unit(tough)

    t.atk_cd = 0.0
    w.tick()  # Texas attacks → enemy survives → no kill → no reset

    assert tough.alive, "Enemy must survive"
    assert t.atk_cd > 0.0, (
        f"atk_cd must not be reset when no kill; got {t.atk_cd:.3f}"
    )


# ---------------------------------------------------------------------------
# Test 5: S3 deals arts damage to enemies in range
# ---------------------------------------------------------------------------

def test_s3_arts_damage_in_range():
    """S3 Sword Rain must deal arts damage to all in-range enemies."""
    w = _world()
    t = make_texas_alter()
    t.deployed = True; t.position = (0.0, 1.0)
    w.add_unit(t)

    in_range = _slug(pos=(1, 1), hp=99999, defence=0)  # tile (1,0) from Texas = in range
    w.add_unit(in_range)

    pre_hp = in_range.hp
    t.skill.sp = float(t.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, t)

    assert in_range.hp < pre_hp, "S3 must deal arts damage to in-range enemy"


# ---------------------------------------------------------------------------
# Test 6: S3 silences enemies in range
# ---------------------------------------------------------------------------

def test_s3_silences_in_range():
    """S3 must apply SILENCE to all enemies in range."""
    w = _world()
    t = make_texas_alter()
    t.deployed = True; t.position = (0.0, 1.0)
    w.add_unit(t)

    enemy = _slug(pos=(1, 1), hp=99999)
    w.add_unit(enemy)

    t.skill.sp = float(t.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, t)

    assert enemy.has_status(StatusKind.SILENCE), "S3 must apply SILENCE to in-range enemy"
    silence = next(s for s in enemy.statuses if s.kind == StatusKind.SILENCE)
    assert silence.source_tag == _S3_SILENCE_TAG


# ---------------------------------------------------------------------------
# Test 7: S3 does NOT hit out-of-range enemies
# ---------------------------------------------------------------------------

def test_s3_no_damage_out_of_range():
    """S3 must not affect enemies outside the attack range."""
    w = _world()
    t = make_texas_alter()
    t.deployed = True; t.position = (0.0, 1.0)
    w.add_unit(t)

    far_enemy = _slug(pos=(4, 1), hp=99999)  # well outside 2-tile range
    w.add_unit(far_enemy)

    pre_hp = far_enemy.hp
    t.skill.sp = float(t.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, t)

    assert far_enemy.hp == pre_hp, "S3 must not hit out-of-range enemy"
    assert not far_enemy.has_status(StatusKind.SILENCE), "S3 must not silence out-of-range enemy"


# ---------------------------------------------------------------------------
# Test 8: SILENCE expires after _S3_SILENCE_DURATION
# ---------------------------------------------------------------------------

def test_s3_silence_expires():
    """SILENCE applied by S3 must expire after the configured duration."""
    w = _world()
    t = make_texas_alter()
    t.deployed = True; t.position = (0.0, 1.0)
    w.add_unit(t)

    enemy = _slug(pos=(1, 1), hp=99999)
    w.add_unit(enemy)

    t.skill.sp = float(t.skill.sp_cost)
    from core.systems.skill_system import manual_trigger
    manual_trigger(w, t)

    assert enemy.has_status(StatusKind.SILENCE), "SILENCE must be applied initially"

    # Tick past the silence duration
    for _ in range(int(TICK_RATE * (_S3_SILENCE_DURATION + 1))):
        w.tick()

    assert not enemy.has_status(StatusKind.SILENCE), "SILENCE must expire after duration"
