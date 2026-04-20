"""Ptilopsis (白面鸮) — 5* Medic (Single-target archetype).

Talent "Unisonant" (E2): While deployed, all operators gain +0.3 SP/s.
  Applies to all SP gain modes (AUTO_TIME, AUTO_ATTACK, AUTO_DEFENSIVE).
  Respects can_use_skill() — silenced/stunned units do not benefit.
S1 "Dawn's Resonance": +50% ATK for 25s (boosts heal output). sp_cost=25, initial=10.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape, TalentComponent
from core.types import (
    Profession, RoleArchetype, SPGainMode, SkillTrigger, AttackType,
    BuffAxis, BuffStack,
)
from core.state.unit_state import Buff
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.plosis import make_plosis as _base_stats


# Standard medic range: 3 forward tiles
MEDIC_RANGE = RangeShape(tiles=((1, 0), (2, 0), (3, 0), (1, -1), (1, 1)))

# --- Talent: Unisonant ---
_UNISONANT_TAG = "ptilopsis_unisonant"
_SP_RATE = 0.3   # SP/s to all operators
_SP_FRAC_ATTR = "_ptilopsis_sp_frac"


def _unisonant_on_tick(world, carrier, dt: float) -> None:
    frac = getattr(carrier, _SP_FRAC_ATTR, 0.0) + _SP_RATE * dt
    sp_bonus = frac
    if sp_bonus >= 0.01:   # avoid accumulating tiny float every tick
        for ally in world.allies():
            if ally is carrier:
                continue
            if ally.skill is None or not ally.can_use_skill():
                continue
            sk = ally.skill
            if sk.active_remaining <= 0.0 and sk.sp < sk.sp_cost:
                sk.sp = min(sk.sp + sp_bonus, float(sk.sp_cost))
        setattr(carrier, _SP_FRAC_ATTR, 0.0)
    else:
        setattr(carrier, _SP_FRAC_ATTR, sp_bonus)


register_talent(_UNISONANT_TAG, on_tick=_unisonant_on_tick)


# --- S1: Dawn's Resonance — +50% ATK for 25s ---
_S1_TAG = "ptilopsis_s1_dawn_resonance"
_S1_ATK_RATIO = 0.50
_S1_BUFF_TAG = "ptilopsis_s1_atk_buff"


def _s1_on_start(world, unit) -> None:
    unit.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG,
    ))


def _s1_on_end(world, unit) -> None:
    unit.buffs = [b for b in unit.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_ptilopsis(slot: str = "S1") -> UnitState:
    """Ptilopsis E2 max. Talent: +0.3 SP/s to all operators. S1: +50% ATK heal buff."""
    op = _base_stats()
    op.name = "Ptilopsis"
    op.archetype = RoleArchetype.MEDIC_ST
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.HEAL
    op.range_shape = MEDIC_RANGE
    op.block = 1
    op.cost = 17
    op.talents = [TalentComponent(name="Unisonant", behavior_tag=_UNISONANT_TAG)]

    if slot == "S1":
        op.skill = SkillComponent(
            name="Dawn's Resonance",
            slot="S1",
            sp_cost=25,
            initial_sp=10,
            duration=25.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
    return op
