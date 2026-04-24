"""Melanite (玫拉) — 5★ Sniper (Heavyshooter).

S1 "Saturated Pulse": sp_cost=40, initial_sp=20, duration=30s, AUTO_TIME, AUTO.
  ATK+160%, attack interval+0.8s (slower attack not modeled).
S2 "Critical Blast": sp_cost=18, initial_sp=6, instant, AUTO_ATTACK, AUTO (stub).
  Charge-based piercing shot — 450% ATK to frontal path, 2 charges. Not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.melnte import make_melnte as _base_stats

SNP_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 4) for dy in range(-1, 2)))

_S1_TAG = "melnte_s1_saturated_pulse"
_S1_ATK_RATIO = 1.60
_S1_BUFF_TAG = "melnte_s1_atk"
_S1_DURATION = 30.0

_S2_TAG = "melnte_s2"
_S2_DURATION = 0.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Melanite S1 — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s (interval+0.8s not modeled)")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_melnte(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Melanite"
    op.archetype = RoleArchetype.SNIPER_HEAVY
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Saturated Pulse", slot="S1", sp_cost=40, initial_sp=20,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Critical Blast", slot="S2", sp_cost=18, initial_sp=6,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
