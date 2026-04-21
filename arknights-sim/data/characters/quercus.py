"""Quercus (夏栎) — 5★ Medic (Incantation Medic archetype).

MEDIC_INCANTATION trait: Attacks deal Arts damage to enemies in range AND
  simultaneously heals all allied operators in range for 50% of damage dealt.
  This makes Quercus a hybrid attacker-healer — she targets enemies for damage
  while her incantation passively sustains allies.

Talent "Woodland Blessing" (simplified): The 50% heal-on-hit ratio is the
  trait mechanic; implemented as an always-active on_attack_hit talent.

S2 "Blessing of the Woods": 20s duration. ATK +20%; heal ratio increases from
  50% → 80% while skill is active.
  sp_cost=30, initial_sp=15, AUTO_TIME, AUTO trigger, requires_target=True.

Base stats from ArknightsGameData (E2 max, trust 100, char_492_quercu).
  HP=2080, ATK=463, DEF=202, RES=25, atk_interval=1.6s, cost=12, block=1.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.quercu import make_quercu as _base_stats


INCANTATION_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 4) for dy in range(-1, 2)
))

# --- Trait / Talent: Incantation Heal-on-Hit ---
_TRAIT_TAG = "quercus_incantation"
_TRAIT_HEAL_RATIO = 0.50      # base: 50% of damage dealt healed to each in-range ally
_S2_HEAL_RATIO = 0.80         # during S2: 80% heal ratio

# --- S2: Blessing of the Woods ---
_S2_TAG = "quercus_s2_blessing"
_S2_ATK_RATIO = 0.20          # +20% ATK
_S2_ATK_BUFF_TAG = "quercus_s2_atk"
_S2_DURATION = 20.0


def _ally_in_range(op: UnitState, ally: UnitState) -> bool:
    if op.position is None or ally.position is None:
        return False
    ox, oy = op.position
    ax, ay = ally.position
    dx = round(ax) - round(ox)
    dy = round(ay) - round(oy)
    return (dx, dy) in set(op.range_shape.tiles)


def _incantation_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    if damage <= 0:
        return
    skill_active = attacker.skill is not None and attacker.skill.active_remaining > 0
    if skill_active and attacker.skill.slot == "S3":
        ratio = _S3_HEAL_RATIO
    elif skill_active:
        ratio = _S2_HEAL_RATIO
    else:
        ratio = _TRAIT_HEAL_RATIO
    heal_amount = int(damage * ratio)
    if heal_amount <= 0:
        return
    for ally in world.allies():
        if ally is attacker or not ally.alive or not ally.deployed:
            continue
        if not _ally_in_range(attacker, ally):
            continue
        healed = ally.heal(heal_amount)
        world.global_state.total_healing_done += healed
        world.log(
            f"Quercus incantation → {ally.name}  "
            f"heal={healed}  (ratio={ratio:.0%} × dmg={damage})"
        )


register_talent(_TRAIT_TAG, on_attack_hit=_incantation_on_attack_hit)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_ATK_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# --- S3: Sacred Grove — ATK+50%, heal ratio 120% ---
_S3_TAG = "quercus_s3_sacred_grove"
_S3_ATK_RATIO = 0.50
_S3_ATK_BUFF_TAG = "quercus_s3_atk"
_S3_HEAL_RATIO = 1.20
_S3_DURATION = 25.0


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))
    world.log(f"Quercus S3 Sacred Grove — ATK+{_S3_ATK_RATIO:.0%}, heal ratio {_S3_HEAL_RATIO:.0%}")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_ATK_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_quercus(slot: str = "S2") -> UnitState:
    """Quercus E2 max. MEDIC_INCANTATION: damages enemies + heals allies on hit. S3: ATK+50% + 120% heal ratio."""
    op = _base_stats()
    op.name = "Quercus"
    op.archetype = RoleArchetype.MEDIC_INCANTATION
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.ARTS
    op.attack_range_melee = False
    op.range_shape = INCANTATION_RANGE
    op.block = 1
    op.cost = 12

    op.talents = [TalentComponent(name="Incantation", behavior_tag=_TRAIT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Blessing of the Woods",
            slot="S2",
            sp_cost=30,
            initial_sp=15,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Sacred Grove",
            slot="S3",
            sp_cost=40,
            initial_sp=15,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
