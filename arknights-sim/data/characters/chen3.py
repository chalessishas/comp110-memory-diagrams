"""赤刃明霄陈 (Chen the Holungday) — 6★ Guard (Fighter archetype).

S1 "赤霄·奔夜": sp_cost=20, initial_sp=10, duration=18s, MANUAL, AUTO_TIME.
  ATK +120%.

S2 "赤霄·绝影-驰": sp_cost=20, initial_sp=15, duration=6s, MANUAL.
  ATK×480% + respawn buff (complex — not modeled).

S3 "赤霄·天喟": sp_cost=25, initial_sp=18, duration=20s, MANUAL.
  HP drain + projectile attack (complex — not modeled).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.chen3 import make_chen3 as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))

# --- S1 ---
_S1_TAG = "chen3_s1_sprint"
_S1_ATK_RATIO = 1.20
_S1_BUFF_TAG = "chen3_s1_atk"
_S1_DURATION = 18.0

# --- S2 / S3 stubs ---
_S2_TAG = "chen3_s2_flash"
_S2_DURATION = 6.0
_S3_TAG = "chen3_s3_skyroar"
_S3_DURATION = 20.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Chen(Holungday) S1 — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_chen3(slot: str = "S1") -> UnitState:
    """Chen the Holungday E2 max. S1: ATK+120%/18s. S2/S3: not modeled."""
    op = _base_stats()
    op.name = "Chen(Holungday)"
    op.archetype = RoleArchetype.GUARD_FIGHTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.ARTS
    op.range_shape = MELEE_RANGE

    if slot == "S1":
        op.skill = SkillComponent(
            name="Chixiao: Night Sprint",
            slot="S1",
            sp_cost=20,
            initial_sp=10,
            duration=_S1_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Chixiao: Flash Drive",
            slot="S2",
            sp_cost=20,
            initial_sp=15,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Chixiao: Sky's Lament",
            slot="S3",
            sp_cost=25,
            initial_sp=18,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
