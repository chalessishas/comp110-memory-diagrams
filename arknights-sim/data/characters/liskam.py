"""Liskam (莱斯坎) — 5★ Defender (Protector).

S1 "Charged Defense": sp_cost=20, initial_sp=0, duration=8s, AUTO_TIME, AUTO.
  DEF+80%. Shield/absorb mechanic not modeled.
S2: sp_cost=55, initial_sp=28, duration=30s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.liskam import make_liskam as _base_stats

DEF_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "liskam_s1_charged_defense"
_S1_DEF_RATIO = 0.80
_S1_BUFF_TAG = "liskam_s1_def"
_S1_DURATION = 8.0

_S2_TAG = "liskam_s2"
_S2_DURATION = 30.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S1_DEF_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Liskam S1 — DEF+{_S1_DEF_RATIO:.0%}/{_S1_DURATION}s (shield not modeled)")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_liskam(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Liskam"
    op.archetype = RoleArchetype.DEF_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = DEF_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Charged Defense", slot="S1", sp_cost=20, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Liskam S2", slot="S2", sp_cost=55, initial_sp=28,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
