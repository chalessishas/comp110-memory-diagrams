"""Rosa (早露) — 5★ Sniper (Spreadshooter archetype).

S1 "ATK Up γ": sp_cost=30, initial_sp=15, duration=30s, MANUAL, AUTO_TIME.
  ATK +100%.

S2 "Split Shot" (conservative): sp_cost=65, initial_sp=39, duration=60s, MANUAL, AUTO_TIME.
  ATK +90%. Multi-target hit not modeled.

Base stats from ArknightsGameData (E2 max, trust 100, char_197_poca).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.poca import make_poca as _base_stats

SNIPER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0), (4, 0),
    (1, -1), (2, -1), (3, -1),
    (1, 1), (2, 1), (3, 1),
))

_S1_TAG = "poca_s1_atk_up"
_S1_ATK_RATIO = 1.00
_S1_BUFF_TAG = "poca_s1_atk"
_S1_DURATION = 30.0
_S2_TAG = "poca_s2_split_shot"
_S2_ATK_RATIO = 0.90
_S2_BUFF_TAG = "poca_s2_atk"
_S2_DURATION = 60.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG))
    world.log(f"Rosa S1 — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG))
    world.log(f"Rosa S2 — ATK+{_S2_ATK_RATIO:.0%}/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_poca(slot: str = "S1") -> UnitState:
    """Rosa E2 max. Spreadshooter Sniper. S1: ATK+100%/30s. S2: ATK+90%/60s (multi-target not modeled)."""
    op = _base_stats()
    op.name = "Rosa"
    op.archetype = RoleArchetype.SNIPER_MARKSMAN
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNIPER_RANGE

    if slot == "S1":
        op.skill = SkillComponent(
            name="ATK Up γ", slot="S1", sp_cost=30, initial_sp=15,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Split Shot", slot="S2", sp_cost=65, initial_sp=39,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
