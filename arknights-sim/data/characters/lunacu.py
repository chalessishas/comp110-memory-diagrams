"""Lunacub (子月) — 5★ Sniper (Marksman archetype).

S1 "Time to Hunt": sp_cost=25, initial_sp=10, duration=18s, MANUAL, AUTO_TIME.
  ATK +100%.

S2 "Umbral Ambush" (conservative): sp_cost=50, initial_sp=15, duration=25s, MANUAL, AUTO_TIME.
  ASPD +140. Camouflage effect not modeled.

Base stats from ArknightsGameData (E2 max, trust 100, char_4014_lunacu).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.lunacu import make_lunacu as _base_stats

SNIPER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0), (4, 0),
    (1, -1), (2, -1), (3, -1),
    (1, 1), (2, 1), (3, 1),
))

_S1_TAG = "lunacu_s1_time_to_hunt"
_S1_ATK_RATIO = 1.00
_S1_BUFF_TAG = "lunacu_s1_atk"
_S1_DURATION = 18.0
_S2_TAG = "lunacu_s2_umbral_ambush"
_S2_ASPD_BONUS = 140.0
_S2_BUFF_TAG = "lunacu_s2_aspd"
_S2_DURATION = 25.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG))
    world.log(f"Lunacub S1 — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
                              value=_S2_ASPD_BONUS, source_tag=_S2_BUFF_TAG))
    world.log(f"Lunacub S2 — ASPD+{_S2_ASPD_BONUS:.0f}/{_S2_DURATION}s (camouflage not modeled)")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_lunacu(slot: str = "S1") -> UnitState:
    """Lunacub E2 max. Marksman Sniper. S1: ATK+100%/18s. S2: ASPD+140/25s (camouflage not modeled)."""
    op = _base_stats()
    op.name = "Lunacub"
    op.archetype = RoleArchetype.SNIPER_MARKSMAN
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNIPER_RANGE

    if slot == "S1":
        op.skill = SkillComponent(
            name="Time to Hunt", slot="S1", sp_cost=25, initial_sp=10,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Umbral Ambush", slot="S2", sp_cost=50, initial_sp=15,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
