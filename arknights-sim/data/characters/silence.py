"""Silence (赫默) — 6* Medic (Single-Target archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
S2 "Medical Protocol": Deploys a healing drone — continuously heals the
  most-injured ally for ATK*1.4/2s (0.70 ATK/s) during 20s duration.
  sp_cost=25, initial_sp=0, AUTO_TIME.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.silent import make_silent as _base_stats


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
    """Accumulate fractional heal; apply integer portion each tick."""
    accum = getattr(carrier, _S2_HEAL_ACCUM, 0.0) + carrier.effective_atk * _S2_HEAL_PER_SECOND * dt
    whole = int(accum)
    if whole > 0:
        target = _find_most_injured(world, carrier)
        if target is not None:
            healed = target.heal(whole)
            world.global_state.total_healing_done += healed
            world.log(
                f"Silence S2 drone → {target.name}  heal={healed}  ({target.hp}/{target.max_hp})"
            )
    setattr(carrier, _S2_HEAL_ACCUM, accum - whole)


def _s2_on_end(world, carrier: UnitState) -> None:
    setattr(carrier, _S2_HEAL_ACCUM, 0.0)


register_skill(_S2_TAG, on_start=_s2_on_start, on_tick=_s2_on_tick, on_end=_s2_on_end)


def make_silence(slot: str = "S2") -> UnitState:
    """Silence E2 max, trust 100. S2 Medical Protocol (sustained on-tick heal)."""
    op = _base_stats()
    op.name = "Silence"
    op.archetype = RoleArchetype.MEDIC_ST
    op.range_shape = MEDIC_RANGE
    op.cost = 19
    if slot == "S2":
        op.skill = SkillComponent(
            name="Medical Protocol",
            slot="S2",
            sp_cost=25,
            initial_sp=0,
            duration=20.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,   # drone fires unconditionally when SP ready
            behavior_tag=_S2_TAG,
        )
    return op
