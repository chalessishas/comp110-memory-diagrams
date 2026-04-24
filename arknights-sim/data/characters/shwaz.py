"""Schwarz (施华兹) — 6★ Sniper (Deadeye).

S1 "Charged Shot": sp_cost=4, initial_sp=0, instant, AUTO_ATTACK, AUTO.
  Next attack deals 190% ATK. Talent proc chance +50%. (next-attack mult not modeled)
S2 "Sharp Eye": sp_cost=34, initial_sp=16, duration=36s, AUTO_TIME, MANUAL.
  ATK +100%.
S3 "Final Tactics": sp_cost=29, initial_sp=9, duration=21s, AUTO_TIME, MANUAL.
  ATK +140%, attack interval +0.4s, talent guaranteed (100% proc).
  Interval penalty and talent DEF debuff not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.shwaz import make_shwaz as _base_stats

SNP_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 4) for dy in range(-1, 2)))

# --- S1 ---
_S1_TAG = "shwaz_s1"; _S1_DURATION = 0.0

# --- S2 ---
_S2_TAG = "shwaz_s2_sharp_eye"
_S2_ATK_RATIO = 1.00
_S2_BUFF_TAG = "shwaz_s2_atk"
_S2_DURATION = 36.0

# --- S3 ---
_S3_TAG = "shwaz_s3_final_tactics"
_S3_ATK_RATIO = 1.40
_S3_BUFF_TAG = "shwaz_s3_atk"
_S3_DURATION = 21.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    world.log(f"Schwarz S2 — ATK+{_S2_ATK_RATIO:.0%}/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))
    world.log(f"Schwarz S3 — ATK+{_S3_ATK_RATIO:.0%}/{_S3_DURATION}s (interval+0.4s not modeled)")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_shwaz(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Schwarz"
    op.archetype = RoleArchetype.SNIPER_DEADEYE
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Charged Shot", slot="S1", sp_cost=4, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Sharp Eye", slot="S2", sp_cost=34, initial_sp=16,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    elif slot == "S3":
        op.skill = SkillComponent(name="Final Tactics", slot="S3", sp_cost=29, initial_sp=9,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
