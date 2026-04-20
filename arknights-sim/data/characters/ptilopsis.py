"""Ptilopsis (白面鸮) — 5* Medic (Single-target archetype).

Talent "Unisonant" (E2): While deployed, all operators gain +0.3 SP/s.
  Applies to all SP gain modes (AUTO_TIME, AUTO_ATTACK, AUTO_DEFENSIVE).
  Respects can_use_skill() — silenced/stunned units do not benefit.
S1 "Dawn's Resonance": +50% ATK for 25s (boosts heal output). sp_cost=25, initial=10.
S2 "Night Cure": +80% ATK for 20s + heals ALL allies in range for 70% ATK per second.
  sp_cost=30, initial_sp=12, AUTO_TIME, AUTO trigger, requires_target=False.
S3 "Dream Catcher": ATK+100% + Unisonant talent upgrades to +0.6 SP/s during skill.
  sp_cost=35, initial_sp=12, AUTO_TIME, MANUAL, 30s.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from math import sqrt
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
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
_SP_RATE = 0.3           # SP/s to all operators (base)
_SP_RATE_S3 = 0.6        # SP/s during S3 (doubled)
_SP_FRAC_ATTR = "_ptilopsis_sp_frac"
_S3_ACTIVE_ATTR = "_ptilopsis_s3_active"


def _unisonant_on_tick(world, carrier, dt: float) -> None:
    rate = _SP_RATE_S3 if getattr(carrier, _S3_ACTIVE_ATTR, False) else _SP_RATE
    frac = getattr(carrier, _SP_FRAC_ATTR, 0.0) + rate * dt
    sp_bonus = frac
    if sp_bonus >= 0.01:   # avoid accumulating tiny float every tick
        now = world.global_state.elapsed
        for ally in world.allies():
            if ally is carrier:
                continue
            if ally.skill is None or not ally.can_use_skill():
                continue
            sk = ally.skill
            if sk.active_remaining <= 0.0 and sk.sp < sk.sp_cost:
                if now >= sk.sp_lockout_until:
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


# --- S2: Night Cure — ATK+80% + AoE heal all allies in range per second ---
_S2_TAG = "ptilopsis_s2_night_cure"
_S2_ATK_RATIO = 0.80
_S2_BUFF_TAG = "ptilopsis_s2_atk_buff"
_S2_HEAL_PER_SEC = 0.70      # heal = 70% of effective ATK per second to each ally
_S2_RANGE = 3.0              # tile radius matching MEDIC_RANGE extent
_S2_HEAL_ACCUM = "_ptilopsis_s2_heal_accum"


def _s2_on_start(world, unit) -> None:
    unit.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    setattr(unit, _S2_HEAL_ACCUM, 0.0)
    world.log(f"Ptilopsis S2 Night Cure — ATK+{_S2_ATK_RATIO:.0%}, AoE heal {_S2_HEAL_PER_SEC:.0%} ATK/s")


def _s2_on_tick(world, unit, dt: float) -> None:
    accum = getattr(unit, _S2_HEAL_ACCUM, 0.0) + dt
    heal_events = int(accum)   # fire whole-second heal pulses
    if heal_events > 0 and unit.position is not None:
        px, py = unit.position
        heal_amount = int(unit.effective_atk * _S2_HEAL_PER_SEC * heal_events)
        for ally in world.allies():
            if ally is unit or not ally.alive or not ally.deployed:
                continue
            if ally.position is None:
                continue
            ax, ay = ally.position
            if sqrt((ax - px) ** 2 + (ay - py) ** 2) <= _S2_RANGE:
                ally.heal(heal_amount)
    setattr(unit, _S2_HEAL_ACCUM, accum - heal_events)


def _s2_on_end(world, unit) -> None:
    unit.buffs = [b for b in unit.buffs if b.source_tag != _S2_BUFF_TAG]
    setattr(unit, _S2_HEAL_ACCUM, 0.0)
    world.log("Ptilopsis S2 ended")


register_skill(_S2_TAG, on_start=_s2_on_start, on_tick=_s2_on_tick, on_end=_s2_on_end)


# --- S3: Dream Catcher — ATK+100% + Unisonant upgrades to 0.6 SP/s ---
_S3_TAG = "ptilopsis_s3_dream_catcher"
_S3_ATK_RATIO = 1.00
_S3_ATK_BUFF_TAG = "ptilopsis_s3_atk"
_S3_DURATION = 30.0


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))
    setattr(carrier, _S3_ACTIVE_ATTR, True)
    world.log(f"Ptilopsis S3 Dream Catcher — ATK+{_S3_ATK_RATIO:.0%}, Unisonant → {_SP_RATE_S3} SP/s")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_ATK_BUFF_TAG]
    setattr(carrier, _S3_ACTIVE_ATTR, False)


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_ptilopsis(slot: str = "S1") -> UnitState:
    """Ptilopsis E2 max. Talent: +0.3 SP/s to all operators. S1: +50% ATK. S2: +80% ATK + AoE heal 70% ATK/s."""
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
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Dream Catcher",
            slot="S3",
            sp_cost=35,
            initial_sp=12,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Night Cure",
            slot="S2",
            sp_cost=30,
            initial_sp=12,
            duration=20.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
