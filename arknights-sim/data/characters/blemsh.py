"""Blemishine (瑕光) — 5★ Defender (Guardian).

S1 "Surging Brilliance": sp_cost=5, initial_sp=0, instant, AUTO_ATTACK, AUTO (stub).
  Charge-based: 220% ATK hit + ally HP restore. Charge + heal not modeled.
S2 "Deterring Radiance": sp_cost=16, initial_sp=0, duration=10s, AUTO_TIME, MANUAL.
  ATK+70%. Sleep AoE + ally HP regen not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.blemsh import make_blemsh as _base_stats

DEF_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "blemsh_s1"
_S1_DURATION = 0.0

_S2_TAG = "blemsh_s2_deterring_radiance"
_S2_ATK_RATIO = 0.70
_S2_BUFF_TAG = "blemsh_s2_atk"
_S2_DURATION = 10.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    world.log(f"Blemishine S2 — ATK+{_S2_ATK_RATIO:.0%}/{_S2_DURATION}s (sleep/regen not modeled)")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_blemsh(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Blemishine"
    op.archetype = RoleArchetype.DEF_GUARDIAN
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = DEF_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Surging Brilliance", slot="S1", sp_cost=5, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Deterring Radiance", slot="S2", sp_cost=16, initial_sp=0,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
