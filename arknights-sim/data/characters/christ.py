"""Miss.Christine (克里斯蒂娜) — 5★ Caster (Primal).

S1 "Mealtime Manners": sp_cost=30, initial_sp=15, duration=25s, MANUAL, AUTO_TIME.
  ATK +50% (2-target not modeled).

S2 "Bacchanalia": sp_cost=35, initial_sp=15, duration=20s (summon mechanic, stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.christ import make_christ as _base_stats

CASTER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 3) for dy in range(-1, 2)
))

_S1_TAG = "christ_s1_mealtime_manners"
_S1_ATK_RATIO = 0.50
_S1_BUFF_TAG = "christ_s1_atk"
_S1_DURATION = 25.0

_S2_TAG = "christ_s2_bacchanalia"
_S2_DURATION = 20.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG))
    world.log(f"Christ S1 — ATK+{_S1_ATK_RATIO*100:.0f}%/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_christ(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Christ"
    op.archetype = RoleArchetype.CASTER_CORE
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CASTER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Mealtime Manners", slot="S1", sp_cost=30, initial_sp=15,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Bacchanalia", slot="S2", sp_cost=35, initial_sp=15,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
