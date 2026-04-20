"""BuffAxis.ATK_INTERVAL — flat-second offset on attack interval.

Validates the computation path in UnitState.current_atk_interval:
    base = atk_interval * 100 / effective_aspd
    result = max(0.067, base + flat_ATK_INTERVAL_offset)

ATK_INTERVAL is a flat seconds modifier applied *after* ASPD scaling,
unlike ASPD which is a multiplier on the base interval.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.state.unit_state import UnitState, Buff, RangeShape
from core.types import BuffAxis, BuffStack, Faction, AttackType
from data.characters.silverash import make_silverash
from data.characters.exusiai import make_exusiai


def _sa() -> UnitState:
    """SilverAsh E2 max — atk_interval=1.3, effective_aspd=100."""
    return make_silverash()


# ---------------------------------------------------------------------------
# Test 1: No ATK_INTERVAL buff — interval matches ASPD formula baseline
# ---------------------------------------------------------------------------

def test_no_interval_buff_baseline():
    """Without ATK_INTERVAL buff, current_atk_interval = atk_interval * 100 / aspd."""
    sa = _sa()
    expected = sa.atk_interval * 100.0 / sa.effective_aspd
    assert abs(sa.current_atk_interval - expected) < 1e-9, (
        f"Baseline interval should be {expected:.4f}s, got {sa.current_atk_interval:.4f}s"
    )


# ---------------------------------------------------------------------------
# Test 2: Negative offset reduces interval (faster attacks)
# ---------------------------------------------------------------------------

def test_negative_offset_reduces_interval():
    """ATK_INTERVAL buff with value=-0.3 reduces interval by 0.3s."""
    sa = _sa()
    base = sa.current_atk_interval   # 1.3s
    sa.buffs.append(Buff(
        axis=BuffAxis.ATK_INTERVAL, stack=BuffStack.FLAT,
        value=-0.3, source_tag="test_fast",
    ))
    expected = base - 0.3
    assert abs(sa.current_atk_interval - expected) < 1e-9, (
        f"With -0.3s offset, interval should be {expected:.4f}s, got {sa.current_atk_interval:.4f}s"
    )


# ---------------------------------------------------------------------------
# Test 3: Positive offset increases interval (slower attacks)
# ---------------------------------------------------------------------------

def test_positive_offset_increases_interval():
    """ATK_INTERVAL buff with value=+0.5 increases interval by 0.5s."""
    sa = _sa()
    base = sa.current_atk_interval
    sa.buffs.append(Buff(
        axis=BuffAxis.ATK_INTERVAL, stack=BuffStack.FLAT,
        value=0.5, source_tag="test_slow",
    ))
    expected = base + 0.5
    assert abs(sa.current_atk_interval - expected) < 1e-9, (
        f"With +0.5s offset, interval should be {expected:.4f}s, got {sa.current_atk_interval:.4f}s"
    )


# ---------------------------------------------------------------------------
# Test 4: Floor at 0.067s (1/15s ≈ 1 frame at 15 fps) is enforced
# ---------------------------------------------------------------------------

def test_floor_0067_enforced():
    """A huge negative offset cannot push interval below 0.067s."""
    sa = _sa()
    sa.buffs.append(Buff(
        axis=BuffAxis.ATK_INTERVAL, stack=BuffStack.FLAT,
        value=-999.0, source_tag="test_floor",
    ))
    assert sa.current_atk_interval == pytest.approx(0.067, abs=1e-9), (
        f"Floor must be 0.067s, got {sa.current_atk_interval:.6f}s"
    )


# ---------------------------------------------------------------------------
# Test 5: Multiple FLAT offsets stack additively
# ---------------------------------------------------------------------------

def test_multiple_flat_offsets_stack_additively():
    """Two ATK_INTERVAL buffs of -0.2 and -0.1 both apply (total -0.3)."""
    sa = _sa()
    base = sa.current_atk_interval
    sa.buffs.append(Buff(
        axis=BuffAxis.ATK_INTERVAL, stack=BuffStack.FLAT,
        value=-0.2, source_tag="test_a",
    ))
    sa.buffs.append(Buff(
        axis=BuffAxis.ATK_INTERVAL, stack=BuffStack.FLAT,
        value=-0.1, source_tag="test_b",
    ))
    expected = base - 0.3
    assert abs(sa.current_atk_interval - expected) < 1e-9, (
        f"Two stacked offsets should sum to {expected:.4f}s, got {sa.current_atk_interval:.4f}s"
    )


# ---------------------------------------------------------------------------
# Test 6: ATK_INTERVAL and ASPD are independent axes — both apply correctly
# ---------------------------------------------------------------------------

def test_interval_offset_applied_before_aspd_scaling():
    """Wiki formula: offset is added to base interval, THEN ASPD-scaled.

    With base=1.3s, ATK_INTERVAL -0.2 → modified_base=1.1s.
    Then +100 ASPD (total=200) → 1.1 * 100/200 = 0.55s.
    This is the correct wiki formula: (base + offset) * 100 / aspd.
    NOT: (base * 100/aspd) + offset (post-scaling, which would give 0.45s).
    """
    sa = _sa()
    sa.buffs.append(Buff(
        axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
        value=100.0, source_tag="test_aspd",
    ))
    sa.buffs.append(Buff(
        axis=BuffAxis.ATK_INTERVAL, stack=BuffStack.FLAT,
        value=-0.2, source_tag="test_offset",
    ))
    # wiki formula: (1.3 + (-0.2)) * 100 / 200 = 1.1 * 0.5 = 0.55
    expected = (1.3 - 0.2) * 100.0 / 200.0
    assert abs(sa.current_atk_interval - expected) < 1e-9, (
        f"Expected {expected:.3f}s (pre-scale wiki formula), got {sa.current_atk_interval:.4f}s"
    )


# ---------------------------------------------------------------------------
# Test 7: Only FLAT stack mode is applied (RATIO/MULTIPLIER ignored)
# ---------------------------------------------------------------------------

def test_only_flat_stack_type_applied():
    """ATK_INTERVAL buffs with non-FLAT stack type are ignored."""
    sa = _sa()
    base = sa.current_atk_interval
    sa.buffs.append(Buff(
        axis=BuffAxis.ATK_INTERVAL, stack=BuffStack.RATIO,
        value=-0.5, source_tag="test_ratio_ignored",
    ))
    assert abs(sa.current_atk_interval - base) < 1e-9, (
        f"RATIO-stack ATK_INTERVAL must be ignored; interval should remain {base:.4f}s"
    )


import pytest
