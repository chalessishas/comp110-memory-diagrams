"""Operator factories. Skills reference back to the carrier via on_start/on_end
callbacks, so operators are constructed in Python rather than YAML."""
from __future__ import annotations
from core.operator import Operator
from core.skill import Skill


def make_liskarm() -> Operator:
    return Operator(
        name="Liskarm",
        max_hp=2000, atk=480, defence=500, res=0,
        atk_interval=1.05, block=1, attack_type="physical",
    )


def make_exusiai() -> Operator:
    """Exusiai E2 L90 — fast ranged sniper deployed on elevated tile."""
    return Operator(
        name="Exusiai",
        max_hp=2000, atk=720, defence=65, res=0,
        atk_interval=0.6, block=0, attack_type="physical",
        attack_range="ranged",
    )


def make_hoshiguma() -> Operator:
    return Operator(
        name="Hoshiguma",
        max_hp=3200, atk=436, defence=800, res=0,
        atk_interval=1.15, block=3, attack_type="physical",
    )


def make_silverash() -> Operator:
    """SilverAsh E2 L90 with S3 'Truesilver Slash' (simplified).

    In-game S3 is a burst with multi-target + AoE. We model only the ATK buff
    portion here — multi-target selection lands in P5 when we add range/AOE.
    """
    op = Operator(
        name="SilverAsh",
        max_hp=2400, atk=620, defence=382, res=10,
        atk_interval=1.6, block=2, attack_type="physical",
        sp=0.0, sp_gain_rate=1.0,
    )

    def s3_on_start(carrier: Operator) -> None:
        carrier._atk_bonus = int(carrier.atk * 1.80)

    def s3_on_end(carrier: Operator) -> None:
        carrier._atk_bonus = 0

    op.skill = Skill(
        name="Truesilver Slash",
        sp_cost=20.0,
        duration=15.0,
        sp_gain_mode="auto_time",
        on_start=s3_on_start,
        on_end=s3_on_end,
    )
    return op
