"""Siege (推进之王) — 6★ Vanguard (Pioneer archetype).

S1 "Charge γ" (M3): Instant (no duration), sp_cost=35, initial_sp=20, AUTO.
  Gains 12 DP immediately on trigger. Requires no target.

S3 "Skull Breaker" (M3): 25s, MANUAL, sp_cost=30, initial_sp=25.
  ATK+280% (total 380× base), attack interval +1s.
  40% chance to Stun the target for 1.5s on each hit.

Base stats (E2 max, trust 100, char_112_siege):
  HP=2251, ATK=575, DEF=409, RES=0, atk_interval=1.05, block=2, cost=14.
"""
from __future__ import annotations

from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape, TalentComponent, StatusEffect,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.siege import make_siege as _base_stats


PIONEER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# Talent tag used for S3 on_attack_hit stun hook
_TALENT_TAG = "siege_s3_stun_hook"

_S1_TAG = "siege_s1_charge_gamma"
_S1_DP_GAIN = 12

_S3_TAG = "siege_s3_skull_breaker"
_S3_ATK_RATIO = 2.80        # total ATK becomes 380% of base → buff ratio = +280%
_S3_ATK_BUFF_TAG = "siege_s3_atk"
_S3_INTERVAL_TAG = "siege_s3_interval"
_S3_STUN_CHANCE = 0.40
_S3_STUN_DURATION = 1.5
_S3_STUN_TAG = "siege_s3_stun"
_S3_DURATION = 25.0


# ── Talent: S3 stun on_attack_hit ────────────────────────────────────────────

def _on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    if not getattr(attacker, "_siege_s3_active", False):
        return
    if world.rng.random() < _S3_STUN_CHANCE:
        target.statuses.append(StatusEffect(
            kind=StatusKind.STUN,
            source_tag=_S3_STUN_TAG,
            expires_at=world.global_state.elapsed + _S3_STUN_DURATION,
            params={},
        ))
        world.log(f"Siege Skull Breaker stun → {target.name} ({_S3_STUN_DURATION}s)")


register_talent(_TALENT_TAG, on_attack_hit=_on_attack_hit)


# ── S1: Charge γ ─────────────────────────────────────────────────────────────

def _s1_on_start(world, carrier: UnitState) -> None:
    world.global_state.refund_dp(_S1_DP_GAIN)
    world.log(f"Siege Charge γ — +{_S1_DP_GAIN} DP (total {world.global_state.dp})")


register_skill(_S1_TAG, on_start=_s1_on_start)


# ── S3: Skull Breaker ─────────────────────────────────────────────────────────

def _s3_on_start(world, carrier: UnitState) -> None:
    carrier._siege_s3_active = True
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK_INTERVAL, stack=BuffStack.FLAT,
        value=1.0, source_tag=_S3_INTERVAL_TAG,
    ))
    world.log(f"Siege Skull Breaker — ATK+{_S3_ATK_RATIO:.0%}, interval+1s, 40% stun")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier._siege_s3_active = False
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S3_ATK_BUFF_TAG, _S3_INTERVAL_TAG)]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


# ── Factory ───────────────────────────────────────────────────────────────────

def make_siege(slot: str = "S1") -> UnitState:
    """Siege E2 max. S1: Charge γ (instant 12 DP). S3: Skull Breaker (ATK+/stun)."""
    op = _base_stats()
    op.name = "Siege"
    op.archetype = RoleArchetype.VAN_PIONEER
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = True
    op.range_shape = PIONEER_RANGE
    op.block = 2
    op.cost = 14
    op.max_hp = 2251
    op.hp = 2251
    op.atk = 575
    op.defence = 409

    op.talents = [TalentComponent(name="Skull Breaker Hook", behavior_tag=_TALENT_TAG)]

    if slot == "S1":
        op.skill = SkillComponent(
            name="Charge γ",
            slot="S1",
            sp_cost=35,
            initial_sp=20,
            duration=0.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Skull Breaker",
            slot="S3",
            sp_cost=30,
            initial_sp=25,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
