"""Cantabile (晓歌) — 5★ Vanguard (Agent).

S1 "Penetrating Gaze": sp_cost=0, initial_sp=0, duration=17s, ON_DEPLOY, AUTO.
  ATK+70%. DP generation not modeled.
S2 "Specular Reflection": sp_cost=28, initial_sp=20, duration=~30s, AUTO_TIME, MANUAL
  (ATK+28%, ASPD+34, Camouflage, +1 DP/attack, 15-ammo limit — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.ctable import make_ctable as _base_stats

VAN_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 3) for dy in range(-1, 2)
))

_S1_TAG = "ctable_s1_penetrating_gaze"
_S1_ATK_RATIO = 0.70
_S1_BUFF_TAG = "ctable_s1_atk"
_S1_DURATION = 17.0

_S2_TAG = "ctable_s2_specular_reflection"
_S2_DURATION = 30.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Cantabile S1 — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s (DP gen not modeled)")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_ctable(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Cantabile"
    op.archetype = RoleArchetype.VAN_AGENT
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = VAN_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Penetrating Gaze", slot="S1", sp_cost=0, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.ON_DEPLOY,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Specular Reflection", slot="S2", sp_cost=28, initial_sp=20,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
