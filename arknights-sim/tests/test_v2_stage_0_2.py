"""main_0-2 Crossroads — two-lane branching stage tests."""
from __future__ import annotations
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from stages.loader import load_stage, build_world, load_and_build
from data.characters import make_silverash, make_liskarm
from core.types import TileType, TICK_RATE


STAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "stages", "main_0-2.yaml")


def test_load_two_lane_stage():
    """Stage parses correctly with two wave entries."""
    stage = load_stage(STAGE_PATH)
    assert stage.id == "main_0-2"
    assert stage.name == "Crossroads"
    assert stage.max_lives == 3
    assert len(stage.waves) == 2, "must have top-lane wave and bottom-lane wave"
    top, bot = stage.waves
    assert top.enemy_id == "originium_slug"
    assert bot.enemy_id == "originium_slug"
    assert top.count == 3 and bot.count == 3
    assert top.first_delay == 0.0
    assert bot.first_delay == 2.0


def test_two_lane_paths_are_distinct():
    """Top-lane and bottom-lane paths diverge from the start."""
    stage = load_stage(STAGE_PATH)
    top_path = stage.waves[0].path
    bot_path = stage.waves[1].path
    # First tile of top lane is y=4; first tile of bottom lane is y=0
    assert top_path[0] == (0, 4), f"top lane starts at wrong tile: {top_path[0]}"
    assert bot_path[0] == (0, 0), f"bottom lane starts at wrong tile: {bot_path[0]}"
    # Both converge at goal tile (8, 2)
    assert top_path[-1] == (8, 2)
    assert bot_path[-1] == (8, 2)


def test_two_lane_schedules_6_spawns():
    """6 enemies (3 per lane) are scheduled in the event queue."""
    stage = load_stage(STAGE_PATH)
    world = build_world(stage)
    assert len(world.event_queue) == 6


def test_two_lane_spawn_timing():
    """Bottom-lane spawns fire 2s after top-lane spawns (first_delay=2.0)."""
    stage = load_stage(STAGE_PATH)
    world = build_world(stage)

    # Drain all 6 events and record their fire times
    events = list(world.event_queue.drain_due(float("inf")))
    fire_times = sorted(e.fire_at for e in events)

    # Top lane: 0, 4, 8  —  Bottom lane: 2, 6, 10
    expected = sorted([0.0, 4.0, 8.0, 2.0, 6.0, 10.0])
    assert fire_times == expected, f"expected {expected}, got {fire_times}"


def test_two_lane_enemies_use_different_paths():
    """Enemies spawned from top lane should travel at y=4; bottom lane at y=0."""
    _, world = load_and_build(STAGE_PATH)

    # Run 1 second — first top-lane slug spawns at t=0 and starts moving
    for _ in range(TICK_RATE):
        world.tick()

    enemies = world.enemies()
    # After 1s, the t=0 top-lane slug has entered and moved along y=4
    top_slugs = [e for e in enemies if e.position is not None and round(e.position[1]) == 4]
    assert len(top_slugs) >= 1, "expected at least 1 slug on top lane (y=4)"


def test_two_lane_goal_tile_exists():
    """Goal tile at (8,2) is correctly placed in the world grid."""
    stage = load_stage(STAGE_PATH)
    world = build_world(stage)
    goal = world.tile_grid.get(8, 2)
    assert goal is not None
    assert goal.type == TileType.GOAL


def test_two_lane_clears_with_operators():
    """Both lanes cleared by operators at convergence point + top lane."""
    _, world = load_and_build(STAGE_PATH)

    # SilverAsh at convergence (4,2) — blocks slugs from both lanes as they merge
    sa = make_silverash()
    sa.deployed = True
    sa.position = (4.0, 2.0)
    sa.block = 2           # give him extra block for this test
    world.add_unit(sa)

    # Liskarm on top lane approach
    lk = make_liskarm()
    lk.deployed = True
    lk.position = (2.0, 4.0)
    world.add_unit(lk)

    result = world.run(max_seconds=180.0)
    assert result == "win", f"expected win but got {result!r}, lives={world.global_state.lives}"
    assert world.global_state.enemies_defeated == 6
