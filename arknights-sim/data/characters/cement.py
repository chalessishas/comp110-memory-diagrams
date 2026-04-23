"""Cement (洋灰) — 5★ Defender (Duelist).

S1 "Stratum Groundbreaker": sp_cost=6, initial_sp=3, duration=0s (multi-charge AoE, stub).

S2 "Structural Support": sp_cost=40, initial_sp=20, duration=60s, MANUAL, AUTO_TIME.
  DEF +420% conservative (max 20 stacks × 21% per stack; stack-decay on hit not modeled).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.cement import make_cement as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "cement_s1_groundbreaker"
_S1_DURATION = 0.0

_S2_TAG = "cement_s2_structural_support"
_S2_DEF_RATIO = 4.20
_S2_BUFF_TAG = "cement_s2_def"
_S2_DURATION = 60.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.DEF, stack=BuffStack.RATIO,
                              value=_S2_DEF_RATIO, source_tag=_S2_BUFF_TAG))
    world.log(f"Cement S2 — DEF+{_S2_DEF_RATIO*100:.0f}% (max stacks)/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_cement(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Cement"
    op.archetype = RoleArchetype.DEF_JUGGERNAUT
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Stratum Groundbreaker", slot="S1", sp_cost=6, initial_sp=3,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Structural Support", slot="S2", sp_cost=40, initial_sp=20,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
