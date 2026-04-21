"""Bubble (泡泡) — 5★ Defender (Protector archetype).

DEF_PROTECTOR archetype: standard high-DEF Defender; no separate trait mechanic.

Talent "Foam Guard" (E2):
  Once per deployment, when HP falls below _TALENT_HP_THRESHOLD, apply a SHIELD
  equal to _TALENT_SHIELD_RATIO × max_hp to self.

S2 "Surfing Time": MANUAL.
  Apply SHIELD = _S2_SHIELD_RATIO × max_hp to self and increase DEF by _S2_DEF_BUFF
  for _S2_DURATION seconds.
  sp_cost=40, initial_sp=15, AUTO_TIME, AUTO trigger.

Base stats from ArknightsGameData (E2 max, trust 100, char_381_bubble):
  HP=3416, ATK=370, DEF=720, RES=0, atk_interval=1.2s, cost=21, block=3.
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, TalentComponent, StatusEffect,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.bubble import make_bubble as _base_stats


_TALENT_TAG = "bubble_foam_guard"
_TALENT_HP_THRESHOLD = 0.50
_TALENT_SHIELD_RATIO = 0.50
_TALENT_SHIELD_TAG = "bubble_foam_guard_shield"

_S2_TAG = "bubble_s2_surfing_time"
_S2_SHIELD_RATIO = 0.60
_S2_DEF_BUFF = 300
_S2_DURATION = 20.0
_S2_SHIELD_TAG = "bubble_s2_shield"
_S2_BUFF_TAG = "bubble_s2_def"

# --- S3: Grand Surf ---
_S3_TAG = "bubble_s3_grand_surf"
_S3_SHIELD_RATIO = 1.00   # SHIELD = 100% max_hp
_S3_DEF_BUFF = 600
_S3_DURATION = 25.0
_S3_SHIELD_TAG = "bubble_s3_shield"
_S3_DEF_BUFF_TAG = "bubble_s3_def"


def _talent_on_tick(world, unit: UnitState, dt: float) -> None:
    if getattr(unit, "_bubble_shield_triggered", False):
        return
    if unit.hp / unit.max_hp < _TALENT_HP_THRESHOLD:
        unit._bubble_shield_triggered = True
        shield_hp = int(unit.max_hp * _TALENT_SHIELD_RATIO)
        unit.statuses.append(StatusEffect(
            kind=StatusKind.SHIELD,
            source_tag=_TALENT_SHIELD_TAG,
            params={"amount": shield_hp},
        ))
        world.log(
            f"Bubble Foam Guard triggered — SHIELD {shield_hp} HP "
            f"({unit.hp}/{unit.max_hp} HP = {unit.hp / unit.max_hp:.0%})"
        )


register_talent(_TALENT_TAG, on_tick=_talent_on_tick)


def _s2_on_start(world, carrier: UnitState) -> None:
    shield_hp = int(carrier.max_hp * _S2_SHIELD_RATIO)
    carrier.statuses.append(StatusEffect(
        kind=StatusKind.SHIELD,
        source_tag=_S2_SHIELD_TAG,
        params={"amount": shield_hp},
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.FLAT,
        value=_S2_DEF_BUFF, source_tag=_S2_BUFF_TAG,
    ))
    world.log(f"Bubble Surfing Time — SHIELD {shield_hp} HP, DEF +{_S2_DEF_BUFF}")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.statuses = [s for s in carrier.statuses if s.source_tag != _S2_SHIELD_TAG]
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def _s3_on_start(world, carrier: UnitState) -> None:
    shield_hp = int(carrier.max_hp * _S3_SHIELD_RATIO)
    carrier.statuses.append(StatusEffect(
        kind=StatusKind.SHIELD,
        source_tag=_S3_SHIELD_TAG,
        params={"amount": shield_hp},
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.FLAT,
        value=_S3_DEF_BUFF, source_tag=_S3_DEF_BUFF_TAG,
    ))
    carrier.hp = min(carrier.hp + shield_hp, carrier.max_hp + shield_hp)
    world.log(f"Bubble S3 Grand Surf — SHIELD {shield_hp} HP, DEF +{_S3_DEF_BUFF} ({_S3_DURATION}s)")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.statuses = [s for s in carrier.statuses if s.source_tag != _S3_SHIELD_TAG]
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_DEF_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_bubble(slot: str = "S2") -> UnitState:
    """Bubble E2 max. DEF_PROTECTOR. Talent: HP<50% once → SHIELD. S2: SHIELD + DEF buff."""
    op = _base_stats()
    op.name = "Bubble"
    op.archetype = RoleArchetype.DEF_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = True
    op.block = 3
    op.cost = 21

    op.talents = [TalentComponent(name="Foam Guard", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Surfing Time",
            slot="S2",
            sp_cost=40,
            initial_sp=15,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Grand Surf",
            slot="S3",
            sp_cost=50,
            initial_sp=20,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
    return op
