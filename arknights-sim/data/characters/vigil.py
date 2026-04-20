"""Vigil (伺夜) — 6* Vanguard (Tactician archetype).

Class trait: Tactician Vanguard — no passive DP accumulation; DP via skills.
S3 "Packleader's Dignity": 12 DP over 15s (DP drip). block=0 during skill.
  sp_cost=50, initial_sp=25, duration=15s, AUTO_TIME, AUTO trigger.
  (Wolf shadow summon mechanic deferred — DP drip modeled faithfully.)

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape, TalentComponent, StatusEffect
from core.types import (
    Profession, RoleArchetype, SPGainMode, SkillTrigger, StatusKind, TICK_RATE,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.vigil import make_vigil as _base_stats


TACTICIAN_RANGE = RangeShape(tiles=((0, 0), (1, 0), (2, 0)))

# --- Talent: Pack Leader's Resolve — self-REGEN while S3 inactive ---
_TALENT_TAG = "vigil_pack_resolve"
_REGEN_SOURCE_TAG = "vigil_pack_resolve_regen"
_REGEN_HPS = 80.0
_REGEN_TTL = 2.0 / TICK_RATE  # two ticks so it lapses quickly when S3 fires


def _pack_resolve_on_tick(world, carrier: UnitState, dt: float) -> None:
    skill_active = carrier.skill is not None and carrier.skill.active_remaining > 0.0
    carrier.statuses = [s for s in carrier.statuses if s.source_tag != _REGEN_SOURCE_TAG]
    if not skill_active:
        elapsed = world.global_state.elapsed
        carrier.statuses.append(StatusEffect(
            kind=StatusKind.REGEN,
            source_tag=_REGEN_SOURCE_TAG,
            expires_at=elapsed + _REGEN_TTL,
            params={"hps": _REGEN_HPS},
        ))


register_talent(_TALENT_TAG, on_tick=_pack_resolve_on_tick)


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
    op.talents = [TalentComponent(name="Pack Leader's Resolve", behavior_tag=_TALENT_TAG)]

    if slot == "S3":
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
