"""Breeze (微风) — 5★ Medic (Therapist archetype).

MEDIC_THERAPIST trait: Each attack heals ALL injured allied operators in range
  simultaneously (not just the single most-injured one). Uses heal_targets=99
  so the multi-target medic path in targeting_system picks every injured ally
  globally, approximating the in-range AoE heal behavior.

Talent "Healing Breeze" (疗愈之风): When 2+ allies are simultaneously healed
  by a single attack, each ally receives an additional 10% max_hp bonus heal.
  Implemented via on_attack_hit (called per healed target from _apply_multi_heal).

S2 "Revitalizing Gale" (活化疾风): 20s duration. ATK (heal power)+30%.
  sp_cost=30, initial_sp=15, AUTO_TIME, AUTO trigger.
S3 "Healing Storm" (治愈风暴): 30s duration. ATK (heal power)+80%.
  sp_cost=40, initial_sp=20, AUTO_TIME, MANUAL trigger.

Base stats from ArknightsGameData (E2 max, trust 100, char_275_breeze).
  HP=1795, ATK=373, DEF=153, RES=0, atk_interval=2.85s, cost=17, block=1.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.breeze import make_breeze as _base_stats


THERAPIST_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 4) for dy in range(-1, 2)
))

_BASE_HEAL_TARGETS = 99       # effectively unlimited: heal all injured allies

# Talent: Healing Breeze — bonus 10% max_hp heal per multi-heal proc
_TALENT_TAG = "breeze_healing_breeze"
_TALENT_BONUS_RATIO = 0.10    # +10% max_hp bonus per healed target
_TALENT_ACCUM_ATTR = "_breeze_heal_count"
_TALENT_TICK_ATTR = "_breeze_heal_tick"   # tick_count when count was last reset

# S2: Revitalizing Gale
_S2_TAG = "breeze_s2_revitalizing_gale"
_S2_ATK_RATIO = 0.30
_S2_ATK_BUFF_TAG = "breeze_s2_atk"
_S2_DURATION = 20.0


def _healing_breeze_on_attack_hit(world, attacker: UnitState, target, heal_amount: int) -> None:
    """Called once per healed target. Track count and apply bonus on 2+ heals."""
    current_tick = world.global_state.tick_count
    if getattr(attacker, _TALENT_TICK_ATTR, -1) != current_tick:
        setattr(attacker, _TALENT_ACCUM_ATTR, 0)
        setattr(attacker, _TALENT_TICK_ATTR, current_tick)
    count = getattr(attacker, _TALENT_ACCUM_ATTR, 0) + 1
    setattr(attacker, _TALENT_ACCUM_ATTR, count)
    # Apply bonus 10% max_hp heal for each heal in a multi-heal event
    if count >= 2 and heal_amount > 0:
        bonus = int(target.max_hp * _TALENT_BONUS_RATIO)
        if bonus > 0:
            extra = target.heal(bonus)
            world.global_state.total_healing_done += extra
            world.log(
                f"Breeze bonus heal → {target.name}  bonus={extra}  "
                f"({target.hp}/{target.max_hp})"
            )


register_talent(_TALENT_TAG, on_attack_hit=_healing_breeze_on_attack_hit)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_ATK_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# --- S3: Healing Storm — ATK+80% for 30s ---
_S3_TAG = "breeze_s3_healing_storm"
_S3_ATK_RATIO = 0.80
_S3_ATK_BUFF_TAG = "breeze_s3_atk"
_S3_DURATION = 30.0


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))
    world.log(f"Breeze S3 Healing Storm — ATK+{_S3_ATK_RATIO:.0%} ({_S3_DURATION}s)")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_ATK_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_breeze(slot: str = "S2") -> UnitState:
    """Breeze E2 max. MEDIC_THERAPIST: heals all injured allies per attack. S2: heal power+30%."""
    op = _base_stats()
    op.name = "Breeze"
    op.archetype = RoleArchetype.MEDIC_THERAPIST
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.HEAL
    op.attack_range_melee = False
    op.range_shape = THERAPIST_RANGE
    op.block = 1
    op.cost = 17
    op.heal_targets = _BASE_HEAL_TARGETS

    op.talents = [TalentComponent(name="Healing Breeze", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Revitalizing Gale",
            slot="S2",
            sp_cost=30,
            initial_sp=15,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Healing Storm",
            slot="S3",
            sp_cost=40,
            initial_sp=20,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
