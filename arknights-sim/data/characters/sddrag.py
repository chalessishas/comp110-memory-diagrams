"""Reed (芦苇) — 5★ Vanguard (Charger).

S1 "Swift Strike γ" (shared): sp_cost=35, initial_sp=15, duration=35s, MANUAL, AUTO_TIME.
  ATK +45%, ASPD +45.

S2 "Soul Spark": sp_cost=35, initial_sp=20, duration=30s, MANUAL, AUTO_TIME.
  ATK+80% + arts bonus on kill (complex — not modeled).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.sddrag import make_sddrag as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "sddrag_s1_swift_strike"
_S1_ATK_RATIO = 0.45
_S1_ASPD_BONUS = 45.0
_S1_ATK_BUFF_TAG = "sddrag_s1_atk"
_S1_ASPD_BUFF_TAG = "sddrag_s1_aspd"
_S1_DURATION = 35.0
_S2_TAG = "sddrag_s2_soul_spark"
_S2_DURATION = 30.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_ATK_BUFF_TAG))
    carrier.buffs.append(Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
                              value=_S1_ASPD_BONUS, source_tag=_S1_ASPD_BUFF_TAG))
    world.log(f"Sddrag S1 — ATK+{_S1_ATK_RATIO:.0%} ASPD+{_S1_ASPD_BONUS:.0f}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S1_ATK_BUFF_TAG, _S1_ASPD_BUFF_TAG)]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_sddrag(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Sddrag"
    op.archetype = RoleArchetype.VAN_CHARGER
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Swift Strike γ", slot="S1", sp_cost=35, initial_sp=15,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Soul Spark", slot="S2", sp_cost=35, initial_sp=20,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
