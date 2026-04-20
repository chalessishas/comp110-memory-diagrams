"""Surtr (史尔特尔) — 6* Guard (Reaper archetype).

Talent "Dainsleif": When HP ≤ 50% max_hp, ATK +35%. Conditional buff via on_tick.
  Removes the buff if HP recovers above the threshold.

S3 "Tyrant of the Undying Flames": 40s duration.
  - ATK +200% for full duration (arts attacks).
  - First 10s: normal operation.
  - After 10s: HP drains at 4% of max_hp per second (true damage).
  - Surtr naturally dies if drain empties HP to 0.
  sp_cost=40, initial_sp=20, AUTO_TIME, AUTO trigger, requires_target=True.

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
from data.characters.generated.surtr import make_surtr as _base_stats


GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# --- Talent: Dainsleif ---
_TALENT_TAG = "surtr_dainsleif"
_TALENT_ATK_RATIO = 0.35      # +35% ATK when HP ≤ threshold
_HP_THRESHOLD = 0.50           # ≤ 50% max_hp
_DAINSLEIF_BUFF_TAG = "surtr_dainsleif_atk"


def _talent_on_tick(world, carrier: UnitState, dt: float) -> None:
    is_low_hp = carrier.hp / carrier.max_hp <= _HP_THRESHOLD
    has_buff = any(b.source_tag == _DAINSLEIF_BUFF_TAG for b in carrier.buffs)
    if is_low_hp and not has_buff:
        carrier.buffs.append(Buff(
            axis=BuffAxis.ATK, stack=BuffStack.RATIO,
            value=_TALENT_ATK_RATIO, source_tag=_DAINSLEIF_BUFF_TAG,
        ))
    elif not is_low_hp and has_buff:
        carrier.buffs = [b for b in carrier.buffs if b.source_tag != _DAINSLEIF_BUFF_TAG]


register_talent(_TALENT_TAG, on_tick=_talent_on_tick)


# --- S2: Radiant Phoenix ---
_S2_TAG = "surtr_s2_radiant_phoenix"
_S2_ATK_RATIO = 0.70     # ATK +70%
_S2_BUFF_TAG = "surtr_s2_atk_buff"
_S2_DURATION = 20.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    world.log(f"Surtr S2 Radiant Phoenix — ATK+{_S2_ATK_RATIO:.0%}/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# --- S3: Tyrant of the Undying Flames ---
_S3_TAG = "surtr_s3_tyrant"
_S3_DURATION = 40.0
_S3_ATK_RATIO = 2.00      # +200% ATK
_S3_DRAIN_DELAY = 10.0    # drain starts after 10s (active_remaining < duration - delay)
_S3_DRAIN_RATE = 0.04     # 4% max_hp per second
_S3_BUFF_TAG = "surtr_s3_atk_buff"
_S3_DRAIN_ACCUM = "_surtr_s3_drain_accum"


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))
    setattr(carrier, _S3_DRAIN_ACCUM, 0.0)
    # Override attack type to arts during S3
    carrier._saved_attack_type = carrier.attack_type
    carrier.attack_type = AttackType.ARTS


def _s3_on_tick(world, carrier: UnitState, dt: float) -> None:
    if not carrier.alive:
        return
    elapsed = _S3_DURATION - carrier.skill.active_remaining
    if elapsed < _S3_DRAIN_DELAY:
        return
    # HP drain phase
    drain_accum = getattr(carrier, _S3_DRAIN_ACCUM, 0.0) + _S3_DRAIN_RATE * carrier.max_hp * dt
    whole = int(drain_accum)
    if whole > 0:
        carrier.take_true(whole)
        world.log(f"Surtr S3 drain → self  -{whole}  ({carrier.hp}/{carrier.max_hp})")
        if not carrier.alive:
            # Drain killed Surtr — clean up skill effects immediately
            _s3_on_end(world, carrier)
            return
    setattr(carrier, _S3_DRAIN_ACCUM, drain_accum - whole)


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]
    saved = getattr(carrier, "_saved_attack_type", None)
    if saved is not None:
        carrier.attack_type = saved


register_skill(_S3_TAG, on_start=_s3_on_start, on_tick=_s3_on_tick, on_end=_s3_on_end)


def make_surtr(slot: str = "S3") -> UnitState:
    """Surtr E2 max. Talent: conditional ATK buff. S3: ATK burst + HP drain."""
    op = _base_stats()
    op.name = "Surtr"
    op.archetype = RoleArchetype.GUARD_REAPER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.ARTS
    op.range_shape = GUARD_RANGE
    op.cost = 21

    op.talents = [TalentComponent(name="Dainsleif", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Radiant Phoenix",
            slot="S2",
            sp_cost=25,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Tyrant of the Undying Flames",
            slot="S3",
            sp_cost=40,
            initial_sp=20,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
    return op
