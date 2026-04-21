"""Franka (芙兰卡) — 5* Guard (Dreadnought archetype).

Talent "Thermite Blade" (E2): 20% chance to ignore target's DEF on each attack.
  Modeled as: proc → deal min(effective_def, effective_atk) as true damage bonus.

S1 "Swift Strike γ" (M3): AUTO, sp_cost=40, initial_sp=10, duration=35s, AUTO_TIME.
  ATK+34%, ASPD+35 while active.

S2 "Vorpal Edge" (M3): AUTO, sp_cost=20, initial_sp=5, duration=26s, AUTO_TIME.
  ATK+70%; every attack ignores target DEF completely; Talent proc chance × 2.5 (50%).

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape, TalentComponent,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.franka import make_franka as _base_stats


DREADNOUGHT_RANGE = RangeShape(tiles=((0, 0),))

# --- Talent: Thermite Blade ---
_TALENT_TAG = "franka_thermite_blade"
_TALENT_PROC_CHANCE = 0.20       # 20% base
_TALENT_S2_PROC_CHANCE = 0.50   # 50% during S2 (×2.5)


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    if attacker.attack_type != AttackType.PHYSICAL:
        return

    s2_active = getattr(attacker, "_franka_s2_active", False)

    if s2_active:
        # Full DEF ignore guaranteed during S2
        bonus = min(target.effective_def, attacker.effective_atk)
        if bonus > 0:
            world.global_state.total_damage_dealt += target.take_true(bonus)
        # Talent additional hit at 50% chance
        if world.rng.random() < _TALENT_S2_PROC_CHANCE:
            extra = target.take_physical(attacker.effective_atk)
            world.global_state.total_damage_dealt += extra
    else:
        # Thermite Blade: 20% chance to ignore DEF
        if world.rng.random() < _TALENT_PROC_CHANCE:
            bonus = min(target.effective_def, attacker.effective_atk)
            if bonus > 0:
                world.global_state.total_damage_dealt += target.take_true(bonus)


register_talent(_TALENT_TAG, on_attack_hit=_talent_on_attack_hit)


# --- S1: Swift Strike γ ---
_S1_TAG = "franka_s1_swift_strike"
_S1_ATK_RATIO = 0.34
_S1_ASPD = 35.0
_S1_BUFF_TAG = "franka_s1_buff"
_S1_DURATION = 35.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
        value=_S1_ASPD, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Franka S1 Swift Strike γ — ATK+{_S1_ATK_RATIO:.0%}, ASPD+{_S1_ASPD:.0f}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


# --- S2: Vorpal Edge ---
_S2_TAG = "franka_s2_vorpal_edge"
_S2_ATK_RATIO = 0.70
_S2_BUFF_TAG = "franka_s2_buff"
_S2_DURATION = 26.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    carrier._franka_s2_active = True
    world.log(f"Franka S2 Vorpal Edge — ATK+{_S2_ATK_RATIO:.0%}, full DEF ignore/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]
    carrier._franka_s2_active = False


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_franka(slot: str = "S2") -> UnitState:
    """Franka E2 max. Talent: 20% DEF ignore. S1: ATK+34%/ASPD+35/35s AUTO. S2: ATK+70%/full DEF ignore/26s AUTO."""
    op = _base_stats()
    op.name = "Franka"
    op.archetype = RoleArchetype.GUARD_DREADNOUGHT
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = DREADNOUGHT_RANGE
    op.talents = [TalentComponent(name="Thermite Blade", behavior_tag=_TALENT_TAG)]

    if slot == "S1":
        op.skill = SkillComponent(
            name="Swift Strike γ",
            slot="S1",
            sp_cost=40,
            initial_sp=10,
            duration=_S1_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S1_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Vorpal Edge",
            slot="S2",
            sp_cost=20,
            initial_sp=5,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
