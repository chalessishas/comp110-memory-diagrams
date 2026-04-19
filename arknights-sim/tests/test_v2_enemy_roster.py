"""Enemy registry bulk smoke: every akgd-generated enemy factory constructs."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from core.state.unit_state import UnitState
from core.types import Faction, Mobility
from data.enemies.registry import list_enemies, get_enemy, enemy_count


def test_enemy_registry_has_1500_plus():
    """M3a target: akgd enemy_database covers 1500+ enemy types."""
    assert enemy_count() >= 1500, f"expected ≥1500, got {enemy_count()}"


@pytest.mark.parametrize("handle", [
    "slime",       # Originium Slug Lv0
    "trslim",      # 简饲源石虫
    "drone",       # curated drone
])
def test_popular_enemies_constructible(handle):
    e = get_enemy(handle)
    assert isinstance(e, UnitState)
    assert e.faction == Faction.ENEMY
    assert e.max_hp > 0


def test_all_enemies_have_positive_hp():
    bad = []
    for h in list_enemies():
        try:
            e = get_enemy(h)
            if e.max_hp <= 0:
                bad.append((h, f"hp={e.max_hp}"))
        except Exception as ex:
            bad.append((h, f"ex: {ex}"))
    assert not bad, f"{len(bad)} enemies failed: {bad[:5]}..."


def test_mobility_split():
    """Verify both ground and airborne enemies exist."""
    ground = airborne = 0
    for h in list_enemies():
        try:
            e = get_enemy(h)
            if e.mobility == Mobility.GROUND:
                ground += 1
            elif e.mobility == Mobility.AIRBORNE:
                airborne += 1
        except Exception:
            pass
    assert ground > 1000, f"expected >1000 ground, got {ground}"
    assert airborne > 100, f"expected >100 airborne, got {airborne}"
