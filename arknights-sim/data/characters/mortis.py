"""Mortis (若叶睦 / BanG Dream! collab) — 5★ Specialist (Dollkeeper, char_4183).

S1 "Belua Multorum es Capitums": sp_cost=23, initial_sp=15, duration=15s, AUTO_TIME, MANUAL.
  DEF+80%. Dollkeeper swap mechanic not modeled.
S2 "Destruction and Renewal": sp_cost=26, initial_sp=8, duration=15s, AUTO_TIME, MANUAL (stub).
  Triple-hit Arts to random targets; multi-target AoE Arts not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.mortis import make_mortis as _base_stats

SPEC_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "mortis_s1_belua"
_S1_DEF_RATIO = 0.80
_S1_BUFF_TAG = "mortis_s1_def"
_S1_DURATION = 15.0

_S2_TAG = "mortis_s2_destruction"
_S2_DURATION = 15.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S1_DEF_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Mortis S1 — DEF+{_S1_DEF_RATIO:.0%}/{_S1_DURATION}s (Dollkeeper swap not modeled)")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_mortis(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Mortis"
    op.archetype = RoleArchetype.SPEC_EXECUTOR
    op.profession = Profession.SPECIALIST
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SPEC_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Belua Multorum es Capitums", slot="S1", sp_cost=23, initial_sp=15,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Destruction and Renewal", slot="S2", sp_cost=26, initial_sp=8,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
