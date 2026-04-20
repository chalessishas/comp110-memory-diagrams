"""Typhon (提丰) — 6* Sniper (Besieger archetype).

Class trait: Prioritizes attacking heaviest enemy; deals 1.5× ATK to blocked enemies.

S3 "Eternal Hunt": Loads 5 ammo arrows. Each attack during S3 fires 1 arrow for
  ATK ×3 physical damage (ATK +200%). Skill ends when all 5 arrows are consumed.
  sp_cost=40, initial_sp=20, AUTO_TIME, AUTO trigger, requires_target=True.

Base stats: E2 max, trust 100 (generated/typhon.py).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import BuffAxis, BuffStack, Profession, RoleArchetype, SPGainMode, SkillTrigger
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.typhon import make_typhon as _base_stats

# 6-tile wide forward range: 4 forward + 2 flanking rows
BESIEGER_RANGE_6STAR = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0), (4, 0),
    (1, -1), (1, 1), (2, -1), (2, 1), (3, -1), (3, 1),
))

# --- Talent: King's Sight — bonus True damage to blocked enemies ---
_TALENT_TAG = "typhon_kings_sight"
_TALENT_BONUS_RATIO = 0.40   # +40% ATK True damage to blocked enemies (wiki M3)


def _kings_sight_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    if len(target.blocked_by_unit_ids) > 0:
        bonus = int(attacker.effective_atk * _TALENT_BONUS_RATIO)
        dealt = target.take_true(bonus)
        world.global_state.total_damage_dealt += dealt
        world.log(f"Typhon King's Sight → {target.name}  true_bonus={dealt}")


register_talent(_TALENT_TAG, on_attack_hit=_kings_sight_on_attack_hit)


# --- S3: Eternal Hunt ---
_S3_TAG = "typhon_s3_eternal_hunt"
_S3_ATK_RATIO = 2.00     # ATK +200% → each arrow deals 3× base ATK
_S3_AMMO = 5             # 5 arrows per activation
_S3_SOURCE_TAG = "typhon_s3_eternal_hunt"


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_SOURCE_TAG,
    ))
    world.log(f"Typhon S3 Eternal Hunt — {_S3_AMMO} arrows, ATK +{_S3_ATK_RATIO:.0%}")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_SOURCE_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_typhon(slot: str = "S3") -> UnitState:
    """Typhon E2 max. Besieger: targets heaviest enemy; 1.5× ATK to blocked enemies. S3: 5-ammo ATK+200%."""
    op = _base_stats()
    op.name = "Typhon"
    op.archetype = RoleArchetype.SNIPER_SIEGE
    op.profession = Profession.SNIPER
    op.range_shape = BESIEGER_RANGE_6STAR
    op.block = 1
    op.cost = 24
    op.talents = [TalentComponent(name="King's Sight", behavior_tag=_TALENT_TAG)]

    if slot == "S3":
        op.skill = SkillComponent(
            name="Eternal Hunt",
            slot="S3",
            sp_cost=40,
            initial_sp=20,
            duration=0.0,            # ammo-based, not duration-based
            ammo_count=_S3_AMMO,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
