"""Kafka (卡夫卡) — 5* Specialist (Executor archetype).

Talent "Anticipation": each normal attack applies a DOT (electric discharge,
  100 DPS for 2s) to the target. Refresh semantics on each hit. This is the
  first StatusKind.DOT usage — the status_decay_system processes DOT effects
  each tick via take_damage(int(dps * dt)), bypassing DEF/RES.

S2 "Electrocute": ATK +50%, 15s duration.
  sp_cost=20, initial_sp=10, AUTO_TIME, AUTO trigger, requires_target=True.

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
from data.characters.generated.kafka import make_kafka as _base_stats


EXECUTOR_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# --- Talent: Anticipation (DOT on hit) ---
_TALENT_TAG = "kafka_anticipation"
_DOT_DPS = 100.0       # true damage per second while DOT is active
_DOT_DURATION = 2.0
_DOT_TAG = "kafka_dot"

# --- S2: Electrocute ---
_S2_TAG = "kafka_s2_electrocute"
_S2_ATK_RATIO = 0.50
_S2_BUFF_TAG = "kafka_s2_atk"
_S2_DURATION = 15.0


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    elapsed = world.global_state.elapsed
    expires = elapsed + _DOT_DURATION

    # Refresh semantics: remove existing DOT from this source, append fresh
    target.statuses = [s for s in target.statuses if s.source_tag != _DOT_TAG]
    target.statuses.append(StatusEffect(
        kind=StatusKind.DOT,
        source_tag=_DOT_TAG,
        expires_at=expires,
        params={"dps": _DOT_DPS},
    ))
    world.log(
        f"Kafka Anticipation → {target.name}  "
        f"DOT {_DOT_DPS:.0f} DPS ({_DOT_DURATION}s)"
    )


register_talent(_TALENT_TAG, on_attack_hit=_talent_on_attack_hit)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_kafka(slot: str = "S2") -> UnitState:
    """Kafka E2 max. Talent: DOT 100 DPS / 2s on every hit. S2: ATK +50%."""
    op = _base_stats()
    op.name = "Kafka"
    op.archetype = RoleArchetype.SPEC_EXECUTOR
    op.profession = Profession.SPECIALIST
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = EXECUTOR_RANGE
    op.cost = 9

    op.talents = [TalentComponent(name="Anticipation", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Electrocute",
            slot="S2",
            sp_cost=20,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    return op
