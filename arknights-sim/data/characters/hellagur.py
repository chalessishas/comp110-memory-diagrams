"""Hellagur (赫拉格) — 6* Guard (Musha archetype).

Musha Guard trait: Cannot be healed by other allied operators while HP > 50%.
  Implemented via heal_block_threshold=0.5 on UnitState.
  Healers skip Hellagur when his HP is above threshold (targeting + application guard).

Talent "True Warrior" (E2): Each attack restores HP equal to 8% of damage dealt (lifesteal).
  Implemented as on_attack_hit callback. Always active (not skill-gated).

S2 "Tenacity" (simplified): ATK +200%, 30s duration.
  sp_cost=50, initial_sp=30, AUTO_TIME, AUTO trigger, requires_target=True.
  (S3 not implemented; S2 is the core combat skill.)

Base stats from ArknightsGameData (E2 max, trust 100, char_188_helage).
  HP=4225, ATK=832, DEF=334, RES=0, atk_interval=1.2s, cost=26, block=1.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.helage import make_helage as _base_stats


GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_MUSHA_HEAL_BLOCK_THRESHOLD = 0.50   # Cannot receive external heals above 50% HP

# --- Talent: True Warrior ---
_TALENT_TAG = "hellagur_true_warrior"
_LIFESTEAL_RATIO = 0.08   # 8% of damage dealt restores HP

# --- S2: Tenacity ---
_S2_TAG = "hellagur_s2_tenacity"
_S2_ATK_RATIO = 2.00
_S2_BUFF_TAG = "hellagur_s2_atk"
_S2_DURATION = 30.0


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    heal_amount = max(1, int(damage * _LIFESTEAL_RATIO))
    if attacker.hp < attacker.max_hp:
        healed = attacker.heal(heal_amount)
        world.global_state.total_healing_done += healed


register_talent(_TALENT_TAG, on_attack_hit=_talent_on_attack_hit)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_hellagur(slot: str = "S2") -> UnitState:
    """Hellagur E2 max. GUARD_MUSHA: heal-blocked above 50% HP; 8% lifesteal."""
    op = _base_stats()
    op.name = "Hellagur"
    op.archetype = RoleArchetype.GUARD_MUSHA
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = True
    op.range_shape = GUARD_RANGE
    op.block = 1
    op.cost = 26
    op.heal_block_threshold = _MUSHA_HEAL_BLOCK_THRESHOLD

    op.talents = [TalentComponent(name="True Warrior", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Tenacity",
            slot="S2",
            sp_cost=50,
            initial_sp=30,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    return op
