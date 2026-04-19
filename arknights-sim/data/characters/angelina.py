"""Angelina — 6* Supporter (Decel Binder archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
Talent 1 "Thoughtful": basic attack inflicts Slow(30%) for 0.8s (E2 rank).
S3 All for One: grants all deployed allies ATK+50% and ASPD+25 for 40s.
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape, TalentComponent, StatusEffect,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.angelina import make_angelina as _base_stats


DECEL_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0), (4, 0),
    (1, 1), (2, 1), (1, -1), (2, -1),
))

# --- Talent: Thoughtful slow ---
_SLOW_TAG = "angelina_thoughtful_slow"
_SLOW_DURATION = 0.8
_SLOW_AMOUNT = 0.30


def _on_attack_hit(world, attacker: UnitState, target: UnitState, damage: int) -> None:
    target.statuses.append(StatusEffect(
        kind=StatusKind.SLOW,
        source_tag=_SLOW_TAG,
        expires_at=world.global_state.elapsed + _SLOW_DURATION,
        params={"amount": _SLOW_AMOUNT},
    ))


register_talent(_SLOW_TAG, on_attack_hit=_on_attack_hit)


# --- S3: All for One ---
_S3_TAG = "angelina_s3_all_for_one"
_S3_ATK_RATIO = 0.50      # +50% ATK at rank 7
_S3_ASPD_BONUS = 25.0     # +25 ASPD at rank 7
_S3_BUFF_TAG = "angelina_s3_aura"


def _s3_on_start(world, carrier: UnitState) -> None:
    for ally in world.allies():
        if not ally.alive or not ally.deployed:
            continue
        ally.buffs.append(Buff(
            axis=BuffAxis.ATK, stack=BuffStack.RATIO,
            value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
        ))
        ally.buffs.append(Buff(
            axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
            value=_S3_ASPD_BONUS, source_tag=_S3_BUFF_TAG,
        ))


def _s3_on_end(world, carrier: UnitState) -> None:
    for ally in world.allies():
        ally.buffs = [b for b in ally.buffs if b.source_tag != _S3_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_angelina(slot: str = "S3") -> UnitState:
    """Angelina E2 max, trust 100. Thoughtful talent + S3 All for One wired."""
    op = _base_stats()
    op.name = "Angelina"
    op.archetype = RoleArchetype.SUP_DECEL
    op.range_shape = DECEL_RANGE
    op.cost = 27
    op.talents = [TalentComponent(name="Thoughtful", behavior_tag=_SLOW_TAG)]
    if slot == "S3":
        op.skill = SkillComponent(
            name="All for One",
            slot="S3",
            sp_cost=30,
            initial_sp=10,
            duration=40.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            behavior_tag=_S3_TAG,
        )
    return op
