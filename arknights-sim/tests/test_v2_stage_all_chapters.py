"""Structural and smoke-simulation tests across all main-line chapters (01–13).

Structural checks (goal_tile, valid_paths) are cheap — they only parse YAML and
build the World without running a simulation. Sample strategy: first 3 stages of
each chapter → 39 parameterized cases.

Simulation smoke tests run world.run() on the first stage of each chapter (13
cases) and assert only that the engine terminates without raising an exception.
win/loss depends on operator placement and is not asserted here — the purpose is
regression-catching, not clearance validation.
"""
from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from stages.loader import load_and_build
from core.types import TileType
from data.characters import make_silverash, make_liskarm

STAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "stages")


def _path(stage_id: str) -> str:
    return os.path.join(STAGE_DIR, f"{stage_id}.yaml")


def _place(world, unit, pos):
    unit.deployed = True
    unit.position = pos
    world.add_unit(unit)


# ---------------------------------------------------------------------------
# Sample: first 3 stages of each chapter (39 stages total)
# ---------------------------------------------------------------------------

_SAMPLE_STAGES = [
    stage_id
    for ch in range(1, 14)
    for n in range(1, 4)
    for stage_id in [f"main_{ch:02d}-{n:02d}"]
    if os.path.exists(_path(f"main_{ch:02d}-{n:02d}"))
]


@pytest.mark.parametrize("stage_id", _SAMPLE_STAGES)
def test_sample_stages_have_goal_tile(stage_id):
    """Each sampled stage must have at least one GOAL tile."""
    stage, _ = load_and_build(_path(stage_id))
    goal_tiles = [t for t in stage.tiles if t[2] == TileType.GOAL]
    assert len(goal_tiles) >= 1, f"{stage_id}: no GOAL tile found"


@pytest.mark.parametrize("stage_id", _SAMPLE_STAGES)
def test_sample_stages_have_valid_wave_paths(stage_id):
    """Every wave path must have at least 2 tiles (start → goal minimum)."""
    stage, _ = load_and_build(_path(stage_id))
    for wave in stage.waves:
        assert len(wave.path) >= 2, (
            f"{stage_id}: wave for '{wave.enemy_id}' has path length {len(wave.path)}"
        )


@pytest.mark.parametrize("stage_id", _SAMPLE_STAGES)
def test_sample_stages_have_positive_wave_counts(stage_id):
    """Every wave should spawn at least 1 enemy."""
    stage, _ = load_and_build(_path(stage_id))
    for wave in stage.waves:
        assert wave.count >= 1, (
            f"{stage_id}: wave for '{wave.enemy_id}' has count={wave.count}"
        )


# ---------------------------------------------------------------------------
# Simulation smoke tests: first stage of each chapter (engine must not crash)
# ---------------------------------------------------------------------------

_SMOKE_STAGES = [
    stage_id
    for ch in range(1, 14)
    for stage_id in [f"main_{ch:02d}-01"]
    if os.path.exists(_path(f"main_{ch:02d}-01"))
]


@pytest.mark.parametrize("stage_id", _SMOKE_STAGES)
def test_chapter_first_stage_simulates_without_crash(stage_id):
    """world.run() must complete without raising exceptions on any ch-01 stage.

    Two operators placed at estimated chokepoints; win/loss not asserted since
    operator placement is not tuned per stage.
    """
    _, world = load_and_build(_path(stage_id))
    sa = make_silverash()
    lk = make_liskarm()
    _place(world, sa, (3.0, 3.0))
    _place(world, lk, (5.0, 3.0))

    result = world.run(max_seconds=180.0)
    assert result in ("win", "loss"), (
        f"{stage_id}: world.run() returned unexpected value {result!r}"
    )


# ---------------------------------------------------------------------------
# Aggregate sanity: total wave count across all chapter-01 stages
# ---------------------------------------------------------------------------

def test_all_chapter01_stages_have_at_least_one_wave():
    """Every first-stage in each chapter must define at least one wave."""
    for stage_id in _SMOKE_STAGES:
        stage, _ = load_and_build(_path(stage_id))
        assert len(stage.waves) >= 1, f"{stage_id}: no waves defined"
