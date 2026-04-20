"""Mlynar (玛恩纳) — 6★ Guard (Liberator archetype).

GUARD_LIBERATOR trait: Stops blocking and attacking when skill is not in use.
  Gradually increases ATK while skill is inactive (up to +200% over 40s).
  When skill activates: block and attacks are restored; ramped ATK is used.
  When skill ends: ATK ramp resets to 0; blocking/attacking suspended again.

Talent "Iron Will" (simplified E2 passive): the ATK ramp + combat-suspension
  mechanic is implemented as an always-active on_tick talent.

S3 "Father's Teachings": ASPD+90 for 25s. The +200% ATK is the accumulated
  ramp (not a separate skill buff). Block=3 restored during skill.
  sp_cost=55, initial_sp=30, AUTO_ATTACK, AUTO trigger.

Base stats from ArknightsGameData (E2 max, trust 100, char_4064_mlynar).
  HP=4266, ATK=385, DEF=502, RES=15, atk_interval=1.2s, cost=12, block=3.
  Note: block=0 on deploy; block=3 only during skill.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.mlynar import make_mlynar as _base_stats


LIBERATOR_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# ATK ramp constants — Terra Wiki: Guard/Liberator trait
_RAMP_MAX_RATIO = 2.0        # +200% ATK at full ramp
_RAMP_DURATION = 40.0        # seconds to reach max ramp
_RAMP_RATE = _RAMP_MAX_RATIO / _RAMP_DURATION  # per second
_RAMP_ATTR = "_liberator_ramp"
_RAMP_BUFF_TAG = "mlynar_ramp_atk"

_INACTIVE_ATK_CD = 9999.0    # prevents attacking when skill inactive

# --- S2: Blood of Iron ---
_S2_TAG = "mlynar_s2_blood_of_iron"
_S2_ATK_RATIO = 0.30
_S2_ASPD_FLAT = 40.0
_S2_BUFF_TAG = "mlynar_s2_buff"
_S2_DURATION = 20.0
_S2_BLOCK = 3

# S3 constants
_TALENT_TAG = "mlynar_iron_will"
_S3_TAG = "mlynar_s3_fathers_teachings"
_S3_BLOCK = 3
_S3_ASPD_FLAT = 90.0
_S3_DURATION = 25.0
_S3_ASPD_BUFF_TAG = "mlynar_s3_aspd"


def _set_ramp_buff(carrier: UnitState, ramp_value: float) -> None:
    """Upsert the ramp ATK buff in-place (avoid allocating a new Buff every tick)."""
    for b in carrier.buffs:
        if b.source_tag == _RAMP_BUFF_TAG:
            b.value = ramp_value
            return
    if ramp_value > 0.0:
        carrier.buffs.append(Buff(
            axis=BuffAxis.ATK, stack=BuffStack.RATIO,
            value=ramp_value, source_tag=_RAMP_BUFF_TAG,
        ))


def _clear_ramp_buff(carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _RAMP_BUFF_TAG]


def _iron_will_on_tick(world, carrier: UnitState, dt: float) -> None:
    if carrier.skill is not None and carrier.skill.active_remaining > 0:
        return  # skill active: don't suppress attacks or accumulate ramp
    # Skill inactive: suppress blocking and attacking
    carrier.block = 0
    carrier.atk_cd = _INACTIVE_ATK_CD
    ramp = getattr(carrier, _RAMP_ATTR, 0.0)
    ramp = min(ramp + _RAMP_RATE * dt, _RAMP_MAX_RATIO)
    setattr(carrier, _RAMP_ATTR, ramp)
    _set_ramp_buff(carrier, ramp)


register_talent(_TALENT_TAG, on_tick=_iron_will_on_tick)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.block = _S2_BLOCK
    carrier.atk_cd = 0.0
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
        value=_S2_ASPD_FLAT, source_tag=_S2_BUFF_TAG,
    ))
    world.log(f"Mlynar S2 Blood of Iron — ATK+{_S2_ATK_RATIO:.0%}, ASPD+{_S2_ASPD_FLAT}/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]
    _clear_ramp_buff(carrier)
    setattr(carrier, _RAMP_ATTR, 0.0)
    carrier.block = 0


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.block = _S3_BLOCK
    carrier.atk_cd = 0.0  # immediate first attack after activation
    carrier.buffs.append(Buff(
        axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
        value=_S3_ASPD_FLAT, source_tag=_S3_ASPD_BUFF_TAG,
    ))


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_ASPD_BUFF_TAG]
    _clear_ramp_buff(carrier)
    setattr(carrier, _RAMP_ATTR, 0.0)
    carrier.block = 0


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_mlynar(slot: str = "S3") -> UnitState:
    """Mlynar E2 max. GUARD_LIBERATOR: ATK ramps +200% over 40s when skill inactive; block=0 when off."""
    op = _base_stats()
    op.name = "Mlynar"
    op.archetype = RoleArchetype.GUARD_LIBERATOR
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = True
    op.range_shape = LIBERATOR_RANGE
    op.block = 0    # starts inactive — talent restores to 3 on skill fire
    op.cost = 12
    op.atk_cd = _INACTIVE_ATK_CD  # prevent first-tick attack before talent runs

    op.talents = [TalentComponent(name="Iron Will", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Blood of Iron",
            slot="S2",
            sp_cost=35,
            initial_sp=15,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Father's Teachings",
            slot="S3",
            sp_cost=55,
            initial_sp=30,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
    return op
