"""夜莺 (Nightingale / Cgbird) — 6★ Medic (Multi-target archetype).

S1 "治疗强化·γ型" (shared): sp_cost=30, initial_sp=20, duration=30s, MANUAL, AUTO_TIME.
  ATK (heal power) +90%.

S2 "法术护盾": ammo-based, ATK×90% + RES+20 for 5s (complex — not modeled).

S3 "圣域": sp_cost=120, initial_sp=115, duration=60s, MANUAL.
  ATK+80% + RES+150% (complex — not modeled).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.cgbird import make_cgbird as _base_stats

MEDIC_RANGE = RangeShape(tiles=((1, 0), (2, 0), (3, 0), (1, -1), (1, 1)))

# --- S1 ---
_S1_TAG = "cgbird_s1_heal_up"
_S1_ATK_RATIO = 0.90
_S1_BUFF_TAG = "cgbird_s1_atk"
_S1_DURATION = 30.0

# --- S2 / S3 stubs ---
_S2_TAG = "cgbird_s2_magic_shield"
_S3_TAG = "cgbird_s3_sanctum"
_S3_DURATION = 60.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Nightingale S1 — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_cgbird(slot: str = "S1") -> UnitState:
    """Nightingale E2 max. S1: ATK+90%/30s. S2/S3: not modeled."""
    op = _base_stats()
    op.name = "Nightingale"
    op.archetype = RoleArchetype.MEDIC_MULTI
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.HEAL
    op.range_shape = MEDIC_RANGE

    if slot == "S1":
        op.skill = SkillComponent(
            name="Heal Up γ",
            slot="S1",
            sp_cost=30,
            initial_sp=20,
            duration=_S1_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Magic Shield",
            slot="S2",
            sp_cost=8,
            initial_sp=0,
            duration=5.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Sanctum",
            slot="S3",
            sp_cost=120,
            initial_sp=115,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
