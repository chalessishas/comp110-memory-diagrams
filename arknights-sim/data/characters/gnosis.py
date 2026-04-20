"""Gnosis (灵知) — 6* Supporter (Hexer archetype).

Talent "Theoretical Analysis": Each attack reduces the target's RES by 15
  (flat) for 2s AND applies COLD for 2s. Stacks toward FREEZE: if target is
  already COLD, upgrades to FREEZE (1.5s, can_act=False) instead.

S2 "Frozen Silence": 20s duration, ATK +80%.
  sp_cost=30, initial_sp=15, AUTO_TIME, AUTO trigger, requires_target=True.

S3 "Permafrost Theory": 20s duration, ATK +150%.
  While active, each attack applies FREEZE directly (skips COLD phase).
  sp_cost=50, initial_sp=20, AUTO_TIME, AUTO trigger, requires_target=True.

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
from data.characters.generated.gnosis import make_gnosis as _base_stats


SUPPORTER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 4) for dy in range(-1, 2)
))

# --- Talent: Theoretical Analysis ---
_TALENT_TAG = "gnosis_theoretical_analysis"
_RES_DOWN_AMOUNT = 15.0
_RES_DOWN_DURATION = 2.0
_RES_DOWN_TAG = "gnosis_res_down"

_COLD_DURATION = 2.0
_COLD_TAG = "gnosis_cold"
_FREEZE_DURATION = 1.5
_FREEZE_TAG = "gnosis_freeze"

# --- S2: Frozen Silence ---
_S2_TAG = "gnosis_s2_frozen_silence"
_S2_ATK_RATIO = 0.80
_S2_BUFF_TAG = "gnosis_s2_atk_buff"
_S2_DURATION = 20.0

# --- S3: Permafrost Theory ---
_S3_TAG = "gnosis_s3_permafrost_theory"
_S3_ATK_RATIO = 1.50           # ATK +150%
_S3_BUFF_TAG = "gnosis_s3_atk_buff"
_S3_FREEZE_DURATION = 2.0      # direct FREEZE (longer than talent's 1.5s)
_S3_FREEZE_TAG = "gnosis_s3_freeze"
_S3_DURATION = 20.0

# Module-level set: unit_ids with S3 instant-freeze active
_s3_instant_freeze: set[int] = set()


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    elapsed = world.global_state.elapsed

    # RES_DOWN (refresh)
    expires_rd = elapsed + _RES_DOWN_DURATION
    target.statuses = [s for s in target.statuses if s.source_tag != _RES_DOWN_TAG]
    target.buffs = [b for b in target.buffs if b.source_tag != _RES_DOWN_TAG]
    target.statuses.append(StatusEffect(
        kind=StatusKind.RES_DOWN, source_tag=_RES_DOWN_TAG,
        expires_at=expires_rd, params={"amount": _RES_DOWN_AMOUNT},
    ))
    target.buffs.append(Buff(
        axis=BuffAxis.RES, stack=BuffStack.FLAT,
        value=-_RES_DOWN_AMOUNT, source_tag=_RES_DOWN_TAG,
        expires_at=expires_rd,
    ))

    # S3 instant FREEZE (skip COLD chain)
    if attacker.unit_id in _s3_instant_freeze:
        target.statuses = [
            s for s in target.statuses
            if s.kind not in (StatusKind.COLD, StatusKind.FREEZE)
        ]
        target.statuses.append(StatusEffect(
            kind=StatusKind.FREEZE, source_tag=_S3_FREEZE_TAG,
            expires_at=elapsed + _S3_FREEZE_DURATION,
        ))
        world.log(
            f"Gnosis S3 Permafrost → {target.name}  "
            f"FREEZE ({_S3_FREEZE_DURATION}s)  RES -{_RES_DOWN_AMOUNT:.0f}"
        )
        return

    # Normal COLD → FREEZE chain
    if target.has_status(StatusKind.COLD):
        target.statuses = [
            s for s in target.statuses
            if s.kind != StatusKind.COLD and s.source_tag != _FREEZE_TAG
        ]
        target.statuses.append(StatusEffect(
            kind=StatusKind.FREEZE, source_tag=_FREEZE_TAG,
            expires_at=elapsed + _FREEZE_DURATION,
        ))
        world.log(f"Gnosis → {target.name}  FREEZE ({_FREEZE_DURATION}s)")
    else:
        target.statuses = [s for s in target.statuses if s.source_tag != _COLD_TAG]
        target.statuses.append(StatusEffect(
            kind=StatusKind.COLD, source_tag=_COLD_TAG,
            expires_at=elapsed + _COLD_DURATION,
        ))
        world.log(f"Gnosis → {target.name}  COLD ({_COLD_DURATION}s)")


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
    _s3_instant_freeze.add(carrier.unit_id)
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))
    world.log(f"Gnosis S3 Permafrost Theory — ATK+{_S3_ATK_RATIO:.0%} instant-FREEZE/{_S3_DURATION}s")


def _s3_on_end(world, carrier: UnitState) -> None:
    _s3_instant_freeze.discard(carrier.unit_id)
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_gnosis(slot: str = "S2") -> UnitState:
    """Gnosis E2 max. Talent: RES_DOWN + COLD/FREEZE chain. S3: ATK+150% + instant FREEZE."""
    op = _base_stats()
    op.name = "Gnosis"
    op.archetype = RoleArchetype.SUP_HEXER
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.range_shape = SUPPORTER_RANGE
    op.cost = 13

    op.talents = [TalentComponent(name="Theoretical Analysis", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Frozen Silence",
            slot="S2",
            sp_cost=30,
            initial_sp=15,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Permafrost Theory",
            slot="S3",
            sp_cost=50,
            initial_sp=20,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
