"""Flint (燧石) — 5★ Guard (Earthshaker archetype).

GUARD_EARTHSHAKER trait: When not blocking any enemies, ATK doubles (+100%).
  Implemented as an on_tick talent that checks blocked enemy count each tick.
  Buff is applied when blocking_count == 0 and removed when > 0.

Talent "Burning Blood" (E2): ATK +100% when not blocking (trait mechanic).

S2 "Smelt and Strike": ATK +70%, Duration 11s.
  sp_cost=24, initial_sp=12, AUTO_TIME, AUTO trigger.

Base stats from ArknightsGameData (E2 max, trust 100, char_415_flint).
  HP=2495, ATK=620, DEF=334, RES=0, atk_interval=0.78s, cost=10, block=1.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.flint import make_flint as _base_stats


EARTHSHAKER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_TALENT_TAG = "flint_burning_blood"
_NOT_BLOCKING_BUFF_TAG = "flint_not_blocking_atk"
_NOT_BLOCKING_ATK_RATIO = 1.0   # +100% ATK when not blocking

_S2_TAG = "flint_s2_smelt_strike"
_S2_ATK_RATIO = 0.70
_S2_BUFF_TAG = "flint_s2_atk"
_S2_DURATION = 11.0

# --- S3: White-Hot Forge ---
_S3_TAG = "flint_s3_whitehot_forge"
_S3_ATK_RATIO = 2.00   # ATK +200%
_S3_BUFF_TAG = "flint_s3_atk"
_S3_DURATION = 12.0


def _talent_on_tick(world, carrier: UnitState, dt: float) -> None:
    if not carrier.deployed or carrier.position is None:
        return
    blocking_count = sum(
        1 for e in world.enemies()
        if carrier.unit_id in e.blocked_by_unit_ids
    )
    has_buff = any(b.source_tag == _NOT_BLOCKING_BUFF_TAG for b in carrier.buffs)
    if blocking_count == 0 and not has_buff:
        carrier.buffs.append(Buff(
            axis=BuffAxis.ATK, stack=BuffStack.RATIO,
            value=_NOT_BLOCKING_ATK_RATIO, source_tag=_NOT_BLOCKING_BUFF_TAG,
        ))
    elif blocking_count > 0 and has_buff:
        carrier.buffs = [b for b in carrier.buffs if b.source_tag != _NOT_BLOCKING_BUFF_TAG]


register_talent(_TALENT_TAG, on_tick=_talent_on_tick)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))
    setattr(carrier, "_attack_all_in_range", True)
    world.log(f"Flint S3 White-Hot Forge — ATK+{_S3_ATK_RATIO:.0%}, AoE ({_S3_DURATION}s)")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]
    setattr(carrier, "_attack_all_in_range", False)


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_flint(slot: str = "S2") -> UnitState:
    """Flint E2 max. Trait: ATK×2 when not blocking. S2: ATK+70%/11s."""
    op = _base_stats()
    op.name = "Flint"
    op.archetype = RoleArchetype.GUARD_EARTHSHAKER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = True
    op.range_shape = EARTHSHAKER_RANGE
    op.block = 1
    op.cost = 10

    op.talents = [TalentComponent(name="Burning Blood", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Smelt and Strike",
            slot="S2",
            sp_cost=24,
            initial_sp=12,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="White-Hot Forge",
            slot="S3",
            sp_cost=45,
            initial_sp=20,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
    return op
