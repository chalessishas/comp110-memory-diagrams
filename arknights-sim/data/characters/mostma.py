"""Mostima (莫斯提马) — 6★ Caster (Mystic).

S1 "ATK Up γ": sp_cost=35, initial_sp=10, duration=30s, AUTO_TIME, MANUAL.
  ATK+60%.
S2 "Space-Time Breach": sp_cost=56, initial_sp=17, duration=6s, AUTO_TIME, MANUAL (stub).
  Burst AoE + Arts Weakness not modeled.
S3 "Key of Chronology": sp_cost=110, initial_sp=62, duration=24s, AUTO_TIME, MANUAL.
  ATK+120%. Stun/recall mechanics not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.mostma import make_mostma as _base_stats

CAST_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))

_S1_TAG = "mostma_s1_atk_up"
_S1_ATK_RATIO = 0.60
_S1_BUFF_TAG = "mostma_s1_atk"
_S1_DURATION = 30.0

_S2_TAG = "mostma_s2"
_S2_DURATION = 6.0

_S3_TAG = "mostma_s3_key_of_chronology"
_S3_ATK_RATIO = 1.20
_S3_BUFF_TAG = "mostma_s3_atk"
_S3_DURATION = 24.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Mostima S1 — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))
    world.log(f"Mostima S3 — ATK+{_S3_ATK_RATIO:.0%}/{_S3_DURATION}s (stun/recall not modeled)")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)
register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_mostma(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Mostima"
    op.archetype = RoleArchetype.CASTER_MYSTIC
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CAST_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="ATK Up γ", slot="S1", sp_cost=35, initial_sp=10,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Space-Time Breach", slot="S2", sp_cost=56, initial_sp=17,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    elif slot == "S3":
        op.skill = SkillComponent(name="Key of Chronology", slot="S3", sp_cost=110, initial_sp=62,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
