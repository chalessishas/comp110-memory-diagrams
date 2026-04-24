"""Matterhorn (冰岩) — 5★ Vanguard (Charger).

S1 "Stamina Enhancement": MaxHP+40%/27s, sp_cost=39, initial_sp=5, AUTO_TIME, MANUAL.
  HP regen not modeled (out of scope for current engine).
S2 "Cold Resistance": MaxHP+40%+DEF+15%+RES+70/27s, sp_cost=44, initial_sp=5, AUTO_TIME, MANUAL.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import AttackType, BuffAxis, BuffStack, Profession, RoleArchetype, SkillTrigger, SPGainMode
from core.systems.skill_system import register_skill
from data.characters.generated.mitm import make_mitm as _base_stats

VAN_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "mitm_s1_stamina"; _S1_DURATION = 27.0
_S1_MAXHP_RATIO = 0.40
_S1_MAXHP_BUFF_TAG = "mitm_s1_maxhp"

_S2_TAG = "mitm_s2_cold_resistance"; _S2_DURATION = 27.0
_S2_MAXHP_RATIO = 0.40
_S2_DEF_RATIO = 0.15
_S2_RES_FLAT = 70.0
_S2_MAXHP_BUFF_TAG = "mitm_s2_maxhp"
_S2_DEF_BUFF_TAG = "mitm_s2_def"
_S2_RES_BUFF_TAG = "mitm_s2_res"


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.MAX_HP, stack=BuffStack.RATIO,
        value=_S1_MAXHP_RATIO, source_tag=_S1_MAXHP_BUFF_TAG,
    ))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_MAXHP_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.MAX_HP, stack=BuffStack.RATIO,
        value=_S2_MAXHP_RATIO, source_tag=_S2_MAXHP_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S2_DEF_RATIO, source_tag=_S2_DEF_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.RES, stack=BuffStack.FLAT,
        value=_S2_RES_FLAT, source_tag=_S2_RES_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag not in (
        _S2_MAXHP_BUFF_TAG, _S2_DEF_BUFF_TAG, _S2_RES_BUFF_TAG
    )]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_mitm(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Mitm"
    op.archetype = RoleArchetype.VAN_CHARGER
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = VAN_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Stamina Enhancement", slot="S1", sp_cost=39, initial_sp=5,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Cold Resistance", slot="S2", sp_cost=44, initial_sp=5,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
