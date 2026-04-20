"""Penance (耀骑士临光) — 6★ Guard (Centurion archetype).

GUARD_CENTURION trait: Each attack deals damage to ALL currently blocked enemies.
  When block=1 (skill inactive), cleave has no extra targets.
  When S3 active and block=3, a single attack hits up to 3 enemies simultaneously.

Talent "Penitence, Absolution" (E2, simplified):
  For each enemy currently blocking her, gain +30% ATK (max 3 stacks = +90%).
  Implemented as on_tick buff that updates each tick based on blocking_count.

S3 "Purgatorio": block→3, ATK+20% for 20s.
  sp_cost=60, initial_sp=30, AUTO_TIME, AUTO trigger.

Base stats from ArknightsGameData (E2 max, trust 100, char_1014_nearl2).
  HP=3750, ATK=1149, DEF=295, RES=0, atk_interval=1.5s, cost=19, block=1.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.nearl2 import make_nearl2 as _base_stats


CENTURION_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_TALENT_TAG = "penance_penitence_absolution"
_TALENT_ATK_PER_STACK = 0.30   # +30% ATK per blocked enemy
_TALENT_MAX_STACKS = 3
_TALENT_BUFF_TAG = "penance_talent_atk"

# --- S2: Disciplina ---
_S2_TAG = "penance_s2_disciplina"
_S2_ATK_RATIO = 0.80
_S2_BUFF_TAG = "penance_s2_atk"
_S2_DURATION = 25.0

_S3_TAG = "penance_s3_purgatorio"
_S3_BLOCK = 3
_S3_ATK_RATIO = 0.20
_S3_BUFF_TAG = "penance_s3_atk"
_S3_DURATION = 20.0


def _talent_on_tick(world, carrier: UnitState, dt: float) -> None:
    if not carrier.deployed:
        return
    blocking_count = sum(
        1 for e in world.enemies()
        if carrier.unit_id in e.blocked_by_unit_ids
    )
    stacks = min(blocking_count, _TALENT_MAX_STACKS)
    new_value = stacks * _TALENT_ATK_PER_STACK

    existing = next((b for b in carrier.buffs if b.source_tag == _TALENT_BUFF_TAG), None)
    if existing is not None:
        if stacks == 0:
            carrier.buffs = [b for b in carrier.buffs if b.source_tag != _TALENT_BUFF_TAG]
        else:
            existing.value = new_value
    elif stacks > 0:
        carrier.buffs.append(Buff(
            axis=BuffAxis.ATK, stack=BuffStack.RATIO,
            value=new_value, source_tag=_TALENT_BUFF_TAG,
        ))


register_talent(_TALENT_TAG, on_tick=_talent_on_tick)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    world.log(f"Penance S2 Disciplina — ATK+{_S2_ATK_RATIO:.0%}/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.block = _S3_BLOCK
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.block = 1
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_penance(slot: str = "S3") -> UnitState:
    """Penance E2 max. Trait: attacks all blocked enemies. S3: block→3 + ATK+20%/20s."""
    op = _base_stats()
    op.name = "Penance"
    op.archetype = RoleArchetype.GUARD_CENTURION
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = True
    op.range_shape = CENTURION_RANGE
    op.block = 1
    op.cost = 19

    op.talents = [TalentComponent(name="Penitence, Absolution", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Disciplina",
            slot="S2",
            sp_cost=30,
            initial_sp=15,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Purgatorio",
            slot="S3",
            sp_cost=60,
            initial_sp=30,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
    return op
