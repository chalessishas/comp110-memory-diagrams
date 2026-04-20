"""Aak (阿梓) — 6★ Specialist (Geek archetype).

SPEC_GEEK trait: Aak's normal attacks deal Arts damage (rare for a Specialist).

Talent "Emergency Protocol": After each attack against an enemy, Aak injects
  a random in-range ally with a syringe. The injection deals _SYRINGE_TRUE_DMG
  True damage to the ally, but grants them +_SYRINGE_ATK_RATIO% ATK for
  _SYRINGE_DURATION seconds. If no ally is in range, the injection is skipped.
  Only the nearest ally (by position sort) is targeted to ensure determinism.

S2 "Medical Protocol": 15s duration. Enhanced syringe: deals _S2_SYRINGE_DMG True
  damage to the ally target but grants +_S2_ATK_RATIO% ATK for _S2_DURATION seconds.
  Also grants Aak +_S2_SELF_ATK_RATIO% self-ATK during the skill window.
  sp_cost=30, initial_sp=15, AUTO_TIME, AUTO trigger, requires_target=True.

S3 "Fatal Dose": Instant MANUAL. Injects ALL in-range allies simultaneously.
  Each ally takes 50% max HP as True damage and gains +_S3_ATK_RATIO ATK for 25s.
  sp_cost=50, initial_sp=25, AUTO_TIME, requires_target=False.

Base stats from ArknightsGameData (E2 max, trust 100, char_225_haak):
  HP=2334, ATK=753, DEF=152, RES=10, atk_interval=1.3, block=1.
"""
from __future__ import annotations
import math
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.haak import make_haak as _base_stats


GEEK_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(1, 4) for dy in range(-1, 2)
))

# Talent: Emergency Protocol — syringe injection on each attack
_TALENT_TAG = "aak_emergency_protocol"
_SYRINGE_TRUE_DMG = 400         # true damage dealt to injected ally
_SYRINGE_ATK_RATIO = 0.40       # +40% ATK buff granted to ally
_SYRINGE_DURATION = 10.0
_SYRINGE_BUFF_TAG = "aak_syringe_atk"

# S2: Medical Protocol
_S2_TAG = "aak_s2_medical_protocol"
_S2_SELF_ATK_RATIO = 0.20       # Aak gains +20% ATK during S2
_S2_SELF_ATK_BUFF_TAG = "aak_s2_self_atk"
_S2_SYRINGE_DMG = 150           # reduced self-damage during enhanced protocol
_S2_ATK_RATIO = 0.70            # +70% ATK to ally (stronger than base)
_S2_DURATION = 15.0


def _in_geek_range(attacker: UnitState, ally: UnitState) -> bool:
    if attacker.position is None or ally.position is None:
        return False
    ax, ay = attacker.position
    alx, aly = ally.position
    return any(
        (ax + dx == alx and ay + dy == aly)
        for dx, dy in GEEK_RANGE.tiles
    )


def _inject_nearest_ally(world, attacker: UnitState) -> None:
    """Inject the nearest in-range ally (sorted by distance for test determinism)."""
    is_s2 = getattr(attacker, "_aak_s2_active", False)
    dmg = _S2_SYRINGE_DMG if is_s2 else _SYRINGE_TRUE_DMG
    atk_ratio = _S2_ATK_RATIO if is_s2 else _SYRINGE_ATK_RATIO

    candidates = [
        a for a in world.allies()
        if a is not attacker and a.alive and a.deployed and _in_geek_range(attacker, a)
    ]
    if not candidates:
        return
    # deterministic: pick ally closest to attacker
    ax, ay = attacker.position
    target = min(candidates, key=lambda a: math.hypot(a.position[0] - ax, a.position[1] - ay))

    # Deal true damage to the ally
    if dmg > 0:
        dealt = target.take_true(dmg)
        world.log(
            f"Aak syringe → {target.name}  true_dmg={dealt}  "
            f"({target.hp}/{target.max_hp})"
        )

    # Apply ATK buff (refresh if already present)
    now = world.global_state.elapsed
    new_expires = now + _SYRINGE_DURATION
    existing = next((b for b in target.buffs if b.source_tag == _SYRINGE_BUFF_TAG), None)
    if existing is not None:
        existing.value = atk_ratio    # refresh ratio in case S2 upgraded it
        existing.expires_at = new_expires
    else:
        target.buffs.append(Buff(
            axis=BuffAxis.ATK, stack=BuffStack.RATIO,
            value=atk_ratio, source_tag=_SYRINGE_BUFF_TAG,
            expires_at=new_expires,
        ))
    world.log(
        f"Aak ATK buff → {target.name}  +{atk_ratio:.0%}  "
        f"({_SYRINGE_DURATION}s)"
    )


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    if damage <= 0:
        return
    _inject_nearest_ally(world, attacker)


register_talent(_TALENT_TAG, on_attack_hit=_talent_on_attack_hit)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_SELF_ATK_RATIO, source_tag=_S2_SELF_ATK_BUFF_TAG,
    ))
    carrier._aak_s2_active = True


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_SELF_ATK_BUFF_TAG]
    carrier._aak_s2_active = False


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# --- S3: Fatal Dose — instant, ALL in-range allies take 50% max HP true + ATK +45% for 25s ---
_S3_TAG = "aak_s3_fatal_dose"
_S3_HP_RATIO = 0.50             # 50% max HP as true damage to each ally
_S3_ATK_RATIO = 0.45            # +45% ATK buff
_S3_BUFF_DURATION = 25.0
_S3_BUFF_TAG = "aak_s3_atk"


def _s3_on_start(world, carrier: UnitState) -> None:
    now = world.global_state.elapsed
    expires_at = now + _S3_BUFF_DURATION
    for ally in world.allies():
        if ally is carrier or not ally.alive or not ally.deployed:
            continue
        if not _in_geek_range(carrier, ally):
            continue
        dmg = int(ally.max_hp * _S3_HP_RATIO)
        if dmg > 0:
            dealt = ally.take_true(dmg)
            world.log(f"Aak S3 Fatal Dose → {ally.name}  true_dmg={dealt}  ({ally.hp}/{ally.max_hp})")
        if ally.alive:
            existing = next((b for b in ally.buffs if b.source_tag == _S3_BUFF_TAG), None)
            if existing is not None:
                existing.value = _S3_ATK_RATIO
                existing.expires_at = expires_at
            else:
                ally.buffs.append(Buff(
                    axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                    value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
                    expires_at=expires_at,
                ))
    world.log(f"Aak S3 Fatal Dose — all in-range allies: {_S3_HP_RATIO:.0%} maxHP dmg, ATK+{_S3_ATK_RATIO:.0%} for {_S3_BUFF_DURATION}s")


register_skill(_S3_TAG, on_start=_s3_on_start)


def make_aak(slot: str = "S2") -> UnitState:
    """Aak E2 max. SPEC_GEEK: ARTS attacks; talent injects ally (true dmg + ATK buff). S2: enhanced."""
    op = _base_stats()
    op.name = "Aak"
    op.archetype = RoleArchetype.SPEC_GEEK
    op.profession = Profession.SPECIALIST
    op.attack_type = AttackType.ARTS
    op.attack_range_melee = False
    op.range_shape = GEEK_RANGE
    op.block = 1
    op.cost = 13

    op.talents = [TalentComponent(name="Emergency Protocol", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Medical Protocol",
            slot="S2",
            sp_cost=30,
            initial_sp=15,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Fatal Dose",
            slot="S3",
            sp_cost=50,
            initial_sp=25,
            duration=0.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
