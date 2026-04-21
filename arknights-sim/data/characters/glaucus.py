"""Glaucus (格劳克斯) — 5* Supporter (Decel Binder archetype).

Talent "Tidal Current": every tick, all enemies within range have SLOW applied
  (move_speed -40% while status is active). This is the first on_tick AURA
  debuff — the debuff is not gated on attacking, it affects every enemy in
  range passively. The SLOW expires after 0.3s so any missed tick lets it
  lapse cleanly; each tick refreshes it for enemies still in range.

S2 "Trident Strike": on activation, applies BIND (3s) to all enemies in range
  and deals AoE arts damage once.
  sp_cost=25, initial_sp=10, AUTO_TIME, MANUAL trigger.

S3 "Tidal Prison": 20s sustained duration, MANUAL. On activation, deals 300%
  ATK arts damage to all in range and applies BIND (5s). During skill: SLOW
  aura strengthens to -60% move speed. On end: revert to normal -40% SLOW.
  sp_cost=40, initial_sp=15, AUTO_TIME, MANUAL trigger.

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
from data.characters.generated.glacus import make_glacus as _base_stats


DECEL_BINDER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 4) for dy in range(-1, 2)
))

# --- Talent: Tidal Current (aura SLOW) ---
_TALENT_TAG = "glaucus_tidal_current"
_SLOW_AMOUNT = 0.40          # 40% move speed reduction
_AURA_REFRESH_DT = 0.3       # aura expires 3 ticks after last refresh
_SLOW_TAG = "glaucus_slow_aura"

# --- S2: Trident Strike ---
_S2_TAG = "glaucus_s2_trident"
_S2_BIND_DURATION = 3.0
_S2_BIND_TAG = "glaucus_s2_bind"
_S2_DAMAGE_RATIO = 2.0       # 200% ATK arts damage

# --- S3: Tidal Prison ---
_S3_TAG = "glaucus_s3_tidal_prison"
_S3_BIND_DURATION = 5.0
_S3_BIND_TAG = "glaucus_s3_bind"
_S3_DAMAGE_RATIO = 3.0       # 300% ATK arts damage on activation
_S3_SLOW_AMOUNT = 0.60       # enhanced SLOW during skill (-60% vs normal -40%)
_S3_DURATION = 20.0


def _in_range(op: UnitState, enemy: UnitState) -> bool:
    """Simplified range check: use operator's range_shape tiles."""
    if op.position is None or enemy.position is None:
        return False
    ox, oy = op.position
    ex, ey = enemy.position
    dx = round(ex) - round(ox)
    dy = round(ey) - round(oy)
    return (dx, dy) in set(op.range_shape.tiles)


def _talent_on_tick(world, carrier: UnitState, dt: float) -> None:
    if not carrier.deployed or carrier.position is None:
        return
    elapsed = world.global_state.elapsed
    expires = elapsed + _AURA_REFRESH_DT
    # S3 enhances SLOW amount to -60%
    slow_amount = _S3_SLOW_AMOUNT if getattr(carrier, "_glaucus_s3_active", False) else _SLOW_AMOUNT
    for enemy in world.enemies():
        if not enemy.alive or not _in_range(carrier, enemy):
            continue
        enemy.statuses = [s for s in enemy.statuses if s.source_tag != _SLOW_TAG]
        enemy.statuses.append(StatusEffect(
            kind=StatusKind.SLOW,
            source_tag=_SLOW_TAG,
            expires_at=expires,
            params={"amount": slow_amount},
        ))


register_talent(_TALENT_TAG, on_tick=_talent_on_tick)


def _s2_on_start(world, carrier: UnitState) -> None:
    elapsed = world.global_state.elapsed
    for enemy in world.enemies():
        if not enemy.alive or not _in_range(carrier, enemy):
            continue
        # BIND for S2_BIND_DURATION
        enemy.statuses = [s for s in enemy.statuses if s.source_tag != _S2_BIND_TAG]
        enemy.statuses.append(StatusEffect(
            kind=StatusKind.BIND,
            source_tag=_S2_BIND_TAG,
            expires_at=elapsed + _S2_BIND_DURATION,
        ))
        # Arts damage
        raw = int(carrier.effective_atk * _S2_DAMAGE_RATIO)
        enemy.take_arts(raw)
        world.log(f"Glaucus S2 → {enemy.name}  BIND {_S2_BIND_DURATION}s  arts×{_S2_DAMAGE_RATIO}")


register_skill(_S2_TAG, on_start=_s2_on_start)


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier._glaucus_s3_active = True
    elapsed = world.global_state.elapsed
    for enemy in world.enemies():
        if not enemy.alive or not _in_range(carrier, enemy):
            continue
        enemy.statuses = [s for s in enemy.statuses if s.source_tag != _S3_BIND_TAG]
        enemy.statuses.append(StatusEffect(
            kind=StatusKind.BIND,
            source_tag=_S3_BIND_TAG,
            expires_at=elapsed + _S3_BIND_DURATION,
        ))
        raw = int(carrier.effective_atk * _S3_DAMAGE_RATIO)
        enemy.take_arts(raw)
        world.log(f"Glaucus S3 → {enemy.name}  BIND {_S3_BIND_DURATION}s  arts×{_S3_DAMAGE_RATIO}")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier._glaucus_s3_active = False


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_glaucus(slot: str = "S2") -> UnitState:
    """Glaucus E2 max. Talent: on-tick SLOW aura -40% in range. S2: AoE arts + BIND. S3: 300% arts + 5s BIND + -60% SLOW."""
    op = _base_stats()
    op.name = "Glaucus"
    op.archetype = RoleArchetype.SUP_HEXER  # Decel Binder → closest is HEXER for now
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.range_shape = DECEL_BINDER_RANGE
    op.cost = 15

    op.talents = [TalentComponent(name="Tidal Current", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Trident Strike",
            slot="S2",
            sp_cost=25,
            initial_sp=10,
            duration=0.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Tidal Prison",
            slot="S3",
            sp_cost=40,
            initial_sp=15,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
    return op
