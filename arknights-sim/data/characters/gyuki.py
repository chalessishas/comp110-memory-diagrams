"""Matoimaru (缠丸) — 4★ Guard (Dreadnought archetype).

Talent "Demonic Physique" (E2): DEF -20%; Max HP +20% (passive stat modifier,
  baked into generated base stats).

S1 "Regeneration β" (M3): sp_cost=20, initial_sp=10, instant, MANUAL, AUTO_TIME.
  Restores HP by 50% of Max HP.

S2 "Demonic Power" (M3): sp_cost=25, initial_sp=10, duration=15s, MANUAL, AUTO_TIME.
  ATK +150%; DEF reduces to 0 while active (modeled as flat DEF debuff = −effective_def).

Base stats from ArknightsGameData (E2 max, trust 100, char_289_gyuki).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.gyuki import make_gyuki as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "gyuki_s1_regeneration"
_S1_HEAL_RATIO = 0.50
_S1_DURATION = 0.0

_S2_TAG = "gyuki_s2_demonic_power"
_S2_ATK_RATIO = 1.50
_S2_BUFF_TAG = "gyuki_s2_buff"
_S2_DURATION = 15.0


def _s1_on_start(world, carrier: UnitState) -> None:
    heal = int(carrier.max_hp * _S1_HEAL_RATIO)
    carrier.hp = min(carrier.max_hp, carrier.hp + heal)
    world.log(f"Matoimaru S1 Regeneration β — healed {heal} HP")


register_skill(_S1_TAG, on_start=_s1_on_start)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    # DEF → 0: flat debuff equal to current effective DEF
    current_def = carrier.effective_def
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.FLAT,
        value=-current_def, source_tag=_S2_BUFF_TAG,
    ))
    world.log(f"Matoimaru S2 Demonic Power — ATK+{_S2_ATK_RATIO:.0%}, DEF→0/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_gyuki(slot: str = "S2") -> UnitState:
    """Matoimaru E2 max. S1: heal 50% HP. S2: ATK+150%/DEF→0/15s."""
    op = _base_stats()
    op.name = "Matoimaru"
    op.archetype = RoleArchetype.GUARD_DREADNOUGHT
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE

    if slot == "S1":
        op.skill = SkillComponent(
            name="Regeneration β", slot="S1", sp_cost=20, initial_sp=10,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Demonic Power", slot="S2", sp_cost=25, initial_sp=10,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
