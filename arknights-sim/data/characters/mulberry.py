"""Mulberry (桑葚) — 5* Medic (Wandering Medic archetype).

MEDIC_WANDERING trait: heals ALL deployed allies simultaneously per attack
  (heal_targets=99 ≈ "all"), at reduced efficiency due to archetype trait.

Talent "Natural Recovery": whenever Mulberry heals an ally, reduce all of
  that ally's elemental injury bars by 50%. First integration of
  healing + elemental injury systems via on_attack_hit talent callback.

S2 "Spring Breeze": on activation, clears ALL elemental bars from every
  deployed ally and heals each for 150% ATK (instant AoE cleanse burst).
  sp_cost=15, initial_sp=5, AUTO_TIME, AUTO trigger, no target required.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, RangeShape, TalentComponent,
)
from core.types import (
    AttackType, Profession, RoleArchetype,
    SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.mberry import make_mberry as _base_stats


WANDERING_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 4) for dy in range(-1, 2)
))

# --- Talent: Natural Recovery (elemental bar reduction on heal) ---
_TALENT_TAG = "mulberry_natural_recovery"
_ELEMENTAL_CLEAR_RATIO = 0.50   # reduce each bar by 50% per heal event

# --- S2: Spring Breeze ---
_S2_TAG = "mulberry_s2_spring_breeze"
_S2_HEAL_RATIO = 1.50    # 150% ATK instant AoE heal
_S2_DURATION = 0.0       # instant

# MEDIC_WANDERING heal targets — effectively "all" in practice
_HEAL_TARGETS = 99


def _talent_on_attack_hit(world, healer: UnitState, target: UnitState, dealt: int) -> None:
    """Reduce elemental bars by 50% on each ally healed."""
    if dealt <= 0 or not target.elemental_bars:
        return
    for key in list(target.elemental_bars.keys()):
        target.elemental_bars[key] *= (1.0 - _ELEMENTAL_CLEAR_RATIO)
        if target.elemental_bars[key] < 1.0:
            del target.elemental_bars[key]


register_talent(_TALENT_TAG, on_attack_hit=_talent_on_attack_hit)


def _s2_on_start(world, carrier: UnitState) -> None:
    heal_amount = int(carrier.effective_atk * _S2_HEAL_RATIO)
    for ally in world.allies():
        if not ally.alive or not ally.deployed:
            continue
        ally.elemental_bars.clear()
        healed = ally.heal(heal_amount)
        world.global_state.total_healing_done += healed
        world.log(
            f"Mulberry S2 → {ally.name}  cleanse+heal={healed}  ({ally.hp}/{ally.max_hp})"
        )


register_skill(_S2_TAG, on_start=_s2_on_start)


def make_mulberry(slot: str = "S2") -> UnitState:
    """Mulberry E2 max. MEDIC_WANDERING: heals all allies; talent clears elemental bars."""
    op = _base_stats()
    op.name = "Mulberry"
    op.archetype = RoleArchetype.MEDIC_WANDERING
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.HEAL
    op.range_shape = WANDERING_RANGE
    op.heal_targets = _HEAL_TARGETS
    op.block = 1
    op.cost = 15

    op.talents = [TalentComponent(
        name="Natural Recovery",
        behavior_tag=_TALENT_TAG,
    )]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Spring Breeze",
            slot="S2",
            sp_cost=15,
            initial_sp=5,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    return op
