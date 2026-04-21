"""Ansel (安赛尔) — 3* Medic (Single-target archetype).

Talent "Additional Treatment" (附加治疗): 18% chance on attacks to provide
  extra heal. (Probabilistic; not modeled in ECS — would require per-attack RNG.)

S1 "Heal Range Enhancement" (治疗范围强化): ATK +40% for 25s, extended range.
  sp_cost=35, initial_sp=10, MANUAL, AUTO_TIME.
  (Range extension not modeled in ECS; ATK buff tested.)

Base stats from ArknightsGameData (E1 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.ansel import make_ansel as _base_stats


MEDIC_RANGE = RangeShape(tiles=((1, 0), (2, 0), (3, 0), (1, -1), (1, 1)))

# --- S1: Heal Range Enhancement ---
_S1_TAG = "ansel_s1_heal_range"
_S1_ATK_RATIO = 0.40
_S1_BUFF_TAG = "ansel_s1_atk"
_S1_DURATION = 25.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Ansel S1 — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s (heal power up)")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_ansel(slot: str = "S1") -> UnitState:
    """Ansel E1 max. S1: ATK+40%/25s MANUAL (heal power up)."""
    op = _base_stats()
    op.name = "Ansel"
    op.archetype = RoleArchetype.MEDIC_ST
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.HEAL
    op.range_shape = MEDIC_RANGE

    if slot == "S1":
        op.skill = SkillComponent(
            name="Heal Range Enhancement",
            slot="S1",
            sp_cost=35,
            initial_sp=10,
            duration=_S1_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
