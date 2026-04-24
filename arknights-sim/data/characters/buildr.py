"""Dur-nar (坚雷) — 4★ Defender (ArtsProtector).

S1 "ATK Up β": ATK+50%/25s, sp_cost=37, initial_sp=5, AUTO_TIME, MANUAL.
S2 "Shielded Counterattack": ATK+50%/30s, sp_cost=31, initial_sp=6.
  SP gain: ON_HIT (INCREASE_WHEN_TAKEN_DAMAGE) — modeled as AUTO_TIME (engine limitation).
  Multi-target counterattack component not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.buildr import make_buildr as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "buildr_s1_atk_up"
_S1_ATK_RATIO = 0.50
_S1_BUFF_TAG = "buildr_s1_atk"
_S1_DURATION = 25.0

_S2_TAG = "buildr_s2_shielded_counterattack"
_S2_ATK_RATIO = 0.50
_S2_ATK_BUFF_TAG = "buildr_s2_atk"
_S2_DURATION = 30.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_ATK_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_buildr(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Buildr"
    op.archetype = RoleArchetype.DEF_ARTS_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="ATK Up β", slot="S1", sp_cost=37, initial_sp=5,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Shielded Counterattack", slot="S2", sp_cost=31, initial_sp=6,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
