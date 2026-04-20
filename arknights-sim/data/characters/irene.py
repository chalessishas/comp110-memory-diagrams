"""Irene (艾丽妮) — 6* Guard (Swordmaster archetype).

Talent "Blade of Judgement": Each attack applies FRAGILE (20%, 2s) to the target.
  Enemy takes +20% damage from all sources while FRAGILE is active.
  Implemented via on_attack_hit; refreshes on each subsequent hit.

S3 "Sword of Vengeance": 25s duration, ATK +80%.
  sp_cost=35, initial_sp=10, AUTO_TIME, AUTO trigger, requires_target=True.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape,
    TalentComponent, StatusEffect,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.irene import make_irene as _base_stats


GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# --- Talent: Blade of Judgement ---
_TALENT_TAG = "irene_blade_of_judgement"
_TALENT_FRAGILE_AMOUNT = 0.20    # target takes +20% damage
_TALENT_FRAGILE_DURATION = 2.0   # seconds
_TALENT_FRAGILE_TAG = "irene_talent_fragile"

# --- S3: Sword of Vengeance ---
_S3_TAG = "irene_s3_sword_of_vengeance"
_S3_ATK_RATIO = 0.80
_S3_BUFF_TAG = "irene_s3_atk_buff"
_S3_DURATION = 25.0


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    # Refresh FRAGILE: remove stale, apply fresh
    target.statuses = [s for s in target.statuses if s.source_tag != _TALENT_FRAGILE_TAG]
    target.statuses.append(StatusEffect(
        kind=StatusKind.FRAGILE,
        source_tag=_TALENT_FRAGILE_TAG,
        expires_at=world.global_state.elapsed + _TALENT_FRAGILE_DURATION,
        params={"amount": _TALENT_FRAGILE_AMOUNT},
    ))
    world.log(
        f"Irene Blade of Judgement → {target.name}  "
        f"fragile={_TALENT_FRAGILE_AMOUNT:.0%}  ({_TALENT_FRAGILE_DURATION}s)"
    )


register_talent(_TALENT_TAG, on_attack_hit=_talent_on_attack_hit)


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_irene(slot: str = "S3") -> UnitState:
    """Irene E2 max. Talent: FRAGILE on every hit. S3: ATK burst."""
    op = _base_stats()
    op.name = "Irene"
    op.archetype = RoleArchetype.GUARD_SWORDMASTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    op.cost = 23

    op.talents = [TalentComponent(name="Blade of Judgement", behavior_tag=_TALENT_TAG)]

    if slot == "S3":
        op.skill = SkillComponent(
            name="Sword of Vengeance",
            slot="S3",
            sp_cost=35,
            initial_sp=10,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
    return op
