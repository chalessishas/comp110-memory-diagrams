"""P6 acceptance: two-stage buff pipeline (ratio additive → multiplier multiplicative)."""
from __future__ import annotations
import pytest
from core.operator import Operator
from core.skill import Skill
from data.operators import make_silverash


def _bare_op(**kwargs) -> Operator:
    defaults = dict(
        name="Test", max_hp=1000, atk=500, defence=100, res=0,
        atk_interval=1.0, block=1, attack_type="physical",
    )
    defaults.update(kwargs)
    return Operator(**defaults)


def test_no_buff_effective_atk_equals_base():
    op = _bare_op(atk=500)
    assert op.effective_atk() == 500


def test_single_ratio_buff():
    op = _bare_op(atk=500)
    op._atk_ratio_buffs.append(0.50)  # +50%
    assert op.effective_atk() == int(500 * 1.50)  # 750


def test_ratio_buffs_stack_additively():
    """Two 50% ratio buffs = 100% total ratio, not 125% (which would be multiplicative)."""
    op = _bare_op(atk=500)
    op._atk_ratio_buffs.append(0.50)
    op._atk_ratio_buffs.append(0.50)
    assert op.effective_atk() == int(500 * 2.00)  # 1000, not int(500*1.5*1.5)=1125


def test_multiplier_applies_after_ratio():
    """Multiplier is applied to the ratio-buffed intermediate, not the raw base."""
    op = _bare_op(atk=500)
    op._atk_ratio_buffs.append(1.00)   # 500 * (1+1.0) = 1000 intermediate
    op._atk_multiplier_buffs.append(1.30)  # 1000 * 1.30 = 1300
    assert op.effective_atk() == 1300


def test_multiplier_only_no_ratio():
    op = _bare_op(atk=500)
    op._atk_multiplier_buffs.append(2.0)
    assert op.effective_atk() == 1000


def test_silverash_s3_effective_atk():
    """SilverAsh S3 (+180% ratio) gives effective_atk = int(atk * 2.80)."""
    sa = make_silverash()
    base = sa.atk  # 620
    # fire skill (200 ticks = 20s at sp_gain_rate=1 → 20 SP at sp_cost=20)
    from core.battle import DT
    for _ in range(200):
        sa.update_skill(DT)
    assert sa.skill_active
    assert sa.effective_atk() == int(base * 2.80)


def test_silverash_s3_buff_cleared_on_end():
    sa = make_silverash()
    base = sa.atk
    from core.battle import DT
    for _ in range(350):   # 20s accumulate + 15s duration = 35s = 350 ticks
        sa.update_skill(DT)
    assert not sa.skill_active
    assert not sa._atk_ratio_buffs
    assert sa.effective_atk() == base


def test_ratio_and_multiplier_combined():
    """Stacking both buff types in a realistic scenario (e.g. Warfarin ratio + Skadi mult)."""
    op = _bare_op(atk=600)
    op._atk_ratio_buffs.append(0.55)    # Warfarin-like: +55%
    op._atk_multiplier_buffs.append(1.20)  # external 20% multiplier
    # intermediate = 600 * 1.55 = 930.0, final = int(930 * 1.20) = 1116
    assert op.effective_atk() == int(600 * 1.55 * 1.20)
