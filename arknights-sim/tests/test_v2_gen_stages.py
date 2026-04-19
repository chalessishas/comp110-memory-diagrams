"""Smoke tests for gen_stages.py output — verifies main_00 YAML loads and runs."""
from __future__ import annotations
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from stages.loader import load_stage, load_and_build
from core.types import TICK_RATE, TileType

STAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "stages")


def _stage_path(name: str) -> str:
    return os.path.join(STAGE_DIR, f"{name}.yaml")


# --------------------------------------------------------------------------
# main_00-01 — simplest stage
# --------------------------------------------------------------------------

def test_main_00_01_loads():
    """main_00-01 parses with correct structure."""
    s = load_stage(_stage_path("main_00-01"))
    assert s.id == "main_00-01"
    assert s.width == 9 and s.height == 6
    assert len(s.waves) > 0
    assert len(s.tiles) > 0


def test_main_00_01_has_goal_tile():
    """main_00-01 contains exactly one goal tile."""
    s = load_stage(_stage_path("main_00-01"))
    goals = [(x, y) for x, y, t in s.tiles if t == TileType.GOAL]
    assert len(goals) == 1, f"Expected 1 goal tile, got {goals}"


def test_main_00_01_path_ends_at_goal():
    """Every wave's path ends at the goal tile."""
    s = load_stage(_stage_path("main_00-01"))
    goal = next((x, y) for x, y, t in s.tiles if t == TileType.GOAL)
    for w in s.waves:
        assert w.path[-1] == goal, (
            f"Wave {w.enemy_id} path ends at {w.path[-1]}, expected goal {goal}"
        )


def test_main_00_01_first_spawn():
    """First enemy spawns around t=5s (first_delay from level data)."""
    _stage, world = load_and_build(_stage_path("main_00-01"))
    first_spawn_time = None
    for _ in range(TICK_RATE * 8):
        world.tick()
        if world.units and first_spawn_time is None:
            first_spawn_time = world.global_state.elapsed
            break
    assert first_spawn_time is not None, "No enemy spawned in 8s"
    assert 4.5 <= first_spawn_time <= 6.0, f"First spawn at unexpected time {first_spawn_time}"


def test_main_00_01_enemies_are_known():
    """All enemy IDs in generated YAML are in the registry."""
    from data.enemies.registry import has_enemy
    s = load_stage(_stage_path("main_00-01"))
    for w in s.waves:
        assert has_enemy(w.enemy_id), f"Unknown enemy: {w.enemy_id!r}"


# --------------------------------------------------------------------------
# All generated main_00 stages load without error
# --------------------------------------------------------------------------

@pytest.mark.parametrize("stage_id", [
    f"main_00-{n:02d}" for n in range(1, 12)
])
def test_all_main_00_stages_load(stage_id: str):
    """Every generated main_00 stage parses without error."""
    path = _stage_path(stage_id)
    if not os.path.exists(path):
        pytest.skip(f"{stage_id}.yaml not generated yet")
    s = load_stage(path)
    assert s.id == stage_id
    assert s.width > 0 and s.height > 0
    assert len(s.waves) > 0
    # Verify all paths are non-trivial
    for w in s.waves:
        assert len(w.path) >= 2, f"{stage_id} wave {w.enemy_id} has degenerate path"
