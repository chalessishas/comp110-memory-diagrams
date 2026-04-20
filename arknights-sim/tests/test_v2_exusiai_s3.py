"""Exusiai S3 Light-Speed Strike — ATK+70%, ASPD+20, ATK_INTERVAL -0.40s.

Tests cover:
  - S3 applies ATK +70% ratio buff
  - S3 applies ASPD +20 flat buff
  - S3 applies ATK_INTERVAL -0.40s flat buff
  - Combined formula: interval = max(0.067, (base - 0.4) * 100/(100+20))
  - With base=1.0: (0.6) * 100/120 ≈ 0.500s
  - Extreme ASPD + flat offset stays above 0.067s floor
  - All three buffs cleared on S3 end
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.world import World
from core.state.tile_state import TileGrid, TileState
from core.types import TileType, TICK_RATE, BuffAxis
from core.systems import register_default_systems
from core.systems.skill_system import manual_trigger
from data.characters.exusiai import (
    make_exusiai,
    _S3_ATK_RATIO, _S3_ASPD_BONUS, _S3_INTERVAL_OFFSET, _S3_DURATION,
    _S3_ATK_BUFF_TAG, _S3_ASPD_BUFF_TAG, _S3_INTERVAL_BUFF_TAG,
)
from data.enemies import make_originium_slug


def _world() -> World:
    grid = TileGrid(width=6, height=3)
    for x in range(6):
        for y in range(3):
            grid.set_tile(TileState(x=x, y=y, type=TileType.GROUND))
    w = World(tile_grid=grid)
    w.global_state.dp_gain_rate = 0.0
    register_default_systems(w)
    return w


# ---------------------------------------------------------------------------
# Test 1: S3 applies ATK +70% buff
# ---------------------------------------------------------------------------

def test_s3_atk_buff():
    """S3 must apply ATK +70% ratio buff to Exusiai."""
    w = _world()
    exa = make_exusiai(slot="S3")
    exa.deployed = True; exa.position = (0.0, 1.0); exa.atk_cd = 999.0
    w.add_unit(exa)

    slug = make_originium_slug(path=[(1, 1)] * 5)
    slug.deployed = True; slug.position = (1.0, 1.0)
    w.add_unit(slug)

    base_atk = exa.effective_atk
    exa.skill.sp = float(exa.skill.sp_cost)
    manual_trigger(w, exa)

    assert exa.skill.active_remaining > 0.0, "S3 must be active"
    expected_atk = int(base_atk * (1.0 + _S3_ATK_RATIO))
    assert abs(exa.effective_atk - expected_atk) <= 1, (
        f"S3 ATK must be ×{1 + _S3_ATK_RATIO}; expected={expected_atk}, got={exa.effective_atk}"
    )


# ---------------------------------------------------------------------------
# Test 2: S3 applies ASPD +20 flat buff
# ---------------------------------------------------------------------------

def test_s3_aspd_buff():
    """S3 must apply ASPD +20 flat buff to Exusiai."""
    w = _world()
    exa = make_exusiai(slot="S3")
    exa.deployed = True; exa.position = (0.0, 1.0); exa.atk_cd = 999.0
    w.add_unit(exa)

    slug = make_originium_slug(path=[(1, 1)] * 5)
    slug.deployed = True; slug.position = (1.0, 1.0)
    w.add_unit(slug)

    exa.skill.sp = float(exa.skill.sp_cost)
    manual_trigger(w, exa)

    aspd_buffs = [b for b in exa.buffs if b.source_tag == _S3_ASPD_BUFF_TAG]
    assert len(aspd_buffs) == 1, "S3 must apply exactly one ASPD buff"
    assert abs(aspd_buffs[0].value - _S3_ASPD_BONUS) < 0.01, (
        f"S3 ASPD buff must be +{_S3_ASPD_BONUS}, got {aspd_buffs[0].value}"
    )


# ---------------------------------------------------------------------------
# Test 3: S3 applies ATK_INTERVAL -0.40s flat buff
# ---------------------------------------------------------------------------

def test_s3_interval_buff():
    """S3 must apply ATK_INTERVAL -0.40s flat buff to Exusiai."""
    w = _world()
    exa = make_exusiai(slot="S3")
    exa.deployed = True; exa.position = (0.0, 1.0); exa.atk_cd = 999.0
    w.add_unit(exa)

    slug = make_originium_slug(path=[(1, 1)] * 5)
    slug.deployed = True; slug.position = (1.0, 1.0)
    w.add_unit(slug)

    exa.skill.sp = float(exa.skill.sp_cost)
    manual_trigger(w, exa)

    interval_buffs = [b for b in exa.buffs if b.source_tag == _S3_INTERVAL_BUFF_TAG]
    assert len(interval_buffs) == 1, "S3 must apply exactly one ATK_INTERVAL buff"
    assert abs(interval_buffs[0].value - _S3_INTERVAL_OFFSET) < 0.01, (
        f"S3 ATK_INTERVAL buff must be {_S3_INTERVAL_OFFSET}, got {interval_buffs[0].value}"
    )


# ---------------------------------------------------------------------------
# Test 4: Combined formula — interval ≈ 0.500s
# ---------------------------------------------------------------------------

def test_s3_combined_interval_formula():
    """S3 combined effect: max(0.067, (1.0 - 0.40) * 100 / (100 + 20)) ≈ 0.500s."""
    exa = make_exusiai(slot="S3")
    base = exa.atk_interval  # 1.0s

    # Manually apply S3 buffs for formula verification (no world needed)
    from core.state.unit_state import Buff
    from core.types import BuffStack
    exa.buffs.extend([
        Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
             value=_S3_ASPD_BONUS, source_tag=_S3_ASPD_BUFF_TAG),
        Buff(axis=BuffAxis.ATK_INTERVAL, stack=BuffStack.FLAT,
             value=_S3_INTERVAL_OFFSET, source_tag=_S3_INTERVAL_BUFF_TAG),
    ])

    # Formula: (base + flat_offset) * 100 / effective_aspd
    # = (1.0 + (-0.40)) * 100 / (100 + 20) = 0.6 * 100/120 ≈ 0.5000s
    expected = max(0.067, (base + _S3_INTERVAL_OFFSET) * 100.0 / (100.0 + _S3_ASPD_BONUS))
    actual = exa.current_atk_interval
    assert abs(actual - expected) < 1e-9, (
        f"S3 interval must be ≈{expected:.4f}s; got {actual:.4f}s"
    )
    assert abs(actual - 0.5) < 1e-9, (
        f"With base=1.0, -0.4 flat, +20 ASPD: expected 0.500s; got {actual:.4f}s"
    )


# ---------------------------------------------------------------------------
# Test 5: Extreme ASPD + large flat offset stays above 0.067s floor
# ---------------------------------------------------------------------------

def test_s3_interval_floor_respected():
    """Even with extreme ASPD (S2 +100) stacked with S3's -0.4s flat offset,
    interval must not drop below 0.067s (15 attacks/second minimum)."""
    exa = make_exusiai(slot="S3")
    base = exa.atk_interval  # 1.0s

    from core.state.unit_state import Buff
    from core.types import BuffStack

    # Stack S2 (+100 ASPD) + S3 (+20 ASPD, -0.4s flat)
    exa.buffs.extend([
        Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT, value=100.0, source_tag="s2"),
        Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
             value=_S3_ASPD_BONUS, source_tag=_S3_ASPD_BUFF_TAG),
        Buff(axis=BuffAxis.ATK_INTERVAL, stack=BuffStack.FLAT,
             value=_S3_INTERVAL_OFFSET, source_tag=_S3_INTERVAL_BUFF_TAG),
    ])

    # effective_aspd = min(600, 100 + 100 + 20) = 220
    # interval = (1.0 - 0.4) * 100 / 220 ≈ 0.273s — well above floor
    actual = exa.current_atk_interval
    assert actual >= 0.067, (
        f"Interval must respect 0.067s floor; got {actual:.4f}s"
    )
    expected = max(0.067, (base + _S3_INTERVAL_OFFSET) * 100.0 / min(600.0, 100.0 + 100.0 + 20.0))
    assert abs(actual - expected) < 1e-9, (
        f"Stacked ASPD interval: expected {expected:.4f}s, got {actual:.4f}s"
    )


# ---------------------------------------------------------------------------
# Test 6: All S3 buffs cleared on end
# ---------------------------------------------------------------------------

def test_s3_buffs_cleared_on_end():
    """After S3 ends, all three S3 buffs must be removed from Exusiai."""
    w = _world()
    exa = make_exusiai(slot="S3")
    exa.deployed = True; exa.position = (0.0, 1.0); exa.atk_cd = 999.0
    w.add_unit(exa)

    slug = make_originium_slug(path=[(1, 1)] * 5)
    slug.deployed = True; slug.position = (1.0, 1.0)
    w.add_unit(slug)

    exa.skill.sp = float(exa.skill.sp_cost)
    manual_trigger(w, exa)
    assert exa.skill.active_remaining > 0.0, "S3 must be active"

    for _ in range(int(TICK_RATE * (_S3_DURATION + 1))):
        w.tick()

    assert exa.skill.active_remaining == 0.0, "S3 must have ended"
    s3_tags = {_S3_ATK_BUFF_TAG, _S3_ASPD_BUFF_TAG, _S3_INTERVAL_BUFF_TAG}
    remaining = [b for b in exa.buffs if b.source_tag in s3_tags]
    assert len(remaining) == 0, (
        f"All S3 buffs must be cleared on end; remaining: {[b.source_tag for b in remaining]}"
    )
    # Interval must return to base
    assert abs(exa.current_atk_interval - exa.atk_interval) < 1e-9, (
        f"Interval must return to base {exa.atk_interval}s after S3; got {exa.current_atk_interval}"
    )
