"""End-to-end clearance tests for gen_stages-produced main_00 stages.

These stages were generated from ArknightsGameData JSONs and validate that
real-game wave data is playable through our ECS simulation.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from stages.loader import load_and_build
from data.characters import make_silverash, make_liskarm

STAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "stages")


def _stage_path(name: str) -> str:
    return os.path.join(STAGE_DIR, f"{name}.yaml")


def _place(world, unit, pos):
    """Add an operator directly (bypass DP cost for test simplicity)."""
    unit.deployed = True
    unit.position = pos
    world.add_unit(unit)


def test_main_00_01_clears_with_silverash_liskarm():
    """main_00-01: SilverAsh at chokepoint (3,3), Liskarm at (1,2)."""
    _, world = load_and_build(_stage_path("main_00-01"))

    sa = make_silverash()
    lk = make_liskarm()
    _place(world, sa, (3.0, 3.0))   # path choke: [8,2]→(3,3)→[3,2]→...
    _place(world, lk, (1.0, 2.0))   # second line: ...(3,2)→(1,2)→[1,3]→goal

    result = world.run(max_seconds=180.0)
    assert result == "win", (
        f"stage should clear; lives={world.global_state.lives}, "
        f"defeated={world.global_state.enemies_defeated}"
    )
    assert world.global_state.lives == 3, "no leaks expected with two operators on path"


def test_main_00_01_lives_lost_without_operators():
    """main_00-01 leaks all enemies to the goal when no operators are placed."""
    _, world = load_and_build(_stage_path("main_00-01"))
    # No operators — all enemies leak through
    result = world.run(max_seconds=180.0)
    assert result == "loss", f"expected loss without operators, got {result!r}"


def test_main_00_01_enemy_count():
    """main_00-01 has the correct total number of spawn events."""
    stage, world = load_and_build(_stage_path("main_00-01"))
    total_spawns = sum(w.count for w in stage.waves)
    assert total_spawns == len(world.event_queue), (
        f"expected {total_spawns} spawn events, got {len(world.event_queue)}"
    )


def test_main_00_01_starting_dp():
    """main_00-01 starting DP matches stage spec."""
    stage, world = load_and_build(_stage_path("main_00-01"))
    assert world.global_state.dp == stage.starting_dp


@pytest.mark.parametrize("stage_id", [
    "main_00-02", "main_00-03", "main_00-04", "main_00-05",
    "main_00-06", "main_00-07", "main_00-08", "main_00-09",
    "main_00-10", "main_00-11",
])
def test_generated_stages_have_goal_tile(stage_id):
    """Every generated stage must have at least one GOAL tile."""
    from core.types import TileType
    stage, world = load_and_build(_stage_path(stage_id))
    goal_tiles = [
        t for t in stage.tiles if t[2] == TileType.GOAL
    ]
    assert len(goal_tiles) >= 1, f"{stage_id} has no goal tile"


@pytest.mark.parametrize("stage_id", [
    "main_00-02", "main_00-03", "main_00-04", "main_00-05",
    "main_00-06", "main_00-07", "main_00-08", "main_00-09",
    "main_00-10", "main_00-11",
])
def test_generated_stages_have_valid_paths(stage_id):
    """Every wave in every generated stage must have a path with >= 2 tiles."""
    stage, _ = load_and_build(_stage_path(stage_id))
    for wave in stage.waves:
        assert len(wave.path) >= 2, (
            f"{stage_id} wave {wave.enemy_id} has path length {len(wave.path)}"
        )
