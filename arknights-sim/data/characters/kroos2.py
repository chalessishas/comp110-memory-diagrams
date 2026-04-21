"""Kroos the Keen Glint (寒芒克洛丝) — 6* Sniper (Deadeye archetype).

Talent "Arctic Fox": Each attack applies COLD (−30% move speed, 2s) to
  the target. Stacks toward FREEZE when hit twice: if target is already
  COLD, upgrade to FREEZE (full stop, 1.5s) instead.

S2 "Permafrost Hail": 30s duration, ATK +100%. All hits apply FREEZE
  (1.5s) directly (skips COLD step).
  sp_cost=30, initial_sp=10, AUTO_TIME, AUTO trigger, requires_target=True.

S3 "Blizzard Barrage": 35s duration, MANUAL, ATK +200%. All hits apply
  FREEZE (3s) directly. Enhanced over S2 via longer duration, higher ATK
  multiplier, and longer FREEZE duration.
  sp_cost=40, initial_sp=15, AUTO_TIME, MANUAL trigger, requires_target=True.

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
from data.characters.generated.kroos2 import make_kroos2 as _base_stats


SNIPER_RANGE = RangeShape(tiles=((0, 0), (1, 0), (2, 0), (3, 0)))

_TALENT_TAG = "kroos2_arctic_fox"
_COLD_DURATION = 2.0
_COLD_TAG = "kroos2_cold"
_FREEZE_DURATION = 1.5
_FREEZE_TAG = "kroos2_freeze"

_S2_TAG = "kroos2_s2_permafrost"
_S2_ATK_RATIO = 1.00       # +100% ATK
_S2_BUFF_TAG = "kroos2_s2_atk_buff"
_S2_DURATION = 30.0
_S2_DIRECT_FREEZE = True   # S2 hits apply FREEZE directly

_S3_TAG = "kroos2_s3_blizzard_barrage"
_S3_ATK_RATIO = 2.00       # +200% ATK
_S3_BUFF_TAG = "kroos2_s3_atk_buff"
_S3_DURATION = 35.0
_S3_FREEZE_DURATION = 3.0  # longer FREEZE than S2's 1.5s


def _apply_cold_or_freeze(world, target, *, direct_freeze: bool = False, freeze_dur: float = _FREEZE_DURATION) -> None:
    """Apply COLD; if already COLD, upgrade to FREEZE. S2/S3 can skip to FREEZE."""
    if direct_freeze or target.has_status(StatusKind.COLD):
        target.statuses = [
            s for s in target.statuses
            if s.source_tag not in (_COLD_TAG, _FREEZE_TAG)
        ]
        target.statuses.append(StatusEffect(
            kind=StatusKind.FREEZE,
            source_tag=_FREEZE_TAG,
            expires_at=world.global_state.elapsed + freeze_dur,
        ))
        world.log(f"Kroos2 FREEZE → {target.name}  ({freeze_dur}s)")
    else:
        target.statuses = [s for s in target.statuses if s.source_tag != _COLD_TAG]
        target.statuses.append(StatusEffect(
            kind=StatusKind.COLD,
            source_tag=_COLD_TAG,
            expires_at=world.global_state.elapsed + _COLD_DURATION,
        ))
        world.log(f"Kroos2 COLD → {target.name}  ({_COLD_DURATION}s)")


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    direct_freeze = getattr(attacker, "_kroos2_s2_active", False) or getattr(attacker, "_kroos2_s3_active", False)
    freeze_dur = _S3_FREEZE_DURATION if getattr(attacker, "_kroos2_s3_active", False) else _FREEZE_DURATION
    _apply_cold_or_freeze(world, target, direct_freeze=direct_freeze, freeze_dur=freeze_dur)


register_talent(_TALENT_TAG, on_attack_hit=_talent_on_attack_hit)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    carrier._kroos2_s2_active = True


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]
    carrier._kroos2_s2_active = False


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))
    carrier._kroos2_s3_active = True
    world.log(f"Kroos2 S3 Blizzard Barrage — ATK +{_S3_ATK_RATIO:.0%}, FREEZE {_S3_FREEZE_DURATION}s on hit")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]
    carrier._kroos2_s3_active = False


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_kroos2(slot: str = "S2") -> UnitState:
    """Kroos2 E2 max. Talent: COLD/FREEZE on hit. S2: ATK+100% + direct FREEZE. S3: ATK+200% + 3s FREEZE MANUAL."""
    op = _base_stats()
    op.name = "Kroos2"
    op.archetype = RoleArchetype.SNIPER_DEADEYE
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNIPER_RANGE
    op.cost = 15

    op.talents = [TalentComponent(name="Arctic Fox", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Permafrost Hail",
            slot="S2",
            sp_cost=30,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Blizzard Barrage",
            slot="S3",
            sp_cost=40,
            initial_sp=15,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
    return op
