"""Ethan (伊桑) — 5* Specialist (Ambusher archetype).

Talent "Neurotoxin": each normal attack applies ATK_DOWN (flat -200 ATK)
  to the target for 2s. Refresh semantics.

S2 "Venom Burst": ATK +50%, 15s duration.
  sp_cost=20, initial_sp=10, AUTO_TIME, AUTO trigger, requires_target=True.

S3 "Binding Storm" (毒缚风暴): MANUAL, 20s duration.
  ATK +100%. Each attack hit also applies BIND (3s) to the target.
  sp_cost=40, initial_sp=10, AUTO_TIME.

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
from data.characters.generated.ethan import make_ethan as _base_stats


AMBUSHER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 3) for dy in range(-1, 2)
))

# --- Talent: Neurotoxin ---
_TALENT_TAG = "ethan_neurotoxin"
_ATK_DOWN_AMOUNT = 200   # flat ATK reduction
_ATK_DOWN_DURATION = 2.0
_ATK_DOWN_TAG = "ethan_atk_down"

# --- S2: Venom Burst ---
_S2_TAG = "ethan_s2_venom_burst"
_S2_ATK_RATIO = 0.50
_S2_BUFF_TAG = "ethan_s2_atk"
_S2_DURATION = 15.0

# --- S3: Binding Storm ---
_S3_TAG = "ethan_s3_binding_storm"
_S3_ATK_RATIO = 1.00   # ATK +100%
_S3_BUFF_TAG = "ethan_s3_atk"
_S3_BIND_DURATION = 3.0
_S3_BIND_TAG = "ethan_s3_bind"
_S3_DURATION = 20.0
_S3_ACTIVE_ATTR = "_ethan_s3_active"


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    elapsed = world.global_state.elapsed
    expires = elapsed + _ATK_DOWN_DURATION

    target.statuses = [s for s in target.statuses if s.source_tag != _ATK_DOWN_TAG]
    target.buffs = [b for b in target.buffs if b.source_tag != _ATK_DOWN_TAG]

    target.statuses.append(StatusEffect(
        kind=StatusKind.ATK_DOWN,
        source_tag=_ATK_DOWN_TAG,
        expires_at=expires,
        params={"amount": _ATK_DOWN_AMOUNT},
    ))
    target.buffs.append(Buff(
        axis=BuffAxis.ATK,
        stack=BuffStack.FLAT,
        value=-_ATK_DOWN_AMOUNT,
        source_tag=_ATK_DOWN_TAG,
        expires_at=expires,
    ))
    world.log(
        f"Ethan Neurotoxin → {target.name}  "
        f"ATK_DOWN -{_ATK_DOWN_AMOUNT} ({_ATK_DOWN_DURATION}s)"
    )
    # S3 Binding Storm: also apply BIND on hit while active
    if getattr(attacker, _S3_ACTIVE_ATTR, False):
        target.statuses = [s for s in target.statuses if s.source_tag != _S3_BIND_TAG]
        target.statuses.append(StatusEffect(
            kind=StatusKind.BIND,
            source_tag=_S3_BIND_TAG,
            expires_at=elapsed + _S3_BIND_DURATION,
        ))


register_talent(_TALENT_TAG, on_attack_hit=_talent_on_attack_hit)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))
    setattr(carrier, _S3_ACTIVE_ATTR, True)
    world.log(f"Ethan S3 Binding Storm — ATK+{_S3_ATK_RATIO:.0%}, BIND on hit ({_S3_DURATION}s)")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]
    setattr(carrier, _S3_ACTIVE_ATTR, False)


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_ethan(slot: str = "S2") -> UnitState:
    """Ethan E2 max. Talent: ATK_DOWN -200 on every hit. S2: ATK +50%."""
    op = _base_stats()
    op.name = "Ethan"
    op.archetype = RoleArchetype.SPEC_AMBUSHER
    op.profession = Profession.SPECIALIST
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = AMBUSHER_RANGE
    op.cost = 19

    op.talents = [TalentComponent(name="Neurotoxin", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Venom Burst",
            slot="S2",
            sp_cost=20,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Binding Storm",
            slot="S3",
            sp_cost=40,
            initial_sp=10,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
    return op
