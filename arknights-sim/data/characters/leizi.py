"""Leizi (惊蛰) — 6* Caster (Chain Caster archetype).

Chain Caster trait: attacks chain to 2 additional nearest enemies after primary hit.
  Implemented via chain_count=2 on UnitState + _apply_chain in combat_system.

S3 "Thunderstruck Mane": ATK +50%, chain count increases to 5 (6 total), 20s.
  sp_cost=40, initial_sp=20, AUTO_TIME.

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
from data.characters.generated.leizi import make_leizi as _base_stats


# --- Talent: Voltage ---
_VOLTAGE_TAG = "leizi_voltage"
_SP_PER_CHAIN = 10        # every 10 SP gives +1 extra chain
_MAX_BONUS_CHAINS = 3     # max +3 chains beyond base (base=2 → max=5)


def _voltage_on_tick(world, carrier: UnitState, dt: float) -> None:
    sk = carrier.skill
    if sk is None or sk.active_remaining > 0:
        return   # S3 active — S3 manages chain_count itself
    bonus = min(int(sk.sp / _SP_PER_CHAIN), _MAX_BONUS_CHAINS)
    carrier.chain_count = _BASE_CHAIN_COUNT + bonus


register_talent(_VOLTAGE_TAG, on_tick=_voltage_on_tick)


CHAIN_CASTER_RANGE = RangeShape(tiles=tuple(
    (dx, dy)
    for dx in range(-1, 4)
    for dy in range(-1, 2)
))

_S3_TAG = "leizi_s3_thunderstruck_mane"
_S3_ATK_RATIO = 0.50          # +50% ATK
_S3_ATK_BUFF_TAG = "leizi_s3_atk"
_S3_CHAIN_COUNT = 5           # 5 extra targets = 6 total
_BASE_CHAIN_COUNT = 2


def _s3_on_start(world, unit: UnitState) -> None:
    unit.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))
    unit.chain_count = _S3_CHAIN_COUNT


def _s3_on_end(world, unit: UnitState) -> None:
    unit.buffs = [b for b in unit.buffs if b.source_tag != _S3_ATK_BUFF_TAG]
    unit.chain_count = _BASE_CHAIN_COUNT


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_leizi(slot: str = "S3") -> UnitState:
    """Leizi E2 max. Chain Caster: hits 3 enemies (primary + 2 chains). S3: 6 total + ATK+50%/20s."""
    op = _base_stats()
    op.name = "Leizi"
    op.archetype = RoleArchetype.CASTER_CHAIN
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CHAIN_CASTER_RANGE
    op.attack_range_melee = False
    op.block = 1
    op.cost = 32
    op.chain_count = _BASE_CHAIN_COUNT
    op.chain_damage_ratio = 1.0
    op.talents = [TalentComponent(name="Voltage", behavior_tag=_VOLTAGE_TAG)]

    if slot == "S3":
        op.skill = SkillComponent(
            name="Thunderstruck Mane",
            slot="S3",
            sp_cost=40,
            initial_sp=20,
            duration=20.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
    return op
