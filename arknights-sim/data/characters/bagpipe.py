"""Bagpipe (风笛) — 6* Vanguard (Pioneer archetype).

Talent "Glorious March" (E2): While Bagpipe is deployed, all other Vanguard
  operators gain ATK +25%. Implemented as a short-lived buff refreshed every tick.
  Also wires the S3 slow-on-hit effect (only active when _bagpipe_s3_active=True).

S3 "Last Wish": For 40s, ATK +200%; attacks apply 50% SLOW for 1s to target.
  sp_cost=35, initial_sp=20, AUTO, requires_target=True.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent, StatusEffect
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession, RoleArchetype,
    SPGainMode, SkillTrigger, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.bpipe import make_bpipe as _base_stats


PIONEER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# Combined talent: Glorious March (on_tick) + S3 slow (on_attack_hit)
_BAGPIPE_TAG = "bagpipe_glorious_march"
_MARCH_ATK_RATIO = 0.25
_MARCH_BUFF_TAG = "bagpipe_march_atk_buff"
_MARCH_REFRESH_DT = 0.3   # expires 0.3s; on_tick refreshes every 0.1s

# S3 constants
_S3_TAG = "bagpipe_s3_last_wish"
_S3_ATK_RATIO = 2.00
_S3_SLOW_DURATION = 1.0
_S3_BUFF_TAG = "bagpipe_s3_atk_buff"
_S3_SLOW_TAG = "bagpipe_s3_slow"


def _march_on_tick(world, carrier, dt: float) -> None:
    now = world.global_state.elapsed
    for ally in world.allies():
        if ally is carrier or not ally.deployed:
            continue
        if ally.profession != Profession.VANGUARD:
            continue
        for b in ally.buffs:
            if b.source_tag == _MARCH_BUFF_TAG:
                b.expires_at = now + _MARCH_REFRESH_DT
                break
        else:
            ally.buffs.append(Buff(
                axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                value=_MARCH_ATK_RATIO, source_tag=_MARCH_BUFF_TAG,
                expires_at=now + _MARCH_REFRESH_DT,
            ))


def _march_on_attack_hit(world, attacker, target, damage: int) -> None:
    if not getattr(attacker, "_bagpipe_s3_active", False):
        return
    target.statuses = [s for s in target.statuses if s.source_tag != _S3_SLOW_TAG]
    target.statuses.append(StatusEffect(
        kind=StatusKind.SLOW,
        source_tag=_S3_SLOW_TAG,
        expires_at=world.global_state.elapsed + _S3_SLOW_DURATION,
        params={"amount": 0.5},
    ))


register_talent(_BAGPIPE_TAG, on_tick=_march_on_tick, on_attack_hit=_march_on_attack_hit)


# --- S3: Last Wish ---
def _s3_on_start(world, unit) -> None:
    unit.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))
    unit._bagpipe_s3_active = True


def _s3_on_end(world, unit) -> None:
    unit.buffs = [b for b in unit.buffs if b.source_tag != _S3_BUFF_TAG]
    unit._bagpipe_s3_active = False


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_bagpipe(slot: str = "S3") -> UnitState:
    """Bagpipe E2 max. Talent: Vanguard ATK+25%. S3: +200% ATK + SLOW on hit."""
    op = _base_stats()
    op.name = "Bagpipe"
    op.archetype = RoleArchetype.VAN_PIONEER
    op.profession = Profession.VANGUARD
    op.range_shape = PIONEER_RANGE
    op.block = 1
    op.cost = 13
    op.talents = [TalentComponent(name="Glorious March", behavior_tag=_BAGPIPE_TAG)]

    if slot == "S3":
        op.skill = SkillComponent(
            name="Last Wish",
            slot="S3",
            sp_cost=35,
            initial_sp=20,
            duration=40.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
    return op
