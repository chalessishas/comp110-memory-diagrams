"""Texas Alter (缄默德克萨斯) — 6★ Specialist (Executor archetype).

SPEC_EXECUTOR trait: Attacks deal physical damage to surrounding enemies.
  (Simplified: 2-tile forward melee range, same as Kafka.)

Talent "Surging Current" (E2):
  After killing an enemy, immediately reset atk_cd to 0 (next attack fires
  on the following tick). Models the "instant re-attack" kill-chain mechanic.

S3 "Sword Rain": MANUAL, instant cast.
  Deals 100% ATK arts damage to ALL in-range enemies simultaneously.
  Applies SILENCE for 6s to each hit enemy.
  sp_cost=50, initial_sp=25, duration=1.0s (effectively instant).

Base stats from ArknightsGameData (E2 max, trust 100, char_1028_texas2).
  HP=1598, ATK=659, DEF=320, RES=0, atk_interval=0.93s, cost=10, block=1.
  redeploy_cd=18s (fastest redeployable Specialist).
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, RangeShape,
    TalentComponent, StatusEffect,
)
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.texas2 import make_texas2 as _base_stats


EXECUTOR_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_TALENT_TAG = "texas2_surging_current"

_S3_TAG = "texas2_s3_sword_rain"
_S3_SILENCE_DURATION = 6.0
_S3_SILENCE_TAG = "texas2_s3_silence"
_S3_DURATION = 1.0    # effectively instant — AoE fires on_start


def _talent_on_kill(world, killer: UnitState, killed: UnitState) -> None:
    killer.atk_cd = 0.0
    world.log(f"Texas Alter kill-reset → next attack immediately")


register_talent(_TALENT_TAG, on_kill=_talent_on_kill)


def _s3_on_start(world, carrier: UnitState) -> None:
    if carrier.position is None:
        return
    elapsed = world.global_state.elapsed
    raw = carrier.effective_atk

    for e in world.enemies():
        if not e.alive or e.position is None:
            continue
        ex, ey = e.position
        cx, cy = carrier.position
        dx = round(ex) - round(cx)
        dy = round(ey) - round(cy)
        if (dx, dy) not in set(carrier.range_shape.tiles):
            continue
        # Arts damage
        dealt = e.take_arts(raw)
        world.global_state.total_damage_dealt += dealt
        world.log(f"Texas Alter S3 → {e.name}  arts={dealt}  ({e.hp}/{e.max_hp})")
        # Silence
        e.statuses = [s for s in e.statuses if s.source_tag != _S3_SILENCE_TAG]
        e.statuses.append(StatusEffect(
            kind=StatusKind.SILENCE,
            source_tag=_S3_SILENCE_TAG,
            expires_at=elapsed + _S3_SILENCE_DURATION,
        ))


register_skill(_S3_TAG, on_start=_s3_on_start)


def make_texas_alter(slot: str = "S3") -> UnitState:
    """Texas Alter E2 max. Talent: kill → atk_cd=0. S3: AoE arts + SILENCE all in range."""
    op = _base_stats()
    op.name = "Texas Alter"
    op.archetype = RoleArchetype.SPEC_EXECUTOR
    op.profession = Profession.SPECIALIST
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = True
    op.range_shape = EXECUTOR_RANGE
    op.block = 1
    op.cost = 10

    op.talents = [TalentComponent(name="Surging Current", behavior_tag=_TALENT_TAG)]

    if slot == "S3":
        op.skill = SkillComponent(
            name="Sword Rain",
            slot="S3",
            sp_cost=50,
            initial_sp=25,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
    return op
