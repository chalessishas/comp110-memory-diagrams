"""Beagle (米格鲁) — 3* Defender (Protector archetype).

S1 "DEF Up α" (防御力强化·α型): DEF +50% for 30s.
  sp_cost=40, initial_sp=0, MANUAL, AUTO_TIME.

Base stats from ArknightsGameData (E1 max, trust 100).
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
from data.characters.generated.beagle import make_beagle as _base_stats


DEFENDER_MELEE = RangeShape(tiles=((0, 0),))

# --- S1: DEF Up α ---
_S1_TAG = "beagle_s1_def_up"
_S1_DEF_RATIO = 0.50
_S1_BUFF_TAG = "beagle_s1_def"
_S1_DURATION = 30.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S1_DEF_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Beagle S1 DEF Up α — DEF+{_S1_DEF_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_beagle(slot: str = "S1") -> UnitState:
    """Beagle E1 max. S1: DEF+50%/30s MANUAL."""
    op = _base_stats()
    op.name = "Beagle"
    op.archetype = RoleArchetype.DEF_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = DEFENDER_MELEE

    if slot == "S1":
        op.skill = SkillComponent(
            name="DEF Up α",
            slot="S1",
            sp_cost=40,
            initial_sp=0,
            duration=_S1_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
    return op
