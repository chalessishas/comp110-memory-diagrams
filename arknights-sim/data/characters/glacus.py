"""Glacius (格劳克斯) — 5★ Supporter (Abjurer archetype).

SUP_ABJURER trait: While deployed, all allies within attack range gain a passive
  Arts resistance bonus (_AURA_RES_BONUS flat RES). The buff is refreshed every tick
  with a short expires_at window so it cleans up automatically if the aura is lost.

Talent "Frost Guard": Each attack applies COLD (slows, 3s) to the primary target.
  If target is already COLD, upgrade to FREEZE (2s) instead.

S2 "Arctic Barrier": 20s duration. ATK +40%; all attacks apply FREEZE directly
  (bypass COLD step). The ally RES aura continues unchanged during S2.
  sp_cost=25, initial_sp=12, AUTO_TIME, AUTO trigger, requires_target=True.

Base stats from ArknightsGameData (E2 max, trust 100, char_326_glacus):
  HP=1567, ATK=540, DEF=100, RES=20, atk_interval=1.9, block=1.
"""
from __future__ import annotations
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
from data.characters.generated.glacus import make_glacus as _base_stats


ABJURER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 4) for dy in range(-1, 2)
))

# Aura: passive RES buff to allies in range (refreshed every tick)
_AURA_TAG = "glacus_frost_guard_aura"
_AURA_RES_BUFF_TAG = "glacus_aura_res"
_AURA_RES_BONUS = 10.0          # +10 flat RES to allies in range
_AURA_TTL = 0.3                 # seconds before expires_at; re-stamped each tick

# Talent: Frost Guard — COLD → FREEZE escalation on hit
_TALENT_TAG = "glacus_frost_guard"
_COLD_DURATION = 3.0
_COLD_TAG = "glacus_cold"
_FREEZE_DURATION = 2.0
_FREEZE_TAG = "glacus_freeze"

# S2: Arctic Barrier
_S2_TAG = "glacus_s2_arctic_barrier"
_S2_ATK_RATIO = 0.40
_S2_ATK_BUFF_TAG = "glacus_s2_atk"
_S2_DURATION = 20.0


def _in_abjurer_range(carrier: UnitState, ally: UnitState) -> bool:
    if carrier.position is None or ally.position is None:
        return False
    cx, cy = carrier.position
    alx, aly = ally.position
    return any(
        (cx + dx == alx and cy + dy == aly)
        for dx, dy in ABJURER_RANGE.tiles
    )


def _aura_on_tick(world, carrier: UnitState, dt: float) -> None:
    now = world.global_state.elapsed
    new_expires = now + _AURA_TTL + dt
    for ally in world.allies():
        if ally is carrier or not ally.alive or not ally.deployed:
            continue
        if not _in_abjurer_range(carrier, ally):
            # Remove aura if ally moved out of range
            ally.buffs = [b for b in ally.buffs if b.source_tag != _AURA_RES_BUFF_TAG]
            continue
        existing = next((b for b in ally.buffs if b.source_tag == _AURA_RES_BUFF_TAG), None)
        if existing is not None:
            existing.expires_at = new_expires
        else:
            ally.buffs.append(Buff(
                axis=BuffAxis.RES, stack=BuffStack.FLAT,
                value=_AURA_RES_BONUS, source_tag=_AURA_RES_BUFF_TAG,
                expires_at=new_expires,
            ))


register_talent(_AURA_TAG, on_tick=_aura_on_tick)


def _apply_cold_or_freeze(world, attacker: UnitState, target) -> None:
    direct_freeze = getattr(attacker, "_glacus_s2_active", False)
    if direct_freeze or target.has_status(StatusKind.COLD):
        target.statuses = [
            s for s in target.statuses
            if s.source_tag not in (_COLD_TAG, _FREEZE_TAG)
        ]
        target.statuses.append(StatusEffect(
            kind=StatusKind.FREEZE,
            source_tag=_FREEZE_TAG,
            expires_at=world.global_state.elapsed + _FREEZE_DURATION,
        ))
        world.log(f"Glacus FREEZE → {target.name}  ({_FREEZE_DURATION}s)")
    else:
        target.statuses = [s for s in target.statuses if s.source_tag != _COLD_TAG]
        target.statuses.append(StatusEffect(
            kind=StatusKind.COLD,
            source_tag=_COLD_TAG,
            expires_at=world.global_state.elapsed + _COLD_DURATION,
        ))
        world.log(f"Glacus COLD → {target.name}  ({_COLD_DURATION}s)")


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    if damage <= 0:
        return
    _apply_cold_or_freeze(world, attacker, target)


register_talent(_TALENT_TAG, on_attack_hit=_talent_on_attack_hit)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))
    carrier._glacus_s2_active = True


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_ATK_BUFF_TAG]
    carrier._glacus_s2_active = False


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# S3: Arctic Tempest — ATK+100%, FREEZE all enemies in range at activation
_S3_TAG = "glacus_s3_arctic_tempest"
_S3_ATK_RATIO = 1.00
_S3_ATK_BUFF_TAG = "glacus_s3_atk"
_S3_FREEZE_DURATION = 4.0
_S3_FREEZE_TAG = "glacus_s3_freeze"
_S3_DURATION = 25.0


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))
    carrier._glacus_s2_active = True  # reuse flag: direct FREEZE on all hits
    elapsed = world.global_state.elapsed
    if carrier.position is None:
        return
    cx, cy = carrier.position
    tiles = set(carrier.range_shape.tiles)
    for e in world.enemies():
        if not e.alive or e.position is None:
            continue
        ex, ey = e.position
        if (round(ex) - round(cx), round(ey) - round(cy)) not in tiles:
            continue
        e.statuses = [s for s in e.statuses if s.source_tag not in (_COLD_TAG, _FREEZE_TAG, _S3_FREEZE_TAG)]
        e.statuses.append(StatusEffect(
            kind=StatusKind.FREEZE,
            source_tag=_S3_FREEZE_TAG,
            expires_at=elapsed + _S3_FREEZE_DURATION,
        ))
    world.log(f"Glacus S3 Arctic Tempest — ATK+{_S3_ATK_RATIO:.0%}, AoE FREEZE {_S3_FREEZE_DURATION}s")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_ATK_BUFF_TAG]
    carrier._glacus_s2_active = False


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_glacus(slot: str = "S2") -> UnitState:
    """Glacius E2 max. SUP_ABJURER: ally RES aura + COLD/FREEZE on hit. S2: ATK+40%, direct FREEZE."""
    op = _base_stats()
    op.name = "Glacius"
    op.archetype = RoleArchetype.SUP_ABJURER
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.attack_range_melee = False
    op.range_shape = ABJURER_RANGE
    op.block = 1
    op.cost = 15

    op.talents = [
        TalentComponent(name="Abjurer Aura", behavior_tag=_AURA_TAG),
        TalentComponent(name="Frost Guard", behavior_tag=_TALENT_TAG),
    ]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Arctic Barrier",
            slot="S2",
            sp_cost=25,
            initial_sp=12,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Arctic Tempest",
            slot="S3",
            sp_cost=35,
            initial_sp=15,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
