"""Huang (煌) — Guard (Centurion archetype).

Centurion trait: Attacks all currently-blocked enemies simultaneously
  (handled by combat_system GUARD_CENTURION branch).

S1 "ATK Up γ" (conservative): sp_cost=20, initial_sp=5, duration=25s, MANUAL, AUTO_TIME.
  ATK +50%.

S2 "Whirlwind Slash" (conservative): sp_cost=35, initial_sp=10, duration=20s, MANUAL, AUTO_TIME.
  ATK +80%.

Base stats from ArknightsGameData (E2 max, trust 100, char_017_huang).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.huang import make_huang as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "huang_s1_atk_up"
_S1_ATK_RATIO = 0.50
_S1_BUFF_TAG = "huang_s1_atk"
_S1_DURATION = 25.0
_S2_TAG = "huang_s2_whirlwind"
_S2_ATK_RATIO = 0.80
_S2_BUFF_TAG = "huang_s2_atk"
_S2_DURATION = 20.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG))
    world.log(f"Huang S1 — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG))
    world.log(f"Huang S2 — ATK+{_S2_ATK_RATIO:.0%}/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_huang(slot: str = "S1") -> UnitState:
    """Huang E2 max. Centurion trait: attacks all blocked. S1: ATK+50%/25s. S2: ATK+80%/20s."""
    op = _base_stats()
    op.name = "Huang"
    op.archetype = RoleArchetype.GUARD_CENTURION
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE

    if slot == "S1":
        op.skill = SkillComponent(
            name="ATK Up γ", slot="S1", sp_cost=20, initial_sp=5,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Whirlwind Slash", slot="S2", sp_cost=35, initial_sp=10,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
