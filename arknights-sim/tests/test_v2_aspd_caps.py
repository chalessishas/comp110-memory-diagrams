"""ASPD hard caps: [20, 600] per wiki. interval = base * 100 / clamped_aspd."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.state.unit_state import UnitState, Buff
from core.types import BuffAxis, BuffStack, Faction


def _unit(atk_interval: float = 1.0) -> UnitState:
    u = UnitState(name="test", faction=Faction.ALLY, atk_interval=atk_interval)
    return u


def test_aspd_floor_clamps_at_20():
    """Extreme -ASPD buff cannot push effective ASPD below 20."""
    u = _unit(atk_interval=1.0)
    # Base ASPD=100, subtract 200 → would be -100 without cap
    u.buffs.append(Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT, value=-200.0, source_tag="debuff"))
    # clamped to 20 → interval = 1.0 * 100/20 = 5.0s
    assert abs(u.current_atk_interval - 5.0) < 1e-9, \
        f"Expected 5.0s (ASPD floor=20), got {u.current_atk_interval}"


def test_aspd_ceiling_clamps_at_600():
    """Extreme +ASPD buff cannot push effective ASPD above 600."""
    u = _unit(atk_interval=1.0)
    # Base ASPD=100, add 1000 → would be 1100 without cap
    u.buffs.append(Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT, value=1000.0, source_tag="buff"))
    # clamped to 600 → interval = 1.0 * 100/600 ≈ 0.1667s
    expected = 1.0 * 100.0 / 600.0
    assert abs(u.current_atk_interval - expected) < 1e-9, \
        f"Expected {expected:.4f}s (ASPD cap=600), got {u.current_atk_interval}"


def test_normal_aspd_unaffected_by_caps():
    """ASPD within [20, 600] passes through unchanged."""
    u = _unit(atk_interval=1.0)
    u.buffs.append(Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT, value=100.0, source_tag="buff"))
    # effective_aspd = 200, no clamping → interval = 0.5s
    assert abs(u.current_atk_interval - 0.5) < 1e-9, \
        f"Expected 0.5s interval with +100 ASPD, got {u.current_atk_interval}"
