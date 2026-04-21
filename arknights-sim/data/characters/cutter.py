"""Cutter (刻刀) — 5* Guard (Fighter archetype).

Class trait: Normal attacks deal damage twice.
Talent "Photoetched Marks" (E2): 20% chance to recover 1 additional SP per hit.

S1 "Redshift" (M3): sp_cost=15, initial_sp=5, instant (duration=0), MANUAL, AUTO_ATTACK.
  Fires 4 physical attacks at 260% ATK to random alive enemies.

S2 "Crimson Crescent" (M3): sp_cost=16, initial_sp=1, instant (duration=0), MANUAL, AUTO_ATTACK.
  AoE physical attack at 360% ATK to up to 5 nearby enemies.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, RangeShape, TalentComponent,
)
from core.types import (
    AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.cutter import make_cutter as _base_stats


FIGHTER_RANGE = RangeShape(tiles=((0, 0),))

# --- Talent: Photoetched Marks ---
_TALENT_TAG = "cutter_photoetched_marks"
_TALENT_SP_CHANCE = 0.20


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    # Trait: second physical hit
    dealt2 = target.take_physical(attacker.effective_atk)
    world.global_state.total_damage_dealt += dealt2

    # Talent: 20% chance to recover 1 extra SP
    sk = attacker.skill
    if sk is not None and not sk.active_remaining > 0:
        if world.rng.random() < _TALENT_SP_CHANCE:
            sk.sp = min(sk.sp + 1.0, float(sk.sp_cost))


register_talent(_TALENT_TAG, on_attack_hit=_talent_on_attack_hit)


# --- S1: Redshift ---
_S1_TAG = "cutter_s1_redshift"
_S1_ATK_RATIO = 2.60
_S1_HIT_COUNT = 4


def _s1_on_start(world, carrier: UnitState) -> None:
    enemies = [e for e in world.enemies() if e.alive]
    if not enemies:
        world.log("Cutter S1 Redshift — no enemies, skill wasted")
        return
    raw = int(carrier.effective_atk * _S1_ATK_RATIO)
    for _ in range(_S1_HIT_COUNT):
        target = world.rng.choice(enemies)
        dmg = target.take_physical(raw)
        world.global_state.total_damage_dealt += dmg
        enemies = [e for e in enemies if e.alive]
        if not enemies:
            break
    world.log(f"Cutter S1 Redshift — {_S1_HIT_COUNT}× {_S1_ATK_RATIO:.0%} ATK")


register_skill(_S1_TAG, on_start=_s1_on_start)


# --- S2: Crimson Crescent ---
_S2_TAG = "cutter_s2_crimson_crescent"
_S2_ATK_RATIO = 3.60
_S2_MAX_TARGETS = 5


def _s2_on_start(world, carrier: UnitState) -> None:
    enemies = [e for e in world.enemies() if e.alive][:_S2_MAX_TARGETS]
    raw = int(carrier.effective_atk * _S2_ATK_RATIO)
    for target in enemies:
        dmg = target.take_physical(raw)
        world.global_state.total_damage_dealt += dmg
    world.log(f"Cutter S2 Crimson Crescent — {_S2_ATK_RATIO:.0%} ATK × {len(enemies)} targets")


register_skill(_S2_TAG, on_start=_s2_on_start)


def make_cutter(slot: str = "S2") -> UnitState:
    """Cutter E2 max. Trait: attacks twice. Talent: 20% SP recovery. S1: 4× 260% ATK. S2: AoE 360% ATK × 5."""
    op = _base_stats()
    op.name = "Cutter"
    op.archetype = RoleArchetype.GUARD_FIGHTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = FIGHTER_RANGE
    op.talents = [TalentComponent(name="Photoetched Marks", behavior_tag=_TALENT_TAG)]

    if slot == "S1":
        op.skill = SkillComponent(
            name="Redshift",
            slot="S1",
            sp_cost=15,
            initial_sp=5,
            duration=0.0,
            sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Crimson Crescent",
            slot="S2",
            sp_cost=16,
            initial_sp=1,
            duration=0.0,
            sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
