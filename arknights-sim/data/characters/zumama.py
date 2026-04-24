"""Eunectes (锏) — 6★ Defender (DEF_GUARDIAN; Duelist subclass).

S1 "Tomahawk": sp_cost=0, initial_sp=0, ON_DEPLOY, AUTO. Passive ATK+18%, DEF+18%.
S2 "Menacing Slash": sp_cost=32, initial_sp=12, duration=17s, AUTO_TIME, MANUAL.
  ATK+130%, ASPD–0.4s interval (attack speed penalty not modeled). Stun blocked — not modeled.
S3 "Iron Will": sp_cost=49, initial_sp=22, duration=32s, AUTO_TIME, MANUAL.
  ATK+170%, DEF+120%, block+2, HP regen 3%/s. Block/regen not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.zumama import make_zumama as _base_stats

OP_RANGE = RangeShape(tiles=((0, 0),))

# --- S1 ---
_S1_TAG = "zumama_s1_tomahawk"
_S1_ATK_RATIO = 0.18
_S1_DEF_RATIO = 0.18
_S1_ATK_BUFF = "zumama_s1_atk"
_S1_DEF_BUFF = "zumama_s1_def"
_S1_DURATION = 9999.0

# --- S2 ---
_S2_TAG = "zumama_s2_menacing_slash"
_S2_ATK_RATIO = 1.30
_S2_ATK_BUFF = "zumama_s2_atk"
_S2_DURATION = 17.0

# --- S3 ---
_S3_TAG = "zumama_s3_iron_will"
_S3_ATK_RATIO = 1.70
_S3_DEF_RATIO = 1.20
_S3_ATK_BUFF = "zumama_s3_atk"
_S3_DEF_BUFF = "zumama_s3_def"
_S3_DURATION = 32.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_ATK_BUFF))
    carrier.buffs.append(Buff(axis=BuffAxis.DEF, stack=BuffStack.RATIO,
                              value=_S1_DEF_RATIO, source_tag=_S1_DEF_BUFF))
    world.log(f"Eunectes S1 (passive) — ATK+{_S1_ATK_RATIO:.0%}, DEF+{_S1_DEF_RATIO:.0%}")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S1_ATK_BUFF, _S1_DEF_BUFF)]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF))
    world.log(f"Eunectes S2 — ATK+{_S2_ATK_RATIO:.0%}/{_S2_DURATION}s (ASPD penalty/stun not modeled)")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_ATK_BUFF]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF))
    carrier.buffs.append(Buff(axis=BuffAxis.DEF, stack=BuffStack.RATIO,
                              value=_S3_DEF_RATIO, source_tag=_S3_DEF_BUFF))
    world.log(f"Eunectes S3 — ATK+{_S3_ATK_RATIO:.0%}, DEF+{_S3_DEF_RATIO:.0%}/{_S3_DURATION}s"
              " (block+2/HP regen not modeled)")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S3_ATK_BUFF, _S3_DEF_BUFF)]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_zumama(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Eunectes"
    op.archetype = RoleArchetype.DEF_GUARDIAN
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = OP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Tomahawk", slot="S1", sp_cost=0, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.ON_DEPLOY,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Menacing Slash", slot="S2", sp_cost=32, initial_sp=12,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    elif slot == "S3":
        op.skill = SkillComponent(name="Iron Will", slot="S3", sp_cost=49, initial_sp=22,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
