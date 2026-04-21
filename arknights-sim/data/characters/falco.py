"""Plume (翎羽) — 3★ Vanguard (Pioneer).

S1 "Swift Strike α" (shared skcom_quickattack[1]):
  sp_cost=45, initial_sp=0, duration=25s, MANUAL, AUTO_TIME.
  ATK +25%, ASPD +25.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.falco import make_falco as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "falco_s1_swift_strike"
_S1_ATK_RATIO = 0.25
_S1_ASPD_BONUS = 25.0
_S1_ATK_BUFF_TAG = "falco_s1_atk"
_S1_ASPD_BUFF_TAG = "falco_s1_aspd"
_S1_DURATION = 25.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_ATK_BUFF_TAG))
    carrier.buffs.append(Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
                              value=_S1_ASPD_BONUS, source_tag=_S1_ASPD_BUFF_TAG))
    world.log(f"Falco S1 — ATK+{_S1_ATK_RATIO:.0%} ASPD+{_S1_ASPD_BONUS:.0f}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S1_ATK_BUFF_TAG, _S1_ASPD_BUFF_TAG)]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_falco(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Falco"
    op.archetype = RoleArchetype.VAN_PIONEER
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Swift Strike α", slot="S1", sp_cost=45, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
