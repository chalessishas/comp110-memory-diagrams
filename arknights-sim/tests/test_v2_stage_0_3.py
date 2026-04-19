"""main_0-3 Sky and Ground — mixed aerial + ground enemy stage tests."""
from __future__ import annotations
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from stages.loader import load_stage, build_world, load_and_build
from data.characters import make_silverash, make_liskarm
from core.types import TileType, TICK_RATE, Mobility


STAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "stages", "main_0-3.yaml")


def test_load_mixed_stage():
    """Stage parses with 2 waves: one ground slug wave, one aerial drone wave."""
    stage = load_stage(STAGE_PATH)
    assert stage.id == "main_0-3"
    assert len(stage.waves) == 2
    slugs, drones = stage.waves
    assert slugs.enemy_id == "originium_slug"
    assert drones.enemy_id == "originium_drone"
    assert drones.first_delay == 2.0


def test_mixed_stage_schedules_6_spawns():
    stage = load_stage(STAGE_PATH)
    world = build_world(stage)
    assert len(world.event_queue) == 6


def test_aerial_enemies_bypass_ground_block():
    """Deployed ground operator must NOT block aerial drones."""
    _, world = load_and_build(STAGE_PATH)

    lk = make_liskarm()
    lk.deployed = True
    lk.position = (2.0, 1.0)
    lk.block = 3               # wide block — would stop all ground enemies
    world.add_unit(lk)

    # Run 5 seconds — t=2.0 first drone spawns, moves 5×1.5=7.5 tiles in 5s
    for _ in range(TICK_RATE * 5):
        world.tick()

    drones = [e for e in world.enemies() if e.mobility == Mobility.AIRBORNE]
    for d in drones:
        # Drone should NOT be in blocked_by_unit_ids (aerial bypass)
        assert not d.blocked_by_unit_ids, (
            f"Aerial drone must not be blocked: blocked_by={d.blocked_by_unit_ids}"
        )


def test_ground_enemies_are_still_blocked():
    """Ground slugs must be blocked normally even when drones are present."""
    _, world = load_and_build(STAGE_PATH)

    lk = make_liskarm()
    lk.deployed = True
    lk.position = (2.0, 1.0)
    lk.block = 3
    world.add_unit(lk)

    # Run 3 ticks — first slug spawns at t=0 and moves toward Liskarm
    for _ in range(TICK_RATE * 2):
        world.tick()

    slugs = [e for e in world.enemies() if e.mobility != Mobility.AIRBORNE]
    blocked = [e for e in slugs if e.blocked_by_unit_ids]
    assert len(blocked) >= 1, "At least one ground slug should be blocked"


def test_stage_clears_with_two_operators():
    """SilverAsh + Liskarm should clear all 6 enemies (3 slugs + 3 drones)."""
    _, world = load_and_build(STAGE_PATH)

    # SilverAsh handles both slugs and drones via ranged attacks
    sa = make_silverash()
    sa.deployed = True
    sa.position = (2.0, 1.0)
    world.add_unit(sa)

    # Liskarm provides block for slugs + backup damage
    lk = make_liskarm()
    lk.deployed = True
    lk.position = (4.0, 1.0)
    world.add_unit(lk)

    result = world.run(max_seconds=180.0)
    assert result == "win", f"expected win, got {result!r}, lives={world.global_state.lives}"
    assert world.global_state.enemies_defeated == 6, (
        f"expected 6 defeated, got {world.global_state.enemies_defeated}"
    )
