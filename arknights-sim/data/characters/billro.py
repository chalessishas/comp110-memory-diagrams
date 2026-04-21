"""卡涅利安 (Carnelian / Billro) — 6★ Caster (Mystic Caster).

S1 "沙暴守卫": sp_cost=18, initial_sp=5, duration=20s, MANUAL, AUTO_TIME.
  ATK +60%, DEF +100%.

S2/S3: complex (ASPD reduction, enemy slow, mega ATK) — not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.billro import make_billro as _base_stats

CASTER_RANGE = RangeShape(tiles=((1, 0), (2, 0), (3, 0), (1, -1), (1, 1), (2, -1), (2, 1)))

# --- S1 ---
_S1_TAG = "billro_s1_sandstorm_guard"
_S1_ATK_RATIO = 0.60
_S1_DEF_RATIO = 1.00
_S1_ATK_BUFF_TAG = "billro_s1_atk"
_S1_DEF_BUFF_TAG = "billro_s1_def"
_S1_DURATION = 20.0

# --- S2 / S3 stubs ---
_S2_TAG = "billro_s2_sandstorm_blade"
_S2_DURATION = 25.0
_S3_TAG = "billro_s3_scorching_sandstorm"
_S3_DURATION = 21.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_ATK_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S1_DEF_RATIO, source_tag=_S1_DEF_BUFF_TAG,
    ))
    world.log(f"Carnelian S1 — ATK+{_S1_ATK_RATIO:.0%} DEF+{_S1_DEF_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag not in (_S1_ATK_BUFF_TAG, _S1_DEF_BUFF_TAG)]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_billro(slot: str = "S1") -> UnitState:
    """Carnelian E2 max. S1: ATK+60%+DEF+100%/20s. S2/S3: not modeled."""
    op = _base_stats()
    op.name = "Carnelian"
    op.archetype = RoleArchetype.CASTER_MYSTIC
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CASTER_RANGE

    if slot == "S1":
        op.skill = SkillComponent(
            name="Sandstorm Guard",
            slot="S1",
            sp_cost=18,
            initial_sp=5,
            duration=_S1_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Sandstorm Blade",
            slot="S2",
            sp_cost=40,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Scorching Sandstorm",
            slot="S3",
            sp_cost=50,
            initial_sp=20,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
