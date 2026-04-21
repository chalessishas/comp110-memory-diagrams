"""Asbestos (星极) — 5* Guard (Arts Fighter archetype).

Trait: ARTS damage. block=1.

S1 "Constellation Guard" (星座守护): ATK +50%, DEF +80% for 30s.
  sp_cost=30, initial_sp=10, MANUAL, AUTO_TIME.

S2 "Starlight Sword" (星辉剑): ATK +80%, DEF +80%, block +1 for 15s.
  sp_cost=20, initial_sp=10, MANUAL, AUTO_TIME.

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
from data.characters.generated.astesi import make_astesi as _base_stats


GUARD_MELEE_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# --- S1: Constellation Guard ---
_S1_TAG = "astesi_s1_constellation"
_S1_ATK_RATIO = 0.50
_S1_DEF_RATIO = 0.80
_S1_ATK_BUFF_TAG = "astesi_s1_atk"
_S1_DEF_BUFF_TAG = "astesi_s1_def"
_S1_DURATION = 30.0

# --- S2: Starlight Sword ---
_S2_TAG = "astesi_s2_starlight"
_S2_ATK_RATIO = 0.80
_S2_DEF_RATIO = 0.80
_S2_BLOCK_BONUS = 1
_S2_ATK_BUFF_TAG = "astesi_s2_atk"
_S2_DEF_BUFF_TAG = "astesi_s2_def"
_S2_DURATION = 15.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_ATK_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S1_DEF_RATIO, source_tag=_S1_DEF_BUFF_TAG,
    ))
    world.log(f"Asbestos S1 Constellation Guard — ATK+{_S1_ATK_RATIO:.0%} DEF+{_S1_DEF_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S1_ATK_BUFF_TAG, _S1_DEF_BUFF_TAG)]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S2_DEF_RATIO, source_tag=_S2_DEF_BUFF_TAG,
    ))
    carrier.block += _S2_BLOCK_BONUS
    world.log(f"Asbestos S2 Starlight Sword — ATK+{_S2_ATK_RATIO:.0%} DEF+{_S2_DEF_RATIO:.0%} block+{_S2_BLOCK_BONUS}/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG)]
    carrier.block -= _S2_BLOCK_BONUS


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_astesi(slot: str = "S2") -> UnitState:
    """Asbestos E2 max. S1: ATK+50%+DEF+80%/30s. S2: ATK+80%+DEF+80%+block+1/15s."""
    op = _base_stats()
    op.name = "Asbestos"
    op.archetype = RoleArchetype.GUARD_FIGHTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.ARTS
    op.range_shape = GUARD_MELEE_RANGE

    if slot == "S1":
        op.skill = SkillComponent(
            name="Constellation Guard",
            slot="S1",
            sp_cost=30,
            initial_sp=10,
            duration=_S1_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Starlight Sword",
            slot="S2",
            sp_cost=20,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
