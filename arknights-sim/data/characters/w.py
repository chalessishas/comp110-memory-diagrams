"""W (W) — 6* Sniper.

Talent "Last Will" (simplified): Each attack levitates the target for 1.5s.
  Levitated enemies cannot move or attack (can_act() = False).
  Refreshes on every subsequent hit.
  Original: kill-stacking explosive chain; simplified to on-hit LEVITATE.

S2 "Extra Supplies" (simplified): 15s duration, ATK +60%.
  sp_cost=30, initial_sp=10, AUTO_TIME, AUTO trigger, requires_target=True.

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
from data.characters.generated.cqbw import make_cqbw as _base_stats


SNIPER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 5) for dy in range(-1, 2)
))

# --- Talent: Last Will ---
_TALENT_TAG = "w_last_will"
_LEVITATE_DURATION = 1.5
_LEVITATE_TAG = "w_levitate"

# --- S2: Extra Supplies ---
_S2_TAG = "w_s2_extra_supplies"
_S2_ATK_RATIO = 0.60
_S2_BUFF_TAG = "w_s2_atk_buff"
_S2_DURATION = 15.0


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    # Refresh LEVITATE: remove stale, apply fresh
    target.statuses = [s for s in target.statuses if s.source_tag != _LEVITATE_TAG]
    target.statuses.append(StatusEffect(
        kind=StatusKind.LEVITATE,
        source_tag=_LEVITATE_TAG,
        expires_at=world.global_state.elapsed + _LEVITATE_DURATION,
    ))
    world.log(
        f"W Last Will → {target.name}  levitate ({_LEVITATE_DURATION}s)"
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


def make_w(slot: str = "S2") -> UnitState:
    """W E2 max. Talent: LEVITATE on every hit. S2: ATK burst."""
    op = _base_stats()
    op.name = "W"
    op.archetype = RoleArchetype.SNIPER_SIEGE
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNIPER_RANGE
    op.cost = 29

    op.talents = [TalentComponent(name="Last Will", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Extra Supplies",
            slot="S2",
            sp_cost=30,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    return op
