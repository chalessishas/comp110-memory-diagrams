"""Nightmare (夜魔) — 5* Caster (Phalanx archetype).

Talent "Nightmare's Lullaby": Each attack applies SLEEP (2s) to the target.
  Sleeping enemies cannot move or attack (can_act() = False).
  A sleeping enemy wakes immediately when it takes any damage.
  Status is refreshed on every subsequent hit.

S2 "Darkening": 20s duration, ATK +60%.
  sp_cost=25, initial_sp=10, AUTO_TIME, AUTO trigger, requires_target=True.

S3 "Eternal Sleep": Instant MANUAL AoE. Deals 400% ATK arts to all enemies in
  range, and applies 4s SLEEP to each hit enemy.
  sp_cost=35, initial_sp=10, AUTO_TIME.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from math import floor
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
from data.characters.generated.nightm import make_nightm as _base_stats


CASTER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 4) for dy in range(-1, 2)
))

# --- Talent: Nightmare's Lullaby ---
_TALENT_TAG = "nightmare_lullaby"
_SLEEP_DURATION = 2.0
_SLEEP_TAG = "nightmare_sleep"

# --- S2: Darkening ---
_S2_TAG = "nightmare_s2_darkening"
_S2_ATK_RATIO = 0.60
_S2_BUFF_TAG = "nightmare_s2_atk_buff"
_S2_DURATION = 20.0

# --- S3: Eternal Sleep ---
_S3_TAG = "nightmare_s3_eternal_sleep"
_S3_ATK_MULTIPLIER = 4.00    # 400% ATK arts burst
_S3_SLEEP_DURATION = 4.0     # 4s SLEEP on all hit enemies


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    # Refresh SLEEP: remove stale, apply fresh
    target.statuses = [s for s in target.statuses if s.source_tag != _SLEEP_TAG]
    target.statuses.append(StatusEffect(
        kind=StatusKind.SLEEP,
        source_tag=_SLEEP_TAG,
        expires_at=world.global_state.elapsed + _SLEEP_DURATION,
    ))
    world.log(
        f"Nightmare Lullaby → {target.name}  sleep ({_SLEEP_DURATION}s)"
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


def _s3_on_start(world, carrier: UnitState) -> None:
    if carrier.position is None:
        return
    ox, oy = carrier.position
    tiles = set(carrier.range_shape.tiles)
    raw = int(floor(carrier.effective_atk * _S3_ATK_MULTIPLIER))
    now = world.global_state.elapsed
    sleep_tag = f"{_S3_TAG}_sleep"
    for enemy in world.enemies():
        if not enemy.alive or not enemy.deployed or enemy.position is None:
            continue
        dx = round(enemy.position[0]) - round(ox)
        dy = round(enemy.position[1]) - round(oy)
        if (dx, dy) not in tiles:
            continue
        dealt = enemy.take_arts(raw)
        world.global_state.total_damage_dealt += dealt
        enemy.statuses = [s for s in enemy.statuses if s.source_tag != sleep_tag]
        enemy.statuses.append(StatusEffect(
            kind=StatusKind.SLEEP,
            source_tag=sleep_tag,
            expires_at=now + _S3_SLEEP_DURATION,
        ))
        world.log(f"Nightmare S3 Eternal Sleep → {enemy.name}  dmg={dealt}  sleep {_S3_SLEEP_DURATION}s")


register_skill(_S3_TAG, on_start=_s3_on_start)


def make_nightmare(slot: str = "S2") -> UnitState:
    """Nightmare E2 max. Talent: SLEEP on every hit. S2: ATK burst. S3: instant AoE Arts + mass Sleep."""
    op = _base_stats()
    op.name = "Nightmare"
    op.archetype = RoleArchetype.CASTER_PHALANX
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CASTER_RANGE
    op.cost = 20

    op.talents = [TalentComponent(name="Nightmare's Lullaby", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Darkening",
            slot="S2",
            sp_cost=25,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Eternal Sleep",
            slot="S3",
            sp_cost=35,
            initial_sp=10,
            duration=0.0,   # instant
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
