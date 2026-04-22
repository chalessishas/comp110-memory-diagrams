"""Ambriel (安比尔) — 4★ Sniper (Deadeye archetype).

S1 "Snaring Shell" (conservative): sp_cost=30, initial_sp=10, duration=30s, MANUAL, AUTO_TIME.
  ATK +30%. Slow effect not modeled.

S2 "Radar Sweep": sp_cost=25, initial_sp=10, duration=35s, MANUAL, AUTO_TIME.
  ATK +100%. Global attack range not modeled (range change requires tile system extension).

Base stats from ArknightsGameData (E2 max, trust 100, char_302_glaze).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.glaze import make_glaze as _base_stats

SNIPER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0), (4, 0),
    (1, -1), (2, -1), (3, -1),
    (1, 1), (2, 1), (3, 1),
))

_S1_TAG = "glaze_s1_snaring_shell"
_S1_ATK_RATIO = 0.30
_S1_BUFF_TAG = "glaze_s1_atk"
_S1_DURATION = 30.0
_S2_TAG = "glaze_s2_radar_sweep"
_S2_ATK_RATIO = 1.00
_S2_BUFF_TAG = "glaze_s2_atk"
_S2_DURATION = 35.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG))
    world.log(f"Ambriel S1 — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s (slow not modeled)")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG))
    world.log(f"Ambriel S2 — ATK+{_S2_ATK_RATIO:.0%}/{_S2_DURATION}s (global range not modeled)")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_glaze(slot: str = "S1") -> UnitState:
    """Ambriel E2 max. Deadeye Sniper. S1: ATK+30%/30s (slow not modeled). S2: ATK+100%/35s (global range not modeled)."""
    op = _base_stats()
    op.name = "Ambriel"
    op.archetype = RoleArchetype.SNIPER_DEADEYE
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNIPER_RANGE

    if slot == "S1":
        op.skill = SkillComponent(
            name="Snaring Shell", slot="S1", sp_cost=30, initial_sp=10,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Radar Sweep", slot="S2", sp_cost=25, initial_sp=10,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
