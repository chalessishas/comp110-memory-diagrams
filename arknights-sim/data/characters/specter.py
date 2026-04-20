"""Specter (幽灵鲨) — 6* Guard (Dreadnought archetype).

Talent "Undying Will" (E2): Once per deployment, when Specter would die,
  she instead survives at 1 HP. She then gains DEF +200%, RES +20% and
  DAMAGE_IMMUNE for 10s, then recovers to 40% HP after the window.

S2 "Pather's Light": ATK +160%, 30s, AUTO_TIME. Attacks also restore
  5% of damage dealt as HP to Specter.

S3 "Deathless Aegis": ATK +400%, ASPD +50, duration 30s, MANUAL trigger.
  While active, Specter cannot die (undying_charges=999). On end, buffs
  cleared and undying_charges restored to pre-S3 value.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent, StatusEffect
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession, RoleArchetype,
    SPGainMode, SkillTrigger, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.ghost import make_ghost as _base_stats


DREADNOUGHT_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_UNDYING_TAG = "specter_undying_will"
_UNDYING_DEF_RATIO = 2.00   # DEF +200%
_UNDYING_RES_FLAT = 20.0    # RES +20
_UNDYING_DURATION = 10.0
_UNDYING_DEF_BUFF = "specter_undying_def"
_UNDYING_IMMUNE_SOURCE = "specter_undying_immune"
_HP_RECOVER_RATIO = 0.40    # recover to 40% HP after undying window


def _undying_on_battle_start(world, unit) -> None:
    unit.undying_charges = 1   # one save per deployment


def _undying_on_tick(world, carrier, dt: float) -> None:
    if not getattr(carrier, "_undying_just_triggered", False):
        return
    carrier._undying_just_triggered = False
    now = world.global_state.elapsed
    # Apply DEF buff + RES buff + DAMAGE_IMMUNE for 10s
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_UNDYING_DEF_RATIO, source_tag=_UNDYING_DEF_BUFF,
        expires_at=now + _UNDYING_DURATION,
    ))
    carrier.statuses.append(StatusEffect(
        kind=StatusKind.DAMAGE_IMMUNE,
        source_tag=_UNDYING_IMMUNE_SOURCE,
        expires_at=now + _UNDYING_DURATION,
    ))
    # Schedule HP recovery at end of window
    carrier._undying_recover_at = now + _UNDYING_DURATION
    world.log(f"{carrier.name} Undying Will triggered! Immune for {_UNDYING_DURATION}s")


def _undying_on_tick2(world, carrier, dt: float) -> None:
    # Check if immune window ended — recover HP
    recover_at = getattr(carrier, "_undying_recover_at", None)
    if recover_at is not None and world.global_state.elapsed >= recover_at:
        recover_hp = int(carrier.max_hp * _HP_RECOVER_RATIO)
        carrier.hp = min(carrier.max_hp, carrier.hp + recover_hp)
        carrier._undying_recover_at = None


def _undying_combined_on_tick(world, carrier, dt: float) -> None:
    _undying_on_tick(world, carrier, dt)
    _undying_on_tick2(world, carrier, dt)


def _undying_on_attack_hit(world, attacker, target, damage: int) -> None:
    if not getattr(attacker, "_specter_s2_active", False):
        return
    heal = max(1, int(damage * _S2_LIFESTEAL))
    if attacker.hp < attacker.max_hp:
        actual = attacker.heal(heal)
        world.global_state.total_healing_done += actual


register_talent(
    _UNDYING_TAG,
    on_battle_start=_undying_on_battle_start,
    on_tick=_undying_combined_on_tick,
    on_attack_hit=_undying_on_attack_hit,
)


# --- S2: Pather's Light ---
_S2_TAG = "specter_s2_pathers_light"
_S2_ATK_RATIO = 1.60
_S2_LIFESTEAL = 0.05   # 5% of damage dealt heals Specter
_S2_BUFF_TAG = "specter_s2_atk_buff"


def _s2_on_start(world, unit) -> None:
    unit.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    unit._specter_s2_active = True


def _s2_on_end(world, unit) -> None:
    unit.buffs = [b for b in unit.buffs if b.source_tag != _S2_BUFF_TAG]
    unit._specter_s2_active = False


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# --- S3: Deathless Aegis ---
_S3_TAG = "specter_s3_deathless_aegis"
_S3_ATK_RATIO = 4.00        # ATK +400%
_S3_ASPD_BONUS = 50.0       # ASPD +50
_S3_DURATION = 30.0
_S3_ATK_BUFF_TAG = "specter_s3_atk"
_S3_ASPD_BUFF_TAG = "specter_s3_aspd"
_S3_UNDYING_SENTINEL = 999  # effectively infinite undying during S3


def _s3_on_start(world, unit) -> None:
    unit.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))
    unit.buffs.append(Buff(
        axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
        value=_S3_ASPD_BONUS, source_tag=_S3_ASPD_BUFF_TAG,
    ))
    unit._s3_saved_undying = unit.undying_charges
    unit.undying_charges = _S3_UNDYING_SENTINEL
    world.log(f"{unit.name} Deathless Aegis — ATK+400%, ASPD+50, immortal for {_S3_DURATION}s")


def _s3_on_end(world, unit) -> None:
    unit.buffs = [b for b in unit.buffs if b.source_tag not in (_S3_ATK_BUFF_TAG, _S3_ASPD_BUFF_TAG)]
    unit.undying_charges = getattr(unit, "_s3_saved_undying", 0)
    world.log(f"{unit.name} Deathless Aegis ended")


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_specter(slot: str = "S2") -> UnitState:
    """Specter E2 max. Talent: undying save once (DEF+200%/immune 10s). S2: +160% ATK + lifesteal."""
    op = _base_stats()
    op.name = "Specter"
    op.archetype = RoleArchetype.GUARD_DREADNOUGHT
    op.profession = Profession.GUARD
    op.range_shape = DREADNOUGHT_RANGE
    op.block = 3
    op.cost = 23
    op.talents = [TalentComponent(name="Undying Will", behavior_tag=_UNDYING_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Pather's Light",
            slot="S2",
            sp_cost=40,
            initial_sp=20,
            duration=30.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Deathless Aegis",
            slot="S3",
            sp_cost=65,
            initial_sp=30,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
    return op
