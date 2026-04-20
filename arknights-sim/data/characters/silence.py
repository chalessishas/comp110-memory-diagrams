"""Silence (赫默) — 6* Medic (Single-Target archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
S2 "Medical Protocol": Deploys a healing drone — continuously heals the
  most-injured ally for ATK*1.4/2s (0.70 ATK/s) during 20s duration.
  sp_cost=25, initial_sp=0, AUTO_TIME.

S3 "Curative Panacea": ATK+60%, heals ALL deployed allies per tick at
  0.70 ATK/s each, duration=25s MANUAL.
  sp_cost=45, initial_sp=0, AUTO_TIME.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.silent import make_silent as _base_stats


# --- Talent: Reinforcement ---
_TALENT_TAG = "silence_reinforcement"
_TALENT_CRIT_ATTR = "_silence_heal_crit"
_CRIT_CHANCE = 0.15       # E2 max: 15% heal crit chance
_CRIT_MULTIPLIER = 2.0    # crit heals deal 2× the normal amount


def _reinforcement_on_battle_start(world, carrier: UnitState) -> None:
    setattr(carrier, _TALENT_CRIT_ATTR, _CRIT_CHANCE)


register_talent(_TALENT_TAG, on_battle_start=_reinforcement_on_battle_start)


MEDIC_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 2) for dy in range(-1, 2)
))

_S2_TAG = "silence_s2_medical_protocol"
_S2_HEAL_PER_SECOND = 0.70   # 1.4 * ATK over 2s = 0.70 ATK/s at rank 7

# Accumulator key stored on the carrier unit (avoids adding a field to UnitState)
_S2_HEAL_ACCUM = "_silence_s2_accum"


def _find_most_injured(world, carrier: UnitState) -> UnitState | None:
    """Return the deployed ally with the lowest HP/max_hp ratio (excluding self)."""
    best = None
    best_ratio = 1.0
    for ally in world.allies():
        if not ally.deployed or ally is carrier:
            continue
        if ally.hp >= ally.max_hp:
            continue   # full HP — not a valid heal target
        ratio = ally.hp / ally.max_hp
        if ratio < best_ratio:
            best_ratio = ratio
            best = ally
    return best


def _s2_on_start(world, carrier: UnitState) -> None:
    setattr(carrier, _S2_HEAL_ACCUM, 0.0)


def _s2_on_tick(world, carrier: UnitState, dt: float) -> None:
    """Accumulate fractional heal; apply integer portion each tick. Crit if talent active."""
    accum = getattr(carrier, _S2_HEAL_ACCUM, 0.0) + carrier.effective_atk * _S2_HEAL_PER_SECOND * dt
    whole = int(accum)
    if whole > 0:
        heal_amount = whole
        crit_chance = getattr(carrier, _TALENT_CRIT_ATTR, 0.0)
        if crit_chance > 0.0 and world.rng.random() < crit_chance:
            heal_amount = int(whole * _CRIT_MULTIPLIER)
        target = _find_most_injured(world, carrier)
        if target is not None:
            healed = target.heal(heal_amount)
            world.global_state.total_healing_done += healed
            world.log(
                f"Silence S2 drone → {target.name}  heal={healed}  ({target.hp}/{target.max_hp})"
            )
    setattr(carrier, _S2_HEAL_ACCUM, accum - whole)


def _s2_on_end(world, carrier: UnitState) -> None:
    setattr(carrier, _S2_HEAL_ACCUM, 0.0)


register_skill(_S2_TAG, on_start=_s2_on_start, on_tick=_s2_on_tick, on_end=_s2_on_end)


# --- S3: Curative Panacea ---
_S3_TAG = "silence_s3_curative_panacea"
_S3_ATK_RATIO = 0.60         # ATK +60%
_S3_ATK_BUFF_TAG = "silence_s3_atk"
_S3_HEAL_PER_SECOND = 0.70   # 0.70 ATK/s to each ally
_S3_HEAL_ACCUM = "_silence_s3_accum"
_S3_DURATION = 25.0


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))
    setattr(carrier, _S3_HEAL_ACCUM, 0.0)
    world.log(f"Silence S3 Curative Panacea — ATK+{_S3_ATK_RATIO:.0%}, AoE heal all allies")


def _s3_on_tick(world, carrier: UnitState, dt: float) -> None:
    accum = getattr(carrier, _S3_HEAL_ACCUM, 0.0) + carrier.effective_atk * _S3_HEAL_PER_SECOND * dt
    whole = int(accum)
    if whole > 0:
        crit_chance = getattr(carrier, _TALENT_CRIT_ATTR, 0.0)
        heal_amount = whole
        if crit_chance > 0.0 and world.rng.random() < crit_chance:
            heal_amount = int(whole * _CRIT_MULTIPLIER)
        for ally in world.allies():
            if not ally.deployed or ally is carrier or ally.hp >= ally.max_hp:
                continue
            healed = ally.heal(heal_amount)
            world.global_state.total_healing_done += healed
    setattr(carrier, _S3_HEAL_ACCUM, accum - whole)


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_ATK_BUFF_TAG]
    setattr(carrier, _S3_HEAL_ACCUM, 0.0)


register_skill(_S3_TAG, on_start=_s3_on_start, on_tick=_s3_on_tick, on_end=_s3_on_end)


def make_silence(slot: str = "S2") -> UnitState:
    """Silence E2 max, trust 100. S2 Medical Protocol (sustained on-tick heal)."""
    op = _base_stats()
    op.name = "Silence"
    op.archetype = RoleArchetype.MEDIC_ST
    op.range_shape = MEDIC_RANGE
    op.cost = 19
    op.talents = [TalentComponent(name="Reinforcement", behavior_tag=_TALENT_TAG)]
    if slot == "S3":
        op.skill = SkillComponent(
            name="Curative Panacea",
            slot="S3",
            sp_cost=45,
            initial_sp=0,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Medical Protocol",
            slot="S2",
            sp_cost=25,
            initial_sp=0,
            duration=20.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    return op
