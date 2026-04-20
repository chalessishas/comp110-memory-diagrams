"""Vigil (伺夜) — 6* Vanguard (Tactician archetype).

Class trait: Tactician Vanguard — no passive DP accumulation; DP via skills.
S3 "Packleader's Dignity": 12 DP over 15s (DP drip). block=0 during skill.
  sp_cost=50, initial_sp=25, duration=15s, AUTO_TIME, AUTO trigger.
  (Wolf shadow summon mechanic deferred — DP drip modeled faithfully.)

Talent "Wolven Nature" (E2): DEF ignore 175 on all physical attacks.
  (Game: applies when hitting enemies blocked by wolf summons; wolf summons not implemented,
   so the ignore is applied unconditionally as an approximation.)
  Implemented as on_attack_hit bonus true damage = min(target.effective_def, 175),
  which equals the DEF-ignore damage gain when raw_atk > 5% floor.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape, TalentComponent
from core.types import (
    AttackType, Profession, RoleArchetype, SPGainMode, SkillTrigger,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.vigil import make_vigil as _base_stats


TACTICIAN_RANGE = RangeShape(tiles=((0, 0), (1, 0), (2, 0)))

# --- Talent: Wolven Nature — DEF ignore 175 ---
_TALENT_TAG = "vigil_wolven_nature"
_DEF_IGNORE = 175


def _wolven_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    if attacker.attack_type != AttackType.PHYSICAL:
        return
    bonus = min(target.effective_def, _DEF_IGNORE)
    if bonus > 0:
        extra = target.take_true(bonus)
        world.global_state.total_damage_dealt += extra


register_talent(_TALENT_TAG, on_attack_hit=_wolven_on_attack_hit)


# --- S2: Pack Rally — 6 DP / 12s drip ---
_S2_TAG = "vigil_s2_pack_rally"
_S2_DP_RATE = 6.0 / 12.0    # 0.5 DP/s
_S2_DP_FRAC_ATTR = "_vigil_s2_dp_frac"
_S2_DURATION = 12.0

# --- S3: Packleader's Dignity — 12 DP / 15s drip ---
_S3_TAG = "vigil_s3_packleaders_dignity"
_S3_DP_RATE = 12.0 / 15.0   # 0.8 DP/s over 15s
_S3_DP_FRAC_ATTR = "_vigil_s3_dp_frac"


def _s3_on_start(world, unit) -> None:
    unit._saved_block = unit.block
    unit.block = 0
    setattr(unit, _S3_DP_FRAC_ATTR, 0.0)


def _s3_on_tick(world, unit, dt: float) -> None:
    frac = getattr(unit, _S3_DP_FRAC_ATTR, 0.0) + _S3_DP_RATE * dt
    gained = int(frac)
    if gained > 0:
        world.global_state.refund_dp(gained)
    setattr(unit, _S3_DP_FRAC_ATTR, frac - gained)


def _s3_on_end(world, unit) -> None:
    unit.block = getattr(unit, "_saved_block", 1)
    setattr(unit, _S3_DP_FRAC_ATTR, 0.0)


def _s2_on_start(world, unit) -> None:
    setattr(unit, _S2_DP_FRAC_ATTR, 0.0)
    world.log(f"Vigil S2 Pack Rally — 6 DP over {_S2_DURATION}s")


def _s2_on_tick(world, unit, dt: float) -> None:
    frac = getattr(unit, _S2_DP_FRAC_ATTR, 0.0) + _S2_DP_RATE * dt
    gained = int(frac)
    if gained > 0:
        world.global_state.refund_dp(gained)
    setattr(unit, _S2_DP_FRAC_ATTR, frac - gained)


def _s2_on_end(world, unit) -> None:
    setattr(unit, _S2_DP_FRAC_ATTR, 0.0)


register_skill(_S2_TAG, on_start=_s2_on_start, on_tick=_s2_on_tick, on_end=_s2_on_end)


register_skill(_S3_TAG, on_start=_s3_on_start, on_tick=_s3_on_tick, on_end=_s3_on_end)


def make_vigil(slot: str = "S3") -> UnitState:
    """Vigil E2 max. S3 Packleader's Dignity: 12 DP / 15s drip, block=0."""
    op = _base_stats()
    op.name = "Vigil"
    op.archetype = RoleArchetype.VAN_TACTICIAN
    op.profession = Profession.VANGUARD
    op.range_shape = TACTICIAN_RANGE
    op.block = 1
    op.cost = 17
    op.talents = [TalentComponent(name="Wolven Nature", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Pack Rally",
            slot="S2",
            sp_cost=30,
            initial_sp=15,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Packleader's Dignity",
            slot="S3",
            sp_cost=50,
            initial_sp=25,
            duration=15.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
    return op
