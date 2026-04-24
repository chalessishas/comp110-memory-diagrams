"""Cairn — 4★ Defender (PrimCaster/ArtsFighter).

S1 "Overlay Restoration": MAX_HP+100%/30s, sp_cost=35, initial_sp=16, AUTO_TIME, MANUAL.
S2 "Cairn S2" skipped — barrier (shield_hp_ratio) + damage aura, not a stat buff.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.cairn import make_cairn as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "cairn_s1_overlay_restoration"
_S1_MAXHP_RATIO = 1.00
_S1_MAXHP_BUFF_TAG = "cairn_s1_maxhp"
_S1_DURATION = 30.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.MAX_HP, stack=BuffStack.RATIO,
                              value=_S1_MAXHP_RATIO, source_tag=_S1_MAXHP_BUFF_TAG))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_MAXHP_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_cairn(slot: str | None = None) -> UnitState:
    op = _base_stats()
    op.name = "Cairn"
    op.archetype = RoleArchetype.DEF_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Overlay Restoration", slot="S1", sp_cost=35, initial_sp=16,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
