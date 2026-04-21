"""Aciddrop (酸糖) — 4* Sniper (Marksman archetype).

S1 "Fancy Shot" (花式点射): ASPD +70 for 20s.
  sp_cost=35, initial_sp=20, MANUAL, AUTO_TIME.

S2 "Trigger Moment" (扳机时刻): ATK +40% for 25s.
  sp_cost=50, initial_sp=35, MANUAL, AUTO_TIME.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.acdrop import make_acdrop as _base_stats


MARKSMAN_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 3) for dy in range(-1, 2)
))

# --- S1: Fancy Shot ---
_S1_TAG = "acdrop_s1_fancy_shot"
_S1_ASPD_BONUS = 70.0
_S1_BUFF_TAG = "acdrop_s1_aspd"
_S1_DURATION = 20.0

# --- S2: Trigger Moment ---
_S2_TAG = "acdrop_s2_trigger_moment"
_S2_ATK_RATIO = 0.40
_S2_BUFF_TAG = "acdrop_s2_atk"
_S2_DURATION = 25.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
        value=_S1_ASPD_BONUS, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Aciddrop S1 Fancy Shot — ASPD+{_S1_ASPD_BONUS:.0f}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    world.log(f"Aciddrop S2 Trigger Moment — ATK+{_S2_ATK_RATIO:.0%}/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_acdrop(slot: str = "S2") -> UnitState:
    """Aciddrop E2 max. S1: ASPD+70/20s. S2: ATK+40%/25s."""
    op = _base_stats()
    op.name = "Aciddrop"
    op.archetype = RoleArchetype.SNIPER_MARKSMAN
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MARKSMAN_RANGE

    if slot == "S1":
        op.skill = SkillComponent(
            name="Fancy Shot",
            slot="S1",
            sp_cost=35,
            initial_sp=20,
            duration=_S1_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Trigger Moment",
            slot="S2",
            sp_cost=50,
            initial_sp=35,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
