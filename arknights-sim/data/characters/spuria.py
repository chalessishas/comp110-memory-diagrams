"""Spuria (空构) — 5* Specialist (Dollkeeper archetype).

SPEC_DOLLKEEPER archetype: Survives one fatal hit by switching to a substitute
  body. The substitution fires in the same tick as the fatal damage via
  the on_tick talent callback reading `_undying_just_triggered`.

Talent "Contract of the Substitute": When the fatal-hit undying charge
  triggers (hp would reach 0 but undying_charges > 0 saves it):
    - HP is restored to _SUBSTITUTE_HP_RATIO of max_hp (≈30% = ~628 HP)
    - A self-DOT is applied (_SUBSTITUTE_DRAIN_DPS for _SUBSTITUTE_DURATION)
      to simulate the substitute body draining over time
  The transformation fires once per deployment (undying_charges = 1).

S1 "Hollow Burst": ATK +80% for 8s.
  sp_cost=10, initial_sp=5, AUTO_TIME, AUTO trigger, requires_target=True.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape,
    TalentComponent, StatusEffect,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.spuria import make_spuria as _base_stats


EXECUTOR_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# --- Talent: Contract of the Substitute ---
_TALENT_TAG = "spuria_dollkeeper_contract"
_SUBSTITUTE_HP_RATIO = 0.30       # restore to 30% of max_hp on switch
_SUBSTITUTE_DRAIN_DPS = 80.0      # HP drain per second in substitute form
_SUBSTITUTE_DURATION = 20.0       # substitute body lasts up to 20s
_SUBSTITUTE_DOT_TAG = "spuria_substitute_drain"

# --- S2: Puppet Control ---
_S2_TAG = "spuria_s2_puppet_control"
_S2_ATK_RATIO = 1.20         # ATK +120% for duration
_S2_BUFF_TAG = "spuria_s2_atk"
_S2_DURATION = 15.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    # Restore substitute charge if it has been spent
    if carrier.undying_charges == 0:
        carrier.undying_charges = 1
        world.log(f"Spuria S2 — substitute charge restored")
    world.log(f"Spuria S2 Puppet Control — ATK+{_S2_ATK_RATIO:.0%}/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# --- S1: Hollow Burst ---
_S1_TAG = "spuria_s1_hollow_burst"
_S1_ATK_RATIO = 0.80
_S1_BUFF_TAG = "spuria_s1_atk"
_S1_DURATION = 8.0


def _talent_on_tick(world, carrier: UnitState, dt: float) -> None:
    if not getattr(carrier, '_undying_just_triggered', False):
        return
    carrier._undying_just_triggered = False

    # Substitute body: restore HP to 30% max_hp
    carrier.hp = max(1, int(carrier.max_hp * _SUBSTITUTE_HP_RATIO))

    # Apply self-DOT drain (simulates substitute body HP bleeding over time)
    elapsed = world.global_state.elapsed
    carrier.statuses = [
        s for s in carrier.statuses if s.source_tag != _SUBSTITUTE_DOT_TAG
    ]
    carrier.statuses.append(StatusEffect(
        kind=StatusKind.DOT,
        source_tag=_SUBSTITUTE_DOT_TAG,
        expires_at=elapsed + _SUBSTITUTE_DURATION,
        params={"dps": _SUBSTITUTE_DRAIN_DPS},
    ))
    world.log(
        f"Spuria → substitute body activated  "
        f"HP={carrier.hp}/{carrier.max_hp}  "
        f"drain {_SUBSTITUTE_DRAIN_DPS:.0f} DPS / {_SUBSTITUTE_DURATION}s"
    )


register_talent(_TALENT_TAG, on_tick=_talent_on_tick)


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG,
    ))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_spuria(slot: str = "S1") -> UnitState:
    """Spuria E2 max. Talent: substitute body on fatal (30% HP restore + self-DOT). S1: ATK+80%/8s."""
    op = _base_stats()
    op.name = "Spuria"
    op.archetype = RoleArchetype.SPEC_DOLLKEEPER
    op.profession = Profession.SPECIALIST
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = EXECUTOR_RANGE
    op.block = 1
    op.cost = 12
    op.undying_charges = 1   # one substitute body activation per deployment

    op.talents = [TalentComponent(
        name="Contract of the Substitute",
        behavior_tag=_TALENT_TAG,
    )]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Puppet Control",
            slot="S2",
            sp_cost=25,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S1":
        op.skill = SkillComponent(
            name="Hollow Burst",
            slot="S1",
            sp_cost=10,
            initial_sp=5,
            duration=_S1_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
    return op
