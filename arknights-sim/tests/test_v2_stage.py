"""P-stage acceptance — stage YAML loading + wave spawning via EventQueue."""
from __future__ import annotations
import os
import sys
import pytest

# Evict cached v1 stages so the v2 package takes precedence
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
for _k in list(sys.modules.keys()):
    if _k == "stages" or _k.startswith("stages."):
        del sys.modules[_k]

from stages.loader import load_stage, build_world, load_and_build
from data.characters import make_silverash, make_liskarm
from core.types import TileType


STAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "stages", "main_0-1.yaml")


def test_load_stage_parses_yaml():
    stage = load_stage(STAGE_PATH)
    assert stage.id == "main_0-1"
    assert stage.name == "Abandoned Frontline"
    assert stage.width == 8
    assert stage.max_lives == 3
    assert len(stage.tiles) == 8
    # one wave of 5 slugs at 4s interval
    assert len(stage.waves) == 1
    w = stage.waves[0]
    assert w.enemy_id == "originium_slug"
    assert w.count == 5
    assert w.interval == 4.0


def test_build_world_schedules_all_spawns():
    stage = load_stage(STAGE_PATH)
    world = build_world(stage)
    # 5 spawn events pre-tick
    assert len(world.event_queue) == 5
    assert world.global_state.lives == 3


def test_stage_resolves_goal_tile():
    stage = load_stage(STAGE_PATH)
    world = build_world(stage)
    goal = world.tile_grid.get(7, 2)
    assert goal is not None
    assert goal.type == TileType.GOAL


def test_stage_clears_with_silverash_plus_liskarm():
    """End-to-end: main_0-1 cleared by SilverAsh + Liskarm."""
    _, world = load_and_build(STAGE_PATH)

    silverash = make_silverash()
    silverash.deployed = True
    silverash.position = (2.0, 2.0)
    world.add_unit(silverash)

    liskarm = make_liskarm()
    liskarm.deployed = True
    liskarm.position = (4.0, 2.0)
    world.add_unit(liskarm)

    result = world.run(max_seconds=120.0)
    assert result == "win", f"expected win, lives={world.global_state.lives}"
    assert world.global_state.lives == 3
    # 5 slugs should have been defeated
    assert world.global_state.enemies_defeated == 5


def test_stage_spawn_events_drain_on_time():
    """5 slugs should enter the battle between t=0 and t=16s (interval 4 × 4)."""
    _, world = load_and_build(STAGE_PATH)
    silverash = make_silverash()
    silverash.deployed = True
    silverash.position = (2.0, 2.0)
    world.add_unit(silverash)

    # tick forward 17 seconds
    for _ in range(170):
        world.tick()

    # all spawns should have fired
    assert len(world.event_queue) == 0
