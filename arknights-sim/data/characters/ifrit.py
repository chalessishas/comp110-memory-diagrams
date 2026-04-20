"""Ifrit — 6* Caster (Core Caster archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
S2 "Combustion": Instant AOE arts burst — deals 260% ATK arts damage to all enemies in range.
sp_cost=22, initial_sp=10.

S3 "Flamethrower": ATK+220%, range expands to 4×3 zone for 40s. All enemies in
  the expanded range take 60% ATK/s Arts damage (continuous burn).
  sp_cost=50, initial_sp=20, AUTO_TIME, requires_target=True.
"""
from __future__ import annotations
from math import floor
from core.state.unit_state import UnitState, SkillComponent, RangeShape, TalentComponent, Buff
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.ifrit import make_ifrit as _base_stats


# --- Talent: Injection ---
_INJECTION_TAG = "ifrit_injection"
_INJECTION_BUFF_TAG = "ifrit_injection_def"
_DEF_REDUCTION = 0.15    # -15% DEF (E2 max)
_INJECTION_DURATION = 10.0


def _injection_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    now = world.global_state.elapsed
    new_expires = now + _INJECTION_DURATION
    existing = next((b for b in target.buffs if b.source_tag == _INJECTION_BUFF_TAG), None)
    if existing is not None:
        existing.expires_at = new_expires
    else:
        target.buffs.append(Buff(
            axis=BuffAxis.DEF, stack=BuffStack.RATIO,
            value=-_DEF_REDUCTION, source_tag=_INJECTION_BUFF_TAG,
            expires_at=new_expires,
        ))


register_talent(_INJECTION_TAG, on_attack_hit=_injection_on_attack_hit)


# Ifrit fires straight ahead in a 1×5 line (standard Core Caster range)
CORE_CASTER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0),
    (1, 1), (2, 1),
    (1, -1), (2, -1),
))

_S2_TAG = "ifrit_s2_combustion"
_S2_ATK_MULTIPLIER = 2.60   # 260% ATK at rank 7


def _s2_on_start(world, carrier: UnitState) -> None:
    """Instant AOE: deal 260% ATK arts damage to all enemies in range."""
    if carrier.position is None:
        return
    ox, oy = carrier.position
    tiles = set(carrier.range_shape.tiles)
    burst_atk = int(floor(carrier.effective_atk * _S2_ATK_MULTIPLIER))
    for enemy in world.enemies():
        if not enemy.alive or enemy.position is None:
            continue
        dx = round(enemy.position[0]) - round(ox)
        dy = round(enemy.position[1]) - round(oy)
        if (dx, dy) not in tiles:
            continue
        dealt = enemy.take_arts(burst_atk)
        world.global_state.total_damage_dealt += dealt
        world.log(
            f"Ifrit S2 burst → {enemy.name}  dmg={dealt}  ({enemy.hp}/{enemy.max_hp})"
        )


register_skill(_S2_TAG, on_start=_s2_on_start)


# --- S3: Flamethrower — range expand + ATK+220% + burn aura ---
_S3_TAG = "ifrit_s3_flamethrower"
_S3_ATK_RATIO = 2.20          # ATK +220%
_S3_BUFF_TAG = "ifrit_s3_atk"
_S3_BURN_RATIO = 0.60         # 60% ATK/s Arts damage to all in expanded range
_S3_DURATION = 40.0
_S3_DMG_ACCUM = "_ifrit_s3_burn_accum"

_S3_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(1, 5) for dy in range(-1, 2)
))  # 4-wide, 3-tall expanded burn zone


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier._saved_range = carrier.range_shape
    carrier.range_shape = _S3_RANGE
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))
    setattr(carrier, _S3_DMG_ACCUM, 0.0)
    world.log(f"Ifrit S3 Flamethrower — ATK+{_S3_ATK_RATIO:.0%}, burn zone 4×3 / {_S3_DURATION}s")


def _s3_on_tick(world, carrier: UnitState, dt: float) -> None:
    accum = getattr(carrier, _S3_DMG_ACCUM, 0.0) + dt
    pulses = int(accum + 1e-9)
    setattr(carrier, _S3_DMG_ACCUM, accum - pulses)
    if pulses <= 0 or carrier.position is None:
        return
    raw = int(carrier.effective_atk * _S3_BURN_RATIO * pulses)
    ox, oy = carrier.position
    tiles = set(carrier.range_shape.tiles)
    for enemy in world.enemies():
        if not enemy.alive or not enemy.deployed or enemy.position is None:
            continue
        dx = round(enemy.position[0]) - round(ox)
        dy = round(enemy.position[1]) - round(oy)
        if (dx, dy) not in tiles:
            continue
        dealt = enemy.take_arts(raw)
        world.global_state.total_damage_dealt += dealt


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.range_shape = getattr(carrier, "_saved_range", CORE_CASTER_RANGE)
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]
    setattr(carrier, _S3_DMG_ACCUM, 0.0)


register_skill(_S3_TAG, on_start=_s3_on_start, on_tick=_s3_on_tick, on_end=_s3_on_end)


def make_ifrit(slot: str = "S2") -> UnitState:
    """Ifrit E2 max, trust 100. S2 Combustion wired."""
    op = _base_stats()
    op.name = "Ifrit"
    op.archetype = RoleArchetype.CASTER_CORE
    op.range_shape = CORE_CASTER_RANGE
    op.cost = 34
    op.talents = [TalentComponent(name="Injection", behavior_tag=_INJECTION_TAG)]
    if slot == "S2":
        op.skill = SkillComponent(
            name="Combustion",
            slot="S2",
            sp_cost=22,
            initial_sp=10,
            duration=0.0,   # instant — fires once and SP resets
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            behavior_tag=_S2_TAG,
            requires_target=True,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Flamethrower",
            slot="S3",
            sp_cost=50,
            initial_sp=20,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            behavior_tag=_S3_TAG,
            requires_target=False,   # area burn, no attack target needed
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
