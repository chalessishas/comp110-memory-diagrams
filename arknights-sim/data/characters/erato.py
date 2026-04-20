"""Erato (埃拉托) — 5* Sniper (Besieger archetype).

Class trait: Prioritizes attacking heaviest enemy; deals 1.5× ATK to blocked enemies.

S1 "Strafing Fire": ATK +100% for 20s.
  sp_cost=30, initial_sp=10, AUTO_TIME, AUTO trigger, requires_target=True.

Base stats: E2 max, trust 100 (generated/erato.py).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import AttackType, BuffAxis, BuffStack, Profession, RoleArchetype, SPGainMode, SkillTrigger
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.erato import make_erato as _base_stats


# --- Talent: Precision Strike — 10% crit chance on attacks ---
_TALENT_TAG = "erato_precision_strike"
_CRIT_CHANCE = 0.10


def _precision_on_battle_start(world, carrier: UnitState) -> None:
    carrier.crit_chance = _CRIT_CHANCE
    world.log(f"Erato Precision Strike — crit_chance = {_CRIT_CHANCE:.0%}")


register_talent(_TALENT_TAG, on_battle_start=_precision_on_battle_start)

# Standard Besieger Sniper range: 3 forward + flanking tiles
BESIEGER_RANGE_5STAR = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0),
    (1, -1), (1, 1), (2, -1), (2, 1),
))

# --- S2: Killshot ---
_S2_TAG = "erato_s2_killshot"
_S2_ATK_RATIO = 2.00    # ATK +200% → each shot deals 3× base ATK
_S2_AMMO = 3            # 3 heavy rounds
_S2_SOURCE_TAG = "erato_s2_killshot"


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_SOURCE_TAG,
    ))
    world.log(f"Erato S2 Killshot — {_S2_AMMO} rounds, ATK+{_S2_ATK_RATIO:.0%}")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_SOURCE_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# --- S1: Strafing Fire ---
_S1_TAG = "erato_s1_strafing_fire"
_S1_ATK_RATIO = 1.00     # ATK +100%
_S1_SOURCE_TAG = "erato_s1_strafing_fire"


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_SOURCE_TAG,
    ))
    world.log(f"Erato S1 Strafing Fire — ATK +{_S1_ATK_RATIO:.0%}")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_SOURCE_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_erato(slot: str = "S1") -> UnitState:
    """Erato E2 max. Besieger: targets heaviest enemy; 1.5× ATK to blocked enemies. S1: ATK+100% 20s."""
    op = _base_stats()
    op.name = "Erato"
    op.archetype = RoleArchetype.SNIPER_SIEGE
    op.profession = Profession.SNIPER
    op.range_shape = BESIEGER_RANGE_5STAR
    op.block = 1
    op.cost = 23
    op.talents = [TalentComponent(name="Precision Strike", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Killshot",
            slot="S2",
            sp_cost=35,
            initial_sp=15,
            duration=0.0,
            ammo_count=_S2_AMMO,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S1":
        op.skill = SkillComponent(
            name="Strafing Fire",
            slot="S1",
            sp_cost=30,
            initial_sp=10,
            duration=20.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S1_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
