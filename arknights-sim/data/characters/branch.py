"""Branch (折桠/Foldartol) — 5★ Defender (Juggernaut/Unyielding).

S1 "Desperate Resistance": DEF+90%/12s, sp_cost=20, initial_sp=6.
  SP gain: ON_HIT (INCREASE_WHEN_TAKEN_DAMAGE) — modeled as AUTO_TIME (engine limitation).
S2 "Set on Survival": ATK+120%+DEF+40%/15s, sp_cost=22, initial_sp=3, AUTO_TIME, MANUAL.
  Frighten side effect not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.branch import make_branch as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "branch_s1_desperate_resistance"; _S1_DURATION = 12.0
_S1_DEF_RATIO = 0.90
_S1_BUFF_TAG = "branch_s1_def"

_S2_TAG = "branch_s2_set_on_survival"; _S2_DURATION = 15.0
_S2_ATK_RATIO = 1.20
_S2_DEF_RATIO = 0.40
_S2_ATK_BUFF_TAG = "branch_s2_atk"
_S2_DEF_BUFF_TAG = "branch_s2_def"


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.DEF, stack=BuffStack.RATIO,
                              value=_S1_DEF_RATIO, source_tag=_S1_BUFF_TAG))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG))
    carrier.buffs.append(Buff(axis=BuffAxis.DEF, stack=BuffStack.RATIO,
                              value=_S2_DEF_RATIO, source_tag=_S2_DEF_BUFF_TAG))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag not in (_S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG)]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_branch(slot: str | None = None) -> UnitState:
    op = _base_stats()
    op.name = "Branch"
    op.archetype = RoleArchetype.DEF_JUGGERNAUT
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Desperate Resistance", slot="S1", sp_cost=20, initial_sp=6,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Set on Survival", slot="S2", sp_cost=22, initial_sp=3,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
