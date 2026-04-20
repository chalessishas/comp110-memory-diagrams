"""Ines (伊内丝) — 6★ Vanguard (Agent archetype).

VAN_AGENT trait: Gains CAMOUFLAGE on deployment (enemies cannot target her).

Talent "Quiet Visitor" (E2):
  When deployed, all enemies within _TALENT_RANGE Manhattan tiles are SILENCED
  for _TALENT_SILENCE_DURATION seconds.

S3 "Obedient Strings": MANUAL, instant.
  Deals _S3_ATK_RATIO×ATK Physical damage to all in-range enemies.
  Applies SILENCE to each hit enemy for _S3_SILENCE_DURATION seconds.
  After the burst, Ines regains CAMOUFLAGE for _S3_CAMO_DURATION seconds.
  sp_cost=50, initial_sp=15, duration=1.0s (fires on_start).

Base stats from ArknightsGameData (E2 max, trust 100, char_4087_ines):
  HP=2121, ATK=639, DEF=311, RES=0, atk_interval=1.0, cost=11, block=1.
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
from data.characters.generated.ines import make_ines as _base_stats


AGENT_RANGE = RangeShape(tiles=((0, 0), (1, 0), (2, 0), (3, 0)))

# --- VAN_AGENT trait: CAMOUFLAGE on deploy ---
_CAMO_DURATION = 15.0
_CAMO_TAG = "ines_vanguard_camouflage"

# --- Talent: Quiet Visitor ---
_TALENT_TAG = "ines_quiet_visitor"
_TALENT_SILENCE_DURATION = 6.0
_TALENT_SILENCE_TAG = "ines_talent_silence"
_TALENT_RANGE = 4    # Manhattan distance

# --- S3: Obedient Strings ---
_S3_TAG = "ines_s3_obedient_strings"
_S3_ATK_RATIO = 2.0
_S3_SILENCE_DURATION = 8.0
_S3_SILENCE_TAG = "ines_s3_silence"
_S3_CAMO_DURATION = 20.0
_S3_DURATION = 1.0


def _talent_on_battle_start(world, unit: UnitState) -> None:
    elapsed = world.global_state.elapsed

    # Trait: CAMOUFLAGE for VAN_AGENT
    unit.statuses = [s for s in unit.statuses if s.source_tag != _CAMO_TAG]
    unit.statuses.append(StatusEffect(
        kind=StatusKind.CAMOUFLAGE,
        source_tag=_CAMO_TAG,
        expires_at=elapsed + _CAMO_DURATION,
    ))
    world.log(f"Ines deployed → CAMOUFLAGE for {_CAMO_DURATION}s")

    if unit.position is None:
        return
    ux, uy = unit.position

    # Talent: SILENCE nearby enemies
    for enemy in world.enemies():
        if not enemy.alive or enemy.position is None:
            continue
        dx = abs(round(enemy.position[0]) - round(ux))
        dy = abs(round(enemy.position[1]) - round(uy))
        if dx + dy > _TALENT_RANGE:
            continue
        enemy.statuses = [s for s in enemy.statuses if s.source_tag != _TALENT_SILENCE_TAG]
        enemy.statuses.append(StatusEffect(
            kind=StatusKind.SILENCE,
            source_tag=_TALENT_SILENCE_TAG,
            expires_at=elapsed + _TALENT_SILENCE_DURATION,
        ))
        world.log(f"Ines Quiet Visitor → {enemy.name}  silence ({_TALENT_SILENCE_DURATION}s)")


register_talent(_TALENT_TAG, on_battle_start=_talent_on_battle_start)


def _s3_on_start(world, carrier: UnitState) -> None:
    if carrier.position is None:
        return
    elapsed = world.global_state.elapsed
    raw = int(carrier.effective_atk * _S3_ATK_RATIO)
    cx, cy = carrier.position

    for e in world.enemies():
        if not e.alive or e.position is None:
            continue
        dx = round(e.position[0]) - round(cx)
        dy = round(e.position[1]) - round(cy)
        if (dx, dy) not in set(carrier.range_shape.tiles):
            continue
        dealt = e.take_physical(raw)
        world.global_state.total_damage_dealt += dealt
        world.log(f"Ines S3 → {e.name}  phys={dealt}  ({e.hp}/{e.max_hp})")
        e.statuses = [s for s in e.statuses if s.source_tag != _S3_SILENCE_TAG]
        e.statuses.append(StatusEffect(
            kind=StatusKind.SILENCE,
            source_tag=_S3_SILENCE_TAG,
            expires_at=elapsed + _S3_SILENCE_DURATION,
        ))

    # Re-apply CAMOUFLAGE after burst
    carrier.statuses = [s for s in carrier.statuses if s.source_tag != _CAMO_TAG]
    carrier.statuses.append(StatusEffect(
        kind=StatusKind.CAMOUFLAGE,
        source_tag=_CAMO_TAG,
        expires_at=elapsed + _S3_CAMO_DURATION,
    ))
    world.log(f"Ines S3 → regains CAMOUFLAGE for {_S3_CAMO_DURATION}s")


register_skill(_S3_TAG, on_start=_s3_on_start)


def make_ines(slot: str = "S3") -> UnitState:
    """Ines E2 max. Trait+Talent: CAMOUFLAGE + SILENCE on deploy. S3: AoE + SILENCE + re-CAMO."""
    op = _base_stats()
    op.name = "Ines"
    op.archetype = RoleArchetype.VAN_AGENT
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = True
    op.range_shape = AGENT_RANGE
    op.block = 1
    op.cost = 11

    op.talents = [TalentComponent(name="Quiet Visitor", behavior_tag=_TALENT_TAG)]

    if slot == "S3":
        op.skill = SkillComponent(
            name="Obedient Strings",
            slot="S3",
            sp_cost=50,
            initial_sp=15,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
    return op
