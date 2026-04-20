"""Skadi (斯卡蒂) — 6* Guard (Dreadnought archetype).

Talent "Predator": When Skadi kills an enemy, she recovers 15% of max HP.
  Fires via on_kill hook; heals even when at full HP would be a no-op.

S2 "Surge": ATK +130% for 30s.
  sp_cost=40, initial_sp=15, AUTO_TIME, AUTO trigger, requires_target=True.

S3 "Abyssal Resonance": ATK +200%, RES +100 for 30s.
  Cost: drains 3% max HP per second (true damage, stops at 1 HP).
  sp_cost=55, initial_sp=25, AUTO_TIME, AUTO trigger, requires_target=True.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.skadi import make_skadi as _base_stats


GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# --- Talent: Predator ---
_TALENT_TAG = "skadi_predator"
_TALENT_HEAL_RATIO = 0.15    # recover 15% max HP on kill

# --- S2: Surge ---
_S2_TAG = "skadi_s2_surge"
_S2_ATK_RATIO = 1.30
_S2_BUFF_TAG = "skadi_s2_atk_buff"
_S2_DURATION = 30.0

# --- S3: Abyssal Resonance ---
_S3_TAG = "skadi_s3_abyssal_resonance"
_S3_ATK_RATIO = 2.00         # +200% ATK
_S3_RES_BONUS = 100          # +100 RES (near arts-immunity)
_S3_DRAIN_PCT = 0.03         # 3% max HP drained per second (true dmg)
_S3_BUFF_TAG_ATK = "skadi_s3_atk"
_S3_BUFF_TAG_RES = "skadi_s3_res"
_S3_DURATION = 30.0
_S3_drain_accum: dict[int, float] = {}  # unit_id → accumulated drain seconds


def _talent_on_kill(world, killer: UnitState, killed) -> None:
    heal = int(killer.max_hp * _TALENT_HEAL_RATIO)
    healed = killer.heal(heal)
    if healed > 0:
        world.log(f"Skadi Predator kill-heal  +{healed}  ({killer.hp}/{killer.max_hp})")


register_talent(_TALENT_TAG, on_kill=_talent_on_kill)


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
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG_ATK,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.RES, stack=BuffStack.RATIO,
        value=_S3_RES_BONUS, source_tag=_S3_BUFF_TAG_RES,
    ))
    _S3_drain_accum[carrier.unit_id] = 0.0
    world.log(f"Skadi S3 Abyssal Resonance — ATK+{_S3_ATK_RATIO:.0%} RES+{_S3_RES_BONUS} / {_S3_DURATION}s")


def _s3_on_tick(world, carrier: UnitState, dt: float) -> None:
    accum = _S3_drain_accum.get(carrier.unit_id, 0.0) + dt
    drained_seconds = int(accum)
    _S3_drain_accum[carrier.unit_id] = accum - drained_seconds
    if drained_seconds > 0 and carrier.hp > 1:
        drain = int(carrier.max_hp * _S3_DRAIN_PCT * drained_seconds)
        # true damage; can't kill — stop at 1 HP
        actual = min(drain, carrier.hp - 1)
        if actual > 0:
            carrier.hp -= actual
            world.log(f"Skadi S3 drain  -{actual}  HP=({carrier.hp}/{carrier.max_hp})")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S3_BUFF_TAG_ATK, _S3_BUFF_TAG_RES)]
    _S3_drain_accum.pop(carrier.unit_id, None)


register_skill(_S3_TAG, on_start=_s3_on_start, on_tick=_s3_on_tick, on_end=_s3_on_end)


def make_skadi(slot: str = "S2") -> UnitState:
    """Skadi E2 max. Talent: heal on kill. S2: ATK burst. S3: ATK+200%+RES drain."""
    op = _base_stats()
    op.name = "Skadi"
    op.archetype = RoleArchetype.GUARD_DREADNOUGHT
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    op.cost = 19

    op.talents = [TalentComponent(name="Predator", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Surge",
            slot="S2",
            sp_cost=40,
            initial_sp=15,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Abyssal Resonance",
            slot="S3",
            sp_cost=55,
            initial_sp=25,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
