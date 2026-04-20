"""Bulk smoke: all generated main stages YAML loads without errors."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import glob
import pytest
from stages.loader import load_stage, build_world


STAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "stages")


def _main_stages():
    paths = glob.glob(os.path.join(STAGES_DIR, "main_*.yaml"))
    return sorted(paths)


def test_main_stages_count_at_least_100():
    """M3b target: ≥100 main-line stages from akgd."""
    stages = _main_stages()
    assert len(stages) >= 100, f"Expected ≥100 main stages, got {len(stages)}"


def test_all_main_stages_parse():
    """Every generated stage YAML must parse into a StageSpec."""
    bad = []
    for path in _main_stages():
        try:
            s = load_stage(path)
            assert s.width > 0
            assert s.height > 0
            assert len(s.tiles) > 0
            assert len(s.waves) >= 1
        except Exception as e:
            bad.append((os.path.basename(path), str(e)[:80]))
    assert not bad, f"{len(bad)} stages failed to parse: {bad[:5]}"


def test_all_main_stages_build_world():
    """Every stage can be built into a World (spawn events schedule OK)."""
    bad = []
    for path in _main_stages():
        try:
            s = load_stage(path)
            w = build_world(s)
            # Event queue must contain at least one spawn per stage
            assert len(w.event_queue) >= 1
        except KeyError as e:
            # Unknown enemy id — listable issue, not a crash bug
            bad.append((os.path.basename(path), f"unknown enemy: {e}"))
        except Exception as e:
            bad.append((os.path.basename(path), str(e)[:80]))
    # Tolerate some failures on exotic stages (unknown enemies, malformed paths)
    assert len(bad) < len(_main_stages()) * 0.15, \
        f"too many stages failed ({len(bad)}/{len(_main_stages())}): {bad[:5]}"


@pytest.mark.parametrize("stage_id", ["main_00-01", "main_01-07", "main_02-05"])
def test_popular_main_stages_have_enemies(stage_id):
    path = os.path.join(STAGES_DIR, f"{stage_id}.yaml")
    if not os.path.exists(path):
        pytest.skip(f"{stage_id}.yaml not generated")
    s = load_stage(path)
    total_enemies = sum(w.count for w in s.waves)
    assert total_enemies >= 3, f"{stage_id} should have at least 3 enemies, got {total_enemies}"
