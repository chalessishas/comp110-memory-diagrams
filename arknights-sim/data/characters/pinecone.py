"""Pinecone (松果) — 5★ Sniper (Artillery archetype).

SNIPER_ARTILLERY trait: Each attack deals full Physical damage to the primary
  target AND simultaneously deals Arts damage equal to 80% of ATK to all
  enemies within a 0.9-tile radius around the target. The secondary Arts
  splash fires via an on_attack_hit talent hook after the main physical hit.
  Primary is reduced by enemy DEF; splash is reduced by enemy RES.

Talent "Blast Shell" (爆裂弹): After each physical hit, deal Arts splash
  (80% of ATK) to enemies within 0.9 tiles of the primary target.

S2 "Heavy Barrage" (重炮齐射): 20s duration. ATK+30%; splash radius expands
  from 0.9 to 1.5 tiles. Radius is read dynamically from skill state.
  sp_cost=35, initial_sp=15, AUTO_TIME, AUTO trigger, requires_target=True.

Base stats from ArknightsGameData (E2 max, trust 100, char_440_pinecn).
  HP=2200, ATK=722, DEF=167, RES=0, atk_interval=2.3s, cost=30, block=1.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.pinecn import make_pinecn as _base_stats


# Long-range forward field (4 tiles ahead × 3 rows)
ARTILLERY_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(1, 5) for dy in range(-1, 2)
))

# Talent: Blast Shell (physical hit → Arts AoE splash)
_TALENT_TAG = "pinecone_blast_shell"
_ARTS_SPLASH_RATIO = 0.80     # Arts splash = 80% of ATK
_SPLASH_RADIUS = 0.9          # base AoE radius in tiles

# S2: Heavy Barrage
_S2_TAG = "pinecone_s2_heavy_barrage"
_S2_ATK_RATIO = 0.30
_S2_ATK_BUFF_TAG = "pinecone_s2_atk"
_S2_SPLASH_RADIUS = 1.5       # expanded radius during S2
_S2_DURATION = 20.0


def _blast_shell_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    """After each physical hit, emit Arts AoE splash around the target."""
    if damage <= 0 or target.position is None:
        return
    is_s2 = attacker.skill is not None and attacker.skill.active_remaining > 0
    radius = _S2_SPLASH_RADIUS if is_s2 else _SPLASH_RADIUS
    arts_raw = int(attacker.effective_atk * _ARTS_SPLASH_RATIO)
    if arts_raw <= 0:
        return
    tx, ty = target.position
    for other in world.enemies():
        if other is target or not other.alive or other.position is None:
            continue
        ox, oy = other.position
        if (ox - tx) ** 2 + (oy - ty) ** 2 <= radius ** 2:
            dealt = other.take_arts(arts_raw)
            if dealt > 0:
                world.global_state.total_damage_dealt += dealt
                world.log(
                    f"Pinecone Blast Shell → {other.name}  arts={dealt}  "
                    f"({other.hp}/{other.max_hp})"
                )


register_talent(_TALENT_TAG, on_attack_hit=_blast_shell_on_attack_hit)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_ATK_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# S3: Grand Barrage — ATK+100%, splash radius 2.5, _attack_all_in_range=True
_S3_TAG = "pinecone_s3_grand_barrage"
_S3_ATK_RATIO = 1.00
_S3_ATK_BUFF_TAG = "pinecone_s3_atk"
_S3_SPLASH_RADIUS = 2.5
_S3_DURATION = 20.0


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))
    carrier._attack_all_in_range = True
    world.log(f"Pinecone S3 Grand Barrage — ATK+{_S3_ATK_RATIO:.0%}, splash {_S3_SPLASH_RADIUS}t, AoE primary")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_ATK_BUFF_TAG]
    carrier._attack_all_in_range = False


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_pinecone(slot: str = "S2") -> UnitState:
    """Pinecone E2 max. SNIPER_ARTILLERY: physical hit + Arts AoE splash. S3: ATK+100%, splash 2.5t, AoE."""
    op = _base_stats()
    op.name = "Pinecone"
    op.archetype = RoleArchetype.SNIPER_ARTILLERY
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = False
    op.range_shape = ARTILLERY_RANGE
    op.block = 1
    op.cost = 30

    op.talents = [TalentComponent(name="Blast Shell", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Heavy Barrage",
            slot="S2",
            sp_cost=35,
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
            name="Grand Barrage",
            slot="S3",
            sp_cost=45,
            initial_sp=20,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
