"""Gnosis (灵知) — 6* Supporter (Hexer archetype).

Talent "Theoretical Analysis" (simplified): Each attack reduces the target's
  RES by 15 (flat) for 2s. Applied as both a StatusEffect (visibility) and a
  timed Buff (mechanical: BuffAxis.RES, FLAT, -15). Refreshes on each hit.

S2 "Frozen Silence" (simplified): 20s duration, ATK +80%.
  sp_cost=30, initial_sp=15, AUTO_TIME, AUTO trigger, requires_target=True.

Base stats from ArknightsGameData (E2 max, trust 100).
Note: COLD/FREEZE chain (actual talent second effect) deferred.
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
from data.characters.generated.gnosis import make_gnosis as _base_stats


SUPPORTER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 4) for dy in range(-1, 2)
))

# --- Talent: Theoretical Analysis ---
_TALENT_TAG = "gnosis_theoretical_analysis"
_RES_DOWN_AMOUNT = 15.0       # flat RES reduction
_RES_DOWN_DURATION = 2.0
_RES_DOWN_TAG = "gnosis_res_down"

# --- S2: Frozen Silence ---
_S2_TAG = "gnosis_s2_frozen_silence"
_S2_ATK_RATIO = 0.80
_S2_BUFF_TAG = "gnosis_s2_atk_buff"
_S2_DURATION = 20.0


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    expires = world.global_state.elapsed + _RES_DOWN_DURATION
    # Remove stale RES_DOWN status + buff (refresh semantics)
    target.statuses = [s for s in target.statuses if s.source_tag != _RES_DOWN_TAG]
    target.buffs = [b for b in target.buffs if b.source_tag != _RES_DOWN_TAG]
    # StatusEffect for visibility / has_status() checks
    target.statuses.append(StatusEffect(
        kind=StatusKind.RES_DOWN,
        source_tag=_RES_DOWN_TAG,
        expires_at=expires,
        params={"amount": _RES_DOWN_AMOUNT},
    ))
    # Buff for mechanical effect — negative FLAT reduces effective RES
    target.buffs.append(Buff(
        axis=BuffAxis.RES,
        stack=BuffStack.FLAT,
        value=-_RES_DOWN_AMOUNT,
        source_tag=_RES_DOWN_TAG,
        expires_at=expires,
    ))
    world.log(
        f"Gnosis Theoretical Analysis → {target.name}  "
        f"RES -{_RES_DOWN_AMOUNT:.0f} ({_RES_DOWN_DURATION}s)"
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


def make_gnosis(slot: str = "S2") -> UnitState:
    """Gnosis E2 max. Talent: RES_DOWN -15 on every hit. S2: ATK burst."""
    op = _base_stats()
    op.name = "Gnosis"
    op.archetype = RoleArchetype.SUP_HEXER
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.range_shape = SUPPORTER_RANGE
    op.cost = 13

    op.talents = [TalentComponent(name="Theoretical Analysis", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Frozen Silence",
            slot="S2",
            sp_cost=30,
            initial_sp=15,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    return op
