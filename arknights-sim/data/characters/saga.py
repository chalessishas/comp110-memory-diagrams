"""Saga (嵯峨) — 5* Vanguard (Warrior archetype).

Talent "Tengu's Edge": When SP is at maximum (sp ≥ sp_cost), ATK +12%.
  Buff disappears the same tick the skill fires (sp drops to 0 on activation).
  Implemented via on_tick conditional buff.

S2 "Tsurugi": 30s duration, ATK +120%.
  sp_cost=35, initial_sp=10, AUTO_TIME, AUTO trigger, requires_target=True.

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
from data.characters.generated.saga import make_saga as _base_stats


GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# --- Talent: Tengu's Edge ---
_TALENT_TAG = "saga_tengus_edge"
_TALENT_ATK_RATIO = 0.12    # ATK +12% when SP is full
_TALENT_BUFF_TAG = "saga_tengus_edge_atk"

# --- S2: Tsurugi ---
_S2_TAG = "saga_s2_tsurugi"
_S2_ATK_RATIO = 1.20        # ATK +120%
_S2_BUFF_TAG = "saga_s2_atk_buff"
_S2_DURATION = 30.0


def _talent_on_tick(world, carrier: UnitState, dt: float) -> None:
    sk = carrier.skill
    is_sp_full = sk is not None and sk.active_remaining == 0.0 and sk.sp >= sk.sp_cost
    has_buff = any(b.source_tag == _TALENT_BUFF_TAG for b in carrier.buffs)
    if is_sp_full and not has_buff:
        carrier.buffs.append(Buff(
            axis=BuffAxis.ATK, stack=BuffStack.RATIO,
            value=_TALENT_ATK_RATIO, source_tag=_TALENT_BUFF_TAG,
        ))
    elif not is_sp_full and has_buff:
        carrier.buffs = [b for b in carrier.buffs if b.source_tag != _TALENT_BUFF_TAG]


register_talent(_TALENT_TAG, on_tick=_talent_on_tick)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_saga(slot: str = "S2") -> UnitState:
    """Saga E2 max. Talent: ATK buff at full SP. S2: ATK burst 30s."""
    op = _base_stats()
    op.name = "Saga"
    op.archetype = RoleArchetype.GUARD_FIGHTER
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    op.cost = 14

    op.talents = [TalentComponent(name="Tengu's Edge", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Tsurugi",
            slot="S2",
            sp_cost=35,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    return op
