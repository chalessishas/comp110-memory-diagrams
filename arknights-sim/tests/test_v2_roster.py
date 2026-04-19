"""Bulk smoke: every generated + curated operator constructs without error."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from core.state.unit_state import UnitState
from core.types import Faction, Profession
from data.characters.registry import list_operators, get_operator, operator_count


def test_registry_has_hundreds_of_operators():
    """M2 target: ≥ 300 playable operators after akgd bulk ingest."""
    count = operator_count()
    assert count >= 300, f"expected ≥300 operators, got {count}"


def test_curated_silverash_overrides_generated():
    """Curated silverash.py sets archetype/cost=31 on top of generated stats."""
    # generated handle is 'svrash'; curated handle is 'silverash'
    curated = get_operator("silverash")
    assert curated.name == "SilverAsh"
    assert curated.archetype is not None
    assert curated.cost == 31  # curated override vs akgd base 20


@pytest.mark.parametrize("handle", [
    "svrash",    # SilverAsh (generated)
    "hsguma",    # Hoshiguma
    "nearl2",    # Nearl alter
    "logos",     # Logos (6* caster)
    "texas2",    # Texas alter
])
def test_popular_6star_operators_constructible(handle):
    op = get_operator(handle)
    assert isinstance(op, UnitState)
    assert op.faction == Faction.ALLY
    assert op.max_hp > 0
    assert op.atk > 0
    assert op.atk_interval > 0
    assert op.profession is not None


def test_all_operators_have_positive_stats():
    """Every generated factory must produce a valid UnitState with non-trivial stats."""
    bad: list[tuple[str, str]] = []
    for handle in list_operators():
        try:
            op = get_operator(handle)
            if op.max_hp <= 0 or op.atk < 0 or op.defence < 0:
                bad.append((handle, f"hp={op.max_hp} atk={op.atk} def={op.defence}"))
            if op.atk_interval <= 0:
                bad.append((handle, f"atk_interval={op.atk_interval}"))
        except Exception as e:
            bad.append((handle, f"exception: {e}"))
    assert not bad, f"{len(bad)} operators failed validation: {bad[:5]}..."


def test_profession_coverage():
    """All 8 professions should appear among the roster."""
    profs = set()
    for handle in list_operators():
        op = get_operator(handle)
        if op.profession is not None:
            profs.add(op.profession)
    assert len(profs) == 8, f"Expected all 8 professions, got {profs}"
    expected = {Profession.GUARD, Profession.SNIPER, Profession.CASTER,
                Profession.DEFENDER, Profession.MEDIC, Profession.SUPPORTER,
                Profession.SPECIALIST, Profession.VANGUARD}
    assert profs == expected
