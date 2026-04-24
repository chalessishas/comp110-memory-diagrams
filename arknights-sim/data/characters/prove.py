"""Provence (普罗旺斯) — 5★ Sniper (Deadeye).

S1 "Wolf's Eye": passive, no SP. ATK+16% each time target loses 20% HP (conditional, not modeled).
S2 "Prey Seeker": sp_cost=30, initial_sp=0, duration=30s, AUTO_TIME, MANUAL.
  ATK+160%. Target restriction (won't attack >80% HP) not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.prove import make_prove as _base_stats

SNP_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 4) for dy in range(-1, 2)))

_S1_TAG = "prove_s1"
_S1_DURATION = 0.0

_S2_TAG = "prove_s2_prey_seeker"
_S2_ATK_RATIO = 1.60
_S2_BUFF_TAG = "prove_s2_atk"
_S2_DURATION = 30.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    world.log(f"Provence S2 — ATK+{_S2_ATK_RATIO:.0%}/{_S2_DURATION}s (>80% HP restriction not modeled)")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_prove(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Provence"
    op.archetype = RoleArchetype.SNIPER_DEADEYE
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Wolf's Eye", slot="S1", sp_cost=0, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Prey Seeker", slot="S2", sp_cost=30, initial_sp=0,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
