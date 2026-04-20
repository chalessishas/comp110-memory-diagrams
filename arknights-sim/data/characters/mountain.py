"""Mountain (山) — 6* Guard (Strength archetype).

Talent "Natural God" (E2): When this unit is not blocking any enemies,
  ATK +18%. Implemented as a short-lived buff refreshed every tick.

S2 "Mountain Spirit": ATK +160%, 20s duration.
  sp_cost=2, sp_gain_mode=AUTO_ATTACK, trigger=AUTO.
  Simplified: ignores kill-extension mechanic (each kill +1s up to +3s).

S3 "Blood and Iron": ATK +200%, ASPD +40, 10s duration.
  sp_cost=30, sp_gain_mode=AUTO_ATTACK.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession, RoleArchetype,
    SPGainMode, SkillTrigger,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.f12yin import make_f12yin as _base_stats


STRENGTH_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_NATURAL_GOD_TAG = "mountain_natural_god"
_NATURAL_GOD_ATK_RATIO = 0.18
_NATURAL_GOD_BUFF_TAG = "mountain_natural_god_atk"
_NATURAL_GOD_REFRESH_DT = 0.2   # short-lived; refreshed every 0.1s tick

_S2_TAG = "mountain_s2_spirit"
_S2_ATK_RATIO = 1.60
_S2_BUFF_TAG = "mountain_s2_atk"

_S3_TAG = "mountain_s3_blood_iron"
_S3_ATK_RATIO = 2.00
_S3_ASPD_FLAT = 40.0
_S3_ATK_BUFF_TAG = "mountain_s3_atk"
_S3_ASPD_BUFF_TAG = "mountain_s3_aspd"


def _natural_god_on_tick(world, carrier, dt: float) -> None:
    now = world.global_state.elapsed
    # Count how many enemies have this operator in their blocked_by list
    blocked_count = sum(
        1 for e in world.enemies()
        if carrier.unit_id in e.blocked_by_unit_ids
    )
    if blocked_count == 0:
        for b in carrier.buffs:
            if b.source_tag == _NATURAL_GOD_BUFF_TAG:
                b.expires_at = now + _NATURAL_GOD_REFRESH_DT
                break
        else:
            carrier.buffs.append(Buff(
                axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                value=_NATURAL_GOD_ATK_RATIO, source_tag=_NATURAL_GOD_BUFF_TAG,
                expires_at=now + _NATURAL_GOD_REFRESH_DT,
            ))


register_talent(_NATURAL_GOD_TAG, on_tick=_natural_god_on_tick)


# --- S2: Mountain Spirit ---
def _s2_on_start(world, unit) -> None:
    unit.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))


def _s2_on_end(world, unit) -> None:
    unit.buffs = [b for b in unit.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# --- S3: Blood and Iron ---
def _s3_on_start(world, unit) -> None:
    unit.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))
    unit.buffs.append(Buff(
        axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
        value=_S3_ASPD_FLAT, source_tag=_S3_ASPD_BUFF_TAG,
    ))


def _s3_on_end(world, unit) -> None:
    unit.buffs = [b for b in unit.buffs
                  if b.source_tag not in (_S3_ATK_BUFF_TAG, _S3_ASPD_BUFF_TAG)]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_mountain(slot: str = "S2") -> UnitState:
    """Mountain E2 max. Talent: ATK+18% when not blocking. S2: ATK+160%/20s. S3: ATK+200%+ASPD+40/10s."""
    op = _base_stats()
    op.name = "Mountain"
    op.archetype = RoleArchetype.GUARD_DREADNOUGHT
    op.profession = Profession.GUARD
    op.range_shape = STRENGTH_RANGE
    op.block = 1
    op.cost = 11
    op.talents = [TalentComponent(name="Natural God", behavior_tag=_NATURAL_GOD_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Mountain Spirit",
            slot="S2",
            sp_cost=2,
            initial_sp=0,
            duration=20.0,
            sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Blood and Iron",
            slot="S3",
            sp_cost=30,
            initial_sp=0,
            duration=10.0,
            sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
    return op
