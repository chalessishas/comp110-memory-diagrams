"""Mudrock (泥岩) — 6★ Defender (Juggernaut).

S1 "DEF Up γ": sp_cost=35, initial_sp=10, duration=40s, AUTO_TIME, AUTO.
  DEF+60%.
S2 "Crag Splitter": sp_cost=5, initial_sp=0, instant, AUTO_ATTACK, AUTO (stub).
  Charge trigger — per-attack 210% ATK AoE + HP restore + 30% stun chance. Not modeled.
S3 "Bloodline of Desecrated Earth": sp_cost=29, initial_sp=12, duration=30s, AUTO_TIME, MANUAL (stub).
  Complex 2-phase: 10s invulnerable+slow, then 20s ATK+100%/DEF+50%/ASPD+43/AoE stun. Not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.mudrok import make_mudrok as _base_stats

DEF_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "mudrok_s1_def_up"
_S1_DEF_RATIO = 0.60
_S1_BUFF_TAG = "mudrok_s1_def"
_S1_DURATION = 40.0

_S2_TAG = "mudrok_s2"
_S2_DURATION = 0.0

_S3_TAG = "mudrok_s3"
_S3_DURATION = 30.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S1_DEF_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Mudrock S1 — DEF+{_S1_DEF_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_mudrok(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Mudrock"
    op.archetype = RoleArchetype.DEF_JUGGERNAUT
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = DEF_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="DEF Up γ", slot="S1", sp_cost=35, initial_sp=10,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Crag Splitter", slot="S2", sp_cost=5, initial_sp=0,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S2_TAG)
    elif slot == "S3":
        op.skill = SkillComponent(name="Bloodline of Desecrated Earth", slot="S3",
            sp_cost=29, initial_sp=12, duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME, trigger=SkillTrigger.MANUAL,
            requires_target=False, behavior_tag=_S3_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
