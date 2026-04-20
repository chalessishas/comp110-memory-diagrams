"""Mostima (莫斯提马) — 6★ Caster (Mystic archetype).

CASTER_MYSTIC trait: Arts attack against ground enemies.

Talent "Serenity" (E2):
  When Mostima kills an enemy, immediately gain _TALENT_SP_ON_KILL bonus SP.
  Models the rapid SP charging that defines the archetype.

S3 "Ley Lines": MANUAL, instant.
  Deals _S3_ATK_RATIO×ATK Arts damage to ALL enemies currently on the field
  (global range — no position check). Applies STUN for _S3_STUN_DURATION to
  each hit enemy. sp_cost=60, initial_sp=30, duration=1.0s (fires on_start).

Base stats from ArknightsGameData (E2 max, trust 100, char_213_mostma):
  HP=1831, ATK=939, DEF=132, RES=20, atk_interval=2.9s, cost=34, block=1.
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
from data.characters.generated.mostma import make_mostma as _base_stats


MYSTIC_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0),
    (1, 1), (2, 1), (1, -1), (2, -1),
))

_TALENT_TAG = "mostima_serenity"
_TALENT_SP_ON_KILL = 10.0

_S3_TAG = "mostima_s3_ley_lines"
_S3_ATK_RATIO = 1.7
_S3_STUN_DURATION = 3.5
_S3_STUN_TAG = "mostima_s3_stun"
_S3_DURATION = 1.0


def _talent_on_kill(world, killer: UnitState, killed: UnitState) -> None:
    if killer.skill is None:
        return
    gain = min(_TALENT_SP_ON_KILL, killer.skill.sp_cost - killer.skill.sp)
    killer.skill.sp += gain
    world.log(f"Mostima Serenity → kill SP+{gain:.0f}  ({killer.skill.sp:.0f}/{killer.skill.sp_cost})")


register_talent(_TALENT_TAG, on_kill=_talent_on_kill)


def _s3_on_start(world, carrier: UnitState) -> None:
    elapsed = world.global_state.elapsed
    raw = int(carrier.effective_atk * _S3_ATK_RATIO)

    for e in world.enemies():
        if not e.alive:
            continue
        dealt = e.take_arts(raw)
        world.global_state.total_damage_dealt += dealt
        world.log(f"Mostima Ley Lines → {e.name}  arts={dealt}  ({e.hp}/{e.max_hp})")
        e.statuses = [s for s in e.statuses if s.source_tag != _S3_STUN_TAG]
        e.statuses.append(StatusEffect(
            kind=StatusKind.STUN,
            source_tag=_S3_STUN_TAG,
            expires_at=elapsed + _S3_STUN_DURATION,
        ))


register_skill(_S3_TAG, on_start=_s3_on_start)


def make_mostima(slot: str = "S3") -> UnitState:
    """Mostima E2 max. Talent: SP+10 on kill. S3: global AoE Arts + STUN all."""
    op = _base_stats()
    op.name = "Mostima"
    op.archetype = RoleArchetype.CASTER_MYSTIC
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.attack_range_melee = False
    op.range_shape = MYSTIC_RANGE
    op.block = 1
    op.cost = 34

    op.talents = [TalentComponent(name="Serenity", behavior_tag=_TALENT_TAG)]

    if slot == "S3":
        op.skill = SkillComponent(
            name="Ley Lines",
            slot="S3",
            sp_cost=60,
            initial_sp=30,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
    return op
