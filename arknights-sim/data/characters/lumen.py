"""Lumen (流明) — 6* Medic (Multi-Target archetype).

MEDIC_MULTI trait: heals 3 most-injured allies simultaneously per attack.
  Each hit heals the 3 allies with the lowest hp/max_hp ratio.

Talent "Intensive Care" (E2): Each ally Lumen heals restores +1 SP to Lumen.
  With 3 heal targets, this is effectively +3 SP per attack cycle.

S2 "Group Recovery": ATK +30%, heal targets 3 → 5 for 15s.
  sp_cost=20, initial_sp=10, AUTO_TIME, AUTO trigger.

S3 "Emergency Protocol": On activation, instantly heals ALL deployed allies
  for 150% ATK. Also raises ATK +100% and heal_targets 3 → 7 for 20s.
  sp_cost=35, initial_sp=15, AUTO_TIME, AUTO trigger.

Base stats from ArknightsGameData (E2 max, trust 100, char_4042_lumen).
  HP=1825, ATK=585, DEF=141, RES=10, atk_interval=2.85s, cost=23, block=1.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.lumen import make_lumen as _base_stats


MEDIC_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 4) for dy in range(-1, 2)
))

_S2_TAG = "lumen_s2_group_recovery"
_S2_ATK_RATIO = 0.30
_S2_BUFF_TAG = "lumen_s2_atk"
_S2_HEAL_TARGETS = 5
_S2_DURATION = 15.0

_BASE_HEAL_TARGETS = 3

# --- S3: Emergency Protocol ---
_S3_TAG = "lumen_s3_emergency_protocol"
_S3_ATK_RATIO = 1.00          # ATK +100%
_S3_BUFF_TAG = "lumen_s3_atk"
_S3_BURST_RATIO = 1.50        # instant heal = 150% ATK applied to all allies
_S3_HEAL_TARGETS = 7
_S3_DURATION = 20.0

_INTENSIVE_CARE_TAG = "lumen_intensive_care"
_SP_PER_HEAL = 1.0


def _intensive_care_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    sk = getattr(attacker, "skill", None)
    if sk is None or sk.active_remaining > 0:
        return
    if world.global_state.elapsed < sk.sp_lockout_until:
        return
    sk.sp = min(sk.sp + _SP_PER_HEAL, float(sk.sp_cost))


register_talent(_INTENSIVE_CARE_TAG, on_attack_hit=_intensive_care_on_attack_hit)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.heal_targets = _S2_HEAL_TARGETS
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.heal_targets = _BASE_HEAL_TARGETS
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def _s3_on_start(world, carrier: UnitState) -> None:
    burst = int(carrier.effective_atk * _S3_BURST_RATIO)
    for ally in world.allies():
        if ally.alive and ally.deployed and ally.hp < ally.max_hp:
            actual = ally.heal(burst)
            world.global_state.total_healing_done += actual
    carrier.heal_targets = _S3_HEAL_TARGETS
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))
    world.log(f"Lumen S3 Emergency Protocol — burst {burst} to all allies  ATK+{_S3_ATK_RATIO:.0%}/{_S3_DURATION}s")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.heal_targets = _BASE_HEAL_TARGETS
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_lumen(slot: str = "S2") -> UnitState:
    """Lumen E2 max. MEDIC_MULTI: heals 3 most-injured allies per attack."""
    op = _base_stats()
    op.name = "Lumen"
    op.archetype = RoleArchetype.MEDIC_MULTI
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.HEAL
    op.attack_range_melee = False
    op.range_shape = MEDIC_RANGE
    op.block = 1
    op.cost = 23
    op.heal_targets = _BASE_HEAL_TARGETS
    op.talents = [TalentComponent(
        name="Intensive Care",
        behavior_tag=_INTENSIVE_CARE_TAG,
    )]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Group Recovery",
            slot="S2",
            sp_cost=20,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Emergency Protocol",
            slot="S3",
            sp_cost=35,
            initial_sp=15,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
