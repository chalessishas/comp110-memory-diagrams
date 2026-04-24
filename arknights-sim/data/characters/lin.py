"""Lin (林) — 6★ Caster (Phalanx).

S1 "Rampaging": sp_cost=6, initial_sp=0, instant, AUTO_ATTACK, AUTO (stub).
S2 "Realm of Ice and Snow": sp_cost=35, initial_sp=25, duration=25s, AUTO_TIME, MANUAL (stub).
S3 "Riving Lighttails": sp_cost=52, initial_sp=22, duration=28s, AUTO_TIME, MANUAL.
  ATK+160%. Freeze/multi-target FX not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.lin import make_lin as _base_stats

CAST_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))

_S1_TAG = "lin_s1"
_S1_DURATION = 0.0

_S2_TAG = "lin_s2"
_S2_DURATION = 25.0

_S3_TAG = "lin_s3_riving_lighttails"
_S3_ATK_RATIO = 1.60
_S3_BUFF_TAG = "lin_s3_atk"
_S3_DURATION = 28.0


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))
    world.log(f"Lin S3 — ATK+{_S3_ATK_RATIO:.0%}/{_S3_DURATION}s (freeze/AoE not modeled)")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_lin(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Lin"
    op.archetype = RoleArchetype.CASTER_PHALANX
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CAST_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Rampaging", slot="S1", sp_cost=6, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Realm of Ice and Snow", slot="S2", sp_cost=35, initial_sp=25,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    elif slot == "S3":
        op.skill = SkillComponent(name="Riving Lighttails", slot="S3", sp_cost=52, initial_sp=22,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
