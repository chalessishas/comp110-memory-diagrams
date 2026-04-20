"""Vigna — 4* Vanguard (Charger archetype).

Charger class trait: gains 1 DP when this unit kills an enemy.
Talent "Fierce Stabbing" (E2): 10% crit (×1.5 dmg); 30% during skill active.
  Implemented via crit_chance field on UnitState + world.rng in combat_system.
Skill S2 "Hammer-On" (rank VII, E2):
  ATK +200%, Attack Interval +0.5s for 30s.
  sp_cost=25, initial_sp=10, AUTO_TIME, MANUAL trigger.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.talent_registry import register_talent
from core.systems.skill_system import register_skill
from data.characters.generated.vigna import make_vigna as _base_stats
from data.characters.registry import _CHARGER_DP_TAG


CHARGER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_FIERCE_STABBING_TAG = "vigna_fierce_stabbing"
_CRIT_BASE = 0.10
_CRIT_SKILL = 0.30

_S2_TAG = "vigna_s2_hammer_on"
_S2_ATK_TAG = "vigna_s2_atk"
_S2_INTERVAL_TAG = "vigna_s2_interval"
_S2_ATK_RATIO = 2.0    # +200% ATK
_S2_INTERVAL = 0.5     # +0.5s attack interval


def _fierce_stabbing_on_tick(world, carrier: UnitState, dt: float) -> None:
    sk = carrier.skill
    is_skill_active = sk is not None and sk.active_remaining > 0
    carrier.crit_chance = _CRIT_SKILL if is_skill_active else _CRIT_BASE


register_talent(_FIERCE_STABBING_TAG, on_tick=_fierce_stabbing_on_tick)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK_INTERVAL, stack=BuffStack.FLAT,
        value=_S2_INTERVAL, source_tag=_S2_INTERVAL_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S2_ATK_TAG, _S2_INTERVAL_TAG)]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_vigna() -> UnitState:
    """Vigna E2 max. Charger trait: +1 DP on kill. Fierce Stabbing: 10%/30% crit."""
    op = _base_stats()
    op.name = "Vigna"
    op.archetype = RoleArchetype.VAN_CHARGER
    op.range_shape = CHARGER_RANGE
    op.block = 1
    op.cost = 11
    op.talents = [
        TalentComponent(name="Fierce Stabbing", behavior_tag=_FIERCE_STABBING_TAG),
        TalentComponent(name="Charger (DP on kill)", behavior_tag=_CHARGER_DP_TAG),
    ]
    op.skill = SkillComponent(
        name="Hammer-On", slot="S2",
        sp_cost=25, initial_sp=10, duration=30.0,
        sp_gain_mode=SPGainMode.AUTO_TIME,
        trigger=SkillTrigger.MANUAL,
        behavior_tag=_S2_TAG,
    )
    op.skill.sp = float(op.skill.initial_sp)
    return op
