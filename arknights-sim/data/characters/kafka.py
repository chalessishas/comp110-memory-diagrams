"""Kafka (卡夫卡) — 5★ Specialist (Executor).

Real game skills:
  S1 "Cube of Absurdism": ON_DEPLOY stub (no behavior modeled).
  S2 real slot is "Shears of Surrealism" (ON_DEPLOY, also a stub).

S2_SIM ("Electrocute") and S3_SIM ("Iron Judgment") are FICTIONAL SIMULATION
SCENARIOS that exercise real engine subsystems (ATK buff, AoE arts damage,
stun, DOT). They are not based on actual Kafka skill data but retained for
engine-level test coverage.

Talent "Anticipation": DOT-on-hit approximation (unverified vs game data).
"""
from __future__ import annotations
from math import floor
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape,
    TalentComponent, StatusEffect,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.kafka import make_kafka as _base_stats


EXECUTOR_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# --- Talent: Anticipation (DOT on hit, approximation) ---
_TALENT_TAG = "kafka_anticipation"
_DOT_DPS = 100.0
_DOT_DURATION = 2.0
_DOT_TAG = "kafka_dot"

# --- Real S1 stub ---
_S1_TAG = "kafka_s1_cube"
_S1_DURATION = 0.0

# --- Fictional S2 simulation (exercises ATK buff system) ---
_S2_TAG = "kafka_s2_electrocute"
_S2_ATK_RATIO = 0.50
_S2_BUFF_TAG = "kafka_s2_atk"
_S2_DURATION = 15.0

# --- Fictional S3 simulation (exercises AoE damage + stun systems) ---
_S3_TAG = "kafka_s3_iron_judgment"
_S3_ATK_MULTIPLIER = 5.00
_S3_STUN_DURATION = 2.5


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    elapsed = world.global_state.elapsed
    expires = elapsed + _DOT_DURATION
    target.statuses = [s for s in target.statuses if s.source_tag != _DOT_TAG]
    target.statuses.append(StatusEffect(
        kind=StatusKind.DOT,
        source_tag=_DOT_TAG,
        expires_at=expires,
        params={"dps": _DOT_DPS},
    ))
    world.log(f"Kafka Anticipation → {target.name}  DOT {_DOT_DPS:.0f} DPS ({_DOT_DURATION}s)")


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
    if carrier.position is None:
        return
    ox, oy = carrier.position
    tiles = set(carrier.range_shape.tiles)
    raw = int(floor(carrier.effective_atk * _S3_ATK_MULTIPLIER))
    now = world.global_state.elapsed
    stun_tag = f"{_S3_TAG}_stun"
    for enemy in world.enemies():
        if not enemy.alive or not enemy.deployed or enemy.position is None:
            continue
        dx = round(enemy.position[0]) - round(ox)
        dy = round(enemy.position[1]) - round(oy)
        if (dx, dy) not in tiles:
            continue
        dealt = enemy.take_arts(raw)
        world.global_state.total_damage_dealt += dealt
        enemy.statuses.append(StatusEffect(
            kind=StatusKind.STUN,
            source_tag=stun_tag,
            expires_at=now + _S3_STUN_DURATION,
        ))
        world.log(f"Kafka S3 SIM → {enemy.name}  dmg={dealt}  stun {_S3_STUN_DURATION}s")


register_skill(_S3_TAG, on_start=_s3_on_start)


def make_kafka(slot: str | None = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Kafka"
    op.archetype = RoleArchetype.SPEC_EXECUTOR
    op.profession = Profession.SPECIALIST
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = EXECUTOR_RANGE
    op.cost = 9

    op.talents = [TalentComponent(name="Anticipation", behavior_tag=_TALENT_TAG)]

    if slot == "S1":
        op.skill = SkillComponent(name="Cube of Absurdism", slot="S1", sp_cost=0, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.ON_DEPLOY,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Electrocute", slot="S2", sp_cost=20, initial_sp=10,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Iron Judgment", slot="S3", sp_cost=30, initial_sp=10,
            duration=0.0, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=True, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
