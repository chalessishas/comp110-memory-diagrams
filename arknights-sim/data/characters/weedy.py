"""Weedy (温蒂) — 6* Specialist (Sentinel archetype).

Talent "Free-Flowing": When not blocking any enemy, DEF +70%. Conditional
  buff via on_tick; removed immediately when blocking begins.

S3 "Torrential Stream": 30s duration.
  - ATK +160%, converts to ARTS attacks.
  - AoE: attacks all enemies in range (sets _attack_all_in_range).
  - Each hit applies 2s BIND to the target.
  sp_cost=45, initial_sp=20, AUTO_TIME, AUTO trigger, requires_target=True.

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
from data.characters.generated.weedy import make_weedy as _base_stats


# Sentinel Specialist range: self tile + 1 forward
SPECIALIST_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# --- Talent: Free-Flowing ---
_TALENT_TAG = "weedy_free_flowing"
_TALENT_DEF_RATIO = 0.70
_TALENT_DEF_BUFF_TAG = "weedy_free_flowing_def"

# --- S3: Torrential Stream ---
_S3_TAG = "weedy_s3_torrential"
_S3_DURATION = 30.0
_S3_ATK_RATIO = 1.60
_S3_BIND_DURATION = 2.0
_S3_BUFF_TAG = "weedy_s3_atk_buff"
_S3_BIND_TAG = "weedy_s3_bind"


def _talent_on_tick(world, carrier: UnitState, dt: float) -> None:
    is_blocking = any(carrier.unit_id in e.blocked_by_unit_ids for e in world.enemies())
    has_buff = any(b.source_tag == _TALENT_DEF_BUFF_TAG for b in carrier.buffs)
    if not is_blocking and not has_buff:
        carrier.buffs.append(Buff(
            axis=BuffAxis.DEF, stack=BuffStack.RATIO,
            value=_TALENT_DEF_RATIO, source_tag=_TALENT_DEF_BUFF_TAG,
        ))
    elif is_blocking and has_buff:
        carrier.buffs = [b for b in carrier.buffs if b.source_tag != _TALENT_DEF_BUFF_TAG]


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    if not getattr(attacker, "_weedy_bind_active", False):
        return
    # Refresh bind: remove stale, apply fresh
    target.statuses = [s for s in target.statuses if s.source_tag != _S3_BIND_TAG]
    target.statuses.append(StatusEffect(
        kind=StatusKind.BIND,
        source_tag=_S3_BIND_TAG,
        expires_at=world.global_state.elapsed + _S3_BIND_DURATION,
    ))
    world.log(f"Weedy S3 bind → {target.name}  ({_S3_BIND_DURATION}s)")


register_talent(
    _TALENT_TAG,
    on_tick=_talent_on_tick,
    on_attack_hit=_talent_on_attack_hit,
)


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))
    carrier._saved_attack_type = carrier.attack_type
    carrier.attack_type = AttackType.ARTS
    carrier._attack_all_in_range = True
    carrier._weedy_bind_active = True


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]
    saved = getattr(carrier, "_saved_attack_type", None)
    if saved is not None:
        carrier.attack_type = saved
    carrier._attack_all_in_range = False
    carrier._weedy_bind_active = False


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_weedy(slot: str = "S3") -> UnitState:
    """Weedy E2 max. Talent: DEF buff when not blocking. S3: AoE ARTS + BIND."""
    op = _base_stats()
    op.name = "Weedy"
    op.archetype = RoleArchetype.GUARD_DREADNOUGHT   # Sentinel Specialist
    op.profession = Profession.SPECIALIST
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SPECIALIST_RANGE
    op.cost = 21

    op.talents = [TalentComponent(name="Free-Flowing", behavior_tag=_TALENT_TAG)]

    if slot == "S3":
        op.skill = SkillComponent(
            name="Torrential Stream",
            slot="S3",
            sp_cost=45,
            initial_sp=20,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
    return op
