"""Catherine (凯瑟琳) — 4★ Supporter (Decel).

S1 "Wrought by Age": sp_cost=0, initial_sp=0, duration=0s (passive trigger, stub).

S2 "Tempered by War": sp_cost=30, initial_sp=15, duration=30s, MANUAL, AUTO_TIME.
  DEF +30% (max_hp/regen not modeled).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.cathy import make_cathy as _base_stats

CASTER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0),
    (1, -1), (1, 1), (2, -1), (2, 1),
))

_S1_TAG = "cathy_s1_wrought_by_age"
_S1_DURATION = 0.0

_S2_TAG = "cathy_s2_tempered_by_war"
_S2_DEF_RATIO = 0.30
_S2_BUFF_TAG = "cathy_s2_def"
_S2_DURATION = 30.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.DEF, stack=BuffStack.RATIO,
                              value=_S2_DEF_RATIO, source_tag=_S2_BUFF_TAG))
    world.log(f"Cathy S2 — DEF+{_S2_DEF_RATIO*100:.0f}%/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_cathy(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Cathy"
    op.archetype = RoleArchetype.SUP_DECEL
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CASTER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Wrought by Age", slot="S1", sp_cost=0, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Tempered by War", slot="S2", sp_cost=30, initial_sp=15,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
