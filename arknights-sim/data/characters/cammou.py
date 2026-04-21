"""卡达 (Cammou / Kadar) — 4★ Caster.

S1 "攻击力强化·β型" (shared): sp_cost=35, initial_sp=10, duration=25s, MANUAL, AUTO_TIME.
  ATK +80%.

S2 "沙漠流沙": sp_cost=30, initial_sp=10, duration=30s, MANUAL, AUTO_TIME.
  ATK +70%, 27% chance to STUN 1s per hit (not modeled).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.cammou import make_cammou as _base_stats

CASTER_RANGE = RangeShape(tiles=((1, 0), (2, 0), (3, 0), (1, -1), (1, 1), (2, -1), (2, 1)))

# --- S1 ---
_S1_TAG = "cammou_s1_atk_up"
_S1_ATK_RATIO = 0.80
_S1_BUFF_TAG = "cammou_s1_atk"
_S1_DURATION = 25.0

# --- S2 ---
_S2_TAG = "cammou_s2_desert_quicksand"
_S2_DURATION = 30.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Cammou S1 — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_cammou(slot: str = "S1") -> UnitState:
    """Cammou E2 max. S1: ATK+80%/25s. S2: ATK+70%+proc STUN (not modeled)."""
    op = _base_stats()
    op.name = "Cammou"
    op.archetype = RoleArchetype.CASTER_CORE
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CASTER_RANGE

    if slot == "S1":
        op.skill = SkillComponent(
            name="ATK Up β",
            slot="S1",
            sp_cost=35,
            initial_sp=10,
            duration=_S1_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Desert Quicksand",
            slot="S2",
            sp_cost=30,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
