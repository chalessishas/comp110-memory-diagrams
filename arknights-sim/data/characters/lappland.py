"""Lappland (拉普兰德) — 6* Guard (Swordmaster archetype).

Talent "Blade Arts": Each attack applies SILENCE (3s) to the target.
  SILENCE blocks skill SP accumulation and skill activation.
  Applied via on_attack_hit; refreshes on every subsequent hit.

S2 "Starvation": 30s duration, ATK +80%.
  sp_cost=35, initial_sp=15, AUTO_TIME, AUTO trigger, requires_target=True.
  (Multi-hit simplified: +80% ATK single-target, no dual-strike mechanics.)

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape,
    TalentComponent, StatusEffect,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.lappland import make_lappland as _base_stats


GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# --- Talent: Blade Arts ---
_TALENT_TAG = "lappland_blade_arts"
_SILENCE_DURATION = 3.0
_SILENCE_TAG = "lappland_silence"

# --- S2: Starvation ---
_S2_TAG = "lappland_s2_starvation"
_S2_ATK_RATIO = 0.80
_S2_BUFF_TAG = "lappland_s2_atk_buff"
_S2_DURATION = 30.0


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    # Refresh SILENCE: remove stale, apply fresh
    target.statuses = [s for s in target.statuses if s.source_tag != _SILENCE_TAG]
    target.statuses.append(StatusEffect(
        kind=StatusKind.SILENCE,
        source_tag=_SILENCE_TAG,
        expires_at=world.global_state.elapsed + _SILENCE_DURATION,
    ))
    world.log(
        f"Lappland Blade Arts → {target.name}  silence ({_SILENCE_DURATION}s)"
    )


register_talent(_TALENT_TAG, on_attack_hit=_talent_on_attack_hit)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_lappland(slot: str = "S2") -> UnitState:
    """Lappland E2 max. Talent: SILENCE on every hit. S2: ATK burst."""
    op = _base_stats()
    op.name = "Lappland"
    op.archetype = RoleArchetype.GUARD_SWORDMASTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    op.cost = 18

    op.talents = [TalentComponent(name="Blade Arts", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Starvation",
            slot="S2",
            sp_cost=35,
            initial_sp=15,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    return op
